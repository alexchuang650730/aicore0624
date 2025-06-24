import * as vscode from 'vscode';
import { AuthenticationService, AuthProvider as AuthProviderType } from '../services/AuthenticationService';

export class AuthProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'powerautomation.auth';
    private _view?: vscode.WebviewView;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _authService: AuthenticationService
    ) {}

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
                    case 'login':
                        await this._handleLogin(message.provider, message.credentials);
                        break;
                    case 'register':
                        await this._handleRegister(message.provider, message.userData);
                        break;
                    case 'logout':
                        await this._handleLogout();
                        break;
                    case 'sendVerificationCode':
                        await this._handleSendVerificationCode(message.phone);
                        break;
                    case 'resetPassword':
                        await this._handleResetPassword(message.email);
                        break;
                    case 'switchMode':
                        this._switchAuthMode(message.mode);
                        break;
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

    private async _handleLogin(provider: string, credentials: any) {
        if (!this._view) return;

        try {
            this._view.webview.postMessage({ type: 'loginStart' });
            
            const user = await this._authService.login(provider, credentials);
            
            this._view.webview.postMessage({ 
                type: 'loginSuccess', 
                user: user 
            });

            vscode.window.showInformationMessage(`歡迎回來，${user.username}！`);
            this.refresh();
        } catch (error) {
            this._view.webview.postMessage({ 
                type: 'loginError', 
                error: (error as Error).toString() 
            });
        }
    }

    private async _handleRegister(provider: string, userData: any) {
        if (!this._view) return;

        try {
            this._view.webview.postMessage({ type: 'registerStart' });
            
            const user = await this._authService.register(provider, userData);
            
            this._view.webview.postMessage({ 
                type: 'registerSuccess', 
                user: user 
            });

            vscode.window.showInformationMessage(`註冊成功！歡迎，${user.username}！`);
            this.refresh();
        } catch (error) {
            this._view.webview.postMessage({ 
                type: 'registerError', 
                error: (error as Error).toString() 
            });
        }
    }

    private async _handleLogout() {
        try {
            await this._authService.logout();
            vscode.window.showInformationMessage('已成功登出');
            this.refresh();
        } catch (error) {
            vscode.window.showErrorMessage(`登出失敗: ${error}`);
        }
    }

    private async _handleSendVerificationCode(phone: string) {
        if (!this._view) return;

        try {
            await this._authService.sendPhoneVerificationCode(phone);
            this._view.webview.postMessage({ 
                type: 'verificationCodeSent',
                phone: phone
            });
        } catch (error) {
            this._view.webview.postMessage({ 
                type: 'verificationCodeError', 
                error: (error as Error).toString() 
            });
        }
    }

    private async _handleResetPassword(email: string) {
        if (!this._view) return;

        try {
            await this._authService.resetPassword(email);
            this._view.webview.postMessage({ 
                type: 'passwordResetSent',
                email: email
            });
        } catch (error) {
            this._view.webview.postMessage({ 
                type: 'passwordResetError', 
                error: (error as Error).toString() 
            });
        }
    }

    private _switchAuthMode(mode: 'login' | 'register') {
        if (this._view) {
            this._view.webview.postMessage({ 
                type: 'switchMode', 
                mode: mode 
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const isAuthenticated = this._authService.isAuthenticated();
        const currentUser = this._authService.getCurrentUser();
        const authProviders = this._authService.getAuthProviders();

        if (isAuthenticated && currentUser) {
            return this._getAuthenticatedView(currentUser);
        } else {
            return this._getLoginView(authProviders);
        }
    }

    private _getAuthenticatedView(user: any): string {
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用戶資料</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 16px;
        }

        .user-profile {
            text-align: center;
            padding: 20px 0;
        }

        .user-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin: 0 auto 16px;
            background: var(--vscode-button-background);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
        }

        .user-name {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .user-email {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 8px;
        }

        .user-subscription {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            background: var(--vscode-statusBarItem-activeBackground);
            color: var(--vscode-statusBarItem-activeForeground);
        }

        .stats-section {
            margin: 24px 0;
        }

        .section-title {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--vscode-descriptionForeground);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .stat-card {
            background: var(--vscode-input-background);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            border-left: 3px solid var(--vscode-focusBorder);
        }

        .stat-number {
            font-size: 20px;
            font-weight: 700;
            color: var(--vscode-terminal-ansiGreen);
            display: block;
            margin-bottom: 4px;
        }

        .stat-label {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
        }

        .action-button {
            width: 100%;
            padding: 12px;
            margin-bottom: 8px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 6px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 12px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .action-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .action-button.danger {
            background: var(--vscode-statusBarItem-errorBackground);
            color: var(--vscode-statusBarItem-errorForeground);
        }

        .provider-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            margin-top: 8px;
        }

        .last-login {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-top: 16px;
        }
    </style>
</head>
<body>
    <div class="user-profile">
        <div class="user-avatar">
            ${user.avatar ? `<img src="${user.avatar}" style="width:100%;height:100%;border-radius:50%;">` : '👤'}
        </div>
        <div class="user-name">${user.username}</div>
        <div class="user-email">${user.email}</div>
        <div class="user-subscription">${user.subscription}</div>
        <div class="provider-badge">
            ${this._getProviderIcon(user.provider)} ${this._getProviderName(user.provider)}
        </div>
        <div class="last-login">
            上次登錄: ${new Date(user.lastLogin).toLocaleString()}
        </div>
    </div>

    <div class="stats-section">
        <div class="section-title">📊 帳戶統計</div>
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">${user.credits}</span>
                <div class="stat-label">可用積分</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">156</span>
                <div class="stat-label">今日使用</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">$8.42</span>
                <div class="stat-label">本月節省</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">98.7%</span>
                <div class="stat-label">成功率</div>
            </div>
        </div>
    </div>

    <div class="stats-section">
        <div class="section-title">⚙️ 帳戶管理</div>
        <button class="action-button" onclick="editProfile()">
            ✏️ 編輯資料
        </button>
        <button class="action-button" onclick="manageSubscription()">
            💳 管理訂閱
        </button>
        <button class="action-button" onclick="viewUsage()">
            📈 使用統計
        </button>
        <button class="action-button" onclick="downloadData()">
            📥 下載數據
        </button>
        <button class="action-button danger" onclick="logout()">
            🚪 登出
        </button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function logout() {
            vscode.postMessage({ type: 'logout' });
        }

        function editProfile() {
            // 實現編輯資料功能
            console.log('編輯資料');
        }

        function manageSubscription() {
            // 實現訂閱管理功能
            console.log('管理訂閱');
        }

        function viewUsage() {
            // 實現使用統計功能
            console.log('查看使用統計');
        }

        function downloadData() {
            // 實現數據下載功能
            console.log('下載數據');
        }
    </script>
</body>
</html>`;
    }

    private _getLoginView(authProviders: AuthProviderType[]): string {
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
        }

        .auth-header {
            text-align: center;
            margin-bottom: 32px;
        }

        .auth-logo {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .auth-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .auth-subtitle {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .auth-tabs {
            display: flex;
            margin-bottom: 24px;
            background: var(--vscode-input-background);
            border-radius: 6px;
            padding: 4px;
        }

        .auth-tab {
            flex: 1;
            padding: 8px 12px;
            text-align: center;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .auth-tab.active {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }

        .auth-form {
            margin-bottom: 24px;
        }

        .form-group {
            margin-bottom: 16px;
        }

        .form-label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .form-input {
            width: 100%;
            padding: 10px 12px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            color: var(--vscode-input-foreground);
            font-size: 13px;
            box-sizing: border-box;
        }

        .form-input:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        .form-row {
            display: flex;
            gap: 8px;
        }

        .form-row .form-input {
            flex: 1;
        }

        .verification-button {
            padding: 10px 16px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 4px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 11px;
            cursor: pointer;
            white-space: nowrap;
        }

        .verification-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .verification-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .submit-button {
            width: 100%;
            padding: 12px;
            background: var(--vscode-button-background);
            border: none;
            border-radius: 6px;
            color: var(--vscode-button-foreground);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
            margin-bottom: 16px;
        }

        .submit-button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .submit-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .auth-divider {
            text-align: center;
            margin: 24px 0;
            position: relative;
            color: var(--vscode-descriptionForeground);
            font-size: 11px;
        }

        .auth-divider::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: var(--vscode-panel-border);
        }

        .auth-divider span {
            background: var(--vscode-editor-background);
            padding: 0 12px;
        }

        .provider-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 16px;
        }

        .provider-button {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 12px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            color: var(--vscode-foreground);
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .provider-button:hover {
            background: var(--vscode-list-hoverBackground);
            border-color: var(--vscode-focusBorder);
        }

        .provider-icon {
            font-size: 14px;
        }

        .forgot-password {
            text-align: center;
            margin-top: 16px;
        }

        .forgot-password a {
            color: var(--vscode-textLink-foreground);
            text-decoration: none;
            font-size: 11px;
        }

        .forgot-password a:hover {
            text-decoration: underline;
        }

        .loading {
            opacity: 0.6;
            pointer-events: none;
        }

        .error-message {
            background: var(--vscode-statusBarItem-errorBackground);
            color: var(--vscode-statusBarItem-errorForeground);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-bottom: 16px;
            display: none;
        }

        .success-message {
            background: var(--vscode-statusBarItem-activeBackground);
            color: var(--vscode-statusBarItem-activeForeground);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin-bottom: 16px;
            display: none;
        }

        .register-form {
            display: none;
        }

        .register-form.active {
            display: block;
        }

        .login-form.active {
            display: block;
        }

        .terms-checkbox {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 16px;
            font-size: 11px;
        }

        .terms-checkbox input {
            margin-top: 2px;
        }

        .terms-checkbox a {
            color: var(--vscode-textLink-foreground);
            text-decoration: none;
        }

        .terms-checkbox a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="auth-header">
        <div class="auth-logo">🤖</div>
        <div class="auth-title">PowerAutomation v3.0.0</div>
        <div class="auth-subtitle">智能自動化平台 - 新一代AI驅動解決方案</div>
    </div>

    <div class="auth-tabs">
        <div class="auth-tab active" onclick="switchTab('login')">登錄</div>
        <div class="auth-tab" onclick="switchTab('register')">註冊</div>
    </div>

    <div class="error-message" id="errorMessage"></div>
    <div class="success-message" id="successMessage"></div>

    <!-- 登錄表單 -->
    <div class="login-form active" id="loginForm">
        <div class="auth-form">
            <div class="form-group">
                <label class="form-label">登錄方式</label>
                <select class="form-input" id="loginProvider" onchange="switchLoginProvider()">
                    <option value="email">📧 郵箱登錄</option>
                    <option value="phone">📱 手機號登錄</option>
                    <option value="apikey">🔑 API Key登錄</option>
                </select>
            </div>

            <!-- 郵箱登錄 -->
            <div id="emailLogin">
                <div class="form-group">
                    <label class="form-label">郵箱地址</label>
                    <input type="email" class="form-input" id="loginEmail" placeholder="請輸入郵箱地址">
                </div>
                <div class="form-group">
                    <label class="form-label">密碼</label>
                    <input type="password" class="form-input" id="loginPassword" placeholder="請輸入密碼">
                </div>
            </div>

            <!-- 手機號登錄 -->
            <div id="phoneLogin" style="display:none;">
                <div class="form-group">
                    <label class="form-label">手機號碼</label>
                    <input type="tel" class="form-input" id="loginPhone" placeholder="請輸入手機號碼">
                </div>
                <div class="form-group">
                    <label class="form-label">驗證碼</label>
                    <div class="form-row">
                        <input type="text" class="form-input" id="loginCode" placeholder="請輸入驗證碼">
                        <button class="verification-button" onclick="sendVerificationCode('login')">
                            發送驗證碼
                        </button>
                    </div>
                </div>
            </div>

            <!-- API Key登錄 -->
            <div id="apikeyLogin" style="display:none;">
                <div class="form-group">
                    <label class="form-label">API Key</label>
                    <input type="password" class="form-input" id="loginApiKey" placeholder="請輸入API Key">
                </div>
            </div>

            <button class="submit-button" onclick="handleLogin()">
                🚀 登錄
            </button>
        </div>

        <div class="auth-divider">
            <span>或使用第三方登錄</span>
        </div>

        <div class="provider-buttons">
            ${authProviders.filter(p => ['github', 'google', 'microsoft'].includes(p.id)).map(provider => `
                <button class="provider-button" onclick="handleOAuthLogin('${provider.id}')">
                    <span class="provider-icon">${provider.icon}</span>
                    <span>${provider.name}</span>
                </button>
            `).join('')}
        </div>

        <div class="forgot-password">
            <a href="#" onclick="showForgotPassword()">忘記密碼？</a>
        </div>
    </div>

    <!-- 註冊表單 -->
    <div class="register-form" id="registerForm">
        <div class="auth-form">
            <div class="form-group">
                <label class="form-label">註冊方式</label>
                <select class="form-input" id="registerProvider" onchange="switchRegisterProvider()">
                    <option value="email">📧 郵箱註冊</option>
                    <option value="phone">📱 手機號註冊</option>
                </select>
            </div>

            <!-- 郵箱註冊 -->
            <div id="emailRegister">
                <div class="form-group">
                    <label class="form-label">用戶名</label>
                    <input type="text" class="form-input" id="registerUsername" placeholder="請輸入用戶名">
                </div>
                <div class="form-group">
                    <label class="form-label">郵箱地址</label>
                    <input type="email" class="form-input" id="registerEmail" placeholder="請輸入郵箱地址">
                </div>
                <div class="form-group">
                    <label class="form-label">密碼</label>
                    <input type="password" class="form-input" id="registerPassword" placeholder="請輸入密碼">
                </div>
                <div class="form-group">
                    <label class="form-label">確認密碼</label>
                    <input type="password" class="form-input" id="registerConfirmPassword" placeholder="請再次輸入密碼">
                </div>
            </div>

            <!-- 手機號註冊 -->
            <div id="phoneRegister" style="display:none;">
                <div class="form-group">
                    <label class="form-label">用戶名</label>
                    <input type="text" class="form-input" id="registerPhoneUsername" placeholder="請輸入用戶名">
                </div>
                <div class="form-group">
                    <label class="form-label">手機號碼</label>
                    <input type="tel" class="form-input" id="registerPhone" placeholder="請輸入手機號碼">
                </div>
                <div class="form-group">
                    <label class="form-label">驗證碼</label>
                    <div class="form-row">
                        <input type="text" class="form-input" id="registerCode" placeholder="請輸入驗證碼">
                        <button class="verification-button" onclick="sendVerificationCode('register')">
                            發送驗證碼
                        </button>
                    </div>
                </div>
            </div>

            <div class="terms-checkbox">
                <input type="checkbox" id="agreeTerms">
                <label for="agreeTerms">
                    我已閱讀並同意 <a href="#" onclick="showTerms()">服務條款</a> 和 <a href="#" onclick="showPrivacy()">隱私政策</a>
                </label>
            </div>

            <button class="submit-button" onclick="handleRegister()">
                ✨ 註冊帳號
            </button>
        </div>

        <div class="auth-divider">
            <span>或使用第三方註冊</span>
        </div>

        <div class="provider-buttons">
            ${authProviders.filter(p => ['github', 'google', 'microsoft'].includes(p.id)).map(provider => `
                <button class="provider-button" onclick="handleOAuthRegister('${provider.id}')">
                    <span class="provider-icon">${provider.icon}</span>
                    <span>${provider.name}</span>
                </button>
            `).join('')}
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let currentMode = 'login';
        let verificationTimer = null;

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'loginStart':
                case 'registerStart':
                    setLoading(true);
                    break;
                case 'loginSuccess':
                case 'registerSuccess':
                    setLoading(false);
                    showSuccess('操作成功！');
                    break;
                case 'loginError':
                case 'registerError':
                    setLoading(false);
                    showError(message.error);
                    break;
                case 'verificationCodeSent':
                    showSuccess(\`驗證碼已發送到 \${message.phone}\`);
                    startVerificationTimer();
                    break;
                case 'verificationCodeError':
                    showError(message.error);
                    break;
                case 'passwordResetSent':
                    showSuccess(\`密碼重置郵件已發送到 \${message.email}\`);
                    break;
                case 'passwordResetError':
                    showError(message.error);
                    break;
            }
        });

        function switchTab(mode) {
            currentMode = mode;
            
            // 更新標籤樣式
            document.querySelectorAll('.auth-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // 切換表單
            document.getElementById('loginForm').classList.toggle('active', mode === 'login');
            document.getElementById('registerForm').classList.toggle('active', mode === 'register');
            
            clearMessages();
        }

        function switchLoginProvider() {
            const provider = document.getElementById('loginProvider').value;
            
            document.getElementById('emailLogin').style.display = provider === 'email' ? 'block' : 'none';
            document.getElementById('phoneLogin').style.display = provider === 'phone' ? 'block' : 'none';
            document.getElementById('apikeyLogin').style.display = provider === 'apikey' ? 'block' : 'none';
        }

        function switchRegisterProvider() {
            const provider = document.getElementById('registerProvider').value;
            
            document.getElementById('emailRegister').style.display = provider === 'email' ? 'block' : 'none';
            document.getElementById('phoneRegister').style.display = provider === 'phone' ? 'block' : 'none';
        }

        function handleLogin() {
            const provider = document.getElementById('loginProvider').value;
            let credentials = {};

            switch (provider) {
                case 'email':
                    credentials = {
                        email: document.getElementById('loginEmail').value,
                        password: document.getElementById('loginPassword').value
                    };
                    break;
                case 'phone':
                    credentials = {
                        phone: document.getElementById('loginPhone').value,
                        code: document.getElementById('loginCode').value
                    };
                    break;
                case 'apikey':
                    credentials = {
                        apiKey: document.getElementById('loginApiKey').value
                    };
                    break;
            }

            if (!validateCredentials(provider, credentials)) {
                return;
            }

            vscode.postMessage({
                type: 'login',
                provider: provider,
                credentials: credentials
            });
        }

        function handleRegister() {
            const provider = document.getElementById('registerProvider').value;
            let userData = {};

            if (!document.getElementById('agreeTerms').checked) {
                showError('請先同意服務條款和隱私政策');
                return;
            }

            switch (provider) {
                case 'email':
                    const password = document.getElementById('registerPassword').value;
                    const confirmPassword = document.getElementById('registerConfirmPassword').value;
                    
                    if (password !== confirmPassword) {
                        showError('兩次輸入的密碼不一致');
                        return;
                    }

                    userData = {
                        username: document.getElementById('registerUsername').value,
                        email: document.getElementById('registerEmail').value,
                        password: password
                    };
                    break;
                case 'phone':
                    userData = {
                        username: document.getElementById('registerPhoneUsername').value,
                        phone: document.getElementById('registerPhone').value,
                        code: document.getElementById('registerCode').value
                    };
                    break;
            }

            if (!validateUserData(provider, userData)) {
                return;
            }

            vscode.postMessage({
                type: 'register',
                provider: provider,
                userData: userData
            });
        }

        function handleOAuthLogin(provider) {
            vscode.postMessage({
                type: 'login',
                provider: provider,
                credentials: {}
            });
        }

        function handleOAuthRegister(provider) {
            vscode.postMessage({
                type: 'register',
                provider: provider,
                userData: {}
            });
        }

        function sendVerificationCode(mode) {
            const phoneInput = mode === 'login' ? 
                document.getElementById('loginPhone') : 
                document.getElementById('registerPhone');
            
            const phone = phoneInput.value;
            
            if (!phone) {
                showError('請輸入手機號碼');
                return;
            }

            vscode.postMessage({
                type: 'sendVerificationCode',
                phone: phone
            });
        }

        function startVerificationTimer() {
            const buttons = document.querySelectorAll('.verification-button');
            let countdown = 60;
            
            buttons.forEach(button => {
                button.disabled = true;
                button.textContent = \`\${countdown}s後重發\`;
            });

            verificationTimer = setInterval(() => {
                countdown--;
                buttons.forEach(button => {
                    button.textContent = \`\${countdown}s後重發\`;
                });
                
                if (countdown <= 0) {
                    clearInterval(verificationTimer);
                    buttons.forEach(button => {
                        button.disabled = false;
                        button.textContent = '發送驗證碼';
                    });
                }
            }, 1000);
        }

        function validateCredentials(provider, credentials) {
            switch (provider) {
                case 'email':
                    if (!credentials.email || !credentials.password) {
                        showError('請填寫完整的登錄信息');
                        return false;
                    }
                    break;
                case 'phone':
                    if (!credentials.phone || !credentials.code) {
                        showError('請填寫手機號和驗證碼');
                        return false;
                    }
                    break;
                case 'apikey':
                    if (!credentials.apiKey) {
                        showError('請輸入API Key');
                        return false;
                    }
                    break;
            }
            return true;
        }

        function validateUserData(provider, userData) {
            switch (provider) {
                case 'email':
                    if (!userData.username || !userData.email || !userData.password) {
                        showError('請填寫完整的註冊信息');
                        return false;
                    }
                    if (userData.password.length < 6) {
                        showError('密碼長度至少6位');
                        return false;
                    }
                    break;
                case 'phone':
                    if (!userData.username || !userData.phone || !userData.code) {
                        showError('請填寫完整的註冊信息');
                        return false;
                    }
                    break;
            }
            return true;
        }

        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }

        function showSuccess(message) {
            const successDiv = document.getElementById('successMessage');
            successDiv.textContent = message;
            successDiv.style.display = 'block';
            
            setTimeout(() => {
                successDiv.style.display = 'none';
            }, 3000);
        }

        function clearMessages() {
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('successMessage').style.display = 'none';
        }

        function setLoading(loading) {
            const forms = document.querySelectorAll('.auth-form');
            forms.forEach(form => {
                form.classList.toggle('loading', loading);
            });
        }

        function showForgotPassword() {
            const email = prompt('請輸入您的郵箱地址：');
            if (email) {
                vscode.postMessage({
                    type: 'resetPassword',
                    email: email
                });
            }
        }

        function showTerms() {
            alert('服務條款內容...');
        }

        function showPrivacy() {
            alert('隱私政策內容...');
        }

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 設置默認值（用於演示）
            document.getElementById('loginEmail').value = 'demo@powerautomation.ai';
            document.getElementById('loginPassword').value = 'demo123';
        });
    </script>
</body>
</html>`;
    }

    private _getProviderIcon(provider: string): string {
        const icons: { [key: string]: string } = {
            'email': '📧',
            'github': '🐙',
            'google': '🔍',
            'microsoft': '🪟',
            'phone': '📱',
            'apikey': '🔑'
        };
        return icons[provider] || '🔐';
    }

    private _getProviderName(provider: string): string {
        const names: { [key: string]: string } = {
            'email': '郵箱',
            'github': 'GitHub',
            'google': 'Google',
            'microsoft': 'Microsoft',
            'phone': '手機',
            'apikey': 'API Key'
        };
        return names[provider] || provider;
    }
}

