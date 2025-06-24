"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatProvider = void 0;
const vscode = __importStar(require("vscode"));
class ChatProvider {
    constructor(_extensionUri, _mcpServerManager) {
        this._extensionUri = _extensionUri;
        this._mcpServerManager = _mcpServerManager;
    }
    resolveWebviewView(webviewView, context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        // 處理來自webview的消息
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'sendMessage':
                    await this._handleChatMessage(message.text);
                    break;
                case 'analyzeFile':
                    await this._analyzeFile(message.fileName);
                    break;
            }
        }, undefined, []);
    }
    refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }
    async _handleChatMessage(text) {
        if (!this._view)
            return;
        // 發送消息到MCP服務器處理
        try {
            const response = await this._mcpServerManager.sendMessage(text);
            this._view.webview.postMessage({
                type: 'addMessage',
                message: {
                    type: 'assistant',
                    content: response,
                    timestamp: new Date().toLocaleTimeString()
                }
            });
        }
        catch (error) {
            this._view.webview.postMessage({
                type: 'addMessage',
                message: {
                    type: 'assistant',
                    content: `抱歉，處理您的請求時出現錯誤：${error}`,
                    timestamp: new Date().toLocaleTimeString()
                }
            });
        }
    }
    async _analyzeFile(fileName) {
        if (!this._view)
            return;
        try {
            const analysis = await this._mcpServerManager.analyzeFile(fileName);
            this._view.webview.postMessage({
                type: 'addMessage',
                message: {
                    type: 'assistant',
                    content: `📄 文件分析結果：\\n\\n${analysis}`,
                    timestamp: new Date().toLocaleTimeString()
                }
            });
        }
        catch (error) {
            this._view.webview.postMessage({
                type: 'addMessage',
                message: {
                    type: 'assistant',
                    content: `文件分析失敗：${error}`,
                    timestamp: new Date().toLocaleTimeString()
                }
            });
        }
    }
    _getHtmlForWebview(webview) {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const isMinimalMode = config.get('minimalMode', false);
        if (isMinimalMode) {
            return `<!DOCTYPE html>
<html><body style="display:none;"></body></html>`;
        }
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant Chat</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .chat-header {
            padding: 16px;
            background: var(--vscode-panel-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-title {
            font-size: 14px;
            font-weight: 600;
        }

        .chat-status {
            font-size: 10px;
            color: var(--vscode-terminal-ansiGreen);
            background: rgba(0, 255, 0, 0.1);
            padding: 2px 6px;
            border-radius: 2px;
        }

        .chat-messages {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            background: var(--vscode-editor-background);
        }

        .message {
            margin-bottom: 16px;
            max-width: 85%;
        }

        .message.user {
            margin-left: auto;
            text-align: right;
        }

        .message-content {
            display: inline-block;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 13px;
            line-height: 1.4;
            word-wrap: break-word;
            white-space: pre-wrap;
        }

        .message.user .message-content {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border-bottom-right-radius: 4px;
        }

        .message.assistant .message-content {
            background: var(--vscode-input-background);
            color: var(--vscode-foreground);
            border-bottom-left-radius: 4px;
        }

        .message-time {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-top: 4px;
        }

        .chat-input-area {
            padding: 16px;
            background: var(--vscode-panel-background);
            border-top: 1px solid var(--vscode-panel-border);
        }

        .chat-input {
            width: 100%;
            padding: 10px 12px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            color: var(--vscode-input-foreground);
            font-size: 13px;
            resize: none;
            min-height: 60px;
            font-family: inherit;
            box-sizing: border-box;
        }

        .chat-input:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        .chat-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
        }

        .input-actions {
            display: flex;
            gap: 6px;
        }

        .input-action {
            padding: 4px 8px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 3px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 10px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .input-action:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .send-button {
            padding: 6px 14px;
            background: var(--vscode-button-background);
            border: none;
            border-radius: 4px;
            color: var(--vscode-button-foreground);
            font-size: 11px;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.2s;
        }

        .send-button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .send-button:disabled {
            background: var(--vscode-button-secondaryBackground);
            cursor: not-allowed;
        }

        .typing-indicator {
            display: none;
            padding: 8px 14px;
            background: var(--vscode-input-background);
            border-radius: 12px;
            margin-bottom: 16px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .typing-indicator.show {
            display: block;
        }

        /* 滾動條樣式 */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: var(--vscode-scrollbarSlider-background);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--vscode-scrollbarSlider-hoverBackground);
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="chat-header">
        <div class="chat-title">💬 AI助手對話</div>
        <div class="chat-status">在線</div>
    </div>

    <div class="chat-messages" id="chatMessages">
        <div class="message assistant">
            <div class="message-content">
                您好！我是PowerAutomation AI助手。我可以幫您：

• 🔍 分析代碼和文檔
• 🧪 運行Manus自動化測試
• 📊 生成報告和統計
• 🤖 管理MCP適配器
• 📁 處理文件和數據

請告訴我您需要什麼幫助，或者從右側選擇文件進行分析。
            </div>
            <div class="message-time">剛剛</div>
        </div>
    </div>

    <div class="typing-indicator" id="typingIndicator">
        AI正在思考中...
    </div>

    <div class="chat-input-area">
        <textarea class="chat-input" id="chatInput" 
                  placeholder="輸入您的問題或指令..."></textarea>
        <div class="chat-actions">
            <div class="input-actions">
                <button class="input-action" onclick="attachFile()">📎 附件</button>
                <button class="input-action" onclick="insertCode()">💻 代碼</button>
                <button class="input-action" onclick="clearChat()">🗑️ 清空</button>
            </div>
            <button class="send-button" id="sendButton" onclick="sendMessage()">發送</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let messageHistory = [];

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'addMessage':
                    addMessage(message.message);
                    break;
            }
        });

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const text = input.value.trim();
            
            if (!text) return;

            // 添加用戶消息
            addMessage({
                type: 'user',
                content: text,
                timestamp: new Date().toLocaleTimeString()
            });

            // 清空輸入框
            input.value = '';
            
            // 顯示輸入指示器
            showTypingIndicator();

            // 發送到擴展處理
            vscode.postMessage({
                type: 'sendMessage',
                text: text
            });
        }

        function addMessage(message) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = \`message \${message.type}\`;
            
            messageDiv.innerHTML = \`
                <div class="message-content">\${message.content}</div>
                <div class="message-time">\${message.timestamp}</div>
            \`;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            // 隱藏輸入指示器
            hideTypingIndicator();
            
            messageHistory.push(message);
        }

        function showTypingIndicator() {
            document.getElementById('typingIndicator').classList.add('show');
        }

        function hideTypingIndicator() {
            document.getElementById('typingIndicator').classList.remove('show');
        }

        function attachFile() {
            vscode.postMessage({
                type: 'attachFile'
            });
        }


        function clearChat() {
            document.getElementById('chatMessages').innerHTML = '';
            messageHistory = [];
        }

        // 鍵盤快捷鍵
        document.getElementById('chatInput').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                sendMessage();
            }
            
            // 自動調整高度
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });

        // 初始化
        document.getElementById('chatInput').focus();
    </script>
</body>
</html>`;
    }
}
exports.ChatProvider = ChatProvider;
ChatProvider.viewType = 'powerautomation.chat';
//# sourceMappingURL=ChatProvider.js.map