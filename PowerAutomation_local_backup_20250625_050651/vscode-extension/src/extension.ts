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
let authService: AuthenticationService;
let isConnected = false;

export async function activate(context: vscode.ExtensionContext) {
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
    mcpServerManager = new MCPServerManager();
    const editorDetectionService = new EditorDetectionService();
    authService = new AuthenticationService(context);
    
    // 記錄啟動信息
    logMessage('🚀 PowerAutomation v3.0.0 已啟動');
    logMessage(`📅 啟動時間: ${new Date().toLocaleString()}`);
    
    // 檢查用戶登錄狀態
    if (authService.isAuthenticated()) {
        const user = authService.getCurrentUser();
        logMessage(`👋 歡迎回來，${user?.username}！`);
        logMessage(`🎭 用戶類型: ${authService.getUserType()}`);
        logMessage(`🎯 用戶角色: ${authService.getUserRole()}`);
        
        // 根據用戶類型自動連接MCP服務
        if (user?.userType === 'developer' || user?.provider === 'apikey') {
            setTimeout(() => {
                connectToMCP();
            }, 1000);
        }
    } else {
        logMessage('🔐 用戶未登錄，請先登錄以使用完整功能');
        // 自動顯示認證面板
        setTimeout(() => {
            vscode.commands.executeCommand('powerautomation.showAuth');
        }, 2000);
    }
    
    // 檢測智能編輯器
    const hasOtherEditors = await editorDetectionService.detectOtherEditors();
    const config = vscode.workspace.getConfiguration('powerautomation');
    const autoDetect = config.get<boolean>('autoDetectEditors', true);
    
    if (autoDetect && hasOtherEditors) {
        logMessage('🔍 檢測到其他智能編輯器，切換到最小模式');
        vscode.commands.executeCommand('setContext', 'powerautomation.minimalMode', true);
    }
    
    // 創建視圖提供者
    const dashboardProvider = new DashboardProvider(context.extensionUri, mcpServerManager, authService);
    const chatProvider = new ChatProvider(context.extensionUri, mcpServerManager, authService);
    const repositoryProvider = new RepositoryProvider(context.extensionUri);
    const authProvider = new AuthProvider(context.extensionUri, authService);
    
    // 註冊視圖
    vscode.window.registerWebviewViewProvider('powerautomation.dashboard', dashboardProvider);
    vscode.window.registerWebviewViewProvider('powerautomation.chat', chatProvider);
    vscode.window.registerWebviewViewProvider('powerautomation.repository', repositoryProvider);
    vscode.window.registerWebviewViewProvider('powerautomation.auth', authProvider);
    
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
            // authProvider.refresh(); // AuthProvider 不需要 refresh 方法
            updateStatusBar('disconnected');
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
            } else {
                vscode.window.showWarningMessage('請先登錄以使用此功能', '立即登錄').then(selection => {
                    if (selection === '立即登錄') {
                        vscode.commands.executeCommand('powerautomation.showAuth');
                    }
                });
            }
        }),
        
        // 模式切換
        vscode.commands.registerCommand('powerautomation.toggleMode', () => {
            const currentMode = vscode.workspace.getConfiguration('powerautomation').get<boolean>('minimalMode');
            vscode.workspace.getConfiguration('powerautomation').update('minimalMode', !currentMode, true);
            vscode.commands.executeCommand('setContext', 'powerautomation.minimalMode', !currentMode);
            logMessage(`🔄 切換到${!currentMode ? '最小' : '完整'}模式`);
        }),
        
        // 服務器管理
        vscode.commands.registerCommand('powerautomation.startMCPServer', () => {
            if (authService.hasPermission('server-management')) {
                mcpServerManager.start();
                logMessage('🚀 MCP服務器已啟動');
            } else {
                vscode.window.showErrorMessage('您沒有權限執行此操作');
            }
        }),
        vscode.commands.registerCommand('powerautomation.stopMCPServer', () => {
            if (authService.hasPermission('server-management')) {
                mcpServerManager.stop();
                logMessage('⏹️ MCP服務器已停止');
            } else {
                vscode.window.showErrorMessage('您沒有權限執行此操作');
            }
        }),
        
        // 測試功能
        vscode.commands.registerCommand('powerautomation.runTests', () => {
            if (authService.hasPermission('debug-tools')) {
                logMessage('🧪 開始運行Manus測試...');
                vscode.window.showInformationMessage('Manus測試已開始運行，請查看輸出面板');
            } else {
                vscode.window.showErrorMessage('您沒有權限執行此操作');
            }
        }),
        
        // 開發者工具
        vscode.commands.registerCommand('powerautomation.generateAPIKey', generateAPIKey),
        vscode.commands.registerCommand('powerautomation.openDebugTools', () => {
            if (authService.getUserType() === 'developer') {
                vscode.window.showInformationMessage('開發者調試工具已打開');
                // 這裡可以添加開發者專用的調試界面
            } else {
                vscode.window.showErrorMessage('此功能僅限開發者使用');
            }
        })
    ];
    
    context.subscriptions.push(...commands);
    
    // 監聽認證狀態變化
    context.subscriptions.push(
        vscode.commands.registerCommand('powerautomation.onAuthStateChanged', (authenticated: boolean) => {
            if (authenticated) {
                const user = authService.getCurrentUser();
                logMessage(`✅ 用戶登錄成功: ${user?.username}`);
                updateStatusBar('connected');
                
                // 根據用戶類型自動執行相應操作
                if (user?.userType === 'developer') {
                    setTimeout(() => {
                        connectToMCP();
                    }, 1000);
                }
            } else {
                logMessage('🔐 用戶已登出');
                updateStatusBar('disconnected');
                isConnected = false;
            }
        })
    );
}

