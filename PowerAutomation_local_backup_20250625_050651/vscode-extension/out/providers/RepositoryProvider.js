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
exports.RepositoryProvider = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
class RepositoryProvider {
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
    }
    resolveWebviewView(webviewView, context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        // 處理來自webview的消息
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'selectFile':
                    await this._selectFile(message.fileName);
                    break;
                case 'analyzeFile':
                    await this._analyzeFile(message.fileName);
                    break;
                case 'openFile':
                    await this._openFile(message.fileName);
                    break;
                case 'refreshRepository':
                    this.refresh();
                    break;
            }
        }, undefined, []);
    }
    refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }
    async _selectFile(fileName) {
        // 通知其他視圖文件被選中
        vscode.commands.executeCommand('powerautomation.fileSelected', fileName);
    }
    async _analyzeFile(fileName) {
        // 發送分析請求到Chat視圖
        vscode.commands.executeCommand('powerautomation.analyzeFile', fileName);
    }
    async _openFile(fileName) {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            const filePath = path.join(workspaceFolders[0].uri.fsPath, fileName);
            const document = await vscode.workspace.openTextDocument(filePath);
            await vscode.window.showTextDocument(document);
        }
    }
    _getFileList() {
        // 模擬文件列表 - 實際實現中會讀取工作區文件
        return [
            {
                name: 'server',
                type: 'folder',
                icon: '📁',
                children: [
                    { name: 'server_manager.py', type: 'file', icon: '🐍', language: 'python' },
                    { name: 'integrations', type: 'folder', icon: '📁' },
                    { name: 'automation', type: 'folder', icon: '📁' }
                ]
            },
            {
                name: 'tests',
                type: 'folder',
                icon: '📁',
                children: [
                    { name: 'manus_tests', type: 'folder', icon: '📁' },
                    { name: 'automation_tests', type: 'folder', icon: '📁' },
                    { name: 'basic_test.py', type: 'file', icon: '🧪', language: 'python' }
                ]
            },
            { name: 'powerautomation_local_mcp.py', type: 'file', icon: '🤖', language: 'python' },
            { name: 'README.md', type: 'file', icon: '📖', language: 'markdown' },
            { name: 'config.toml', type: 'file', icon: '⚙️', language: 'toml' },
            { name: 'requirements.txt', type: 'file', icon: '📋', language: 'text' }
        ];
    }
    _getHtmlForWebview(webview) {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const isMinimalMode = config.get('minimalMode', false);
        if (isMinimalMode) {
            return `<!DOCTYPE html>
<html><body style="display:none;"></body></html>`;
        }
        const fileList = this._getFileList();
        const workspaceName = vscode.workspace.workspaceFolders?.[0]?.name || 'PowerAutomation_local';
        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repository Explorer</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .repo-header {
            padding: 16px;
            background: var(--vscode-panel-background);
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .repo-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
        }

        .repo-selector {
            width: 100%;
            padding: 6px 10px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            color: var(--vscode-input-foreground);
            font-size: 12px;
        }

        .repo-selector:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        .repo-info {
            padding: 16px;
            background: var(--vscode-panel-background);
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .repo-name {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .repo-branch {
            font-size: 11px;
            color: var(--vscode-terminal-ansiGreen);
            margin-bottom: 8px;
        }

        .repo-stats {
            display: flex;
            gap: 12px;
        }

        .repo-stat {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
        }

        .repo-stat-value {
            color: var(--vscode-foreground);
            font-weight: 600;
        }

        .file-explorer {
            flex: 1;
            overflow-y: auto;
        }

        .file-tree {
            padding: 8px 0;
        }

        .file-tree-item {
            display: flex;
            align-items: center;
            padding: 6px 16px;
            cursor: pointer;
            transition: background-color 0.2s;
            user-select: none;
        }

        .file-tree-item:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .file-tree-item.selected {
            background: var(--vscode-list-activeSelectionBackground);
            color: var(--vscode-list-activeSelectionForeground);
        }

        .file-tree-item.folder {
            font-weight: 500;
        }

        .file-icon {
            margin-right: 8px;
            font-size: 12px;
            width: 16px;
            text-align: center;
        }

        .file-name {
            font-size: 12px;
            flex: 1;
        }

        .file-actions {
            opacity: 0;
            display: flex;
            gap: 4px;
            transition: opacity 0.2s;
        }

        .file-tree-item:hover .file-actions {
            opacity: 1;
        }

        .file-action {
            padding: 2px 4px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 2px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 10px;
            cursor: pointer;
        }

        .file-action:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .file-actions-panel {
            padding: 16px;
            background: var(--vscode-panel-background);
            border-top: 1px solid var(--vscode-panel-border);
        }

        .file-action-button {
            width: 100%;
            padding: 8px 12px;
            margin-bottom: 6px;
            background: var(--vscode-button-secondaryBackground);
            border: none;
            border-radius: 4px;
            color: var(--vscode-button-secondaryForeground);
            font-size: 11px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .file-action-button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .file-action-button.primary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }

        .file-action-button.primary:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .search-box {
            width: 100%;
            padding: 6px 10px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            color: var(--vscode-input-foreground);
            font-size: 11px;
            margin-bottom: 12px;
        }

        .search-box:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        /* 滾動條樣式 */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: var(--vscode-scrollbarSlider-background);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--vscode-scrollbarSlider-hoverBackground);
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="repo-header">
        <div class="repo-title">📦 倉庫選擇</div>
        <select class="repo-selector" onchange="switchRepository(this.value)">
            <option value="powerautomation">PowerAutomation Local</option>
            <option value="aicore0623">aicore0623</option>
            <option value="aicore0622">aicore0622</option>
            <option value="manus-system">Manus System</option>
        </select>
    </div>

    <div class="repo-info">
        <div class="repo-name">${workspaceName}</div>
        <div class="repo-branch">🌿 main</div>
        <div class="repo-stats">
            <span class="repo-stat">📄 <span class="repo-stat-value">67</span> 文件</span>
            <span class="repo-stat">📊 <span class="repo-stat-value">15K</span> 行</span>
        </div>
    </div>

    <div class="file-explorer">
        <div style="padding: 0 16px 8px;">
            <input type="text" class="search-box" placeholder="🔍 搜索文件..." 
                   onkeyup="filterFiles(this.value)">
        </div>
        
        <div class="file-tree" id="fileTree">
            ${this._generateFileTreeHtml(fileList)}
        </div>
    </div>

    <div class="file-actions-panel">
        <button class="file-action-button primary" onclick="analyzeSelectedFile()">
            📖 分析選中文件
        </button>
        <button class="file-action-button" onclick="openSelectedFile()">
            📝 打開文件
        </button>
        <button class="file-action-button" onclick="searchInFiles()">
            🔍 搜索內容
        </button>
        <button class="file-action-button" onclick="refreshRepository()">
            🔄 刷新倉庫
        </button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let selectedFile = 'powerautomation_local_mcp.py';

        function switchRepository(repoName) {
            console.log('切換到倉庫:', repoName);
            vscode.postMessage({
                type: 'switchRepository',
                repoName: repoName
            });
        }

        function selectFile(element, fileName) {
            // 移除其他選中狀態
            document.querySelectorAll('.file-tree-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            // 添加選中狀態
            element.classList.add('selected');
            selectedFile = fileName;
            
            vscode.postMessage({
                type: 'selectFile',
                fileName: fileName
            });
        }

        function analyzeSelectedFile() {
            if (selectedFile) {
                vscode.postMessage({
                    type: 'analyzeFile',
                    fileName: selectedFile
                });
            }
        }

        function openSelectedFile() {
            if (selectedFile) {
                vscode.postMessage({
                    type: 'openFile',
                    fileName: selectedFile
                });
            }
        }

        function searchInFiles() {
            // 實現文件內容搜索
            console.log('搜索文件內容');
        }

        function refreshRepository() {
            vscode.postMessage({
                type: 'refreshRepository'
            });
        }

        function toggleFolder(element) {
            const folderName = element.querySelector('.file-name').textContent;
            console.log('切換文件夾:', folderName);
            // 實現文件夾展開/收起邏輯
        }

        function filterFiles(searchTerm) {
            const items = document.querySelectorAll('.file-tree-item');
            items.forEach(item => {
                const fileName = item.querySelector('.file-name').textContent.toLowerCase();
                if (fileName.includes(searchTerm.toLowerCase())) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        // 初始化選中第一個文件
        document.addEventListener('DOMContentLoaded', function() {
            const firstFile = document.querySelector('.file-tree-item[data-file]');
            if (firstFile) {
                firstFile.click();
            }
        });
    </script>
</body>
</html>`;
    }
    _generateFileTreeHtml(files, level = 0) {
        return files.map(file => {
            const indent = '  '.repeat(level);
            const isFile = file.type === 'file';
            const dataAttr = isFile ? `data-file="${file.name}"` : '';
            let html = `
                <div class="file-tree-item ${file.type}" ${dataAttr}
                     onclick="${isFile ? `selectFile(this, '${file.name}')` : `toggleFolder(this)`}">
                    <span class="file-icon">${file.icon}</span>
                    <span class="file-name">${file.name}</span>
                    ${isFile ? `
                    <div class="file-actions">
                        <button class="file-action" onclick="event.stopPropagation(); analyzeFile('${file.name}')">📖</button>
                        <button class="file-action" onclick="event.stopPropagation(); openFile('${file.name}')">📝</button>
                    </div>
                    ` : ''}
                </div>
            `;
            if (file.children) {
                html += this._generateFileTreeHtml(file.children, level + 1);
            }
            return html;
        }).join('');
    }
}
exports.RepositoryProvider = RepositoryProvider;
RepositoryProvider.viewType = 'powerautomation.repository';
//# sourceMappingURL=RepositoryProvider.js.map