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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const DashboardProvider_1 = require("./providers/DashboardProvider");
const ChatProvider_1 = require("./providers/ChatProvider");
const RepositoryProvider_1 = require("./providers/RepositoryProvider");
const AuthProvider_1 = require("./providers/AuthProvider");
const MCPServerManager_1 = require("./services/MCPServerManager");
const EditorDetectionService_1 = require("./services/EditorDetectionService");
const AuthenticationService_1 = require("./services/AuthenticationService");
const axios_1 = __importDefault(require("axios"));
let statusBarItem;
let outputChannel;
let mcpServerManager;
let authService;
let isConnected = false;
// 全局提供程序实例
let dashboardProvider;
let chatProvider;
let repositoryProvider;
let authProvider;
async function activate(context) {
    // 創建輸出面板
    outputChannel = vscode.window.createOutputChannel('PowerAutomation');
    context.subscriptions.push(outputChannel);
    // 創建狀態欄項目
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'powerautomation.showAuth';
    updateStatusBar('disconnected');
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    // 初始化服務
    mcpServerManager = new MCPServerManager_1.MCPServerManager();
    const editorDetectionService = new EditorDetectionService_1.EditorDetectionService();
    authService = new AuthenticationService_1.AuthenticationService(context);
    // 記錄啟動信息
    logMessage('🚀 PowerAutomation v3.1.1 已啟動');
    logMessage(`📅 啟動時間: ${new Date().toLocaleString()}`);
    // 設置初始上下文
    vscode.commands.executeCommand('setContext', 'powerautomation.enabled', true);
    vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', authService.isAuthenticated());
    // 創建視圖提供者 - 確保正確初始化
    try {
        dashboardProvider = new DashboardProvider_1.DashboardProvider(context.extensionUri, mcpServerManager, authService);
        chatProvider = new ChatProvider_1.ChatProvider(context.extensionUri, mcpServerManager, authService);
        repositoryProvider = new RepositoryProvider_1.RepositoryProvider(context.extensionUri);
        authProvider = new AuthProvider_1.AuthProvider(context.extensionUri, authService);
        logMessage('✅ 所有視圖提供者已創建');
    }
    catch (error) {
        logMessage(`❌ 創建視圖提供者失敗: ${error}`);
        vscode.window.showErrorMessage('PowerAutomation 初始化失敗，請重新加載窗口');
        return;
    }
    // 註冊視圖 - 添加錯誤處理
    try {
        const authViewDisposable = vscode.window.registerWebviewViewProvider('powerautomation.auth', authProvider, {
            webviewOptions: {
                retainContextWhenHidden: true
            }
        });
        const dashboardViewDisposable = vscode.window.registerWebviewViewProvider('powerautomation.dashboard', dashboardProvider, {
            webviewOptions: {
                retainContextWhenHidden: true
            }
        });
        const chatViewDisposable = vscode.window.registerWebviewViewProvider('powerautomation.chat', chatProvider, {
            webviewOptions: {
                retainContextWhenHidden: true
            }
        });
        const repositoryViewDisposable = vscode.window.registerWebviewViewProvider('powerautomation.repository', repositoryProvider, {
            webviewOptions: {
                retainContextWhenHidden: true
            }
        });
        context.subscriptions.push(authViewDisposable, dashboardViewDisposable, chatViewDisposable, repositoryViewDisposable);
        logMessage('✅ 所有視圖已註冊');
    }
    catch (error) {
        logMessage(`❌ 註冊視圖失敗: ${error}`);
        vscode.window.showErrorMessage('PowerAutomation 視圖註冊失敗');
    }
    // 檢查用戶登錄狀態
    if (authService.isAuthenticated()) {
        const user = authService.getCurrentUser();
        logMessage(`👋 歡迎回來，${user?.username}！`);
        logMessage(`🎭 用戶類型: ${authService.getUserType()}`);
        logMessage(`🎯 用戶角色: ${authService.getUserRole()}`);
        // 更新認證狀態
        vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', true);
        // 根據用戶類型自動連接MCP服務
        if (user?.userType === 'developer' || user?.provider === 'apikey') {
            setTimeout(() => {
                connectToMCP();
            }, 1000);
        }
    }
    else {
        logMessage('🔐 用戶未登錄，請先登錄以使用完整功能');
        vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', false);
        // 自動顯示認證面板
        setTimeout(() => {
            vscode.commands.executeCommand('powerautomation.showAuth');
        }, 2000);
    }
    // 檢測智能編輯器
    const hasOtherEditors = await editorDetectionService.detectOtherEditors();
    const config = vscode.workspace.getConfiguration('powerautomation');
    const autoDetect = config.get('autoDetectEditors', true);
    if (autoDetect && hasOtherEditors) {
        logMessage('🔍 檢測到其他智能編輯器，切換到最小模式');
        vscode.commands.executeCommand('setContext', 'powerautomation.minimalMode', true);
    }
    // 註冊命令
    const commands = [
        // 認證相關命令
        vscode.commands.registerCommand('powerautomation.showAuth', () => {
            vscode.commands.executeCommand('powerautomation.auth.focus');
        }),
        vscode.commands.registerCommand('powerautomation.login', async () => {
            vscode.commands.executeCommand('powerautomation.auth.focus');
        }),
        vscode.commands.registerCommand('powerautomation.logout', async () => {
            await authService.logout();
            logMessage('👋 用戶已登出');
            vscode.window.showInformationMessage('已成功登出');
            // 更新認證狀態
            vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', false);
            updateStatusBar('disconnected');
            // 刷新所有視圖
            refreshAllViews();
        }),
        // 視圖刷新命令
        vscode.commands.registerCommand('powerautomation.refreshViews', () => {
            refreshAllViews();
        }),
        // MCP 連接相關命令
        vscode.commands.registerCommand('powerautomation.connectMCP', connectToMCP),
        vscode.commands.registerCommand('powerautomation.disconnectMCP', disconnectFromMCP),
        vscode.commands.registerCommand('powerautomation.testConnection', testConnection),
        // 界面相關命令
        vscode.commands.registerCommand('powerautomation.showDashboard', showDashboard),
        vscode.commands.registerCommand('powerautomation.showOutput', showOutput),
        vscode.commands.registerCommand('powerautomation.openDashboard', () => {
            if (authService.isAuthenticated()) {
                dashboardProvider.show();
            }
            else {
                vscode.window.showWarningMessage('請先登錄以使用此功能', '立即登錄').then(selection => {
                    if (selection === '立即登錄') {
                        vscode.commands.executeCommand('powerautomation.showAuth');
                    }
                });
            }
        }),
        // 模式切換
        vscode.commands.registerCommand('powerautomation.toggleMode', () => {
            const currentMode = vscode.workspace.getConfiguration('powerautomation').get('minimalMode');
            vscode.workspace.getConfiguration('powerautomation').update('minimalMode', !currentMode, true);
            vscode.commands.executeCommand('setContext', 'powerautomation.minimalMode', !currentMode);
            logMessage(`🔄 切換到${!currentMode ? '最小' : '完整'}模式`);
        }),
        // 服務器管理
        vscode.commands.registerCommand('powerautomation.startMCPServer', () => {
            if (authService.hasPermission('server-management')) {
                mcpServerManager.start();
                logMessage('🚀 MCP服務器已啟動');
            }
            else {
                vscode.window.showErrorMessage('您沒有權限執行此操作');
            }
        }),
        vscode.commands.registerCommand('powerautomation.stopMCPServer', () => {
            if (authService.hasPermission('server-management')) {
                mcpServerManager.stop();
                logMessage('⏹️ MCP服務器已停止');
            }
            else {
                vscode.window.showErrorMessage('您沒有權限執行此操作');
            }
        }),
        // 測試功能
        vscode.commands.registerCommand('powerautomation.runTests', () => {
            if (authService.hasPermission('debug-tools')) {
                logMessage('🧪 開始運行Manus測試...');
                vscode.window.showInformationMessage('Manus測試已開始運行，請查看輸出面板');
            }
            else {
                vscode.window.showErrorMessage('您沒有權限執行此操作');
            }
        }),
        // 開發者工具
        vscode.commands.registerCommand('powerautomation.generateAPIKey', generateAPIKey),
        vscode.commands.registerCommand('powerautomation.openDebugTools', () => {
            if (authService.getUserType() === 'developer') {
                vscode.window.showInformationMessage('開發者調試工具已打開');
                // 這裡可以添加開發者專用的調試界面
            }
            else {
                vscode.window.showErrorMessage('此功能僅限開發者使用');
            }
        })
    ];
    context.subscriptions.push(...commands);
    // 監聽認證狀態變化
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.onAuthStateChanged', (authenticated) => {
        vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', authenticated);
        if (authenticated) {
            const user = authService.getCurrentUser();
            logMessage(`✅ 用戶登錄成功: ${user?.username}`);
            updateStatusBar('connected');
            // 刷新所有視圖
            refreshAllViews();
            // 根據用戶類型自動執行相應操作
            if (user?.userType === 'developer') {
                setTimeout(() => {
                    connectToMCP();
                }, 1000);
            }
        }
        else {
            logMessage('🔐 用戶已登出');
            updateStatusBar('disconnected');
            isConnected = false;
            // 刷新所有視圖
            refreshAllViews();
        }
    }));
    logMessage('✅ PowerAutomation 擴展初始化完成');
}
exports.activate = activate;
function refreshAllViews() {
    try {
        if (dashboardProvider) {
            dashboardProvider.refresh();
        }
        if (chatProvider) {
            chatProvider.refresh();
        }
        if (repositoryProvider) {
            repositoryProvider.refresh();
        }
        // AuthProvider 會自動根據認證狀態更新
        logMessage('🔄 所有視圖已刷新');
    }
    catch (error) {
        logMessage(`❌ 刷新視圖失敗: ${error}`);
    }
}
function updateStatusBar(status) {
    const user = authService?.getCurrentUser();
    const userInfo = user ? ` (${user.username})` : '';
    switch (status) {
        case 'disconnected':
            statusBarItem.text = '$(circle-outline) PowerAutomation v3.1.1';
            statusBarItem.tooltip = `PowerAutomation - ${user ? '已登錄但未連接MCP服務' : '未登錄'}${userInfo}`;
            statusBarItem.backgroundColor = undefined;
            break;
        case 'connecting':
            statusBarItem.text = '$(sync~spin) PowerAutomation v3.1.1';
            statusBarItem.tooltip = `PowerAutomation - 正在連接MCP服務...${userInfo}`;
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            break;
        case 'connected':
            statusBarItem.text = '$(check) PowerAutomation v3.1.1';
            statusBarItem.tooltip = `PowerAutomation - 已連接MCP服務${userInfo}`;
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.prominentBackground');
            break;
        case 'error':
            statusBarItem.text = '$(error) PowerAutomation v3.1.1';
            statusBarItem.tooltip = `PowerAutomation - MCP服務連接錯誤${userInfo}`;
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            break;
    }
}
function logMessage(message) {
    const timestamp = new Date().toLocaleTimeString();
    outputChannel.appendLine(`[${timestamp}] ${message}`);
}
async function connectToMCP() {
    if (!authService.isAuthenticated()) {
        vscode.window.showWarningMessage('請先登錄以連接MCP服務', '立即登錄').then(selection => {
            if (selection === '立即登錄') {
                vscode.commands.executeCommand('powerautomation.showAuth');
            }
        });
        return;
    }
    if (isConnected) {
        vscode.window.showInformationMessage('已經連接到MCP服務');
        return;
    }
    updateStatusBar('connecting');
    logMessage('🔗 開始連接到MCP服務...');
    const config = vscode.workspace.getConfiguration('powerautomation');
    const user = authService.getCurrentUser();
    let endpoint = config.get('mcpEndpoint', 'http://18.212.97.173:8080');
    let apiKey = '';
    // 根據用戶類型獲取認證信息
    if (user?.provider === 'apikey') {
        // 開發者使用API Key
        apiKey = user.id.replace('api_', 'pa_'); // 簡化的API Key獲取
        logMessage(`🔑 使用開發者API Key認證`);
    }
    else {
        // 普通用戶使用配置的API Key
        apiKey = config.get('apiKey', '');
        if (!apiKey || apiKey.trim() === '') {
            updateStatusBar('error');
            logMessage('❌ 錯誤: 未配置API Key');
            vscode.window.showErrorMessage('請先配置API Key', '生成API Key').then(selection => {
                if (selection === '生成API Key') {
                    generateAPIKey();
                }
            });
            return;
        }
    }
    const timeout = config.get('timeout', 30000);
    logMessage(`📡 MCP端點: ${endpoint}`);
    logMessage(`👤 用戶: ${user?.username} (${user?.userType})`);
    logMessage(`🔑 認證方式: ${user?.provider}`);
    try {
        const response = await axios_1.default.post(`${endpoint}/api/process`, {
            request: 'connection_test',
            context: {
                source: 'vscode_vsix',
                client: 'powerautomation',
                user_id: user?.id,
                user_type: user?.userType,
                version: '3.1.1'
            }
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'User-Agent': 'PowerAutomation-VSIX/3.1.1'
            },
            timeout: timeout
        });
        if (response.status === 200) {
            isConnected = true;
            updateStatusBar('connected');
            logMessage('✅ MCP服務連接成功！');
            logMessage(`📊 服務器響應: ${JSON.stringify(response.data)}`);
            vscode.window.showInformationMessage('已成功連接到PowerAutomation MCP服務');
            // 開始心跳
            startHeartbeat();
        }
        else {
            throw new Error(`連接失敗: ${response.status} ${response.statusText}`);
        }
    }
    catch (error) {
        isConnected = false;
        updateStatusBar('error');
        const errorMessage = error.response?.data?.message || error.message || '未知錯誤';
        logMessage(`❌ MCP服務連接失敗: ${errorMessage}`);
        // 根據錯誤類型提供不同的處理建議
        if (error.response?.status === 401) {
            vscode.window.showErrorMessage('認證失敗，請檢查API Key或重新登錄', '重新登錄').then(selection => {
                if (selection === '重新登錄') {
                    vscode.commands.executeCommand('powerautomation.logout');
                }
            });
        }
        else if (error.response?.status === 404) {
            vscode.window.showErrorMessage('服務端點不存在，請檢查配置', '檢查配置').then(selection => {
                if (selection === '檢查配置') {
                    vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation');
                }
            });
        }
        else {
            vscode.window.showErrorMessage(`MCP連接失敗: ${errorMessage}`, '重試', '檢查配置').then(selection => {
                if (selection === '重試') {
                    setTimeout(connectToMCP, 5000);
                }
                else if (selection === '檢查配置') {
                    vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation');
                }
            });
        }
    }
}
async function disconnectFromMCP() {
    if (!isConnected) {
        vscode.window.showInformationMessage('尚未連接到MCP服務');
        return;
    }
    logMessage('🔌 正在斷開MCP服務連接...');
    isConnected = false;
    updateStatusBar('disconnected');
    logMessage('✅ 已斷開MCP服務連接');
    vscode.window.showInformationMessage('已斷開PowerAutomation MCP服務連接');
}
function startHeartbeat() {
    const config = vscode.workspace.getConfiguration('powerautomation');
    const enableHeartbeat = config.get('enableHeartbeat', true);
    const interval = config.get('heartbeatInterval', 30) * 1000;
    if (!enableHeartbeat) {
        return;
    }
    setInterval(async () => {
        if (!isConnected || !authService.isAuthenticated()) {
            return;
        }
        try {
            const endpoint = config.get('mcpEndpoint', 'http://18.212.97.173:8080');
            const user = authService.getCurrentUser();
            let apiKey = '';
            if (user?.provider === 'apikey') {
                apiKey = user.id.replace('api_', 'pa_');
            }
            else {
                apiKey = config.get('apiKey', '');
            }
            await axios_1.default.post(`${endpoint}/api/heartbeat`, {
                timestamp: Date.now(),
                status: 'active',
                user_id: user?.id,
                user_type: user?.userType
            }, {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json'
                },
                timeout: 5000
            });
            logMessage('💓 心跳發送成功');
        }
        catch (error) {
            logMessage(`💔 心跳發送失敗: ${error.message}`);
            // 心跳失敗時嘗試重新連接
            isConnected = false;
            updateStatusBar('error');
            setTimeout(connectToMCP, 5000);
        }
    }, interval);
}
function showDashboard() {
    if (authService.isAuthenticated()) {
        logMessage('📊 顯示儀表板');
        vscode.commands.executeCommand('powerautomation.openDashboard');
    }
    else {
        vscode.window.showWarningMessage('請先登錄以使用此功能', '立即登錄').then(selection => {
            if (selection === '立即登錄') {
                vscode.commands.executeCommand('powerautomation.showAuth');
            }
        });
    }
}
function showOutput() {
    outputChannel.show();
}
async function testConnection() {
    if (!authService.isAuthenticated()) {
        vscode.window.showWarningMessage('請先登錄以測試連接', '立即登錄').then(selection => {
            if (selection === '立即登錄') {
                vscode.commands.executeCommand('powerautomation.showAuth');
            }
        });
        return;
    }
    logMessage('🧪 開始測試MCP連接...');
    vscode.window.showInformationMessage('正在測試MCP連接，請查看輸出面板');
    const config = vscode.workspace.getConfiguration('powerautomation');
    const endpoint = config.get('mcpEndpoint', 'http://18.212.97.173:8080');
    const user = authService.getCurrentUser();
    let apiKey = '';
    if (user?.provider === 'apikey') {
        apiKey = user.id.replace('api_', 'pa_');
    }
    else {
        apiKey = config.get('apiKey', '');
    }
    try {
        const response = await axios_1.default.get(`${endpoint}/api/health`, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            timeout: 10000
        });
        logMessage(`✅ 連接測試成功: ${JSON.stringify(response.data)}`);
        vscode.window.showInformationMessage('MCP服務連接測試成功');
    }
    catch (error) {
        const errorMessage = error.response?.data?.message || error.message || '未知錯誤';
        logMessage(`❌ 連接測試失敗: ${errorMessage}`);
        vscode.window.showErrorMessage(`連接測試失敗: ${errorMessage}`);
    }
}
function generateAPIKey() {
    if (!authService.hasPermission('api-access')) {
        vscode.window.showErrorMessage('您沒有權限生成API Key');
        return;
    }
    const apiKey = `pa_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;
    vscode.window.showInformationMessage(`已生成新的API Key: ${apiKey}`, '複製到剪貼板', '保存到設置').then(selection => {
        if (selection === '複製到剪貼板') {
            vscode.env.clipboard.writeText(apiKey);
            vscode.window.showInformationMessage('API Key已複製到剪貼板');
        }
        else if (selection === '保存到設置') {
            vscode.workspace.getConfiguration('powerautomation').update('apiKey', apiKey, true);
            vscode.window.showInformationMessage('API Key已保存到設置');
        }
    });
    logMessage(`🔑 已生成新的API Key: ${apiKey}`);
}
function deactivate() {
    logMessage('👋 PowerAutomation 擴展已停用');
    if (outputChannel) {
        outputChannel.dispose();
    }
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map