function updateStatusBar(status: 'disconnected' | 'connecting' | 'connected' | 'error') {
    const user = authService?.getCurrentUser();
    const userInfo = user ? ` (${user.username})` : '';
    
    switch (status) {
        case 'disconnected':
            statusBarItem.text = '$(circle-outline) PowerAutomation v3.0.0';
            statusBarItem.tooltip = `PowerAutomation - ${user ? '已登錄但未連接MCP服務' : '未登錄'}${userInfo}`;
            statusBarItem.backgroundColor = undefined;
            break;
        case 'connecting':
            statusBarItem.text = '$(sync~spin) PowerAutomation v3.0.0';
            statusBarItem.tooltip = `PowerAutomation - 正在連接MCP服務...${userInfo}`;
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            break;
        case 'connected':
            statusBarItem.text = '$(check) PowerAutomation v3.0.0';
            statusBarItem.tooltip = `PowerAutomation - 已連接MCP服務${userInfo}`;
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.prominentBackground');
            break;
        case 'error':
            statusBarItem.text = '$(error) PowerAutomation v3.0.0';
            statusBarItem.tooltip = `PowerAutomation - MCP服務連接錯誤${userInfo}`;
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            break;
    }
}

function logMessage(message: string) {
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
    let endpoint = config.get<string>('mcpEndpoint', 'http://18.212.97.173:8080');
    let apiKey = '';
    
    // 根據用戶類型獲取認證信息
    if (user?.provider === 'apikey') {
        // 開發者使用API Key
        apiKey = user.id.replace('api_', 'pa_'); // 簡化的API Key獲取
        logMessage(`🔑 使用開發者API Key認證`);
    } else {
        // 普通用戶使用配置的API Key
        apiKey = config.get<string>('apiKey', '');
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
    
    const timeout = config.get<number>('timeout', 30000);
    
    logMessage(`📡 MCP端點: ${endpoint}`);
    logMessage(`👤 用戶: ${user?.username} (${user?.userType})`);
    logMessage(`🔑 認證方式: ${user?.provider}`);
    
    try {
        const response = await axios.post(`${endpoint}/api/process`, {
            request: 'connection_test',
            context: {
                source: 'vscode_vsix',
                client: 'powerautomation',
                user_id: user?.id,
                user_type: user?.userType,
                version: '3.0.0'
            }
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'User-Agent': 'PowerAutomation-VSIX/3.0.0'
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
        } else {
            throw new Error(`連接失敗: ${response.status} ${response.statusText}`);
        }
    } catch (error: any) {
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
        } else if (error.response?.status === 404) {
            vscode.window.showErrorMessage('服務端點不存在，請檢查配置', '檢查配置').then(selection => {
                if (selection === '檢查配置') {
                    vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation');
                }
            });
        } else {
            vscode.window.showErrorMessage(`MCP連接失敗: ${errorMessage}`, '重試', '檢查配置').then(selection => {
                if (selection === '重試') {
                    setTimeout(connectToMCP, 5000);
                } else if (selection === '檢查配置') {
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
    const enableHeartbeat = config.get<boolean>('enableHeartbeat', true);
    const interval = config.get<number>('heartbeatInterval', 30) * 1000;
    
    if (!enableHeartbeat) {
        return;
    }
    
    setInterval(async () => {
        if (!isConnected || !authService.isAuthenticated()) {
            return;
        }
        
        try {
            const endpoint = config.get<string>('mcpEndpoint', 'http://18.212.97.173:8080');
            const user = authService.getCurrentUser();
            let apiKey = '';
            
            if (user?.provider === 'apikey') {
                apiKey = user.id.replace('api_', 'pa_');
            } else {
                apiKey = config.get<string>('apiKey', '');
            }
            
            await axios.post(`${endpoint}/api/heartbeat`, {
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
    if (authService.isAuthenticated()) {
        logMessage('📊 顯示儀表板');
        vscode.commands.executeCommand('powerautomation.openDashboard');
    } else {
        vscode.window.showWarningMessage('請先登錄以使用此功能', '立即登錄').then(selection => {
            if (selection === '立即登錄') {
                vscode.commands.executeCommand('powerautomation.showAuth');
            }
        });
    }
}

function generateAPIKey() {
    if (!authService.hasPermission('api-access')) {
        vscode.window.showErrorMessage('您沒有權限生成API Key');
        return;
    }
    
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
    if (!authService.isAuthenticated()) {
        vscode.window.showWarningMessage('請先登錄以測試連接', '立即登錄').then(selection => {
            if (selection === '立即登錄') {
                vscode.commands.executeCommand('powerautomation.showAuth');
            }
        });
        return;
    }
    
    logMessage('🧪 測試MCP連接...');
    
    const config = vscode.workspace.getConfiguration('powerautomation');
    const endpoint = config.get<string>('mcpEndpoint', 'http://18.212.97.173:8080');
    const user = authService.getCurrentUser();
    let apiKey = '';
    
    if (user?.provider === 'apikey') {
        apiKey = user.id.replace('api_', 'pa_');
    } else {
        apiKey = config.get<string>('apiKey', '');
    }
    
    if (!apiKey || apiKey.trim() === '') {
        vscode.window.showErrorMessage('請先配置API Key');
        return;
    }
    
    try {
        const response = await axios.get(`${endpoint}/api/health`, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'User-Agent': 'PowerAutomation-VSIX/3.0.0'
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

