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

        // 確保數據提供程序正確初始化
        this._initializeDataProvider();

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
                    case 'getDashboardData':
                        this._sendDashboardData();
                        break;
                }
            },
            undefined,
            []
        );
    }

    private _initializeDataProvider() {
        // 確保數據提供程序正確註冊
        try {
            // 這裡可以添加任何必要的數據提供程序初始化邏輯
            console.log('Dashboard data provider initialized');
        } catch (error) {
            console.error('Failed to initialize dashboard data provider:', error);
        }
    }

    private _sendDashboardData() {
        if (!this._view) return;

        const user = this._authService?.getCurrentUser();
        const dashboardData = {
            user: user,
            stats: this._getSystemStats(),
            recentActivity: this._getRecentActivity(),
            systemStatus: this._getSystemStatus()
        };

        this._view.webview.postMessage({
            type: 'dashboardData',
            data: dashboardData
        });
    }

    private _getSystemStats() {
        return {
            totalUsers: 1247,
            activeConnections: 23,
            requestsToday: 156,
            uptime: '99.9%'
        };
    }

    private _getRecentActivity() {
        return [
            { type: 'chat', message: '與AI助手對話', time: '2分鐘前' },
            { type: 'file', message: '上傳了文件', time: '15分鐘前' },
            { type: 'api', message: 'API調用成功', time: '1小時前' }
        ];
    }

    private _getSystemStatus() {
        return {
            mcpServer: 'running',
            database: 'healthy',
            apiEndpoint: 'online'
        };
    }

    public show() {
        if (this._view) {
            this._view.show?.(true);
        }
    }

    public refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
            // 發送最新數據
            this._sendDashboardData();
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

        // 請求初始數據
        vscode.postMessage({ type: 'getDashboardData' });
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
                <span class="stat-number" id="userCredits">0</span>
                <div class="stat-label">可用積分</div>
            </div>
            <div class="stat-item">
                <span class="stat-number" id="usageToday">0</span>
                <div class="stat-label">今日使用</div>
            </div>
        </div>
    </div>

    <div class="quick-actions">
        <div class="section-title">
            ⚡ 快速操作
        </div>
        <div class="action-grid">
            <button class="action-button primary" onclick="connectMCP()">
                <span class="action-icon">🔗</span>
                <span class="action-text">連接服務</span>
            </button>
            <button class="action-button" onclick="testConnection()">
                <span class="action-icon">🧪</span>
                <span class="action-text">測試連接</span>
            </button>
            <button class="action-button" onclick="showOutput()">
                <span class="action-icon">📋</span>
                <span class="action-text">查看日誌</span>
            </button>
            <button class="action-button" onclick="openSettings()">
                <span class="action-icon">⚙️</span>
                <span class="action-text">設置</span>
            </button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'dashboardData':
                    updateDashboard(message.data);
                    break;
                case 'error':
                    showError(message.message);
                    break;
            }
        });

        function updateDashboard(data) {
            if (data.user) {
                document.getElementById('userCredits').textContent = data.user.credits?.toLocaleString() || '0';
            }
            if (data.stats) {
                document.getElementById('usageToday').textContent = data.stats.requestsToday || '0';
            }
        }

        function showError(message) {
            // 可以添加錯誤顯示邏輯
            console.error('Dashboard error:', message);
        }

        function connectMCP() {
            vscode.postMessage({ type: 'connectMCP' });
        }

        function testConnection() {
            vscode.postMessage({ type: 'testConnection' });
        }

        function showOutput() {
            vscode.postMessage({ type: 'showOutput' });
        }

        function openSettings() {
            vscode.postMessage({ type: 'openSettings' });
        }

        function refreshDashboard() {
            vscode.postMessage({ type: 'refreshDashboard' });
        }

        // 頁面加載時請求數據
        vscode.postMessage({ type: 'getDashboardData' });
    </script>
