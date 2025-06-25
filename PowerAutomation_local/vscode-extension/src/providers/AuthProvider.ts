import * as vscode from 'vscode';
import { AuthenticationService, AuthProvider as AuthProviderInterface } from '../services/AuthenticationService';

export class AuthProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'powerautomation.auth';
    private _view?: vscode.WebviewView;
    private _authService: AuthenticationService;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        authService: AuthenticationService
    ) {
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

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // 處理來自webview的消息
        webviewView.webview.onDidReceiveMessage(
            async message => {
                switch (message.type) {
                    case 'selectInterface':
                        this._showInterfaceSelection(message.interfaceType);
                        break;
                    case 'login':
                        await this._handleLogin(message.provider, message.credentials);
                        break;
                    case 'logout':
                        await this._handleLogout();
                        break;
                    case 'switchInterface':
                        this._showInterfaceSelection();
                        break;
                    case 'sendVerificationCode':
                        await this._sendVerificationCode(message.phone);
                        break;
                    case 'resetPassword':
                        await this._resetPassword(message.email);
                        break;
                }
            },
            undefined,
            []
        );
    }

    private _showInterfaceSelection(interfaceType?: 'user' | 'advanced') {
        if (this._view) {
            if (interfaceType) {
                this._view.webview.html = this._getLoginInterfaceHtml(interfaceType);
            } else {
                this._view.webview.html = this._getHtmlForWebview(this._view.webview);
            }
        }
    }

    private async _handleLogin(provider: string, credentials: any) {
        try {
            const user = await this._authService.login(provider, credentials);
            
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'loginSuccess',
                    user: user
                });
            }

            // 刷新其他視圖
            vscode.commands.executeCommand('powerautomation.refreshViews');
            
            vscode.window.showInformationMessage(`歡迎，${user.username}！`);
        } catch (error) {
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'loginError',
                    message: error instanceof Error ? error.message : '登錄失敗'
                });
            }
        }
    }

    private async _handleLogout() {
        try {
            await this._authService.logout();
            
            if (this._view) {
                this._view.webview.html = this._getHtmlForWebview(this._view.webview);
            }

            // 刷新其他視圖
            vscode.commands.executeCommand('powerautomation.refreshViews');
            
            vscode.window.showInformationMessage('已成功登出');
        } catch (error) {
            vscode.window.showErrorMessage('登出失敗');
        }
    }

    private async _sendVerificationCode(phone: string) {
        try {
            await this._authService.sendPhoneVerificationCode(phone);
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'verificationCodeSent',
                    message: '驗證碼已發送'
                });
            }
        } catch (error) {
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'error',
                    message: '發送驗證碼失敗'
                });
            }
        }
    }

    private async _resetPassword(email: string) {
        try {
            await this._authService.resetPassword(email);
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'passwordResetSent',
                    message: '重置密碼郵件已發送'
                });
            }
        } catch (error) {
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'error',
                    message: '發送重置郵件失敗'
                });
            }
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const user = this._authService.getCurrentUser();
        
        if (user) {
            return this._getAuthenticatedView(user);
        } else {
            return this._getInterfaceSelectionView();
        }
    }

    private _getInterfaceSelectionView(): string {
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation 登錄</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo {
            font-size: 48px;
            margin-bottom: 16px;
        }

        .title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 14px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 20px;
        }

        .interface-selection {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .interface-option {
            padding: 20px;
            border: 2px solid var(--vscode-input-border);
            border-radius: 12px;
            background: var(--vscode-input-background);
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }

        .interface-option:hover {
            border-color: var(--vscode-button-background);
            background: var(--vscode-button-secondaryBackground);
            transform: translateY(-2px);
        }

        .interface-icon {
            font-size: 32px;
            margin-bottom: 12px;
            display: block;
        }

        .interface-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .interface-description {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            line-height: 1.4;
        }

        .user-interface {
            border-color: #4285f4;
        }

        .user-interface:hover {
            border-color: #3367d6;
            background: rgba(66, 133, 244, 0.1);
        }

        .advanced-interface {
            border-color: #ff6b35;
        }

        .advanced-interface:hover {
            border-color: #e55a2b;
            background: rgba(255, 107, 53, 0.1);
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid var(--vscode-panel-border);
        }

        .footer-text {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🤖</div>
            <div class="title">PowerAutomation</div>
            <div class="subtitle">選擇您的使用方式</div>
        </div>

        <div class="interface-selection">
            <div class="interface-option user-interface" onclick="selectInterface('user')">
                <span class="interface-icon">👤</span>
                <div class="interface-title">用戶模式</div>
                <div class="interface-description">
                    適合日常使用者<br>
                    OAuth 登錄 • 基礎功能 • 簡潔界面
                </div>
            </div>

            <div class="interface-option advanced-interface" onclick="selectInterface('advanced')">
                <span class="interface-icon">🔧</span>
                <div class="interface-title">開發者/管理員模式</div>
                <div class="interface-description">
                    適合開發者和管理員<br>
                    API Key 登錄 • 完整功能 • 高級工具
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="footer-text">
                PowerAutomation v3.1.1 • 智能編程助手
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function selectInterface(interfaceType) {
            vscode.postMessage({
                type: 'selectInterface',
                interfaceType: interfaceType
            });
        }
    </script>
</body>
</html>`;
    }

    private _getLoginInterfaceHtml(interfaceType: 'user' | 'advanced'): string {
        if (interfaceType === 'user') {
            return this._getUserLoginInterface();
        } else {
            return this._getAdvancedLoginInterface();
        }
    }

    private _getUserLoginInterface(): string {
        const providers = this._authService.getAuthProviders('user');
        
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用戶登錄</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .back-button {
            position: absolute;
            top: 16px;
            left: 16px;
            background: none;
            border: none;
            color: var(--vscode-foreground);
            cursor: pointer;
            font-size: 16px;
            padding: 8px;
        }

        .back-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
            border-radius: 4px;
        }

        .logo {
            font-size: 40px;
            margin-bottom: 12px;
        }

        .title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #4285f4;
        }

        .subtitle {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 24px;
        }

        .login-methods {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 24px;
        }

        .login-button {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            background: var(--vscode-input-background);
            color: var(--vscode-foreground);
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            font-size: 13px;
        }

        .login-button:hover {
            border-color: var(--vscode-button-background);
            background: var(--vscode-button-secondaryBackground);
        }

        .login-icon {
            font-size: 18px;
            width: 20px;
            text-align: center;
        }

        .login-text {
            flex: 1;
            font-weight: 500;
        }

        .divider {
            text-align: center;
            margin: 20px 0;
            position: relative;
        }

        .divider::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: var(--vscode-panel-border);
        }

        .divider-text {
            background: var(--vscode-editor-background);
            padding: 0 16px;
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }

        .email-form {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .form-label {
            font-size: 12px;
            font-weight: 500;
            color: var(--vscode-foreground);
        }

        .form-input {
            padding: 10px 12px;
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-size: 13px;
        }

        .form-input:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        .submit-button {
            padding: 12px;
            background: #4285f4;
            border: none;
            border-radius: 6px;
            color: white;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .submit-button:hover {
            background: #3367d6;
        }

        .submit-button:disabled {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-descriptionForeground);
            cursor: not-allowed;
        }

        .forgot-password {
            text-align: center;
            margin-top: 12px;
        }

        .forgot-password a {
            color: #4285f4;
            text-decoration: none;
            font-size: 11px;
        }

        .forgot-password a:hover {
            text-decoration: underline;
        }

        .error-message {
            background: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            color: var(--vscode-inputValidation-errorForeground);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-bottom: 12px;
        }

        .success-message {
            background: var(--vscode-terminal-ansiGreen);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-bottom: 12px;
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <button class="back-button" onclick="goBack()">← 返回</button>
    
    <div class="container">
        <div class="header">
            <div class="logo">👤</div>
            <div class="title">用戶登錄</div>
            <div class="subtitle">使用您的帳號登錄 PowerAutomation</div>
        </div>

        <div id="errorMessage" class="error-message hidden"></div>
        <div id="successMessage" class="success-message hidden"></div>

        <div class="login-methods">
            ${providers.map(provider => `
                <button class="login-button" onclick="loginWith('${provider.id}')">
                    <span class="login-icon">${provider.icon}</span>
                    <span class="login-text">${provider.name}</span>
                </button>
            `).join('')}
        </div>

        <div class="divider">
            <span class="divider-text">或使用郵箱登錄</span>
        </div>

        <form class="email-form" onsubmit="loginWithEmail(event)">
            <div class="form-group">
                <label class="form-label" for="email">郵箱地址</label>
                <input class="form-input" type="email" id="email" required>
            </div>
            <div class="form-group">
                <label class="form-label" for="password">密碼</label>
                <input class="form-input" type="password" id="password" required>
            </div>
            <button class="submit-button" type="submit" id="submitButton">
                登錄
            </button>
        </form>

        <div class="forgot-password">
            <a href="#" onclick="resetPassword()">忘記密碼？</a>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function goBack() {
            vscode.postMessage({ type: 'switchInterface' });
        }

        function loginWith(provider) {
            if (provider === 'email') return;
            
            showMessage('正在跳轉到 ' + provider + ' 登錄...', 'success');
            
            vscode.postMessage({
                type: 'login',
                provider: provider,
                credentials: {}
            });
        }

        function loginWithEmail(event) {
            event.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                showMessage('請輸入郵箱和密碼', 'error');
                return;
            }

            const submitButton = document.getElementById('submitButton');
            submitButton.disabled = true;
            submitButton.textContent = '登錄中...';

            vscode.postMessage({
                type: 'login',
                provider: 'email',
                credentials: { email, password }
            });
        }

        function resetPassword() {
            const email = prompt('請輸入您的郵箱地址：');
            if (email) {
                vscode.postMessage({
                    type: 'resetPassword',
                    email: email
                });
            }
        }

        function showMessage(message, type) {
            const errorDiv = document.getElementById('errorMessage');
            const successDiv = document.getElementById('successMessage');
            
            errorDiv.classList.add('hidden');
            successDiv.classList.add('hidden');
            
            if (type === 'error') {
                errorDiv.textContent = message;
                errorDiv.classList.remove('hidden');
            } else {
                successDiv.textContent = message;
                successDiv.classList.remove('hidden');
            }
        }

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.type) {
                case 'loginError':
                    showMessage(message.message, 'error');
                    const submitButton = document.getElementById('submitButton');
                    submitButton.disabled = false;
                    submitButton.textContent = '登錄';
                    break;
                case 'loginSuccess':
                    showMessage('登錄成功！', 'success');
                    break;
                case 'passwordResetSent':
                    showMessage(message.message, 'success');
                    break;
            }
        });
    </script>
</body>
</html>`;
    }

    private _getAdvancedLoginInterface(): string {
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>開發者/管理員登錄</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .back-button {
            position: absolute;
            top: 16px;
            left: 16px;
            background: none;
            border: none;
            color: var(--vscode-foreground);
            cursor: pointer;
            font-size: 16px;
            padding: 8px;
        }

        .back-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
            border-radius: 4px;
        }

        .logo {
            font-size: 40px;
            margin-bottom: 12px;
        }

        .title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #ff6b35;
        }

        .subtitle {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 24px;
        }

        .api-key-form {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--vscode-foreground);
        }

        .form-input {
            padding: 12px 16px;
            border: 2px solid var(--vscode-input-border);
            border-radius: 8px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-size: 13px;
            font-family: 'Courier New', monospace;
        }

        .form-input:focus {
            outline: none;
            border-color: #ff6b35;
        }

        .form-help {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            line-height: 1.4;
        }

        .endpoint-group {
            margin-top: 8px;
        }

        .endpoint-input {
            font-family: var(--vscode-font-family);
        }

        .submit-button {
            padding: 14px;
            background: #ff6b35;
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .submit-button:hover {
            background: #e55a2b;
        }

        .submit-button:disabled {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-descriptionForeground);
            cursor: not-allowed;
        }

        .key-examples {
            background: var(--vscode-textBlockQuote-background);
            border-left: 4px solid #ff6b35;
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin-top: 16px;
        }

        .key-examples-title {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #ff6b35;
        }

        .key-example {
            font-family: 'Courier New', monospace;
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 4px;
        }

        .key-example.admin {
            color: #dc3545;
        }

        .key-example.dev {
            color: #ffc107;
        }

        .error-message {
            background: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            color: var(--vscode-inputValidation-errorForeground);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-bottom: 12px;
        }

        .success-message {
            background: var(--vscode-terminal-ansiGreen);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-bottom: 12px;
        }

        .hidden {
            display: none;
        }

        .local-mode {
            margin-top: 16px;
            padding: 12px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
        }

        .local-mode-title {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .local-mode-description {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 8px;
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .checkbox {
            width: 16px;
            height: 16px;
        }

        .checkbox-label {
            font-size: 11px;
            color: var(--vscode-foreground);
        }
    </style>
</head>
<body>
    <button class="back-button" onclick="goBack()">← 返回</button>
    
    <div class="container">
        <div class="header">
            <div class="logo">🔧</div>
            <div class="title">開發者/管理員登錄</div>
            <div class="subtitle">使用 API Key 訪問高級功能</div>
        </div>

        <div id="errorMessage" class="error-message hidden"></div>
        <div id="successMessage" class="success-message hidden"></div>

        <form class="api-key-form" onsubmit="loginWithApiKey(event)">
            <div class="form-group">
                <label class="form-label" for="apiKey">API Key</label>
                <input 
                    class="form-input" 
                    type="password" 
                    id="apiKey" 
                    placeholder="輸入您的 API Key"
                    required
                >
                <div class="form-help">
                    請輸入您的開發者或管理員 API Key
                </div>
            </div>

            <div class="form-group endpoint-group">
                <label class="form-label" for="endpoint">MCP 端點 (可選)</label>
                <input 
                    class="form-input endpoint-input" 
                    type="url" 
                    id="endpoint" 
                    placeholder="https://your-mcp-server.com"
                >
                <div class="form-help">
                    留空將使用本地模式，填入端點將驗證 API Key 有效性
                </div>
            </div>

            <div class="local-mode">
                <div class="local-mode-title">🔧 本地開發模式</div>
                <div class="local-mode-description">
                    啟用本地模式可以在沒有網絡連接的情況下使用基礎功能
                </div>
                <div class="checkbox-group">
                    <input type="checkbox" id="localMode" class="checkbox">
                    <label for="localMode" class="checkbox-label">啟用本地模式</label>
                </div>
            </div>

            <button class="submit-button" type="submit" id="submitButton">
                登錄
            </button>
        </form>

        <div class="key-examples">
            <div class="key-examples-title">API Key 格式示例：</div>
            <div class="key-example admin">admin_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</div>
            <div class="key-example dev">dev_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function goBack() {
            vscode.postMessage({ type: 'switchInterface' });
        }

        function loginWithApiKey(event) {
            event.preventDefault();
            
            const apiKey = document.getElementById('apiKey').value;
            const endpoint = document.getElementById('endpoint').value;
            const localMode = document.getElementById('localMode').checked;
            
            if (!apiKey) {
                showMessage('請輸入 API Key', 'error');
                return;
            }

            // 驗證 API Key 格式
            if (!apiKey.startsWith('admin_') && !apiKey.startsWith('dev_')) {
                showMessage('API Key 格式錯誤，必須以 admin_ 或 dev_ 開頭', 'error');
                return;
            }

            const submitButton = document.getElementById('submitButton');
            submitButton.disabled = true;
            submitButton.textContent = '驗證中...';

            vscode.postMessage({
                type: 'login',
                provider: 'apikey',
                credentials: { 
                    apiKey, 
                    endpoint: endpoint || null,
                    localMode 
                }
            });
        }

        function showMessage(message, type) {
            const errorDiv = document.getElementById('errorMessage');
            const successDiv = document.getElementById('successMessage');
            
            errorDiv.classList.add('hidden');
            successDiv.classList.add('hidden');
            
            if (type === 'error') {
                errorDiv.textContent = message;
                errorDiv.classList.remove('hidden');
            } else {
                successDiv.textContent = message;
                successDiv.classList.remove('hidden');
            }
        }

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.type) {
                case 'loginError':
                    showMessage(message.message, 'error');
                    const submitButton = document.getElementById('submitButton');
                    submitButton.disabled = false;
                    submitButton.textContent = '登錄';
                    break;
                case 'loginSuccess':
                    showMessage('登錄成功！', 'success');
                    break;
            }
        });

        // 自動檢測 API Key 類型並顯示相應提示
        document.getElementById('apiKey').addEventListener('input', function(e) {
            const value = e.target.value;
            const submitButton = document.getElementById('submitButton');
            
            if (value.startsWith('admin_')) {
                submitButton.style.background = '#dc3545';
                submitButton.textContent = '管理員登錄';
            } else if (value.startsWith('dev_')) {
                submitButton.style.background = '#ffc107';
                submitButton.style.color = '#000';
                submitButton.textContent = '開發者登錄';
            } else {
                submitButton.style.background = '#ff6b35';
                submitButton.style.color = '#fff';
                submitButton.textContent = '登錄';
            }
        });
    </script>
