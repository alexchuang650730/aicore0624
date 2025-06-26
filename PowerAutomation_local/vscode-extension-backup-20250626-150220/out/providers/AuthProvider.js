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
exports.AuthProvider = void 0;
const vscode = __importStar(require("vscode"));
class AuthProvider {
    constructor(_extensionUri, _authService) {
        this._extensionUri = _extensionUri;
        this._authService = _authService;
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
                case 'login':
                    await this._handleLogin(message.data);
                    break;
                case 'logout':
                    await this._handleLogout();
                    break;
                case 'checkAuthStatus':
                    this._sendAuthStatus();
                    break;
                case 'openSettings':
                    vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation');
                    break;
                case 'generateAPIKey':
                    vscode.commands.executeCommand('powerautomation.generateAPIKey');
                    break;
            }
        }, undefined, []);
        // 發送初始認證狀態
        this._sendAuthStatus();
    }
    async _handleLogin(data) {
        try {
            let credentials = {};
            if (data.type === 'apikey') {
                credentials = { apiKey: data.apiKey };
            }
            else if (data.type === 'oauth') {
                credentials = { provider: data.provider };
            }
            else if (data.type === 'email') {
                credentials = { email: data.email, password: data.password };
            }
            const user = await this._authService.login(data.type, credentials);
            this._sendMessage({
                type: 'loginSuccess',
                user: user
            });
            // 通知擴展認證狀態變化
            vscode.commands.executeCommand('powerautomation.onAuthStateChanged', true);
            // 刷新視圖
            this.refresh();
        }
        catch (error) {
            this._sendMessage({
                type: 'loginError',
                message: error.message || '登錄過程中發生錯誤'
            });
        }
    }
    async _handleLogout() {
        try {
            await this._authService.logout();
            this._sendMessage({
                type: 'logoutSuccess'
            });
            // 通知擴展認證狀態變化
            vscode.commands.executeCommand('powerautomation.onAuthStateChanged', false);
            // 刷新視圖
            this.refresh();
        }
        catch (error) {
            this._sendMessage({
                type: 'error',
                message: error.message || '登出過程中發生錯誤'
            });
        }
    }
    _sendAuthStatus() {
        const isAuthenticated = this._authService.isAuthenticated();
        const user = isAuthenticated ? this._authService.getCurrentUser() : null;
        this._sendMessage({
            type: 'authStatus',
            authenticated: isAuthenticated,
            user: user
        });
    }
    _sendMessage(message) {
        if (this._view) {
            this._view.webview.postMessage(message);
        }
    }
    refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
            // 發送最新認證狀態
            this._sendAuthStatus();
        }
    }
    _getHtmlForWebview(webview) {
        const isAuthenticated = this._authService.isAuthenticated();
        if (isAuthenticated) {
            return this._getAuthenticatedView();
        }
        else {
            return this._getLoginView();
        }
    }
    _getLoginView() {
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
            padding: 16px;
            line-height: 1.5;
        }

        .auth-container {
            max-width: 100%;
            margin: 0 auto;
        }

        .auth-header {
            text-align: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .auth-logo {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .auth-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 4px;
            color: #4285f4;
        }

        .auth-subtitle {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }

        .auth-tabs {
            display: flex;
            margin-bottom: 16px;
            background: var(--vscode-input-background);
            border-radius: 6px;
            padding: 2px;
        }

        .auth-tab {
            flex: 1;
            padding: 8px 12px;
            background: transparent;
            border: none;
            border-radius: 4px;
            color: var(--vscode-foreground);
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .auth-tab.active {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }

        .auth-form {
            display: none;
        }

        .auth-form.active {
            display: block;
        }

        .form-group {
            margin-bottom: 16px;
        }

        .form-label {
            display: block;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 4px;
            color: var(--vscode-foreground);
        }

        .form-input {
            width: 100%;
            padding: 8px 12px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            color: var(--vscode-input-foreground);
            font-size: 12px;
            box-sizing: border-box;
        }

        .form-input:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        .form-button {
            width: 100%;
            padding: 10px 16px;
            background: var(--vscode-button-background);
            border: none;
            border-radius: 4px;
            color: var(--vscode-button-foreground);
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .form-button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .form-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .oauth-buttons {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
            margin-bottom: 16px;
        }

        .oauth-button {
            padding: 10px 16px;
            background: var(--vscode-button-secondaryBackground);
            border: 1px solid var(--vscode-button-border);
            border-radius: 4px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .oauth-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .oauth-icon {
            font-size: 14px;
        }

        .error-message {
            background: rgba(244, 67, 54, 0.1);
            border: 1px solid rgba(244, 67, 54, 0.3);
            border-radius: 4px;
            padding: 8px 12px;
            margin-bottom: 16px;
            color: #f44336;
            font-size: 11px;
            display: none;
        }

        .success-message {
            background: rgba(76, 175, 80, 0.1);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 4px;
            padding: 8px 12px;
            margin-bottom: 16px;
            color: #4caf50;
            font-size: 11px;
            display: none;
        }

        .help-text {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-top: 8px;
            line-height: 1.4;
        }

        .divider {
            text-align: center;
            margin: 16px 0;
            position: relative;
            color: var(--vscode-descriptionForeground);
            font-size: 10px;
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

        .divider span {
            background: var(--vscode-editor-background);
            padding: 0 8px;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 16px;
            color: var(--vscode-descriptionForeground);
            font-size: 11px;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid var(--vscode-descriptionForeground);
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <div class="auth-logo">🔐</div>
            <div class="auth-title">PowerAutomation</div>
            <div class="auth-subtitle">智能編程助手 - 登錄驗證</div>
        </div>

        <div class="error-message" id="errorMessage"></div>
        <div class="success-message" id="successMessage"></div>
        <div class="loading" id="loadingMessage">
            <span class="spinner"></span>
            正在登錄...
        </div>

        <div class="auth-tabs">
            <button class="auth-tab active" onclick="switchTab('user')">用戶模式</button>
            <button class="auth-tab" onclick="switchTab('advanced')">高級模式</button>
        </div>

        <!-- 用戶模式 -->
        <div class="auth-form active" id="userForm">
            <div class="oauth-buttons">
                <button class="oauth-button" onclick="loginWithOAuth('github')">
                    <span class="oauth-icon">🐙</span>
                    使用 GitHub 登錄
                </button>
                <button class="oauth-button" onclick="loginWithOAuth('google')">
                    <span class="oauth-icon">🔍</span>
                    使用 Google 登錄
                </button>
                <button class="oauth-button" onclick="loginWithOAuth('microsoft')">
                    <span class="oauth-icon">🪟</span>
                    使用 Microsoft 登錄
                </button>
            </div>

            <div class="divider">
                <span>或使用郵箱登錄</span>
            </div>

            <form onsubmit="loginWithEmail(event)">
                <div class="form-group">
                    <label class="form-label" for="email">郵箱地址</label>
                    <input type="email" id="email" class="form-input" placeholder="your@email.com" required>
                </div>
                <div class="form-group">
                    <label class="form-label" for="password">密碼</label>
                    <input type="password" id="password" class="form-input" placeholder="請輸入密碼" required>
                </div>
                <button type="submit" class="form-button">登錄</button>
            </form>

            <div class="help-text">
                首次使用？系統將自動為您創建賬戶。<br>
                忘記密碼？請聯繫管理員重置。
            </div>
        </div>

        <!-- 高級模式 -->
        <div class="auth-form" id="advancedForm">
            <form onsubmit="loginWithAPIKey(event)">
                <div class="form-group">
                    <label class="form-label" for="apiKey">API Key</label>
                    <input type="password" id="apiKey" class="form-input" placeholder="請輸入您的 API Key" required>
                </div>
                <button type="submit" class="form-button">使用 API Key 登錄</button>
            </form>

            <div class="help-text">
                開發者可以使用 API Key 直接登錄。<br>
                沒有 API Key？請在設置中生成或聯繫管理員。
            </div>

            <div class="divider">
                <span>快速操作</span>
            </div>

            <button class="oauth-button" onclick="generateAPIKey()">
                <span class="oauth-icon">🔑</span>
                生成新的 API Key
            </button>
            <button class="oauth-button" onclick="openSettings()">
                <span class="oauth-icon">⚙️</span>
                打開設置
            </button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let currentTab = 'user';

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'authStatus':
                    handleAuthStatus(message);
                    break;
                case 'loginSuccess':
                    handleLoginSuccess(message);
                    break;
                case 'loginError':
                    handleLoginError(message);
                    break;
                case 'logoutSuccess':
                    handleLogoutSuccess();
                    break;
                case 'error':
                    showError(message.message);
                    break;
            }
        });

        function switchTab(tab) {
            currentTab = tab;
            
            // 更新標籤樣式
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelector(\`[onclick="switchTab('\${tab}')"]\`).classList.add('active');
            
            // 更新表單顯示
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            document.getElementById(tab === 'user' ? 'userForm' : 'advancedForm').classList.add('active');
            
            hideMessages();
        }

        function loginWithOAuth(provider) {
            showLoading();
            vscode.postMessage({
                type: 'login',
                data: {
                    type: provider,
                    provider: provider
                }
            });
        }

        function loginWithEmail(event) {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                showError('請填寫完整的登錄信息');
                return;
            }
            
            showLoading();
            vscode.postMessage({
                type: 'login',
                data: {
                    type: 'email',
                    email: email,
                    password: password
                }
            });
        }

        function loginWithAPIKey(event) {
            event.preventDefault();
            const apiKey = document.getElementById('apiKey').value;
            
            if (!apiKey) {
                showError('請輸入 API Key');
                return;
            }
            
            showLoading();
            vscode.postMessage({
                type: 'login',
                data: {
                    type: 'apikey',
                    apiKey: apiKey
                }
            });
        }

        function generateAPIKey() {
            vscode.postMessage({ type: 'generateAPIKey' });
        }

        function openSettings() {
            vscode.postMessage({ type: 'openSettings' });
        }

        function handleAuthStatus(message) {
            if (message.authenticated) {
                // 用戶已登錄，可以顯示登出界面或重定向
                console.log('User is authenticated:', message.user);
            }
        }

        function handleLoginSuccess(message) {
            hideLoading();
            showSuccess(\`登錄成功！歡迎，\${message.user?.username || '用戶'}！\`);
            
            // 延遲刷新以顯示成功消息
            setTimeout(() => {
                // 這裡可以觸發視圖刷新或其他操作
                vscode.postMessage({ type: 'checkAuthStatus' });
            }, 1500);
        }

        function handleLoginError(message) {
            hideLoading();
            showError(message.message || '登錄失敗，請重試');
        }

        function handleLogoutSuccess() {
            hideLoading();
            showSuccess('已成功登出');
            
            // 清空表單
            document.getElementById('email').value = '';
            document.getElementById('password').value = '';
            document.getElementById('apiKey').value = '';
        }

        function showError(message) {
            hideMessages();
            const errorEl = document.getElementById('errorMessage');
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }

        function showSuccess(message) {
            hideMessages();
            const successEl = document.getElementById('successMessage');
            successEl.textContent = message;
            successEl.style.display = 'block';
        }

        function showLoading() {
            hideMessages();
            document.getElementById('loadingMessage').classList.add('show');
        }

        function hideLoading() {
            document.getElementById('loadingMessage').classList.remove('show');
        }

        function hideMessages() {
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('successMessage').style.display = 'none';
            hideLoading();
        }

        // 頁面加載時檢查認證狀態
        vscode.postMessage({ type: 'checkAuthStatus' });
    </script>
</body>
</html>`;
    }
    _getAuthenticatedView() {
        const user = this._authService.getCurrentUser();
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation - 已登錄</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 16px;
            line-height: 1.5;
        }

        .auth-container {
            max-width: 100%;
            margin: 0 auto;
        }

        .user-info {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            text-align: center;
        }

        .user-avatar {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .user-name {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .user-type {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 8px;
        }

        .user-role {
            display: inline-block;
            padding: 4px 8px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border-radius: 12px;
            font-size: 10px;
            font-weight: 500;
        }

        .auth-actions {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
        }

        .action-button {
            padding: 10px 16px;
            background: var(--vscode-button-secondaryBackground);
            border: 1px solid var(--vscode-button-border);
            border-radius: 4px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .action-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .action-button.danger {
            background: rgba(244, 67, 54, 0.1);
            color: #f44336;
            border-color: rgba(244, 67, 54, 0.3);
        }

        .action-button.danger:hover {
            background: rgba(244, 67, 54, 0.2);
        }

        .action-icon {
            font-size: 12px;
        }

        .status-info {
            background: rgba(76, 175, 80, 0.1);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 11px;
            color: #4caf50;
            text-align: center;
        }

        .permissions-list {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--vscode-panel-border);
        }

        .permissions-title {
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--vscode-foreground);
        }

        .permission-item {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 4px 0;
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
        }

        .permission-icon {
            font-size: 10px;
            color: #4caf50;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="status-info">
            ✅ 您已成功登錄 PowerAutomation
        </div>

        <div class="user-info">
            <div class="user-avatar">${this._getUserAvatar(user)}</div>
            <div class="user-name">${user?.username || '用戶'}</div>
            <div class="user-type">${this._getUserTypeText(user?.userType || 'user')}</div>
            <div class="user-role">${this._getUserRoleText(user?.role || 'user')}</div>

            ${this._getPermissionsList(user)}
        </div>

        <div class="auth-actions">
            <button class="action-button" onclick="openSettings()">
                <span class="action-icon">⚙️</span>
                設置
            </button>
            <button class="action-button" onclick="generateAPIKey()">
                <span class="action-icon">🔑</span>
                生成 API Key
            </button>
            <button class="action-button danger" onclick="logout()">
                <span class="action-icon">🚪</span>
                登出
            </button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function logout() {
            if (confirm('確定要登出嗎？')) {
                vscode.postMessage({ type: 'logout' });
            }
        }

        function openSettings() {
            vscode.postMessage({ type: 'openSettings' });
        }

        function generateAPIKey() {
            vscode.postMessage({ type: 'generateAPIKey' });
        }

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'logoutSuccess':
                    // 登出成功後會自動刷新視圖
                    break;
                case 'error':
                    alert('錯誤: ' + message.message);
                    break;
            }
        });
    </script>
</body>
</html>`;
    }
    _getUserAvatar(user) {
        if (user?.userType === 'developer')
            return '👨‍💻';
        if (user?.role === 'admin')
            return '👑';
        return '👤';
    }
    _getUserTypeText(userType) {
        switch (userType) {
            case 'developer': return '開發者用戶';
            case 'enterprise': return '企業用戶';
            default: return '普通用戶';
        }
    }
    _getUserRoleText(role) {
        switch (role) {
            case 'admin': return '管理員';
            case 'developer': return '開發者';
            default: return '用戶';
        }
    }
    _getPermissionsList(user) {
        const permissions = user?.permissions || [];
        if (!permissions || permissions.length === 0) {
            return '';
        }
        const permissionTexts = {
            'chat': '💬 AI 聊天',
            'file-upload': '📁 文件上傳',
            'history': '📚 歷史記錄',
            'mcp-access': '🔗 MCP 訪問',
            'debug-tools': '🛠️ 調試工具',
            'api-access': '🔑 API 訪問',
            'user-management': '👥 用戶管理',
            'system-config': '⚙️ 系統配置',
            'server-management': '🖥️ 服務器管理',
            'analytics': '📊 數據分析'
        };
        const permissionItems = permissions
            .map((p) => `<div class="permission-item"><span class="permission-icon">✓</span>${permissionTexts[p] || p}</div>`)
            .join('');
        return `
            <div class="permissions-list">
                <div class="permissions-title">您的權限</div>
                ${permissionItems}
            </div>
        `;
    }
}
exports.AuthProvider = AuthProvider;
AuthProvider.viewType = 'powerautomation.auth';
//# sourceMappingURL=AuthProvider.js.map