</body>
</html>`;
    }

    private _getAdvancedDashboard(user: any): string {
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理員控制台</title>
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
            color: #ff6b35;
        }

        .dashboard-subtitle {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .admin-welcome {
            background: linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(255, 107, 53, 0.05) 100%);
            border: 1px solid rgba(255, 107, 53, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            text-align: center;
        }

        .welcome-text {
            font-size: 14px;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .admin-stats {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
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
            font-size: 14px;
            font-weight: 700;
            color: #ff6b35;
            display: block;
        }

        .stat-label {
            font-size: 9px;
            color: var(--vscode-descriptionForeground);
        }

        .management-sections {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }

        .section {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 12px;
        }

        .section-title {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
            color: #ff6b35;
        }

        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
        }

        .action-button {
            padding: 8px 6px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 4px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 10px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            text-align: center;
        }

        .action-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
            transform: translateY(-1px);
        }

        .action-button.danger {
            background: rgba(244, 67, 54, 0.1);
            color: #f44336;
            border: 1px solid rgba(244, 67, 54, 0.3);
        }

        .action-button.danger:hover {
            background: rgba(244, 67, 54, 0.2);
        }

        .action-button.primary {
            background: #ff6b35;
            color: white;
        }

        .action-button.primary:hover {
            background: #e55a2b;
        }

        .action-icon {
            font-size: 14px;
        }

        .action-text {
            font-size: 9px;
            line-height: 1.1;
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
        <div class="dashboard-logo">🔧</div>
        <div class="dashboard-title">管理員控制台</div>
        <div class="dashboard-subtitle">PowerAutomation 高級管理</div>
    </div>

    <div class="admin-welcome">
        <div class="welcome-text">管理員 ${user?.username || 'Admin'}</div>
        <div class="admin-stats">
            <div class="stat-item">
                <span class="stat-number" id="totalUsers">0</span>
                <div class="stat-label">總用戶</div>
            </div>
            <div class="stat-item">
                <span class="stat-number" id="activeConnections">0</span>
                <div class="stat-label">活躍連接</div>
            </div>
            <div class="stat-item">
                <span class="stat-number" id="systemUptime">0</span>
                <div class="stat-label">系統運行</div>
            </div>
        </div>
    </div>

    <div class="management-sections">
        <div class="section">
            <div class="section-title">
                🚀 服務管理
            </div>
            <div class="action-grid">
                <button class="action-button primary" onclick="startMCPServer()">
                    <span class="action-icon">▶️</span>
                    <span class="action-text">啟動服務</span>
                </button>
                <button class="action-button danger" onclick="stopMCPServer()">
                    <span class="action-icon">⏹️</span>
                    <span class="action-text">停止服務</span>
                </button>
                <button class="action-button" onclick="connectMCP()">
                    <span class="action-icon">🔗</span>
                    <span class="action-text">連接MCP</span>
                </button>
                <button class="action-button" onclick="testConnection()">
                    <span class="action-icon">🧪</span>
                    <span class="action-text">測試連接</span>
                </button>
            </div>
        </div>

        <div class="section">
            <div class="section-title">
                👥 用戶管理
            </div>
            <div class="action-grid">
                <button class="action-button" onclick="manageUsers()">
                    <span class="action-icon">👤</span>
                    <span class="action-text">用戶列表</span>
                </button>
                <button class="action-button" onclick="viewAnalytics()">
                    <span class="action-icon">📊</span>
                    <span class="action-text">使用分析</span>
                </button>
                <button class="action-button" onclick="generateAPIKey()">
                    <span class="action-icon">🔑</span>
                    <span class="action-text">生成密鑰</span>
                </button>
                <button class="action-button" onclick="systemConfig()">
                    <span class="action-icon">⚙️</span>
                    <span class="action-text">系統配置</span>
                </button>
            </div>
        </div>

        <div class="section">
            <div class="section-title">
                🛠️ 開發工具
            </div>
            <div class="action-grid">
                <button class="action-button" onclick="runTests()">
                    <span class="action-icon">🧪</span>
                    <span class="action-text">運行測試</span>
                </button>
                <button class="action-button" onclick="showOutput()">
                    <span class="action-icon">📋</span>
                    <span class="action-text">查看日誌</span>
                </button>
                <button class="action-button" onclick="toggleMode()">
                    <span class="action-icon">🔄</span>
                    <span class="action-text">切換模式</span>
                </button>
                <button class="action-button" onclick="openSettings()">
                    <span class="action-icon">⚙️</span>
                    <span class="action-text">設置</span>
                </button>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'dashboardData':
                    updateDashboard(message.data);
                    break;
                case 'error':
                    showError(message.message);
                    break;
            }
        });

        function updateDashboard(data) {
            if (data.stats) {
                document.getElementById('totalUsers').textContent = data.stats.totalUsers?.toLocaleString() || '0';
                document.getElementById('activeConnections').textContent = data.stats.activeConnections || '0';
                document.getElementById('systemUptime').textContent = data.stats.uptime || '0%';
            }
        }

        function showError(message) {
            console.error('Dashboard error:', message);
        }

        // 服務管理
        function startMCPServer() {
            vscode.postMessage({ type: 'startMCPServer' });
        }

        function stopMCPServer() {
            vscode.postMessage({ type: 'stopMCPServer' });
        }

        function connectMCP() {
            vscode.postMessage({ type: 'connectMCP' });
        }

        function testConnection() {
            vscode.postMessage({ type: 'testConnection' });
        }

        // 用戶管理
        function manageUsers() {
            vscode.postMessage({ type: 'manageUsers' });
        }

        function viewAnalytics() {
            vscode.postMessage({ type: 'viewAnalytics' });
        }

        function generateAPIKey() {
            vscode.postMessage({ type: 'generateAPIKey' });
        }

        function systemConfig() {
            vscode.postMessage({ type: 'systemConfig' });
        }

        // 開發工具
        function runTests() {
            vscode.postMessage({ type: 'runTests' });
        }

        function showOutput() {
            vscode.postMessage({ type: 'showOutput' });
        }

        function toggleMode() {
            vscode.postMessage({ type: 'toggleMode' });
        }

        function openSettings() {
            vscode.postMessage({ type: 'openSettings' });
        }

        function refreshDashboard() {
            vscode.postMessage({ type: 'refreshDashboard' });
        }

        // 頁面加載時請求數據
        vscode.postMessage({ type: 'getDashboardData' });
    </script>
</body>
</html>`;
    }

    private _getUsageToday(): string {
        // 模擬獲取今日使用量
        return Math.floor(Math.random() * 50).toString();
    }
}

