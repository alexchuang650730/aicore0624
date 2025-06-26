import * as vscode from 'vscode';

import fetch from 'node-fetch';

export class MCPService {
    private outputChannel: vscode.OutputChannel;
    private endpoint: string;
    private apiKey: string;

    constructor(outputChannel: vscode.OutputChannel) {
        this.outputChannel = outputChannel;
        this.endpoint = vscode.workspace.getConfiguration('powerautomation').get('mcpEndpoint', 'http://18.212.97.173:8080');
        this.apiKey = vscode.workspace.getConfiguration('powerautomation').get('apiKey', '');
    }

    public async sendChatMessage(message: string): Promise<string> {
        try {
            this.log(`發送消息到 MCP: ${message}`);
            
            const response = await fetch(`${this.endpoint}/api/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': this.apiKey ? `Bearer ${this.apiKey}` : '',
                    'User-Agent': 'PowerAutomation-KiloCode/1.0.0'
                },
                body: JSON.stringify({
                    request: message,
                    context: {
                        source: 'vscode_vsix',
                        client: 'powerautomation-kilocode',
                        timestamp: new Date().toISOString()
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data: any = await response.json();
            this.log(`收到 MCP 響應: ${JSON.stringify(data)}`);
            
            if (data.success) {
                return data.result?.content || data.result || '處理完成';
            } else {
                throw new Error(data.error || '未知錯誤');
            }
        } catch (error) {
            this.log(`MCP 服務錯誤: ${error}`);
            return `抱歉，處理您的請求時出現錯誤: ${error}`;
        }
    }

    public async executeAutomation(task: string): Promise<string> {
        try {
            this.log(`執行自動化任務: ${task}`);
            
            const response = await fetch(`${this.endpoint}/api/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': this.apiKey ? `Bearer ${this.apiKey}` : '',
                    'User-Agent': 'PowerAutomation-KiloCode/1.0.0'
                },
                body: JSON.stringify({
                    request: task,
                    context: {
                        source: 'vscode_vsix',
                        client: 'powerautomation-kilocode',
                        type: 'automation',
                        timestamp: new Date().toISOString()
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data: any = await response.json();
            this.log(`自動化任務響應: ${JSON.stringify(data)}`);
            
            return data.result?.content || data.result || '自動化任務執行完成';
        } catch (error) {
            this.log(`自動化任務錯誤: ${error}`);
            throw error;
        }
    }

    private log(message: string) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] MCP: ${message}`;
        console.log(logEntry);
        this.outputChannel.appendLine(logEntry);
    }
}

