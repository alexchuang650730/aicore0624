"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatProvider = void 0;
class ChatProvider {
    constructor(_extensionUri, _mcpService) {
        this._extensionUri = _extensionUri;
        this._mcpService = _mcpService;
    }
    resolveWebviewView(webviewView, context, _token) {
        console.log('ChatProvider: resolveWebviewView called');
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        // 處理來自 webview 的消息
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'sendMessage':
                    await this._handleSendMessage(message.text);
                    break;
                case 'clearChat':
                    this._clearChat();
                    break;
            }
        }, undefined, []);
        console.log('ChatProvider: HTML set successfully');
    }
    refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }
    async _handleSendMessage(text) {
        if (!text.trim())
            return;
        // 顯示用戶消息
        this._addMessage('user', text);
        try {
            // 通過 MCP 服務發送消息
            const response = await this._mcpService.sendChatMessage(text);
            this._addMessage('assistant', response);
        }
        catch (error) {
            this._addMessage('assistant', `錯誤: ${error}`);
        }
    }
    _addMessage(sender, text) {
        if (this._view) {
            this._view.webview.postMessage({
                command: 'addMessage',
                sender: sender,
                text: text,
                timestamp: new Date().toLocaleTimeString()
            });
        }
    }
    _clearChat() {
        if (this._view) {
            this._view.webview.postMessage({
                command: 'clearChat'
            });
        }
    }
    _getHtmlForWebview(webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Assistant</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                }
                .header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 12px 16px;
                    border-bottom: 1px solid var(--vscode-panel-border);
                    background-color: var(--vscode-sideBar-background);
                }
                .title {
                    display: flex;
                    align-items: center;
                    font-weight: bold;
                }
                .icon {
                    margin-right: 8px;
                    font-size: 16px;
                }
                .clear-btn {
                    background: none;
                    border: none;
                    color: var(--vscode-textLink-foreground);
                    cursor: pointer;
                    padding: 4px 8px;
                    border-radius: 4px;
                }
                .clear-btn:hover {
                    background-color: var(--vscode-list-hoverBackground);
                }
                .chat-container {
                    flex: 1;
                    overflow-y: auto;
                    padding: 16px;
                }
                .message {
                    margin-bottom: 16px;
                    padding: 12px;
                    border-radius: 8px;
                    max-width: 80%;
                }
                .message.user {
                    background-color: var(--vscode-textBlockQuote-background);
                    margin-left: auto;
                    text-align: right;
                }
                .message.assistant {
                    background-color: var(--vscode-textCodeBlock-background);
                    margin-right: auto;
                }
                .message-header {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                    margin-bottom: 4px;
                }
                .message-content {
                    line-height: 1.4;
                }
                .input-container {
                    display: flex;
                    padding: 16px;
                    border-top: 1px solid var(--vscode-panel-border);
                    background-color: var(--vscode-sideBar-background);
                }
                .input-field {
                    flex: 1;
                    background-color: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    border-radius: 4px;
                    padding: 8px 12px;
                    margin-right: 8px;
                    font-family: inherit;
                    font-size: inherit;
                }
                .input-field:focus {
                    outline: none;
                    border-color: var(--vscode-focusBorder);
                }
                .send-btn {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    cursor: pointer;
                    font-family: inherit;
                }
                .send-btn:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                .send-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                .welcome {
                    text-align: center;
                    color: var(--vscode-descriptionForeground);
                    margin-top: 32px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">
                    <span class="icon">🤖</span>
                    AI Assistant
                </div>
                <button class="clear-btn" onclick="clearChat()">🗑️ Clear</button>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="welcome">
                    <p>👋 歡迎使用 PowerAutomation AI Assistant</p>
                    <p>基於 SmartInvention-Manus HITL 流程</p>
                    <p>請輸入您的問題或請求...</p>
                </div>
            </div>
            
            <div class="input-container">
                <input 
                    type="text" 
                    id="messageInput" 
                    class="input-field" 
                    placeholder="輸入您的消息..."
                    onkeypress="handleKeyPress(event)"
                />
                <button class="send-btn" onclick="sendMessage()" id="sendBtn">發送</button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const text = input.value.trim();
                    
                    if (!text) return;
                    
                    // 禁用發送按鈕
                    const sendBtn = document.getElementById('sendBtn');
                    sendBtn.disabled = true;
                    sendBtn.textContent = '發送中...';
                    
                    // 清空輸入框
                    input.value = '';
                    
                    // 發送消息到擴展
                    vscode.postMessage({
                        command: 'sendMessage',
                        text: text
                    });
                }
                
                function handleKeyPress(event) {
                    if (event.key === 'Enter') {
                        sendMessage();
                    }
                }
                
                function clearChat() {
                    const chatContainer = document.getElementById('chatContainer');
                    chatContainer.innerHTML = \`
                        <div class="welcome">
                            <p>👋 歡迎使用 PowerAutomation AI Assistant</p>
                            <p>基於 SmartInvention-Manus HITL 流程</p>
                            <p>請輸入您的問題或請求...</p>
                        </div>
                    \`;
                    
                    vscode.postMessage({
                        command: 'clearChat'
                    });
                }
                
                function addMessage(sender, text, timestamp) {
                    const chatContainer = document.getElementById('chatContainer');
                    
                    // 移除歡迎消息
                    const welcome = chatContainer.querySelector('.welcome');
                    if (welcome) {
                        welcome.remove();
                    }
                    
                    const messageDiv = document.createElement('div');
                    messageDiv.className = \`message \${sender}\`;
                    
                    const senderName = sender === 'user' ? '您' : 'AI Assistant';
                    
                    messageDiv.innerHTML = \`
                        <div class="message-header">\${senderName} - \${timestamp}</div>
                        <div class="message-content">\${text}</div>
                    \`;
                    
                    chatContainer.appendChild(messageDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
                    // 重新啟用發送按鈕
                    const sendBtn = document.getElementById('sendBtn');
                    sendBtn.disabled = false;
                    sendBtn.textContent = '發送';
                }
                
                // 監聽來自擴展的消息
                window.addEventListener('message', event => {
                    const message = event.data;
                    
                    switch (message.command) {
                        case 'addMessage':
                            addMessage(message.sender, message.text, message.timestamp);
                            break;
                        case 'clearChat':
                            // 已在 clearChat 函數中處理
                            break;
                    }
                });
            </script>
        </body>
        </html>`;
    }
}
exports.ChatProvider = ChatProvider;
ChatProvider.viewType = 'powerautomation.chat';
//# sourceMappingURL=ChatProvider.js.map