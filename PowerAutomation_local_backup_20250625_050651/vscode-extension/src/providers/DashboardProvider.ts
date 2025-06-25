import * as vscode from 'vscode';
import { MCPServerManager } from '../services/MCPServerManager';
import { AuthenticationService } from '../services/AuthenticationService';

export class DashboardProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'powerautomation.dashboard';
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

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // 處理來自webview的消息
        webviewView.webview.onDidReceiveMessage(
            message => {
                switch (message.type) {
                    case 'startMCPServer':
                        if (this._authService?.hasPermission('server-management')) {
                            vscode.commands.executeCommand('powerautomation.startMCPServer');
                        } else {
                            this._sendError('您沒有權限執行此操作');
                        }
                        break;
                    case 'stopMCPServer':
                        if (this._authService?.hasPermission('server-management')) {
                            vscode.commands.executeCommand('powerautomation.stopMCPServer');
                        } else {
                            this._sendError('您沒有權限執行此操作');
                        }
                        break;
                    case 'runTests':
                        if (this._authService?.hasPermission('debug-tools')) {
                            vscode.commands.executeCommand('powerautomation.runTests');
                        } else {
                            this._sendError('您沒有權限執行此操作');
                        }
                        break;
                    case 'toggleMode':
                        vscode.commands.executeCommand('powerautomation.toggleMode');
                        break;
                    case 'connectMCP':
                        vscode.commands.executeCommand('powerautomation.connectMCP');
                        break;
                    case 'disconnectMCP':
                        vscode.commands.executeCommand('powerautomation.disconnectMCP');
                        break;
                    case 'testConnection':
                        vscode.commands.executeCommand('powerautomation.testConnection');
                        break;
                    case 'generateAPIKey':
                        if (this._authService?.hasPermission('api-access')) {
                            vscode.commands.executeCommand('powerautomation.generateAPIKey');
                        } else {
                            this._sendError('您沒有權限生成API Key');
                        }
                        break;
                    case 'manageUsers':
                        if (this._authService?.hasPermission('user-management')) {
                            vscode.commands.executeCommand('powerautomation.manageUsers');
                        } else {
                            this._sendError('您沒有權限管理用戶');
                        }
                        break;
                    case 'viewAnalytics':
                        if (this._authService?.hasPermission('analytics')) {
                            vscode.commands.executeCommand('powerautomation.viewAnalytics');
                        } else {
                            this._sendError('您沒有權限查看分析數據');
                        }
                        break;
                    case 'systemConfig':
                        if (this._authService?.hasPermission('system-config')) {
                            vscode.commands.executeCommand('powerautomation.systemConfig');
                        } else {
                            this._sendError('您沒有權限配置系統');
                        }
                        break;
                    case 'openSettings':
                        vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation');
                        break;
                    case 'showOutput':
                        vscode.commands.executeCommand('powerautomation.showOutput');
                        break;
                    case 'refreshDashboard':
                        this.refresh();
                        break;
                    case 'requestLogin':
                        vscode.commands.executeCommand('powerautomation.showAuth');
                        break;
                }
            },
            undefined,
            []
        );
    }

    public show() {
        if (this._view) {
            this._view.show?.(true);
        }
    }

    public refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }

    private _sendError(message: string) {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'error',
                message: message
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const user = this._authService?.getCurrentUser();
        const isAuthenticated = this._authService?.isAuthenticated() || false;

        if (!isAuthenticated) {
            return this._getUnauthenticatedView();
        }

        const interfaceType = user?.interfaceType || 'user';
        
        if (interfaceType === 'user') {
            return this._getUserDashboard(user);
        } else {
            return this._getAdvancedDashboard(user);
        }
    }

    private _getUnauthenticatedView(): string {
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - 未登錄</title>
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
    <div class="title">控制台需要登錄</div>
    <div class="subtitle">
        請先登錄以使用 PowerAutomation 控制台<br>
        登錄後您將可以管理服務、查看統計等
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

    private _getUserDashboard(user: any): string {
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用戶控制台</title>
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

        .dashboard-header {
            text-align: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .dashboard-logo {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .dashboard-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 4px;
            color: #4285f4;
        }

        .dashboard-subtitle {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .user-welcome {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            text-align: center;
        }

        .welcome-text {
            font-size: 14px;
            margin-bottom: 8px;
        }

        .user-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 12px;
        }

        .stat-item {
            text-align: center;
            padding: 8px;
            background: var(--vscode-button-secondaryBackground);
            border-radius: 6px;
        }

        .stat-number {
            font-size: 16px;
            font-weight: 700;
            color: #4285f4;
            display: block;
        }

        .stat-label {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
        }

        .quick-actions {
            margin-bottom: 20px;
        }

        .section-title {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .action-button {
            padding: 12px 8px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 6px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            text-align: center;
        }

        .action-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
            transform: translateY(-1px);
        }

        .action-button.primary {
            background: #4285f4;
            color: white;
        }

        .action-button.primary:hover {
            background: #3367d6;
        }

        .action-icon {
            font-size: 16px;
        }

        .action-text {
            font-size: 10px;
            line-height: 1.2;
        }

        .recent-activity {
            margin-bottom: 20px;
        }

        .activity-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .activity-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            background: var(--vscode-input-background);
            border-radius: 6px;
            font-size: 11px;
        }

        .activity-icon {
            width: 16px;
            text-align: center;
        }

        .activity-text {
            flex: 1;
        }

        .activity-time {
            font-size: 9px;
            color: var(--vscode-descriptionForeground);
        }

        .tips-section {
            background: var(--vscode-textBlockQuote-background);
            border-left: 4px solid #4285f4;
            padding: 12px;
            border-radius: 0 6px 6px 0;
        }

        .tips-title {
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #4285f4;
        }

        .tips-text {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            line-height: 1.3;
        }

        .refresh-button {
            position: fixed;
            top: 8px;
            right: 8px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: var(--vscode-button-background);
            border: none;
            color: var(--vscode-button-foreground);
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .refresh-button:hover {
            background: var(--vscode-button-hoverBackground);
        }
    </style>
</head>
<body>
    <button class="refresh-button" onclick="refreshDashboard()" title="刷新儀表板">🔄</button>

    <div class="dashboard-header">
        <div class="dashboard-logo">👤</div>
        <div class="dashboard-title">用戶控制台</div>
        <div class="dashboard-subtitle">PowerAutomation 智能助手</div>
    </div>

    <div class="user-welcome">
        <div class="welcome-text">歡迎回來，${user?.username || 'User'}！</div>
        <div class="user-stats">
            <div class="stat-item">
                <span class="stat-number">${user?.credits?.toLocaleString() || '0'}</span>
                <div class="stat-label">可用積分</div>
            </div>
            <div class="stat-item">
                <span class="stat-number">${this._getUsageToday()}</span>
                <div class="stat-label">今日使用</div>
            </div>
        </div>
    </div>

    <div class="quick-actions">
        <div class="section-title">
            ⚡ 快速操作
        </div>
        <div class="action-grid">
            <button class="action-button primary" onclick="openChat()">
                <span class="action-icon">💬</span>
                <span class="action-text">開始聊天</span>
            </button>
            <button class="action-button" onclick="openFiles()">
                <span class="action-icon">📁</span>
                <span class="action-text">文件管理</span>
            </button>
            <button class="action-button" onclick="viewHistory()">
                <span class="action-icon">📜</span>
                <span class="action-text">歷史記錄</span>
            </button>
            <button class="action-button" onclick="openSettings()">
                <span class="action-icon">⚙️</span>
                <span class="action-text">設置</span>
            </button>
        </div>
    </div>

    <div class="recent-activity">
        <div class="section-title">
            📋 最近活動
        </div>
        <div class="activity-list">
            <div class="activity-item">
                <span class="activity-icon">💬</span>
                <span class="activity-text">與AI助手對話</span>
                <span class="activity-time">2分鐘前</span>
            </div>
            <div class="activity-item">
                <span class="activity-icon">📁</span>
                <span class="activity-text">上傳了文件</span>
                <span class="activity-time">15分鐘前</span>
            </div>
            <div class="activity-item">
                <span class="activity-icon">⚙️</span>
                <span class="activity-text">更新了設置</span>
                <span class="activity-time">1小時前</span>
            </div>
        </div>
    </div>

    <div class="tips-section">
        <div class="tips-title">💡 使用提示</div>
        <div class="tips-text">
            您可以通過聊天功能與AI助手交流，上傳文件進行分析，或查看歷史對話記錄。如需更多功能，請聯繫管理員升級您的帳戶。
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function openChat() {
            vscode.postMessage({ type: 'openChat' });
        }

        function openFiles() {
            vscode.postMessage({ type: 'openFiles' });
        }

        function viewHistory() {
            vscode.postMessage({ type: 'viewHistory' });
        }

        function openSettings() {
            vscode.postMessage({ type: 'openSettings' });
        }

        function refreshDashboard() {
            vscode.postMessage({ type: 'refreshDashboard' });
        }
    </script>
</body>
</html>`;
    }

    private _getAdvancedDashboard(user: any): string {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const mcpEndpoint = config.get<string>('mcpEndpoint', 'http://18.212.97.173:8080');
        const isMinimalMode = config.get<boolean>('minimalMode', false);

        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高級控制台</title>
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

        .dashboard-header {
            text-align: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .dashboard-logo {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .dashboard-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 4px;
            color: ${user?.userType === 'admin' ? '#dc3545' : '#ff6b35'};
        }

        .dashboard-subtitle {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .user-info {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }

        .user-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }

        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: ${this._getUserTypeColor(user?.userType || 'developer')};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: white;
        }

        .user-details {
            flex: 1;
        }

        .user-name {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 2px;
        }

        .user-meta {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }

        .user-badges {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .badge {
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge.user-type {
            background: ${this._getUserTypeColor(user?.userType || 'developer')};
            color: white;
        }

        .badge.subscription {
            background: ${this._getSubscriptionColor(user?.subscription || 'pro')};
            color: white;
        }

        .status-section {
            margin-bottom: 20px;
        }

        .section-title {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 12px;
        }

        .status-card {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }

        .status-card.connected {
            border-color: var(--vscode-terminal-ansiGreen);
            background: rgba(0, 255, 0, 0.1);
        }

        .status-card.disconnected {
            border-color: var(--vscode-terminal-ansiRed);
            background: rgba(255, 0, 0, 0.1);
        }

        .status-icon {
            font-size: 20px;
            margin-bottom: 4px;
            display: block;
        }

        .status-label {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 2px;
        }

        .status-value {
            font-size: 12px;
            font-weight: 600;
        }

        .actions-section {
            margin-bottom: 20px;
        }

        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .action-button {
            padding: 12px 8px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 6px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            text-align: center;
        }

        .action-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
            transform: translateY(-1px);
        }

        .action-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .action-button.primary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }

        .action-button.primary:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .action-button.danger {
            background: var(--vscode-statusBarItem-errorBackground);
            color: var(--vscode-statusBarItem-errorForeground);
        }

        .action-button.admin-only {
            background: #dc3545;
            color: white;
        }

        .action-button.admin-only:hover {
            background: #c82333;
        }

        .action-icon {
            font-size: 16px;
        }

        .action-text {
            font-size: 10px;
            line-height: 1.2;
        }

        .stats-section {
            margin-bottom: 20px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 6px;
        }

        .stat-card {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            padding: 8px;
            text-align: center;
        }

        .stat-number {
            font-size: 14px;
            font-weight: 700;
            color: ${user?.userType === 'admin' ? '#dc3545' : '#ff6b35'};
            display: block;
            margin-bottom: 2px;
        }

        .stat-label {
            font-size: 9px;
            color: var(--vscode-descriptionForeground);
        }

        .features-section {
            margin-bottom: 20px;
        }

        .features-list {
            display: grid;
            grid-template-columns: 1fr;
            gap: 4px;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 8px;
            background: var(--vscode-input-background);
            border-radius: 4px;
            font-size: 11px;
        }

        .feature-icon {
            width: 16px;
            text-align: center;
        }

        .feature-status {
            margin-left: auto;
            font-size: 10px;
        }

        .feature-status.enabled {
            color: var(--vscode-terminal-ansiGreen);
        }

        .feature-status.disabled {
            color: var(--vscode-terminal-ansiRed);
        }

        .refresh-button {
            position: fixed;
            top: 8px;
            right: 8px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: var(--vscode-button-background);
            border: none;
            color: var(--vscode-button-foreground);
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .refresh-button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .error-message {
            background: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            color: var(--vscode-inputValidation-errorForeground);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 11px;
            margin: 8px 0;
        }
    </style>
</head>
<body>
    <button class="refresh-button" onclick="refreshDashboard()" title="刷新儀表板">🔄</button>

    <div class="dashboard-header">
        <div class="dashboard-logo">${user?.userType === 'admin' ? '👑' : '🔧'}</div>
        <div class="dashboard-title">${user?.userType === 'admin' ? '管理員' : '開發者'}控制台</div>
        <div class="dashboard-subtitle">PowerAutomation 高級管理平台</div>
    </div>

    <div class="user-info">
        <div class="user-header">
            <div class="user-avatar">
                ${user?.avatar ? `<img src="${user.avatar}" style="width:100%;height:100%;border-radius:50%;">` : this._getUserTypeIcon(user?.userType || 'developer')}
            </div>
            <div class="user-details">
                <div class="user-name">${user?.username || 'Unknown User'}</div>
                <div class="user-meta">${user?.email || ''} • ${this._getProviderName(user?.provider || 'apikey')}</div>
            </div>
        </div>
        <div class="user-badges">
            <div class="badge user-type">${this._getUserTypeLabel(user?.userType || 'developer')}</div>
            <div class="badge subscription">${this._getSubscriptionLabel(user?.subscription || 'pro')}</div>
        </div>
    </div>

    <div class="status-section">
        <div class="section-title">
            📊 系統狀態
        </div>
        <div class="status-grid">
            <div class="status-card connected">
                <span class="status-icon">✅</span>
                <div class="status-label">認證狀態</div>
                <div class="status-value">已登錄</div>
            </div>
            <div class="status-card disconnected">
                <span class="status-icon">⚠️</span>
                <div class="status-label">MCP 連接</div>
                <div class="status-value">未連接</div>
            </div>
        </div>
    </div>

    <div class="stats-section">
        <div class="section-title">
            📈 使用統計
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">${user?.credits?.toLocaleString() || '0'}</span>
                <div class="stat-label">可用積分</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">${this._getUsageToday()}</span>
                <div class="stat-label">今日使用</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">${this._getUptime()}</span>
                <div class="stat-label">運行時間</div>
            </div>
        </div>
    </div>

    <div class="actions-section">
        <div class="section-title">
            ⚡ ${user?.userType === 'admin' ? '管理操作' : '開發工具'}
        </div>
        <div class="action-grid">
            <button class="action-button primary" onclick="connectMCP()">
                <span class="action-icon">🔗</span>
                <span class="action-text">連接 MCP</span>
            </button>
            <button class="action-button" onclick="testConnection()">
                <span class="action-icon">🧪</span>
                <span class="action-text">測試連接</span>
            </button>
            ${this._authService?.hasPermission('api-access') ? `
            <button class="action-button" onclick="generateAPIKey()">
                <span class="action-icon">🔑</span>
                <span class="action-text">生成 API Key</span>
            </button>
            ` : ''}
            ${this._authService?.hasPermission('server-management') ? `
            <button class="action-button" onclick="startMCPServer()">
                <span class="action-icon">🚀</span>
                <span class="action-text">啟動服務器</span>
            </button>
            ` : ''}
            ${this._authService?.hasPermission('debug-tools') ? `
            <button class="action-button" onclick="runTests()">
                <span class="action-icon">🧪</span>
                <span class="action-text">運行測試</span>
            </button>
            ` : ''}
            ${this._authService?.hasPermission('user-management') ? `
            <button class="action-button admin-only" onclick="manageUsers()">
                <span class="action-icon">👥</span>
                <span class="action-text">用戶管理</span>
            </button>
            ` : ''}
            ${this._authService?.hasPermission('analytics') ? `
            <button class="action-button admin-only" onclick="viewAnalytics()">
                <span class="action-icon">📊</span>
                <span class="action-text">數據分析</span>
            </button>
            ` : ''}
            ${this._authService?.hasPermission('system-config') ? `
            <button class="action-button admin-only" onclick="systemConfig()">
                <span class="action-icon">⚙️</span>
                <span class="action-text">系統配置</span>
            </button>
            ` : ''}
            <button class="action-button" onclick="toggleMode()">
                <span class="action-icon">${isMinimalMode ? '📱' : '🖥️'}</span>
                <span class="action-text">${isMinimalMode ? '完整模式' : '最小模式'}</span>
            </button>
            <button class="action-button" onclick="openSettings()">
                <span class="action-icon">⚙️</span>
                <span class="action-text">設置</span>
            </button>
            <button class="action-button" onclick="showOutput()">
                <span class="action-icon">📋</span>
                <span class="action-text">查看日誌</span>
            </button>
        </div>
    </div>

    <div class="features-section">
        <div class="section-title">
            ✨ 可用功能
        </div>
        <div class="features-list">
            ${user?.permissions?.map((permission: string) => `
                <div class="feature-item">
                    <span class="feature-icon">${this._getFeatureIcon(permission)}</span>
                    <span>${this._getFeatureLabel(permission)}</span>
                    <span class="feature-status enabled">✓</span>
                </div>
            `).join('') || ''}
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function connectMCP() {
            vscode.postMessage({ type: 'connectMCP' });
        }

        function disconnectMCP() {
            vscode.postMessage({ type: 'disconnectMCP' });
        }

        function testConnection() {
            vscode.postMessage({ type: 'testConnection' });
        }

        function generateAPIKey() {
            vscode.postMessage({ type: 'generateAPIKey' });
        }

        function startMCPServer() {
            vscode.postMessage({ type: 'startMCPServer' });
        }

        function stopMCPServer() {
            vscode.postMessage({ type: 'stopMCPServer' });
        }

        function runTests() {
            vscode.postMessage({ type: 'runTests' });
        }

        function manageUsers() {
            vscode.postMessage({ type: 'manageUsers' });
        }

        function viewAnalytics() {
            vscode.postMessage({ type: 'viewAnalytics' });
        }

        function systemConfig() {
            vscode.postMessage({ type: 'systemConfig' });
        }

        function toggleMode() {
            vscode.postMessage({ type: 'toggleMode' });
        }

        function openSettings() {
            vscode.postMessage({ type: 'openSettings' });
        }

        function showOutput() {
            vscode.postMessage({ type: 'showOutput' });
        }

        function refreshDashboard() {
            vscode.postMessage({ type: 'refreshDashboard' });
        }

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.type) {
                case 'error':
                    showError(message.message);
                    break;
                case 'updateStatus':
                    updateStatus(message.status);
                    break;
            }
        });

        function showError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            document.body.appendChild(errorDiv);
            
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }

        function updateStatus(status) {
            console.log('Status updated:', status);
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

    private _getSubscriptionColor(subscription: string): string {
        switch (subscription) {
            case 'free': return '#28a745';
            case 'pro': return '#007bff';
            case 'enterprise': return '#6f42c1';
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
            case 'phone': return '手機';
            default: return '未知';
        }
    }

    private _getFeatureIcon(feature: string): string {
        switch (feature) {
            case 'api-access': return '🔌';
            case 'local-mode': return '🔧';
            case 'advanced-settings': return '⚙️';
            case 'debug-tools': return '🛠️';
            case 'basic-chat': return '💬';
            case 'advanced-chat': return '🤖';
            case 'file-management': return '📁';
            case 'history': return '📜';
            case 'team-management': return '👥';
            case 'analytics': return '📊';
            case 'custom-integration': return '🔗';
            case 'all-features': return '⭐';
            case 'server-management': return '🖥️';
            case 'user-management': return '👥';
            case 'system-config': return '⚙️';
            default: return '✨';
        }
    }

    private _getFeatureLabel(feature: string): string {
        switch (feature) {
            case 'api-access': return 'API 訪問';
            case 'local-mode': return '本地開發模式';
            case 'advanced-settings': return '高級設置';
            case 'debug-tools': return '調試工具';
            case 'basic-chat': return '基礎對話';
            case 'advanced-chat': return '高級對話';
            case 'file-management': return '文件管理';
            case 'history': return '歷史記錄';
            case 'team-management': return '團隊管理';
            case 'analytics': return '數據分析';
            case 'custom-integration': return '自定義集成';
            case 'all-features': return '全部功能';
            case 'server-management': return '服務器管理';
            case 'user-management': return '用戶管理';
            case 'system-config': return '系統配置';
            default: return feature;
        }
    }

    private _getUsageToday(): string {
        return Math.floor(Math.random() * 200).toString();
    }

    private _getUptime(): string {
        const hours = Math.floor(Math.random() * 24);
        const minutes = Math.floor(Math.random() * 60);
        return `${hours}h ${minutes}m`;
    }
}

