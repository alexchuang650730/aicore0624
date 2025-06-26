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
exports.DashboardProvider = void 0;
const vscode = __importStar(require("vscode"));
class DashboardProvider {
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
        webviewView.webview.onDidReceiveMessage(message => {
            switch (message.type) {
                case 'startMCPServer':
                    vscode.commands.executeCommand('powerautomation.startMCPServer');
                    break;
                case 'stopMCPServer':
                    vscode.commands.executeCommand('powerautomation.stopMCPServer');
                    break;
                case 'runTests':
                    vscode.commands.executeCommand('powerautomation.runTests');
                    break;
                case 'toggleMode':
                    vscode.commands.executeCommand('powerautomation.toggleMode');
                    break;
            }
        }, undefined, []);
    }
    show() {
        if (this._view) {
            this._view.show?.(true);
        }
    }
    refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }
    _getHtmlForWebview(webview) {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const isMinimalMode = config.get('minimalMode', false);
        const serverStatus = this._mcpServerManager.isRunning() ? 'running' : 'stopped';
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation Dashboard</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 16px;
        }

        .dashboard-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .dashboard-title {
            font-size: 14px;
            font-weight: 600;
            margin-left: 8px;
        }

        .mode-indicator {
            margin-left: auto;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 2px;
            background: ${isMinimalMode ? 'var(--vscode-statusBarItem-warningBackground)' : 'var(--vscode-statusBarItem-activeBackground)'};
            color: var(--vscode-statusBarItem-activeForeground);
        }

        .status-section {
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--vscode-descriptionForeground);
        }

        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            margin-bottom: 6px;
            background: var(--vscode-input-background);
            border-radius: 4px;
            border-left: 3px solid var(--vscode-focusBorder);
        }

        .status-label {
            font-size: 12px;
        }

        .status-value {
            font-size: 12px;
            font-weight: 600;
        }

        .status-positive {
            color: var(--vscode-terminal-ansiGreen);
        }

        .status-warning {
            color: var(--vscode-terminal-ansiYellow);
        }

        .status-error {
            color: var(--vscode-terminal-ansiRed);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 16px;
        }

        .stat-card {
            background: var(--vscode-input-background);
            padding: 12px;
            border-radius: 4px;
            text-align: center;
        }

        .stat-number {
            font-size: 18px;
            font-weight: 700;
            color: var(--vscode-terminal-ansiGreen);
            display: block;
        }

        .stat-label {
            font-size: 10px;
            margin-top: 4px;
            color: var(--vscode-descriptionForeground);
        }

        .action-button {
            width: 100%;
            padding: 10px 12px;
            margin-bottom: 8px;
            background: var(--vscode-button-background);
            border: none;
            border-radius: 4px;
            color: var(--vscode-button-foreground);
            font-size: 12px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .action-button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .action-button.secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }

        .action-button.secondary:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .server-controls {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }

        .server-controls button {
            flex: 1;
            padding: 8px;
            font-size: 11px;
        }

        .minimal-mode-notice {
            background: var(--vscode-statusBarItem-warningBackground);
            color: var(--vscode-statusBarItem-warningForeground);
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 16px;
            font-size: 11px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <span>🤖</span>
        <div class="dashboard-title">PowerAutomation</div>
        <div class="mode-indicator">${isMinimalMode ? 'MINIMAL' : 'FULL'}</div>
    </div>

    ${isMinimalMode ? `
    <div class="minimal-mode-notice">
        🔍 Minimal mode active - Other smart editors detected
    </div>
    ` : ''}

    <!-- 實時狀態 -->
    <div class="status-section">
        <div class="section-title">📊 實時狀態</div>
        <div class="status-item">
            <span class="status-label">🤖 MCP服務器</span>
            <span class="status-value ${serverStatus === 'running' ? 'status-positive' : 'status-error'}">
                ${serverStatus === 'running' ? '運行中' : '已停止'}
            </span>
        </div>
        <div class="status-item">
            <span class="status-label">💎 積分</span>
            <span class="status-value status-positive">2,847 (+127)</span>
        </div>
        <div class="status-item">
            <span class="status-label">💰 節省</span>
            <span class="status-value status-positive">$8.42</span>
        </div>
        <div class="status-item">
            <span class="status-label">⚡ 智慧路由</span>
            <span class="status-value">端側處理</span>
        </div>
    </div>

    <!-- MCP服務器控制 -->
    <div class="status-section">
        <div class="section-title">🔧 服務器控制</div>
        <div class="server-controls">
            <button class="action-button" onclick="sendMessage('startMCPServer')">
                ▶️ 啟動
            </button>
            <button class="action-button secondary" onclick="sendMessage('stopMCPServer')">
                ⏹️ 停止
            </button>
        </div>
    </div>

    <!-- OCR統計 -->
    <div class="status-section">
        <div class="section-title">📄 OCR統計</div>
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">156</span>
                <div class="stat-label">今日處理</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">98.7%</span>
                <div class="stat-label">準確率</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">2.3s</span>
                <div class="stat-label">平均耗時</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">1,247</span>
                <div class="stat-label">總文檔</div>
            </div>
        </div>
    </div>

    <!-- 快速操作 -->
    <div class="status-section">
        <div class="section-title">🚀 快速操作</div>
        <button class="action-button" onclick="sendMessage('runTests')">
            🧪 運行Manus測試
        </button>
        <button class="action-button secondary" onclick="sendMessage('toggleMode')">
            🔄 切換佈局模式
        </button>
        <button class="action-button secondary">
            📊 查看報告
        </button>
        <button class="action-button secondary">
            ⚙️ 設置
        </button>
    </div>

    <!-- 最近活動 -->
    <div class="status-section">
        <div class="section-title">📋 最近活動</div>
        <div class="status-item">
            <span class="status-label">📄 TC001測試</span>
            <span class="status-value status-positive">完成</span>
        </div>
        <div class="status-item">
            <span class="status-label">🤖 MCP適配器</span>
            <span class="status-value status-warning">運行中</span>
        </div>
        <div class="status-item">
            <span class="status-label">📊 數據同步</span>
            <span class="status-value status-positive">完成</span>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function sendMessage(type, data = {}) {
            vscode.postMessage({
                type: type,
                ...data
            });
        }

        // 定期更新狀態
        setInterval(() => {
            // 這裡可以添加定期更新邏輯
        }, 5000);
    </script>
</body>
</html>`;
    }
}
exports.DashboardProvider = DashboardProvider;
DashboardProvider.viewType = 'powerautomation.dashboard';
//# sourceMappingURL=DashboardProvider.js.map