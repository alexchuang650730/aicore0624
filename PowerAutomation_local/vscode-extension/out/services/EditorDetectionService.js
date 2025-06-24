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
exports.EditorDetectionService = void 0;
const vscode = __importStar(require("vscode"));
class EditorDetectionService {
    constructor() {
        this._knownSmartEditors = [
            'github.copilot',
            'ms-vscode.vscode-ai',
            'tabnine.tabnine-vscode',
            'visualstudioexptteam.vscodeintellicode',
            'ms-toolsai.jupyter',
            'ms-python.python',
            'ms-vscode.cpptools',
            'bradlc.vscode-tailwindcss',
            'esbenp.prettier-vscode'
        ];
    }
    async detectOtherEditors() {
        try {
            // 獲取所有已安裝的擴展
            const extensions = vscode.extensions.all;
            // 檢查是否有其他智能編輯器擴展
            const smartEditorExtensions = extensions.filter(ext => this._knownSmartEditors.includes(ext.id) && ext.isActive);
            console.log('Detected smart editor extensions:', smartEditorExtensions.map(ext => ext.id));
            // 如果檢測到其他智能編輯器，返回true
            return smartEditorExtensions.length > 0;
        }
        catch (error) {
            console.error('Error detecting other editors:', error);
            return false;
        }
    }
    async getActiveEditorInfo() {
        try {
            const extensions = vscode.extensions.all;
            const activeSmartEditors = extensions
                .filter(ext => this._knownSmartEditors.includes(ext.id) && ext.isActive)
                .map(ext => ({
                id: ext.id,
                displayName: ext.packageJSON.displayName || ext.id,
                version: ext.packageJSON.version
            }));
            const recommendations = this._getLayoutRecommendations(activeSmartEditors.map(e => e.id));
            return {
                totalExtensions: extensions.length,
                smartEditors: activeSmartEditors.map(e => `${e.displayName} (${e.version})`),
                recommendations
            };
        }
        catch (error) {
            console.error('Error getting editor info:', error);
            return {
                totalExtensions: 0,
                smartEditors: [],
                recommendations: []
            };
        }
    }
    _getLayoutRecommendations(activeEditors) {
        const recommendations = [];
        if (activeEditors.includes('github.copilot')) {
            recommendations.push('建議使用最小模式，避免與GitHub Copilot衝突');
        }
        if (activeEditors.includes('ms-vscode.vscode-ai')) {
            recommendations.push('檢測到VS Code AI擴展，建議調整佈局以避免重疊');
        }
        if (activeEditors.includes('tabnine.tabnine-vscode')) {
            recommendations.push('TabNine已啟用，建議使用側邊欄模式');
        }
        if (activeEditors.length > 3) {
            recommendations.push('檢測到多個智能編輯器，建議使用最小化佈局');
        }
        if (activeEditors.length === 0) {
            recommendations.push('未檢測到其他智能編輯器，可以使用完整佈局');
        }
        return recommendations;
    }
    async monitorExtensionChanges() {
        // 監聽擴展安裝/卸載事件
        vscode.extensions.onDidChange(() => {
            this.detectOtherEditors().then(hasOtherEditors => {
                // 自動調整佈局模式
                const config = vscode.workspace.getConfiguration('powerautomation');
                const autoDetect = config.get('autoDetectEditors', true);
                if (autoDetect) {
                    config.update('minimalMode', hasOtherEditors, vscode.ConfigurationTarget.Global);
                    if (hasOtherEditors) {
                        vscode.window.showInformationMessage('檢測到其他智能編輯器，已自動切換到最小模式', '查看詳情').then(selection => {
                            if (selection === '查看詳情') {
                                this.showDetectionReport();
                            }
                        });
                    }
                }
            });
        });
    }
    async showDetectionReport() {
        const info = await this.getActiveEditorInfo();
        const report = `
# 智能編輯器檢測報告

## 總體信息
- 已安裝擴展總數: ${info.totalExtensions}
- 檢測到的智能編輯器: ${info.smartEditors.length}

## 活躍的智能編輯器
${info.smartEditors.length > 0 ?
            info.smartEditors.map(editor => `- ${editor}`).join('\\n') :
            '未檢測到活躍的智能編輯器'}

## 佈局建議
${info.recommendations.length > 0 ?
            info.recommendations.map(rec => `- ${rec}`).join('\\n') :
            '無特殊建議'}

## 操作建議
- 如果您希望使用完整佈局，可以手動關閉最小模式
- 如果遇到衝突，建議調整其他擴展的設置
- 可以在設置中關閉自動檢測功能
        `;
        // 創建並顯示報告文檔
        const doc = await vscode.workspace.openTextDocument({
            content: report,
            language: 'markdown'
        });
        await vscode.window.showTextDocument(doc);
    }
    isKnownSmartEditor(extensionId) {
        return this._knownSmartEditors.includes(extensionId);
    }
    addKnownEditor(extensionId) {
        if (!this._knownSmartEditors.includes(extensionId)) {
            this._knownSmartEditors.push(extensionId);
        }
    }
    removeKnownEditor(extensionId) {
        const index = this._knownSmartEditors.indexOf(extensionId);
        if (index > -1) {
            this._knownSmartEditors.splice(index, 1);
        }
    }
    getKnownEditors() {
        return [...this._knownSmartEditors];
    }
}
exports.EditorDetectionService = EditorDetectionService;
//# sourceMappingURL=EditorDetectionService.js.map