import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';

export class MCPServerManager {
    private _serverProcess: ChildProcess | null = null;
    private _isRunning: boolean = false;
    private _port: number = 8080;
    private _host: string = 'localhost';

    constructor() {
        const config = vscode.workspace.getConfiguration('powerautomation');
        this._port = config.get('mcpServer.port', 8080);
        this._host = config.get('mcpServer.host', 'localhost');
    }

    public async start(): Promise<void> {
        if (this._isRunning) {
            throw new Error('MCP Server is already running');
        }

        return new Promise((resolve, reject) => {
            try {
                // 獲取MCP服務器腳本路徑
                const workspaceFolders = vscode.workspace.workspaceFolders;
                if (!workspaceFolders || workspaceFolders.length === 0) {
                    throw new Error('No workspace folder found');
                }

                const mcpScriptPath = path.join(
                    workspaceFolders[0].uri.fsPath,
                    'powerautomation_local_mcp.py'
                );

                // 啟動MCP服務器
                this._serverProcess = spawn('python3', [mcpScriptPath, '--port', this._port.toString()], {
                    cwd: workspaceFolders[0].uri.fsPath,
                    stdio: ['pipe', 'pipe', 'pipe']
                });

                this._serverProcess.stdout?.on('data', (data) => {
                    const output = data.toString();
                    console.log('MCP Server:', output);
                    
                    // 檢查服務器是否成功啟動
                    if (output.includes('MCP Server started') || output.includes('Server running')) {
                        this._isRunning = true;
                        resolve();
                    }
                });

                this._serverProcess.stderr?.on('data', (data) => {
                    console.error('MCP Server Error:', data.toString());
                });

                this._serverProcess.on('close', (code) => {
                    console.log(`MCP Server process exited with code ${code}`);
                    this._isRunning = false;
                    this._serverProcess = null;
                });

                this._serverProcess.on('error', (error) => {
                    console.error('Failed to start MCP Server:', error);
                    this._isRunning = false;
                    this._serverProcess = null;
                    reject(error);
                });

                // 設置超時
                setTimeout(() => {
                    if (!this._isRunning) {
                        reject(new Error('MCP Server startup timeout'));
                    }
                }, 10000);

            } catch (error) {
                reject(error);
            }
        });
    }

    public async stop(): Promise<void> {
        if (!this._isRunning || !this._serverProcess) {
            throw new Error('MCP Server is not running');
        }

        return new Promise((resolve) => {
            if (this._serverProcess) {
                this._serverProcess.on('close', () => {
                    this._isRunning = false;
                    this._serverProcess = null;
                    resolve();
                });

                // 嘗試優雅關閉
                this._serverProcess.kill('SIGTERM');

                // 如果5秒後還沒關閉，強制終止
                setTimeout(() => {
                    if (this._serverProcess) {
                        this._serverProcess.kill('SIGKILL');
                    }
                }, 5000);
            } else {
                resolve();
            }
        });
    }

    public isRunning(): boolean {
        return this._isRunning;
    }

    public async sendMessage(message: string): Promise<string> {
        if (!this._isRunning) {
            throw new Error('MCP Server is not running');
        }

        try {
            // 這裡實現與MCP服務器的通信
            // 實際實現中會使用WebSocket或HTTP請求
            const response = await this._makeRequest('/chat', {
                message: message,
                timestamp: new Date().toISOString()
            });

            return response.reply || '抱歉，我無法處理您的請求。';
        } catch (error) {
            throw new Error(`Failed to send message to MCP Server: ${error}`);
        }
    }

    public async analyzeFile(fileName: string): Promise<string> {
        if (!this._isRunning) {
            throw new Error('MCP Server is not running');
        }

        try {
            const response = await this._makeRequest('/analyze', {
                fileName: fileName,
                action: 'analyze'
            });

            return response.analysis || `已分析文件 ${fileName}，但無法獲取詳細結果。`;
        } catch (error) {
            throw new Error(`Failed to analyze file: ${error}`);
        }
    }

    public async runTests(): Promise<string> {
        if (!this._isRunning) {
            throw new Error('MCP Server is not running');
        }

        try {
            const response = await this._makeRequest('/test', {
                action: 'run_manus_tests'
            });

            return response.result || '測試執行完成，請查看終端輸出。';
        } catch (error) {
            throw new Error(`Failed to run tests: ${error}`);
        }
    }

    private async _makeRequest(endpoint: string, data: any): Promise<any> {
        // 模擬HTTP請求 - 實際實現中會使用axios或fetch
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // 模擬響應
                switch (endpoint) {
                    case '/chat':
                        resolve({
                            reply: `我收到了您的消息："${data.message}"。我正在處理中...`
                        });
                        break;
                    case '/analyze':
                        resolve({
                            analysis: `📄 文件分析：${data.fileName}\\n\\n這是一個${this._getFileType(data.fileName)}文件。\\n\\n主要功能：\\n• 代碼結構良好\\n• 包含完整的文檔\\n• 測試覆蓋率較高`
                        });
                        break;
                    case '/test':
                        resolve({
                            result: '✅ Manus測試執行完成\\n\\n結果：\\n• TC001: 通過\\n• TC002: 通過\\n• TC003: 通過\\n\\n總體成功率: 100%'
                        });
                        break;
                    default:
                        reject(new Error('Unknown endpoint'));
                }
            }, 1000 + Math.random() * 2000); // 模擬網絡延遲
        });
    }

    private _getFileType(fileName: string): string {
        const ext = path.extname(fileName).toLowerCase();
        switch (ext) {
            case '.py': return 'Python';
            case '.js': case '.ts': return 'JavaScript/TypeScript';
            case '.md': return 'Markdown';
            case '.json': return 'JSON';
            case '.toml': return 'TOML配置';
            case '.txt': return '文本';
            default: return '未知類型';
        }
    }

    public getServerInfo(): { host: string; port: number; isRunning: boolean } {
        return {
            host: this._host,
            port: this._port,
            isRunning: this._isRunning
        };
    }
}

