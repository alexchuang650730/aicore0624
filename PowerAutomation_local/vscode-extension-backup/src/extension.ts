import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('PowerAutomation Extension is now active!');
    
    // 註冊命令
    const commands = [
        vscode.commands.registerCommand('powerautomation.login', () => {
            vscode.window.showInformationMessage('PowerAutomation: Login command executed');
        }),
        vscode.commands.registerCommand('powerautomation.sendMessage', () => {
            vscode.window.showInformationMessage('PowerAutomation: Send Message command executed');
        }),
        vscode.commands.registerCommand('powerautomation.getConversations', () => {
            vscode.window.showInformationMessage('PowerAutomation: Get Conversations command executed');
        }),
        vscode.commands.registerCommand('powerautomation.getTasks', () => {
            vscode.window.showInformationMessage('PowerAutomation: Get Tasks command executed');
        }),
        vscode.commands.registerCommand('powerautomation.runTest', () => {
            vscode.window.showInformationMessage('PowerAutomation: Run Test command executed');
        }),
        vscode.commands.registerCommand('powerautomation.viewStatus', () => {
            vscode.window.showInformationMessage('PowerAutomation: View Status command executed');
        })
    ];
    
    commands.forEach(command => context.subscriptions.push(command));
    
    // 創建狀態欄項目
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(gear) PowerAutomation";
    statusBarItem.command = 'powerautomation.viewStatus';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

export function deactivate() {}
