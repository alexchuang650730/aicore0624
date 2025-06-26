"use strict";
/**
 * SmartUI 語音輸入服務
 * 支持語音識別和語音命令處理
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SmartUIVoiceService = void 0;
const vscode = require("vscode");
class SmartUIVoiceService {
    constructor(outputChannel) {
        this.isListening = false;
        this.recognition = null;
        this.outputChannel = outputChannel;
        this.initializeVoiceRecognition();
    }
    /**
     * 初始化語音識別
     */
    initializeVoiceRecognition() {
        try {
            // 在 VS Code 擴展環境中，語音識別功能可能不可用
            // 檢查全局對象支持
            const globalObj = (typeof globalThis !== 'undefined') ? globalThis :
                (typeof global !== 'undefined') ? global : {};
            if ('webkitSpeechRecognition' in globalObj) {
                this.recognition = new globalObj.webkitSpeechRecognition();
                this.setupRecognition();
                this.log('語音識別初始化成功 (WebKit)');
            }
            else if ('SpeechRecognition' in globalObj) {
                this.recognition = new globalObj.SpeechRecognition();
                this.setupRecognition();
                this.log('語音識別初始化成功 (標準)');
            }
            else {
                this.log('當前環境不支持語音識別，將使用替代方案');
                this.initializeFallbackVoice();
            }
        }
        catch (error) {
            this.log(`語音識別初始化失敗: ${error.message}`);
            this.initializeFallbackVoice();
        }
    }
    /**
     * 設置語音識別配置
     */
    setupRecognition() {
        if (!this.recognition)
            return;
        // 基本配置
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'zh-CN'; // 默認中文
        this.recognition.maxAlternatives = 3;
        // 事件監聽
        this.recognition.onstart = () => {
            this.isListening = true;
            this.log('語音識別開始');
            vscode.window.showInformationMessage('🎤 語音識別已啟動');
        };
        this.recognition.onend = () => {
            this.isListening = false;
            this.log('語音識別結束');
        };
        this.recognition.onerror = (event) => {
            this.log(`語音識別錯誤: ${event.error}`);
            vscode.window.showErrorMessage(`語音識別錯誤: ${event.error}`);
        };
        this.recognition.onresult = (event) => {
            this.handleVoiceResult(event);
        };
    }
    /**
     * 初始化替代語音方案
     */
    initializeFallbackVoice() {
        this.log('使用替代語音輸入方案');
        // 可以整合其他語音服務 API，如 Azure Speech、Google Speech 等
    }
    /**
     * 處理語音識別結果
     */
    handleVoiceResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            const transcript = result[0].transcript;
            if (result.isFinal) {
                finalTranscript += transcript;
            }
            else {
                interimTranscript += transcript;
            }
        }
        if (finalTranscript) {
            const voiceCommand = {
                command: finalTranscript.trim(),
                confidence: event.results[event.resultIndex][0].confidence || 0.8,
                timestamp: Date.now(),
                language: this.recognition.lang
            };
            this.log(`語音命令: "${voiceCommand.command}" (信心度: ${(voiceCommand.confidence * 100).toFixed(1)}%)`);
            this.processVoiceCommand(voiceCommand);
        }
        // 顯示臨時結果
        if (interimTranscript) {
            this.showInterimResult(interimTranscript);
        }
    }
    /**
     * 處理語音命令
     */
    processVoiceCommand(voiceCommand) {
        const command = voiceCommand.command.toLowerCase();
        // 預定義的語音命令
        const commandMappings = {
            // 角色切換
            '切換到管理員模式': 'powerautomation.smartui.switchToAdmin',
            '切換到開發者模式': 'powerautomation.smartui.switchToDeveloper',
            '切換到用戶模式': 'powerautomation.smartui.switchToUser',
            '管理員模式': 'powerautomation.smartui.switchToAdmin',
            '開發者模式': 'powerautomation.smartui.switchToDeveloper',
            '用戶模式': 'powerautomation.smartui.switchToUser',
            // Claude 功能
            '分析代碼': 'powerautomation.smartui.analyzeSelection',
            '需求分析': 'powerautomation.smartui.analyzeSelection',
            '代碼審查': 'powerautomation.smartui.reviewCode',
            '審查代碼': 'powerautomation.smartui.reviewCode',
            '解釋代碼': 'powerautomation.smartui.explainCode',
            '代碼解釋': 'powerautomation.smartui.explainCode',
            '生成代碼': 'powerautomation.smartui.generateCode',
            '代碼生成': 'powerautomation.smartui.generateCode',
            // 系統功能
            '顯示狀態': 'powerautomation.smartui.showStatus',
            '系統狀態': 'powerautomation.smartui.showStatus',
            '顯示推薦': 'powerautomation.smartui.showRecommendations',
            '智能推薦': 'powerautomation.smartui.showRecommendations',
            '用戶分析': 'powerautomation.smartui.showUserAnalysis',
            // 語音控制
            '停止語音': 'voice.stop',
            '開始語音': 'voice.start',
            '語音幫助': 'voice.help'
        };
        // 查找匹配的命令
        let matchedCommand = null;
        for (const [voiceText, vscodeCommand] of Object.entries(commandMappings)) {
            if (command.includes(voiceText)) {
                matchedCommand = vscodeCommand;
                break;
            }
        }
        if (matchedCommand) {
            if (matchedCommand.startsWith('voice.')) {
                this.handleVoiceControlCommand(matchedCommand);
            }
            else {
                this.executeVSCodeCommand(matchedCommand, voiceCommand);
            }
        }
        else {
            // 如果沒有匹配的預定義命令，嘗試智能解析
            this.handleIntelligentVoiceCommand(voiceCommand);
        }
        // 調用回調函數
        if (this.onVoiceCommandCallback) {
            this.onVoiceCommandCallback(voiceCommand);
        }
    }
    /**
     * 處理語音控制命令
     */
    handleVoiceControlCommand(command) {
        switch (command) {
            case 'voice.stop':
                this.stopListening();
                break;
            case 'voice.start':
                this.startListening();
                break;
            case 'voice.help':
                this.showVoiceHelp();
                break;
        }
    }
    /**
     * 執行 VS Code 命令
     */
    executeVSCodeCommand(command, voiceCommand) {
        vscode.commands.executeCommand(command).then(() => {
            this.log(`成功執行命令: ${command}`);
            vscode.window.showInformationMessage(`✅ 已執行: ${voiceCommand.command}`);
        }, (error) => {
            this.log(`命令執行失敗: ${command}, 錯誤: ${error.message}`);
            vscode.window.showErrorMessage(`❌ 命令執行失敗: ${error.message}`);
        });
    }
    /**
     * 處理智能語音命令
     */
    handleIntelligentVoiceCommand(voiceCommand) {
        const command = voiceCommand.command.toLowerCase();
        // 智能匹配邏輯
        if (command.includes('分析') || command.includes('檢查')) {
            this.executeVSCodeCommand('powerautomation.smartui.analyzeSelection', voiceCommand);
        }
        else if (command.includes('生成') || command.includes('創建')) {
            this.executeVSCodeCommand('powerautomation.smartui.generateCode', voiceCommand);
        }
        else if (command.includes('解釋') || command.includes('說明')) {
            this.executeVSCodeCommand('powerautomation.smartui.explainCode', voiceCommand);
        }
        else if (command.includes('狀態') || command.includes('監控')) {
            this.executeVSCodeCommand('powerautomation.smartui.showStatus', voiceCommand);
        }
        else {
            // 未識別的命令，提供幫助
            vscode.window.showWarningMessage(`未識別的語音命令: "${voiceCommand.command}"`);
            this.showVoiceHelp();
        }
    }
    /**
     * 顯示臨時結果
     */
    showInterimResult(text) {
        // 在狀態欄顯示臨時識別結果
        vscode.window.setStatusBarMessage(`🎤 ${text}`, 2000);
    }
    /**
     * 顯示語音幫助
     */
    showVoiceHelp() {
        const helpMessage = `
🎤 SmartUI 語音命令幫助

角色切換:
• "切換到開發者模式" - 切換到開發者角色
• "管理員模式" - 切換到管理員角色
• "用戶模式" - 切換到用戶角色

Claude AI 功能:
• "分析代碼" - 分析選中的代碼
• "代碼審查" - 審查選中的代碼
• "解釋代碼" - 解釋選中的代碼
• "生成代碼" - 生成新代碼

系統功能:
• "顯示狀態" - 查看系統狀態
• "智能推薦" - 查看推薦建議
• "用戶分析" - 查看用戶分析

語音控制:
• "停止語音" - 停止語音識別
• "語音幫助" - 顯示此幫助信息
        `.trim();
        vscode.window.showInformationMessage(helpMessage, { modal: true });
    }
    /**
     * 開始語音識別
     */
    startListening(options) {
        if (this.isListening) {
            this.log('語音識別已在運行中');
            return;
        }
        if (!this.recognition) {
            vscode.window.showErrorMessage('語音識別不可用');
            return;
        }
        try {
            // 應用選項
            if (options) {
                if (options.language) {
                    this.recognition.lang = options.language;
                }
                if (options.continuous !== undefined) {
                    this.recognition.continuous = options.continuous;
                }
                if (options.interimResults !== undefined) {
                    this.recognition.interimResults = options.interimResults;
                }
                if (options.maxAlternatives !== undefined) {
                    this.recognition.maxAlternatives = options.maxAlternatives;
                }
            }
            this.recognition.start();
        }
        catch (error) {
            this.log(`啟動語音識別失敗: ${error.message}`);
            vscode.window.showErrorMessage(`啟動語音識別失敗: ${error.message}`);
        }
    }
    /**
     * 停止語音識別
     */
    stopListening() {
        if (!this.isListening) {
            this.log('語音識別未在運行');
            return;
        }
        if (this.recognition) {
            this.recognition.stop();
            vscode.window.showInformationMessage('🔇 語音識別已停止');
        }
    }
    /**
     * 切換語音識別狀態
     */
    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        }
        else {
            this.startListening();
        }
    }
    /**
     * 檢查語音識別是否可用
     */
    isVoiceAvailable() {
        return this.recognition !== null;
    }
    /**
     * 獲取語音識別狀態
     */
    getListeningStatus() {
        return this.isListening;
    }
    /**
     * 設置語音命令回調
     */
    onVoiceCommand(callback) {
        this.onVoiceCommandCallback = callback;
    }
    /**
     * 設置語音識別語言
     */
    setLanguage(language) {
        if (this.recognition) {
            this.recognition.lang = language;
            this.log(`語音識別語言設置為: ${language}`);
        }
    }
    /**
     * 獲取支持的語言列表
     */
    getSupportedLanguages() {
        return [
            'zh-CN',
            'zh-TW',
            'en-US',
            'en-GB',
            'ja-JP',
            'ko-KR',
            'fr-FR',
            'de-DE',
            'es-ES',
            'it-IT',
            'pt-BR',
            'ru-RU' // 俄語
        ];
    }
    /**
     * 銷毀語音服務
     */
    dispose() {
        if (this.isListening) {
            this.stopListening();
        }
        this.recognition = null;
        this.onVoiceCommandCallback = undefined;
        this.log('語音服務已銷毀');
    }
    /**
     * 記錄日誌
     */
    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] [VoiceService] ${message}`;
        console.log(logEntry);
        if (this.outputChannel) {
            this.outputChannel.appendLine(logEntry);
        }
    }
}
exports.SmartUIVoiceService = SmartUIVoiceService;
//# sourceMappingURL=VoiceService.js.map