import * as vscode from 'vscode';

export class EditorDetectionService {
    private _knownSmartEditors = [
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

    public async detectOtherEditors(): Promise<boolean> {
        try {
            // 獲取所有已安裝的擴展
            const extensions = vscode.extensions.all;
            
            // 檢查是否有其他智能編輯器擴展
            const smartEditorExtensions = extensions.filter(ext => 
                this._knownSmartEditors.includes(ext.id) && ext.isActive
            );

            console.log('Detected smart editor extensions:', smartEditorExtensions.map(ext => ext.id));

            // 如果檢測到其他智能編輯器，返回true
            return smartEditorExtensions.length > 0;
        } catch (error) {
            console.error('Error detecting other editors:', error);
            return false;
        }
    }

    public async getActiveEditorInfo(): Promise<{
        totalExtensions: number;
        smartEditors: string[];
        recommendations: string[];
    }> {
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
        } catch (error) {
            console.error('Error getting editor info:', error);
            return {
                totalExtensions: 0,
                smartEditors: [],
                recommendations: []
            };
        }
    }

    private _getLayoutRecommendations(activeEditors: string[]): string[] {
        const recommendations: string[] = [];

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

    public async monitorExtensionChanges(): Promise<void> {
        // 監聽擴展安裝/卸載事件
        vscode.extensions.onDidChange(() => {
            this.detectOtherEditors().then(hasOtherEditors => {
                // 自動調整佈局模式
                const config = vscode.workspace.getConfiguration('powerautomation');
                const autoDetect = config.get('autoDetectEditors', true);
                
                if (autoDetect) {
                    config.update('minimalMode', hasOtherEditors, vscode.ConfigurationTarget.Global);
                    
                    if (hasOtherEditors) {
                        vscode.window.showInformationMessage(
                            '檢測到其他智能編輯器，已自動切換到最小模式',
                            '查看詳情'
                        ).then(selection => {
                            if (selection === '查看詳情') {
                                this.showDetectionReport();
                            }
                        });
                    }
                }
            });
        });
    }

    public async showDetectionReport(): Promise<void> {
        const info = await this.getActiveEditorInfo();
        
        const report = `
# 智能編輯器檢測報告

## 總體信息
- 已安裝擴展總數: ${info.totalExtensions}
- 檢測到的智能編輯器: ${info.smartEditors.length}

## 活躍的智能編輯器
${info.smartEditors.length > 0 ? 
    info.smartEditors.map(editor => `- ${editor}`).join('\\n') : 
    '未檢測到活躍的智能編輯器'
}

## 佈局建議
${info.recommendations.length > 0 ? 
    info.recommendations.map(rec => `- ${rec}`).join('\\n') : 
    '無特殊建議'
}

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

    public isKnownSmartEditor(extensionId: string): boolean {
        return this._knownSmartEditors.includes(extensionId);
    }

    public addKnownEditor(extensionId: string): void {
        if (!this._knownSmartEditors.includes(extensionId)) {
            this._knownSmartEditors.push(extensionId);
        }
    }

    public removeKnownEditor(extensionId: string): void {
        const index = this._knownSmartEditors.indexOf(extensionId);
        if (index > -1) {
            this._knownSmartEditors.splice(index, 1);
        }
    }

    public getKnownEditors(): string[] {
        return [...this._knownSmartEditors];
    }
}

