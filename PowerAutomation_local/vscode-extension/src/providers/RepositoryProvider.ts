import * as vscode from 'vscode';
import { MCPService } from '../services/MCPService';

export class RepositoryProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'powerautomation.repository';
    private _view?: vscode.WebviewView;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _mcpService: MCPService
    ) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        console.log('RepositoryProvider: resolveWebviewView called');
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        
        // 處理來自 webview 的消息
        webviewView.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'openFile':
                        this._openFile(message.path);
                        break;
                    case 'refreshRepository':
                        this.refresh();
                        break;
                }
            },
            undefined,
            []
        );

        console.log('RepositoryProvider: HTML set successfully');
    }

    public refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }

    private _openFile(filePath: string) {
        vscode.workspace.openTextDocument(filePath).then(doc => {
            vscode.window.showTextDocument(doc);
        });
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Repository & Dashboard</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    margin: 0;
                    padding: 16px;
                }
                .header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 16px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                .icon {
                    margin-right: 8px;
                    font-size: 18px;
                }
                .title {
                    font-weight: bold;
                    font-size: 16px;
                }
                .section {
                    margin-bottom: 16px;
                }
                .section-title {
                    font-weight: bold;
                    margin-bottom: 8px;
                    color: var(--vscode-textLink-foreground);
                }
                .file-item {
                    padding: 4px 8px;
                    margin: 2px 0;
                    cursor: pointer;
                    border-radius: 4px;
                    transition: background-color 0.2s;
                }
                .file-item:hover {
                    background-color: var(--vscode-list-hoverBackground);
                }
                .button {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin: 4px 0;
                    width: 100%;
                }
                .button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                .status {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                    margin-top: 16px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <span class="icon">📁</span>
                <span class="title">Repository & Dashboard</span>
            </div>
            
            <div class="section">
                <div class="section-title">📊 Dashboard</div>
                <button class="button" onclick="refreshRepository()">🔄 Refresh Repository</button>
                <button class="button" onclick="openNewFile()">📄 New File</button>
                <button class="button" onclick="openTerminal()">💻 Open Terminal</button>
            </div>
            
            <div class="section">
                <div class="section-title">📂 Recent Files</div>
                <div class="file-item" onclick="openFile('example.js')">📄 example.js</div>
                <div class="file-item" onclick="openFile('README.md')">📄 README.md</div>
                <div class="file-item" onclick="openFile('package.json')">📄 package.json</div>
            </div>
            
            <div class="section">
                <div class="section-title">🔧 Quick Actions</div>
                <button class="button" onclick="runTests()">🧪 Run Tests</button>
                <button class="button" onclick="buildProject()">🏗️ Build Project</button>
                <button class="button" onclick="deployProject()">🚀 Deploy</button>
            </div>
            
            <div class="status">
                ✅ PowerAutomation KiloCode Ready<br>
                🕒 ${new Date().toLocaleString()}
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                
                function openFile(path) {
                    vscode.postMessage({
                        command: 'openFile',
                        path: path
                    });
                }
                
                function refreshRepository() {
                    vscode.postMessage({
                        command: 'refreshRepository'
                    });
                }
                
                function openNewFile() {
                    vscode.postMessage({
                        command: 'openFile',
                        path: 'untitled:Untitled-1'
                    });
                }
                
                function openTerminal() {
                    // 這將通過 VS Code 命令打開終端
                }
                
                function runTests() {
                    // 運行測試的邏輯
                }
                
                function buildProject() {
                    // 構建項目的邏輯
                }
                
                function deployProject() {
                    // 部署項目的邏輯
                }
            </script>
        </body>
        </html>`;
    }
}

