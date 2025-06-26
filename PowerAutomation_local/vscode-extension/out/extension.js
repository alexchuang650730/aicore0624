const vscode = require('vscode');

function activate(context) {
    console.log('PowerAutomation SmartUI is now active!');
    
    // 註冊基本命令
    let disposable = vscode.commands.registerCommand('powerautomation.smartui.hello', function () {
        vscode.window.showInformationMessage('Hello from PowerAutomation SmartUI!');
    });
    
    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
