import * as vscode from 'vscode';
import { DashboardProvider } from './providers/DashboardProvider';
import { ChatProvider } from './providers/ChatProvider';
import { RepositoryProvider } from './providers/RepositoryProvider';
import { AuthProvider } from './providers/AuthProvider';
import { MCPServerManager } from './services/MCPServerManager';
import { EditorDetectionService } from './services/EditorDetectionService';
import { AuthenticationService } from './services/AuthenticationService';
import axios from 'axios';

let statusBarItem: vscode.StatusBarItem;
let outputChannel: vscode.OutputChannel;
let mcpServerManager: MCPServerManager;
let isConnected = false;

export async function activate(context: vscode.ExtensionContext) {
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
    mcpServerManager = new MCPServerManager();
    const editorDetectionService = new EditorDetectionService();
    const authService = new AuthenticationService();
    
    // 記錄啟動信息
    logMessage('🚀 PowerAutomation v3.0.0 已啟動');
    logMessage(`📅 啟動時間: ${new Date().toLocaleString()}`);
    
    // 檢測智能編輯器
    const hasOtherEditors = await editorDetectionService.detectOtherEditors();
    const config = vscode.workspace.getConfiguration('powerautomation');
    const autoDetect = config.get<boolean>('autoDetectEditors', true);
    
    if (autoDetect && hasOtherEditors) {
        logMessage('🔍 檢測到其他智能編輯器，切換到最小模式');
        vscode.commands.executeCommand('setContext', 'powerautomation.minimalMode', true);
    }
    
    // 創建視圖提供者
    const dashboardProvider = new DashboardProvider(context.extensionUri, mcpServerManager);
    const chatProvider = new ChatProvider(context.extensionUri, mcpServerManager);
    const repositoryProvider = new RepositoryProvider(context.extensionUri);
    const authProvider = new AuthProvider(context.extensionUri, authService);
    
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
            const currentMode = vscode.workspace.getConfiguration('powerautomation').get<boolean>('minimalMode');
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
        const apiKey = config.get<string>('apiKey');
        if (apiKey && apiKey.trim() !== '') {
            logMessage('🔄 自動嘗試連接MCP服務...');
            connectToMCP();
        } else {
            logMessage('⚠️ 未配置API Key，請先生成API Key並配置');
        }
    }, 2000);
}

function updateStatusBar(status: 'disconnected' | 'connecting' | 'connected' | 'error') {
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

function logMessage(message: string) {
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
    const endpoint = config.get<string>('mcpEndpoint', 'http://localhost:8080/mcp/v3');
    const apiKey = config.get<string>('apiKey', '');
    const timeout = config.get<number>('timeout', 30000);
    
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
        const response = await axios.post(`${endpoint}/connect`, {
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
        } else {
            throw new Error(`連接失敗: ${response.status} ${response.statusText}`);
        }
    } catch (error: any) {
        isConnected = false;
        updateStatusBar('error');
        const errorMessage = error.response?.data?.message || error.message || '未知錯誤';
        logMessage(`❌ MCP服務連接失敗: ${errorMessage}`);
        vscode.window.showErrorMessage(`MCP連接失敗: ${errorMessage}`, '重試', '檢查配置').then(selection => {
            if (selection === '重試') {
                setTimeout(connectToMCP, 5000);
            } else if (selection === '檢查配置') {
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
    const enableHeartbeat = config.get<boolean>('enableHeartbeat', true);
    const interval = config.get<number>('heartbeatInterval', 30) * 1000;
    
    if (!enableHeartbeat) {
        return;
    }
    
    setInterval(async () => {
        if (!isConnected) {
            return;
        }
        
        try {
            const endpoint = config.get<string>('mcpEndpoint', 'http://localhost:8080/mcp/v3');
            const apiKey = config.get<string>('apiKey', '');
            
            await axios.post(`${endpoint}/heartbeat`, {
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
        } catch (error: any) {
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
        vscode.window.showInformationMessage(
            `API Key已生成並複製到剪貼板: ${apiKey.substring(0, 20)}...`,
            '配置設置'
        ).then(selection => {
            if (selection === '配置設置') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation.apiKey');
            }
        });
    });
}

async function testConnection() {
    logMessage('🧪 測試MCP連接...');
    
    const config = vscode.workspace.getConfiguration('powerautomation');
    const endpoint = config.get<string>('mcpEndpoint', 'http://localhost:8080/mcp/v3');
    const apiKey = config.get<string>('apiKey', '');
    
    if (!apiKey || apiKey.trim() === '') {
        vscode.window.showErrorMessage('請先配置API Key');
        return;
    }
    
    try {
        const response = await axios.get(`${endpoint}/health`, {
            headers: {
                'Authorization': `Bearer ${apiKey}`
            },
            timeout: 10000
        });
        
        if (response.status === 200) {
            logMessage('✅ MCP服務測試成功');
            vscode.window.showInformationMessage('MCP服務連接測試成功！');
        } else {
            throw new Error(`測試失敗: ${response.status}`);
        }
    } catch (error: any) {
        const errorMessage = error.response?.data?.message || error.message || '未知錯誤';
        logMessage(`❌ MCP服務測試失敗: ${errorMessage}`);
        vscode.window.showErrorMessage(`MCP連接測試失敗: ${errorMessage}`);
    }
}

function showOutput() {
    outputChannel.show();
}

export function deactivate() {
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

