import * as vscode from 'vscode';
import { MCPServerManager } from '../services/MCPServerManager';
import { AuthenticationService } from '../services/AuthenticationService';
import axios from 'axios';

export class ChatProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'powerautomation.chat';
    private _view?: vscode.WebviewView;
    private _authService?: AuthenticationService;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _mcpServerManager: MCPServerManager,
        authService?: AuthenticationService
    ) {
        this._authService = authService;
    }

    public setAuthService(authService: AuthenticationService) {
        this._authService = authService;
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        // 立即設置 HTML 內容
        try {
            webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
            console.log('✅ ChatProvider HTML 設置成功');
        } catch (error) {
            console.error('❌ ChatProvider HTML 設置失敗:', error);
        }

        // 處理來自webview的消息
        webviewView.webview.onDidReceiveMessage(
            async message => {
                try {
                    switch (message.type) {
                        case 'sendMessage':
                            await this._handleChatMessage(message.text);
                            break;
                        case 'analyzeFile':
                            await this._analyzeFile(message.fileName);
                            break;
                        case 'powerautomation':
                            await this._handlePowerAutomationMessage(message);
                            break;
                        case 'clearHistory':
                            await this._clearChatHistory();
                            break;
                        case 'exportHistory':
                            await this._exportChatHistory();
                            break;
                    }
                } catch (error) {
                    console.error('ChatProvider 消息處理錯誤:', error);
                    this._sendErrorToWebview(error as Error);
                }
            },
            undefined,
            []
        );
    }

    public refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }

    private async _handleChatMessage(text: string) {
        if (!this._authService?.isAuthenticated()) {
            this._sendErrorToWebview(new Error('請先登錄以使用AI助手功能'));
            return;
        }

        if (!this._authService.hasPermission('chat')) {
            this._sendErrorToWebview(new Error('您沒有權限使用聊天功能'));
            return;
        }

        if (!this._view) return;

        try {
            // 顯示用戶消息
            this._view.webview.postMessage({
                type: 'userMessage',
                message: text,
                timestamp: new Date().toISOString()
            });

            // 顯示正在思考狀態
            this._view.webview.postMessage({
                type: 'thinking',
                message: 'AI 正在思考中...'
            });

            // 獲取用戶信息
            const user = this._authService.getCurrentUser();
            const config = vscode.workspace.getConfiguration('powerautomation');
            const endpoint = config.get<string>('mcpEndpoint', 'http://18.212.97.173:8080');

            // 構建請求
            const requestData = {
                request: text,
                context: {
                    source: 'vscode_vsix',
                    client: 'powerautomation_chat',
                    user_id: user?.id,
                    user_type: user?.userType,
                    user_role: user?.role,
                    timestamp: new Date().toISOString(),
                    workspace: vscode.workspace.name || 'unknown'
                }
            };

            // 獲取認證信息
            let apiKey = '';
            if (user?.provider === 'apikey') {
                apiKey = user.id.replace('api_', 'pa_');
            } else {
                apiKey = config.get<string>('apiKey', '');
            }

            // 發送到 MCP 服務
            const response = await axios.post(`${endpoint}/api/process`, requestData, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`,
                    'User-Agent': 'PowerAutomation-VSIX/3.0.0'
                }
            });

            if (response.status !== 200) {
                throw new Error(`服務器響應錯誤: ${response.status} ${response.statusText}`);
            }

            const result = response.data;

            // 發送AI響應
            this._view.webview.postMessage({
                type: 'aiResponse',
                message: result.result?.content || result.message || '抱歉，我無法處理您的請求。',
                timestamp: new Date().toISOString(),
                metadata: {
                    request_id: result.request_id,
                    execution_time: result.execution_time,
                    tools_used: result.tools_used,
                    confidence: result.confidence
                }
            });

        } catch (error) {
            console.error('Chat message error:', error);
            this._sendErrorToWebview(error as Error);
        }
    }

    private async _analyzeFile(fileName: string) {
        if (!this._authService?.isAuthenticated()) {
            this._sendErrorToWebview(new Error('請先登錄以使用文件分析功能'));
            return;
        }

        if (!this._authService.hasPermission('file-management')) {
            this._sendErrorToWebview(new Error('您沒有權限使用文件分析功能'));
            return;
        }

        if (!this._view) return;

        try {
            // 讀取文件內容
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor) {
                throw new Error('請先打開一個文件');
            }

            const document = activeEditor.document;
            const fileContent = document.getText();
            const fileExtension = document.fileName.split('.').pop() || '';

            // 構建分析請求
            const analysisRequest = `請分析這個 ${fileExtension} 文件：\n\n${fileContent}`;

            // 發送分析請求
            await this._handleChatMessage(analysisRequest);

        } catch (error) {
            console.error('File analysis error:', error);
            this._sendErrorToWebview(error as Error);
        }
    }

    private async _handlePowerAutomationMessage(message: any) {
        if (!this._authService?.isAuthenticated()) {
            this._sendErrorToWebview(new Error('請先登錄以使用PowerAutomation功能'));
            return;
        }

        // 根據用戶權限處理不同的PowerAutomation功能
        const userType = this._authService.getUserType();
        const hasAdvancedFeatures = this._authService.hasPermission('advanced-chat');

        if (message.action === 'smartinvention' && !hasAdvancedFeatures) {
            this._sendErrorToWebview(new Error('SmartInvention功能需要高級權限'));
            return;
        }

        // 處理PowerAutomation特定功能
        await this._handleChatMessage(`PowerAutomation ${message.action}: ${message.data}`);
    }

    private async _clearChatHistory() {
        if (!this._authService?.hasPermission('history')) {
            this._sendErrorToWebview(new Error('您沒有權限清除聊天歷史'));
            return;
        }

        if (this._view) {
            this._view.webview.postMessage({
                type: 'clearHistory'
            });
        }
    }

    private async _exportChatHistory() {
        if (!this._authService?.hasPermission('history')) {
            this._sendErrorToWebview(new Error('您沒有權限導出聊天歷史'));
            return;
        }

        // 實現導出功能
        vscode.window.showInformationMessage('聊天歷史導出功能開發中...');
    }

    private _sendErrorToWebview(error: Error) {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'error',
                message: error.message,
                timestamp: new Date().toISOString()
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const user = this._authService?.getCurrentUser();
        const uiConfig = this._authService?.getUIConfiguration();
        const isAuthenticated = this._authService?.isAuthenticated() || false;

        if (!isAuthenticated) {
            return this._getUnauthenticatedView();
        }

        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant</title>
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
            background: var(--vscode-titleBar-activeBackground);
            color: var(--vscode-titleBar-activeForeground);
            padding: 12px 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header-info {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .user-avatar {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: ${this._getUserTypeColor(user?.userType || 'user')};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: white;
        }

        .header-text {
            display: flex;
            flex-direction: column;
        }

        .header-title {
            font-size: 13px;
            font-weight: 600;
        }

        .header-subtitle {
            font-size: 10px;
            opacity: 0.8;
        }

        .header-actions {
            display: flex;
            gap: 4px;
        }

        .header-button {
            background: none;
            border: none;
            color: var(--vscode-titleBar-activeForeground);
            cursor: pointer;
            padding: 4px;
            border-radius: 3px;
            font-size: 12px;
        }

        .header-button:hover {
            background: var(--vscode-titleBar-hoverBackground);
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .message {
            display: flex;
            flex-direction: column;
            max-width: 85%;
            word-wrap: break-word;
        }

        .message.user {
            align-self: flex-end;
        }

        .message.ai {
            align-self: flex-start;
        }

        .message-content {
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 13px;
            line-height: 1.4;
        }

        .message.user .message-content {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border-bottom-right-radius: 4px;
        }

        .message.ai .message-content {
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-bottom-left-radius: 4px;
        }

        .message-meta {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-top: 4px;
            padding: 0 4px;
        }

        .message.user .message-meta {
            text-align: right;
        }

        .thinking {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            background: var(--vscode-input-background);
            border-radius: 12px;
            border-bottom-left-radius: 4px;
            font-size: 13px;
            color: var(--vscode-descriptionForeground);
            align-self: flex-start;
            max-width: 85%;
        }

        .thinking-dots {
            display: flex;
            gap: 2px;
        }

        .thinking-dot {
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background: var(--vscode-descriptionForeground);
            animation: thinking 1.4s infinite ease-in-out;
        }

        .thinking-dot:nth-child(1) { animation-delay: -0.32s; }
        .thinking-dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes thinking {
            0%, 80%, 100% { opacity: 0.3; }
            40% { opacity: 1; }
        }

        .chat-input-container {
            padding: 16px;
            border-top: 1px solid var(--vscode-panel-border);
            background: var(--vscode-editor-background);
        }

        .chat-input-wrapper {
            display: flex;
            gap: 8px;
            align-items: flex-end;
        }

        .chat-input {
            flex: 1;
            min-height: 36px;
            max-height: 120px;
            padding: 8px 12px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 18px;
            color: var(--vscode-input-foreground);
            font-size: 13px;
            resize: none;
            outline: none;
            font-family: var(--vscode-font-family);
        }

        .chat-input:focus {
            border-color: var(--vscode-focusBorder);
        }

        .chat-input::placeholder {
            color: var(--vscode-input-placeholderForeground);
        }

        .send-button {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: var(--vscode-button-background);
            border: none;
            color: var(--vscode-button-foreground);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            transition: background-color 0.2s;
        }

        .send-button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .quick-actions {
            display: flex;
            gap: 6px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }

        .quick-action {
            padding: 6px 12px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 12px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 11px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .quick-action:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .error-message {
            background: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            color: var(--vscode-inputValidation-errorForeground);
            padding: 12px;
            border-radius: 6px;
            margin: 8px 16px;
            font-size: 12px;
        }

        .welcome-message {
            text-align: center;
            padding: 32px 16px;
            color: var(--vscode-descriptionForeground);
        }

        .welcome-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--vscode-foreground);
        }

        .welcome-subtitle {
            font-size: 12px;
            margin-bottom: 16px;
        }

        .feature-list {
            text-align: left;
            max-width: 280px;
            margin: 0 auto;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 0;
            font-size: 11px;
        }

        .feature-icon {
            width: 16px;
            text-align: center;
        }

        /* 滾動條樣式 */
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: var(--vscode-scrollbarSlider-background);
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: var(--vscode-scrollbarSlider-hoverBackground);
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="chat-header">
        <div class="header-info">
            <div class="user-avatar">
                ${user?.avatar ? `<img src="${user.avatar}" style="width:100%;height:100%;border-radius:50%;">` : this._getUserTypeIcon(user?.userType || 'user')}
            </div>
            <div class="header-text">
                <div class="header-title">AI Assistant</div>
                <div class="header-subtitle">${user?.username} • ${this._getSubscriptionLabel(user?.subscription || 'free')}</div>
            </div>
        </div>
        <div class="header-actions">
            ${this._authService?.hasPermission('history') ? `
            <button class="header-button" onclick="clearHistory()" title="清除歷史">🗑️</button>
            <button class="header-button" onclick="exportHistory()" title="導出歷史">📤</button>
            ` : ''}
            <button class="header-button" onclick="showSettings()" title="設置">⚙️</button>
        </div>
    </div>

    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                <div class="welcome-title">👋 歡迎使用 AI Assistant</div>
                <div class="welcome-subtitle">我是您的智能編程助手，隨時為您提供幫助</div>
                <div class="feature-list">
                    ${uiConfig?.features.map(feature => `
                        <div class="feature-item">
                            <span class="feature-icon">${this._getFeatureIcon(feature)}</span>
                            <span>${this._getFeatureLabel(feature)}</span>
                        </div>
                    `).join('') || ''}
                </div>
            </div>
        </div>

        <div class="chat-input-container">
            ${this._authService?.hasPermission('advanced-chat') ? `
            <div class="quick-actions">
                <button class="quick-action" onclick="quickAction('analyze')">📊 分析代碼</button>
                <button class="quick-action" onclick="quickAction('optimize')">⚡ 優化建議</button>
                <button class="quick-action" onclick="quickAction('debug')">🐛 調試幫助</button>
                ${user?.userType === 'developer' ? `<button class="quick-action" onclick="quickAction('smartinvention')">🧠 SmartInvention</button>` : ''}
            </div>
            ` : ''}
            
            <div class="chat-input-wrapper">
                <textarea 
                    id="chatInput" 
                    class="chat-input" 
                    placeholder="輸入您的問題或需求..."
                    rows="1"
                ></textarea>
                <button id="sendButton" class="send-button" onclick="sendMessage()">
                    ➤
                </button>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let isThinking = false;

        // 自動調整輸入框高度
        const chatInput = document.getElementById('chatInput');
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // 回車發送消息
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message || isThinking) return;
            
            vscode.postMessage({
                type: 'sendMessage',
                text: message
            });
            
            input.value = '';
            input.style.height = 'auto';
        }

        function quickAction(action) {
            const actions = {
                'analyze': '請分析當前打開的代碼文件',
                'optimize': '請提供代碼優化建議',
                'debug': '請幫我調試代碼中的問題',
                'smartinvention': '啟動 SmartInvention 智能分析'
            };
            
            const message = actions[action];
            if (message) {
                document.getElementById('chatInput').value = message;
                sendMessage();
            }
        }

        function clearHistory() {
            vscode.postMessage({ type: 'clearHistory' });
        }

        function exportHistory() {
            vscode.postMessage({ type: 'exportHistory' });
        }

        function showSettings() {
            // 打開設置
            console.log('顯示設置');
        }

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            const chatMessages = document.getElementById('chatMessages');
            
            switch (message.type) {
                case 'userMessage':
                    addMessage('user', message.message, message.timestamp);
                    break;
                    
                case 'aiResponse':
                    removeThinking();
                    addMessage('ai', message.message, message.timestamp, message.metadata);
                    isThinking = false;
                    break;
                    
                case 'thinking':
                    addThinking(message.message);
                    isThinking = true;
                    break;
                    
                case 'error':
                    removeThinking();
                    addError(message.message);
                    isThinking = false;
                    break;
                    
                case 'clearHistory':
                    chatMessages.innerHTML = '';
                    break;
            }
            
            // 滾動到底部
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });

        function addMessage(type, content, timestamp, metadata) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = \`message \${type}\`;
            
            const time = new Date(timestamp).toLocaleTimeString();
            let metaInfo = time;
            
            if (metadata) {
                metaInfo += \` • \${metadata.execution_time}s\`;
                if (metadata.confidence) {
                    metaInfo += \` • \${Math.round(metadata.confidence * 100)}%\`;
                }
            }
            
            messageDiv.innerHTML = \`
                <div class="message-content">\${content}</div>
                <div class="message-meta">\${metaInfo}</div>
            \`;
            
            chatMessages.appendChild(messageDiv);
        }

        function addThinking(message) {
            const chatMessages = document.getElementById('chatMessages');
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'thinking';
            thinkingDiv.id = 'thinking-indicator';
            
            thinkingDiv.innerHTML = \`
                <div class="thinking-dots">
                    <div class="thinking-dot"></div>
                    <div class="thinking-dot"></div>
                    <div class="thinking-dot"></div>
                </div>
                <span>\${message}</span>
            \`;
            
            chatMessages.appendChild(thinkingDiv);
        }

        function removeThinking() {
            const thinking = document.getElementById('thinking-indicator');
            if (thinking) {
                thinking.remove();
            }
        }

        function addError(message) {
            const chatMessages = document.getElementById('chatMessages');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = \`❌ \${message}\`;
            chatMessages.appendChild(errorDiv);
        }
    </script>
</body>
</html>`;
    }

    private _getUnauthenticatedView(): string {
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant - 未登錄</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 32px 16px;
            text-align: center;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .lock-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.6;
        }

        .title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .subtitle {
            font-size: 13px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 24px;
            line-height: 1.4;
        }

        .login-button {
            padding: 12px 24px;
            background: var(--vscode-button-background);
            border: none;
            border-radius: 6px;
            color: var(--vscode-button-foreground);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .login-button:hover {
            background: var(--vscode-button-hoverBackground);
        }
    </style>
</head>
<body>
    <div class="lock-icon">🔒</div>
    <div class="title">AI Assistant 需要登錄</div>
    <div class="subtitle">
        請先登錄以使用 AI 助手功能<br>
        登錄後您將可以享受智能對話、代碼分析等功能
    </div>
    <button class="login-button" onclick="login()">
        立即登錄
    </button>

    <script>
        const vscode = acquireVsCodeApi();

        function login() {
            vscode.postMessage({ type: 'requestLogin' });
        }
    </script>
</body>
</html>`;
    }

    private _getUserTypeColor(userType: string): string {
        switch (userType) {
            case 'developer': return '#ff6b35';
            case 'user': return '#4285f4';
            default: return '#666';
        }
    }

    private _getUserTypeIcon(userType: string): string {
        switch (userType) {
            case 'developer': return '👨‍💻';
            case 'user': return '👤';
            default: return '👤';
        }
    }

    private _getSubscriptionLabel(subscription: string): string {
        switch (subscription) {
            case 'free': return '免費版';
            case 'pro': return '專業版';
            case 'enterprise': return '企業版';
            default: return '未知';
        }
    }

    private _getFeatureIcon(feature: string): string {
        switch (feature) {
            case 'basic-chat': return '💬';
            case 'advanced-chat': return '🤖';
            case 'file-management': return '📁';
            case 'history': return '📜';
            case 'api-access': return '🔌';
            case 'debug-tools': return '🛠️';
            default: return '✨';
        }
    }

    private _getFeatureLabel(feature: string): string {
        switch (feature) {
            case 'basic-chat': return '基礎對話';
            case 'advanced-chat': return '高級對話';
            case 'file-management': return '文件管理';
            case 'history': return '歷史記錄';
            case 'api-access': return 'API 訪問';
            case 'debug-tools': return '調試工具';
            default: return feature;
        }
    }
}

