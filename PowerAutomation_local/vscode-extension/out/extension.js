"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const RepositoryProvider_1 = require("./providers/RepositoryProvider");
const ChatProvider_1 = require("./providers/ChatProvider");
const MCPService_1 = require("./services/MCPService");
const SmartUIController_1 = require("./smartui/SmartUIController");
const types_1 = require("./smartui/types");
let outputChannel;
let mcpService;
let smartUIController;
async function activate(context) {
    console.log('PowerAutomation SmartUI v1.0.0 is now active!');
    // 創建輸出面板
    outputChannel = vscode.window.createOutputChannel('PowerAutomation SmartUI');
    context.subscriptions.push(outputChannel);
    // 初始化 SmartUI 控制器
    logMessage('🧠 初始化 SmartUI Fusion 系統...');
    smartUIController = new SmartUIController_1.SmartUIController(context);
    const smartUIInitialized = await smartUIController.initialize();
    if (smartUIInitialized) {
        logMessage('✅ SmartUI Fusion 系統初始化成功');
        logMessage(`👤 當前角色: ${smartUIController.getCurrentRole()}`);
        logMessage(`🎯 可用功能: ${smartUIController.getFeatures().length} 個`);
    }
    else {
        logMessage('❌ SmartUI Fusion 系統初始化失敗，使用基礎模式');
    }
    // 初始化 MCP 服務
    mcpService = new MCPService_1.MCPService(outputChannel);
    // 記錄啟動信息
    logMessage('🚀 PowerAutomation SmartUI v1.0.0 已啟動');
    logMessage(`📅 啟動時間: ${new Date().toLocaleString()}`);
    logMessage('✅ 基於 SmartUI Fusion 的智慧界面已準備就緒');
    // 創建視圖提供者
    logMessage('📝 創建智慧視圖提供者...');
    const repositoryProvider = new RepositoryProvider_1.RepositoryProvider(context.extensionUri, mcpService);
    const chatProvider = new ChatProvider_1.ChatProvider(context.extensionUri, mcpService);
    // 註冊視圖提供者
    logMessage('📋 註冊智慧視圖提供者...');
    context.subscriptions.push(vscode.window.registerWebviewViewProvider('powerautomation.repository', repositoryProvider));
    context.subscriptions.push(vscode.window.registerWebviewViewProvider('powerautomation.chat', chatProvider));
    logMessage('✅ 智慧視圖提供者註冊完成');
    // 註冊 SmartUI 命令
    registerSmartUICommands(context);
    // 設置 SmartUI 事件監聽
    setupSmartUIEventListeners();
    // 註冊基礎命令
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.openEditor', () => {
        // 記錄用戶交互
        trackUserInteraction('command', 'openEditor');
        vscode.commands.executeCommand('workbench.action.files.newUntitledFile');
    }));
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.showDashboard', () => {
        // 記錄用戶交互
        trackUserInteraction('command', 'showDashboard');
        vscode.commands.executeCommand('workbench.view.extension.powerautomation-activitybar');
    }));
    // 定期更新系統狀態
    const statusUpdateInterval = setInterval(async () => {
        if (smartUIController && smartUIController.isReady()) {
            await smartUIController.updateSystemStatus();
        }
    }, 30000); // 每30秒更新一次
    context.subscriptions.push({
        dispose: () => clearInterval(statusUpdateInterval)
    });
    logMessage('🎉 PowerAutomation SmartUI 啟動完成！');
}
exports.activate = activate;
async function deactivate() {
    logMessage('🔄 正在關閉 PowerAutomation SmartUI...');
    if (smartUIController) {
        await smartUIController.destroy();
        logMessage('✅ SmartUI 控制器已銷毀');
    }
    logMessage('👋 PowerAutomation SmartUI 已關閉');
}
exports.deactivate = deactivate;
function registerSmartUICommands(context) {
    // 角色切換命令
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.switchToAdmin', async () => {
        await switchRole(types_1.UserRole.ADMIN);
    }));
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.switchToDeveloper', async () => {
        await switchRole(types_1.UserRole.DEVELOPER);
    }));
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.switchToUser', async () => {
        await switchRole(types_1.UserRole.USER);
    }));
    // Claude 分析命令
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.analyzeSelection', async () => {
        await analyzeSelectedText('analysis');
    }));
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.reviewCode', async () => {
        await analyzeSelectedText('review');
    }));
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.explainCode', async () => {
        await analyzeSelectedText('explanation');
    }));
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.generateCode', async () => {
        await generateCodeFromRequirements();
    }));
    // 系統狀態命令
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.showStatus', async () => {
        await showSystemStatus();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.showRecommendations', async () => {
        await showRecommendations();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('powerautomation.smartui.showUserAnalysis', async () => {
        await showUserAnalysis();
    }));
    logMessage('🎯 SmartUI 命令註冊完成');
}
function setupSmartUIEventListeners() {
    if (!smartUIController)
        return;
    // 監聽角色切換事件
    smartUIController.addEventListener('ROLE_CHANGED', (event) => {
        const payload = event.payload;
        const { newRole, oldRole } = payload;
        logMessage(`🔄 角色已切換: ${oldRole} → ${newRole}`);
        vscode.window.showInformationMessage(`已切換到 ${getRoleDisplayName(newRole)} 模式`);
    });
    // 監聽分析完成事件
    smartUIController.addEventListener('ANALYSIS_COMPLETE', (event) => {
        const result = event.payload;
        logMessage(`🤖 Claude 分析完成: ${result.type} (信心度: ${(result.confidence * 100).toFixed(1)}%)`);
    });
    // 監聽系統狀態更新事件
    smartUIController.addEventListener('SYSTEM_STATUS_UPDATE', (event) => {
        const status = event.payload;
        if (status.health !== 'healthy') {
            logMessage(`⚠️ 系統狀態警告: ${status.health}`);
        }
    });
    // 監聽用戶操作事件
    smartUIController.addEventListener('USER_ACTION', (event) => {
        const interaction = event.payload;
        logMessage(`👆 用戶操作: ${interaction.type} - ${interaction.element}`);
    });
    logMessage('📡 SmartUI 事件監聽器設置完成');
}
async function switchRole(newRole) {
    if (!smartUIController) {
        vscode.window.showErrorMessage('SmartUI 系統未初始化');
        return;
    }
    try {
        const success = await smartUIController.switchRole(newRole);
        if (success) {
            const roleName = getRoleDisplayName(newRole);
            vscode.window.showInformationMessage(`已切換到 ${roleName} 模式`);
            logMessage(`✅ 角色切換成功: ${newRole}`);
        }
        else {
            vscode.window.showErrorMessage('角色切換失敗');
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`角色切換失敗: ${error.message}`);
        logMessage(`❌ 角色切換失敗: ${error.message}`);
    }
}
async function analyzeSelectedText(type) {
    if (!smartUIController) {
        vscode.window.showErrorMessage('SmartUI 系統未初始化');
        return;
    }
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('請先選擇要分析的文本');
        return;
    }
    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);
    if (!selectedText.trim()) {
        vscode.window.showWarningMessage('請選擇要分析的文本');
        return;
    }
    try {
        // 記錄用戶交互
        trackUserInteraction('analysis', type, { selectedText: selectedText.substring(0, 100) });
        vscode.window.showInformationMessage(`正在使用 Claude 進行${getAnalysisTypeName(type)}...`);
        const result = await smartUIController.analyzeWithClaude(selectedText, type);
        if (result) {
            // 顯示分析結果
            await showAnalysisResult(result);
        }
        else {
            vscode.window.showErrorMessage('分析失敗，請稍後重試');
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`分析失敗: ${error.message}`);
        logMessage(`❌ 分析失敗: ${error.message}`);
    }
}
async function generateCodeFromRequirements() {
    if (!smartUIController) {
        vscode.window.showErrorMessage('SmartUI 系統未初始化');
        return;
    }
    const requirements = await vscode.window.showInputBox({
        prompt: '請輸入代碼需求描述',
        placeHolder: '例如：創建一個計算器函數...'
    });
    if (!requirements)
        return;
    try {
        // 記錄用戶交互
        trackUserInteraction('generation', 'code', { requirements });
        vscode.window.showInformationMessage('正在使用 Claude 生成代碼...');
        const result = await smartUIController.analyzeWithClaude(requirements, 'generation');
        if (result) {
            // 顯示生成結果
            await showAnalysisResult(result);
        }
        else {
            vscode.window.showErrorMessage('代碼生成失敗，請稍後重試');
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`代碼生成失敗: ${error.message}`);
        logMessage(`❌ 代碼生成失敗: ${error.message}`);
    }
}
async function showSystemStatus() {
    if (!smartUIController) {
        vscode.window.showErrorMessage('SmartUI 系統未初始化');
        return;
    }
    try {
        await smartUIController.updateSystemStatus();
        const state = smartUIController.getState();
        const status = state.systemStatus;
        const statusMessage = `
系統狀態: ${getHealthStatusIcon(status.health)} ${status.health}
CPU 使用率: ${status.performance.cpu.toFixed(1)}%
內存使用: ${status.performance.memory.toFixed(1)}MB
響應時間: ${status.performance.responseTime.toFixed(0)}ms

服務狀態:
• Claude: ${getServiceStatusIcon(status.services.claude)} ${status.services.claude}
• MCP: ${getServiceStatusIcon(status.services.mcp)} ${status.services.mcp}
• LiveKit: ${getServiceStatusIcon(status.services.livekit)} ${status.services.livekit}

最後更新: ${new Date(status.lastUpdate).toLocaleString()}
        `.trim();
        vscode.window.showInformationMessage(statusMessage, { modal: true });
    }
    catch (error) {
        vscode.window.showErrorMessage(`獲取系統狀態失敗: ${error.message}`);
    }
}
async function showRecommendations() {
    if (!smartUIController) {
        vscode.window.showErrorMessage('SmartUI 系統未初始化');
        return;
    }
    try {
        const recommendations = await smartUIController.getRecommendations();
        if (recommendations.length === 0) {
            vscode.window.showInformationMessage('暫無個性化推薦');
            return;
        }
        const items = recommendations.map(rec => ({
            label: `${getPriorityIcon(rec.priority)} ${rec.title}`,
            description: rec.description,
            detail: `類型: ${rec.type}`
        }));
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: '選擇要查看的推薦'
        });
        if (selected) {
            vscode.window.showInformationMessage(selected.description);
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`獲取推薦失敗: ${error.message}`);
    }
}
async function showUserAnalysis() {
    if (!smartUIController) {
        vscode.window.showErrorMessage('SmartUI 系統未初始化');
        return;
    }
    try {
        const analysis = await smartUIController.getUserAnalysis();
        if (!analysis) {
            vscode.window.showInformationMessage('暫無用戶分析數據');
            return;
        }
        const analysisMessage = `
用戶角色: ${getRoleDisplayName(analysis.role)}
操作效率: ${(analysis.patterns.efficiency * 100).toFixed(1)}%
平均會話時間: ${Math.round(analysis.patterns.averageSessionTime / 1000 / 60)} 分鐘
偏好布局: ${analysis.patterns.preferredLayout}

常用功能:
${analysis.patterns.mostUsedFeatures.slice(0, 3).map(f => `• ${f}`).join('\n')}

個性化設置:
• 主題: ${analysis.preferences.theme}
• 語言: ${analysis.preferences.language}
        `.trim();
        vscode.window.showInformationMessage(analysisMessage, { modal: true });
    }
    catch (error) {
        vscode.window.showErrorMessage(`獲取用戶分析失敗: ${error.message}`);
    }
}
async function showAnalysisResult(result) {
    // 創建新的文檔顯示分析結果
    const doc = await vscode.workspace.openTextDocument({
        content: formatAnalysisResult(result),
        language: 'markdown'
    });
    await vscode.window.showTextDocument(doc);
}
function formatAnalysisResult(result) {
    const timestamp = new Date(result.timestamp).toLocaleString();
    const role = getRoleDisplayName(result.role);
    const confidence = (result.confidence * 100).toFixed(1);
    let content = `# ${getAnalysisTypeName(result.type)}結果\n\n`;
    content += `**分析時間**: ${timestamp}\n`;
    content += `**分析角色**: ${role}\n`;
    content += `**信心度**: ${confidence}%\n\n`;
    content += `## 原始內容\n\n\`\`\`\n${result.content}\n\`\`\`\n\n`;
    content += `## 分析結果\n\n`;
    if (typeof result.result === 'string') {
        content += result.result;
    }
    else if (result.result.fullContent) {
        content += result.result.fullContent;
    }
    else {
        content += JSON.stringify(result.result, null, 2);
    }
    return content;
}
function trackUserInteraction(type, element, context = {}) {
    if (!smartUIController)
        return;
    const interaction = {
        id: `interaction_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: type,
        element,
        timestamp: Date.now(),
        role: types_1.UserRole.USER,
        context: {
            ...context,
            userId: 'current_user',
            view: 'vscode',
            layout: 'default'
        }
    };
    smartUIController.handleUserInteraction(interaction);
}
function logMessage(message) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    console.log(logEntry);
    if (outputChannel) {
        outputChannel.appendLine(logEntry);
    }
}
// 輔助函數
function getRoleDisplayName(role) {
    const names = {
        [types_1.UserRole.ADMIN]: '系統管理員',
        [types_1.UserRole.DEVELOPER]: '開發者',
        [types_1.UserRole.USER]: '用戶'
    };
    return names[role] || role;
}
function getAnalysisTypeName(type) {
    const names = {
        'analysis': '需求分析',
        'review': '代碼審查',
        'explanation': '代碼解釋',
        'generation': '代碼生成'
    };
    return names[type] || type;
}
function getHealthStatusIcon(health) {
    const icons = {
        'healthy': '✅',
        'warning': '⚠️',
        'error': '❌'
    };
    return icons[health] || '❓';
}
function getServiceStatusIcon(status) {
    const icons = {
        'connected': '🟢',
        'disconnected': '🔴',
        'error': '❌'
    };
    return icons[status] || '❓';
}
function getPriorityIcon(priority) {
    const icons = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    };
    return icons[priority] || '⚪';
}
//# sourceMappingURL=extension.js.map