</body>
</html>`;
    }

    private _getAuthenticatedView(user: any): string {
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>已登錄</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 400px;
            margin: 0 auto;
        }

        .user-card {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }

        .user-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: ${this._getUserTypeColor(user.userType)};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
            margin: 0 auto 16px;
        }

        .user-name {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .user-email {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 12px;
        }

        .user-badges {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 20px;
        }

        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge.user-type {
            background: ${this._getUserTypeColor(user.userType)};
            color: white;
        }

        .badge.interface {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }

        .logout-button {
            width: 100%;
            padding: 12px;
            background: var(--vscode-button-secondaryBackground);
            border: 1px solid var(--vscode-button-secondaryBackground);
            border-radius: 6px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .logout-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .user-info {
            text-align: left;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--vscode-panel-border);
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 11px;
        }

        .info-label {
            color: var(--vscode-descriptionForeground);
        }

        .info-value {
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="user-card">
            <div class="user-avatar">
                ${user.avatar ? `<img src="${user.avatar}" style="width:100%;height:100%;border-radius:50%;">` : this._getUserTypeIcon(user.userType)}
            </div>
            <div class="user-name">${user.username}</div>
            <div class="user-email">${user.email}</div>
            
            <div class="user-badges">
                <div class="badge user-type">${this._getUserTypeLabel(user.userType)}</div>
                <div class="badge interface">${user.interfaceType === 'user' ? '用戶界面' : '高級界面'}</div>
            </div>

            <div class="user-info">
                <div class="info-row">
                    <span class="info-label">登錄方式</span>
                    <span class="info-value">${this._getProviderName(user.provider)}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">訂閱類型</span>
                    <span class="info-value">${this._getSubscriptionLabel(user.subscription)}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">可用積分</span>
                    <span class="info-value">${user.credits?.toLocaleString() || '0'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">權限數量</span>
                    <span class="info-value">${user.permissions?.length || 0} 項</span>
                </div>
            </div>

            <button class="logout-button" onclick="logout()">
                登出
            </button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function logout() {
            vscode.postMessage({ type: 'logout' });
        }
    </script>
</body>
</html>`;
    }

    private _getUserTypeColor(userType: string): string {
        switch (userType) {
            case 'admin': return '#dc3545';
            case 'developer': return '#ff6b35';
            case 'user': return '#4285f4';
            default: return '#666';
        }
    }

    private _getUserTypeIcon(userType: string): string {
        switch (userType) {
            case 'admin': return '👑';
            case 'developer': return '👨‍💻';
            case 'user': return '👤';
            default: return '👤';
        }
    }

    private _getUserTypeLabel(userType: string): string {
        switch (userType) {
            case 'admin': return '管理員';
            case 'developer': return '開發者';
            case 'user': return '用戶';
            default: return '用戶';
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

    private _getProviderName(provider: string): string {
        switch (provider) {
            case 'apikey': return 'API Key';
            case 'github': return 'GitHub';
            case 'google': return 'Google';
            case 'microsoft': return 'Microsoft';
            case 'email': return '郵箱';
            default: return '未知';
        }
    }
}

