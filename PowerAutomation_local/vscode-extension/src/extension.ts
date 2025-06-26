import * as vscode from 'vscode';
import { RepositoryProvider } from './providers/RepositoryProvider';
import { ChatProvider } from './providers/ChatProvider';
import { MCPService } from './services/MCPService';

let outputChannel: vscode.OutputChannel;
let mcpService: MCPService;

export async function activate(context: vscode.ExtensionContext) {
    console.log('PowerAutomation KiloCode v1.0.0 is now active!');
    
    // 創建輸出面板
    outputChannel = vscode.window.createOutputChannel('PowerAutomation');
    context.subscriptions.push(outputChannel);
    
    // 初始化 MCP 服務
    mcpService = new MCPService(outputChannel);
    
    // 記錄啟動信息
    logMessage('🚀 PowerAutomation KiloCode v1.0.0 已啟動');
    logMessage(`📅 啟動時間: ${new Date().toLocaleString()}`);
    logMessage('✅ 基於 KiloCode 的三欄佈局已準備就緒');
    
    // 創建視圖提供者
    logMessage('📝 創建視圖提供者...');
    const repositoryProvider = new RepositoryProvider(context.extensionUri, mcpService);
    const chatProvider = new ChatProvider(context.extensionUri, mcpService);
    
    // 註冊視圖提供者
    logMessage('📋 註冊視圖提供者...');
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('powerautomation.repository', repositoryProvider)
    );
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('powerautomation.chat', chatProvider)
    );
    logMessage('✅ 視圖提供者註冊完成');
    
    // 註冊命令
    context.subscriptions.push(
        vscode.commands.registerCommand('powerautomation.openEditor', () => {
            vscode.commands.executeCommand('workbench.action.files.newUntitledFile');
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('powerautomation.showDashboard', () => {
            vscode.commands.executeCommand('workbench.view.extension.powerautomation-activitybar');
        })
    );
    
    // 創建狀態欄項目
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'powerautomation.showDashboard';
    statusBarItem.text = '$(robot) PowerAutomation';
    statusBarItem.tooltip = 'PowerAutomation - Click to open dashboard';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    
    // 自動打開視圖
    setTimeout(() => {
        vscode.commands.executeCommand('workbench.view.extension.powerautomation-activitybar');
        vscode.commands.executeCommand('workbench.view.extension.powerautomation-panel');
        logMessage('🤖 自動打開三欄佈局');
    }, 1000);
    
    // 顯示歡迎信息
    vscode.window.showInformationMessage(
        'PowerAutomation KiloCode v1.0.0 已啟動！基於 KiloCode 的三欄佈局已就緒。',
        '打開編輯器',
        '查看儀表板'
    ).then(selection => {
        if (selection === '打開編輯器') {
            vscode.commands.executeCommand('powerautomation.openEditor');
        } else if (selection === '查看儀表板') {
            vscode.commands.executeCommand('powerautomation.showDashboard');
        }
    });
    
    logMessage('🎉 PowerAutomation KiloCode 啟動完成');
}

export function deactivate() {
    logMessage('👋 PowerAutomation KiloCode 已停用');
}

function logMessage(message: string) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    console.log(logEntry);
    if (outputChannel) {
        outputChannel.appendLine(logEntry);
    }
}

