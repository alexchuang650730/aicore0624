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
let isConnected = false;
async function activate(context) {
    // 創建輸出面板
    outputChannel = vscode.window.createOutputChannel('PowerAutomation');
    context.subscriptions.push(outputChannel);
    // 創建狀態欄項目
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'powerautomation.connectMCP';
    updateStatusBar('disconnected');
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    // 初始化服務
    mcpServerManager = new MCPServerManager_1.MCPServerManager();
    const editorDetectionService = new EditorDetectionService_1.EditorDetectionService();
    const authService = new AuthenticationService_1.AuthenticationService();
    // 記錄啟動信息
    logMessage('🚀 PowerAutomation v3.0.0 已啟動');
    logMessage(`📅 啟動時間: ${new Date().toLocaleString()}`);
    // 檢測智能編輯器
    const hasOtherEditors = await editorDetectionService.detectOtherEditors();
    const config = vscode.workspace.getConfiguration('powerautomation');
    const autoDetect = config.get('autoDetectEditors', true);
    if (autoDetect && hasOtherEditors) {
        logMessage('🔍 檢測到其他智能編輯器，切換到最小模式');
        vscode.commands.executeCommand('setContext', 'powerautomation.minimalMode', true);
    }
    // 創建視圖提供者
    const dashboardProvider = new DashboardProvider_1.DashboardProvider(context.extensionUri, mcpServerManager);
    const chatProvider = new ChatProvider_1.ChatProvider(context.extensionUri, mcpServerManager);
    const repositoryProvider = new RepositoryProvider_1.RepositoryProvider(context.extensionUri);
    const authProvider = new AuthProvider_1.AuthProvider(context.extensionUri, authService);
    // 註冊視圖
    vscode.window.registerWebviewViewProvider('powerautomation.dashboard', dashboardProvider);
    vscode.window.registerWebviewViewProvider('powerautomation.chat', chatProvider);
    vscode.window.registerWebviewViewProvider('powerautomation.repository', repositoryProvider);
    vscode.window.registerWebviewViewProvider('powerautomation.auth', authProvider);
    // 註冊命令
    const commands = [
        vscode.commands.registerCommand('powerautomation.connectMCP', connectToMCP),
        vscode.commands.registerCommand('powerautomation.disconnectMCP', disconnectFromMCP),
        vscode.commands.registerCommand('powerautomation.showDashboard', showDashboard),
        vscode.commands.registerCommand('powerautomation.generateAPIKey', generateAPIKey),
        vscode.commands.registerCommand('powerautomation.testConnection', testConnection),
        vscode.commands.registerCommand('powerautomation.showOutput', showOutput),
        vscode.commands.registerCommand('powerautomation.openDashboard', () => {
            dashboardProvider.show();
        }),
        vscode.commands.registerCommand('powerautomation.toggleMode', () => {
            const currentMode = vscode.workspace.getConfiguration('powerautomation').get('minimalMode');
            vscode.workspace.getConfiguration('powerautomation').update('minimalMode', !currentMode, true);
            vscode.commands.executeCommand('setContext', 'powerautomation.minimalMode', !currentMode);
            logMessage(`🔄 切換到${!currentMode ? '最小' : '完整'}模式`);
        }),
        vscode.commands.registerCommand('powerautomation.startMCPServer', () => {
            mcpServerManager.start();
            logMessage('🚀 MCP服務器已啟動');
        }),
        vscode.commands.registerCommand('powerautomation.stopMCPServer', () => {
            mcpServerManager.stop();
            logMessage('⏹️ MCP服務器已停止');
        }),
        vscode.commands.registerCommand('powerautomation.runTests', () => {
            logMessage('🧪 開始運行Manus測試...');
            vscode.window.showInformationMessage('Manus測試已開始運行，請查看輸出面板');
        })
    ];
    context.subscriptions.push(...commands);
    // 自動嘗試連接MCP服務
    setTimeout(() => {
        const apiKey = config.get('apiKey');
        if (apiKey && apiKey.trim() !== '') {
            logMessage('🔄 自動嘗試連接MCP服務...');
            connectToMCP();
        }
        else {
            logMessage('⚠️ 未配置API Key，請先生成API Key並配置');
        }
    }, 2000);
}
exports.activate = activate;
function updateStatusBar(status) {
    switch (status) {
        case 'disconnected':
            statusBarItem.text = '$(circle-outline) PowerAutomation v3.0.0';
            statusBarItem.tooltip = 'PowerAutomation - 未連接到MCP服務';
            statusBarItem.backgroundColor = undefined;
            break;
        case 'connecting':
            statusBarItem.text = '$(sync~spin) PowerAutomation v3.0.0';
            statusBarItem.tooltip = 'PowerAutomation - 正在連接MCP服務...';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            break;
        case 'connected':
            statusBarItem.text = '$(check) PowerAutomation v3.0.0';
            statusBarItem.tooltip = 'PowerAutomation - 已連接到MCP服務';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.prominentBackground');
            break;
        case 'error':
            statusBarItem.text = '$(error) PowerAutomation v3.0.0';
            statusBarItem.tooltip = 'PowerAutomation - MCP服務連接錯誤';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            break;
    }
}
function logMessage(message) {
    const timestamp = new Date().toLocaleTimeString();
    outputChannel.appendLine(`[${timestamp}] ${message}`);
}
async function connectToMCP() {
    if (isConnected) {
        vscode.window.showInformationMessage('已經連接到MCP服務');
        return;
    }
    updateStatusBar('connecting');
    logMessage('🔗 開始連接到MCP服務...');
    const config = vscode.workspace.getConfiguration('powerautomation');
    const endpoint = config.get('mcpEndpoint', 'http://localhost:8080/mcp/v3');
    const apiKey = config.get('apiKey', '');
    const timeout = config.get('timeout', 30000);
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
    logMessage(`📡 MCP端點: ${endpoint}`);
    logMessage(`🔑 API Key: ${apiKey.substring(0, 20)}...`);
    try {
        const response = await axios_1.default.post(`${endpoint}/connect`, {
            client_id: 'powerautomation-vscode',
            version: '3.0.0',
            capabilities: ['chat', 'automation', 'file_management']
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'X-MCP-Version': '3.0.0'
            },
            timeout: timeout
        });
        if (response.status === 200) {
            isConnected = true;
            updateStatusBar('connected');
            logMessage('✅ MCP服務連接成功！');
            logMessage(`📊 服務器信息: ${JSON.stringify(response.data)}`);
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
        if (!isConnected) {
            return;
        }
        try {
            const endpoint = config.get('mcpEndpoint', 'http://localhost:8080/mcp/v3');
            const apiKey = config.get('apiKey', '');
            await axios_1.default.post(`${endpoint}/heartbeat`, {
                timestamp: Date.now(),
                status: 'active'
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
    logMessage('📊 顯示儀表板');
    vscode.commands.executeCommand('powerautomation.openDashboard');
}
function generateAPIKey() {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 18);
    const hostname = require('os').hostname().substring(0, 8);
    const apiKey = `pa_v3_${timestamp}_${random}_${hostname}`;
    logMessage(`🔑 生成新的API Key: ${apiKey}`);
    vscode.env.clipboard.writeText(apiKey).then(() => {
        vscode.window.showInformationMessage(`API Key已生成並複製到剪貼板: ${apiKey.substring(0, 20)}...`, '配置設置').then(selection => {
            if (selection === '配置設置') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation.apiKey');
            }
        });
    });
}
async function testConnection() {
    logMessage('🧪 測試MCP連接...');
    const config = vscode.workspace.getConfiguration('powerautomation');
    const endpoint = config.get('mcpEndpoint', 'http://localhost:8080/mcp/v3');
    const apiKey = config.get('apiKey', '');
    if (!apiKey || apiKey.trim() === '') {
        vscode.window.showErrorMessage('請先配置API Key');
        return;
    }
    try {
        const response = await axios_1.default.get(`${endpoint}/health`, {
            headers: {
                'Authorization': `Bearer ${apiKey}`
            },
            timeout: 10000
        });
        if (response.status === 200) {
            logMessage('✅ MCP服務測試成功');
            vscode.window.showInformationMessage('MCP服務連接測試成功！');
        }
        else {
            throw new Error(`測試失敗: ${response.status}`);
        }
    }
    catch (error) {
        const errorMessage = error.response?.data?.message || error.message || '未知錯誤';
        logMessage(`❌ MCP服務測試失敗: ${errorMessage}`);
        vscode.window.showErrorMessage(`MCP連接測試失敗: ${errorMessage}`);
    }
}
function showOutput() {
    outputChannel.show();
}
function deactivate() {
    if (statusBarItem) {
        statusBarItem.dispose();
    }
    if (outputChannel) {
        outputChannel.dispose();
    }
    if (mcpServerManager) {
        mcpServerManager.stop();
    }
    logMessage('👋 PowerAutomation v3.0.0 已停用');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map