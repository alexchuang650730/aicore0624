/**
 * SmartUI 主控制器
 * 整合所有 SmartUI 組件和服務
 */

import * as vscode from 'vscode';
import { 
    SmartUIState, 
    UserRole, 
    SmartUIEvent, 
    UserInteraction, 
    AnalysisResult,
    SystemStatus 
} from './types';
import { SmartUIDecisionEngine } from './core/DecisionEngine';
import { SmartUIUserAnalyzer } from './core/UserAnalyzer';
import { SmartUIClaudeService } from './services/ClaudeService';
import { SmartUIRoleService } from './services/RoleService';

export class SmartUIController {
    private isInitialized = false;
    private state: SmartUIState;
    private eventListeners: Map<string, ((event: SmartUIEvent) => void)[]> = new Map();
    
    // 核心服務
    private decisionEngine: SmartUIDecisionEngine;
    private userAnalyzer: SmartUIUserAnalyzer;
    private claudeService: SmartUIClaudeService;
    private roleService: SmartUIRoleService;

    constructor(private context: vscode.ExtensionContext) {
        // 初始化狀態
        this.state = {
            currentRole: UserRole.USER,
            userPreferences: {
                role: UserRole.USER,
                theme: 'auto',
                language: 'zh-CN',
                layout: {
                    sidebarWidth: 300,
                    panelHeight: 200,
                    showMinimap: true
                },
                features: {
                    autoSave: true,
                    smartSuggestions: true,
                    realTimeAnalysis: true
                },
                shortcuts: {}
            },
            uiLayout: {
                activeView: 'dashboard',
                visiblePanels: [],
                componentStates: {},
                responsiveBreakpoint: 'desktop'
            },
            analysisResults: [],
            systemStatus: {
                health: 'healthy',
                performance: {
                    cpu: 0,
                    memory: 0,
                    responseTime: 0
                },
                services: {
                    claude: 'disconnected',
                    mcp: 'disconnected',
                    livekit: 'disconnected'
                },
                lastUpdate: Date.now()
            },
            activeComponents: []
        };

        // 初始化服務
        this.decisionEngine = new SmartUIDecisionEngine();
        this.userAnalyzer = new SmartUIUserAnalyzer();
        this.claudeService = new SmartUIClaudeService();
        this.roleService = new SmartUIRoleService();
    }

    async initialize(): Promise<boolean> {
        try {
            console.log('🚀 初始化 SmartUI 控制器...');
            
            // 初始化所有服務
            const initResults = await Promise.all([
                this.decisionEngine.initialize(),
                this.userAnalyzer.initialize(),
                this.claudeService.initialize(),
                this.roleService.initialize()
            ]);

            if (!initResults.every(result => result)) {
                throw new Error('部分服務初始化失敗');
            }

            // 設置事件監聽
            this.setupEventListeners();

            // 加載用戶狀態
            await this.loadUserState();

            // 更新系統狀態
            await this.updateSystemStatus();

            this.isInitialized = true;
            console.log('✅ SmartUI 控制器初始化完成');

            // 觸發初始化完成事件
            this.emitEvent({
                type: 'SYSTEM_STATUS_UPDATE',
                payload: this.state.systemStatus
            });

            return true;

        } catch (error) {
            console.error('❌ SmartUI 控制器初始化失敗:', error);
            return false;
        }
    }

    async destroy(): Promise<void> {
        console.log('🔄 銷毀 SmartUI 控制器...');
        
        // 保存用戶狀態
        await this.saveUserState();

        // 銷毀所有服務
        await Promise.all([
            this.decisionEngine.destroy(),
            this.userAnalyzer.destroy(),
            this.claudeService.destroy(),
            this.roleService.destroy()
        ]);

        this.eventListeners.clear();
        this.isInitialized = false;
        
        console.log('✅ SmartUI 控制器已銷毀');
    }

    // 狀態管理
    getState(): SmartUIState {
        return { ...this.state };
    }

    updateState(updates: Partial<SmartUIState>): void {
        this.state = { ...this.state, ...updates };
        console.log('📊 SmartUI 狀態已更新');
    }

    // 角色管理
    getCurrentRole(): UserRole {
        return this.state.currentRole;
    }

    async switchRole(newRole: UserRole): Promise<boolean> {
        if (!this.isInitialized) {
            throw new Error('SmartUI 控制器未初始化');
        }

        try {
            // 使用角色服務切換角色
            const success = await this.roleService.switchRole(newRole);
            
            if (success) {
                const oldRole = this.state.currentRole;
                this.state.currentRole = newRole;
                
                // 更新用戶偏好
                this.state.userPreferences.role = newRole;
                
                // 更新 UI 配置
                const uiConfig = this.roleService.getUIConfig(newRole);
                if (uiConfig) {
                    this.state.uiLayout.activeView = uiConfig.defaultView;
                    this.state.uiLayout.visiblePanels = uiConfig.visibleComponents;
                }

                console.log(`🔄 角色切換成功: ${oldRole} → ${newRole}`);
                return true;
            }

            return false;

        } catch (error) {
            console.error('❌ 角色切換失敗:', error);
            return false;
        }
    }

    // 用戶交互處理
    async handleUserInteraction(interaction: UserInteraction): Promise<void> {
        try {
            console.log(`👆 處理用戶交互: ${interaction.type} - ${interaction.element}`);
            
            // 記錄交互
            this.userAnalyzer.trackInteraction(interaction);
            
            // 觸發交互事件
            this.emitEvent({
                type: 'USER_ACTION',
                payload: interaction
            });

            // 智能決策
            await this.makeSmartDecision(interaction);

        } catch (error) {
            console.error('❌ 處理用戶交互失敗:', error);
        }
    }

    // 智能決策
    private async makeSmartDecision(interaction: UserInteraction): Promise<void> {
        try {
            const context = {
                userId: interaction.context.userId || 'anonymous',
                role: this.state.currentRole,
                currentView: this.state.uiLayout.activeView,
                recentActions: this.getRecentActions(),
                sessionDuration: this.getSessionDuration()
            };

            const options = this.getAvailableOptions(interaction);
            
            if (options.length > 1) {
                const decision = await this.decisionEngine.makeDecision(context, options);
                console.log(`🎯 智能決策: ${decision.decision} (信心度: ${decision.confidence.toFixed(2)})`);
                
                // 執行決策
                await this.executeDecision(decision.decision, interaction);
            }

        } catch (error) {
            console.error('❌ 智能決策失敗:', error);
        }
    }

    // Claude 分析
    async analyzeWithClaude(content: string, type: string): Promise<AnalysisResult | null> {
        try {
            console.log(`🤖 Claude 分析: ${type}`);
            
            const request = {
                id: this.generateId(),
                type: type as any,
                content,
                role: this.state.currentRole,
                context: {
                    timestamp: Date.now(),
                    view: this.state.uiLayout.activeView
                }
            };

            const response = await this.claudeService.sendRequest(request);
            
            if (response.success) {
                const analysisResult: AnalysisResult = {
                    id: this.generateId(),
                    type: type as any,
                    content,
                    result: response.result,
                    confidence: response.confidence || 0.8,
                    timestamp: Date.now(),
                    role: this.state.currentRole
                };

                // 添加到分析結果
                this.state.analysisResults.push(analysisResult);
                
                // 限制結果數量
                if (this.state.analysisResults.length > 100) {
                    this.state.analysisResults = this.state.analysisResults.slice(-100);
                }

                // 觸發分析完成事件
                this.emitEvent({
                    type: 'ANALYSIS_COMPLETE',
                    payload: analysisResult
                });

                return analysisResult;
            }

            return null;

        } catch (error) {
            console.error('❌ Claude 分析失敗:', error);
            return null;
        }
    }

    // 獲取用戶分析
    async getUserAnalysis(): Promise<any> {
        try {
            const userId = this.getUserId();
            return await this.userAnalyzer.analyzeUser(userId);
        } catch (error) {
            console.error('❌ 獲取用戶分析失敗:', error);
            return null;
        }
    }

    // 獲取推薦
    async getRecommendations(): Promise<any[]> {
        try {
            const userId = this.getUserId();
            return await this.userAnalyzer.getRecommendations(userId);
        } catch (error) {
            console.error('❌ 獲取推薦失敗:', error);
            return [];
        }
    }

    // 系統狀態更新
    async updateSystemStatus(): Promise<void> {
        try {
            const statuses = await Promise.all([
                this.decisionEngine.getStatus(),
                this.userAnalyzer.getStatus(),
                this.claudeService.getStatus(),
                this.roleService.getStatus()
            ]);

            // 計算整體健康狀態
            const overallHealth = statuses.every(s => s.health === 'healthy') ? 'healthy' :
                                 statuses.some(s => s.health === 'error') ? 'error' : 'warning';

            // 計算平均性能
            const avgPerformance = {
                cpu: statuses.reduce((sum, s) => sum + s.performance.cpu, 0) / statuses.length,
                memory: statuses.reduce((sum, s) => sum + s.performance.memory, 0) / statuses.length,
                responseTime: statuses.reduce((sum, s) => sum + s.performance.responseTime, 0) / statuses.length
            };

            this.state.systemStatus = {
                health: overallHealth,
                performance: avgPerformance,
                services: {
                    claude: this.claudeService.getStatus().health === 'healthy' ? 'connected' : 'error',
                    mcp: 'connected', // 假設 MCP 服務正常
                    livekit: 'connected' // 假設 LiveKit 服務正常
                },
                lastUpdate: Date.now()
            };

            // 觸發狀態更新事件
            this.emitEvent({
                type: 'SYSTEM_STATUS_UPDATE',
                payload: this.state.systemStatus
            });

        } catch (error) {
            console.error('❌ 更新系統狀態失敗:', error);
        }
    }

    // 事件管理
    addEventListener(eventType: string, listener: (event: SmartUIEvent) => void): void {
        if (!this.eventListeners.has(eventType)) {
            this.eventListeners.set(eventType, []);
        }
        this.eventListeners.get(eventType)!.push(listener);
    }

    removeEventListener(eventType: string, listener: (event: SmartUIEvent) => void): void {
        const listeners = this.eventListeners.get(eventType);
        if (listeners) {
            const index = listeners.indexOf(listener);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }

    private emitEvent(event: SmartUIEvent): void {
        const listeners = this.eventListeners.get(event.type) || [];
        listeners.forEach(listener => {
            try {
                listener(event);
            } catch (error) {
                console.error('事件監聽器錯誤:', error);
            }
        });
    }

    // 私有方法
    private setupEventListeners(): void {
        // 監聽角色服務事件
        this.roleService.addEventListener((event) => {
            this.emitEvent(event);
        });

        console.log('📡 事件監聽器設置完成');
    }

    private async loadUserState(): Promise<void> {
        try {
            // 從 VS Code 存儲中加載用戶狀態
            const savedState = this.context.globalState.get('smartui_state');
            if (savedState) {
                this.state = { ...this.state, ...(savedState as Partial<SmartUIState>) };
                console.log('📖 用戶狀態加載完成');
            }
        } catch (error) {
            console.warn('⚠️ 無法加載用戶狀態，使用默認設置');
        }
    }

    private async saveUserState(): Promise<void> {
        try {
            await this.context.globalState.update('smartui_state', {
                currentRole: this.state.currentRole,
                userPreferences: this.state.userPreferences,
                uiLayout: this.state.uiLayout
            });
            console.log('💾 用戶狀態保存完成');
        } catch (error) {
            console.error('❌ 保存用戶狀態失敗:', error);
        }
    }

    private getRecentActions(): any[] {
        // 獲取最近的用戶操作
        return this.state.analysisResults
            .slice(-10)
            .map(result => ({
                type: result.type,
                timestamp: result.timestamp
            }));
    }

    private getSessionDuration(): number {
        // 計算會話持續時間
        const startTime = (this.context.globalState.get('session_start_time') as number) || Date.now();
        return Date.now() - startTime;
    }

    private getAvailableOptions(interaction: UserInteraction): string[] {
        // 基於交互類型和當前狀態獲取可用選項
        const options = ['default_action'];
        
        if (interaction.type === 'click') {
            options.push('smart_suggestion', 'context_menu', 'quick_action');
        }
        
        if (interaction.element.includes('code')) {
            options.push('code_analysis', 'claude_review', 'documentation');
        }
        
        return options;
    }

    private async executeDecision(decision: string, interaction: UserInteraction): Promise<void> {
        // 執行智能決策
        console.log(`⚡ 執行決策: ${decision}`);
        
        switch (decision) {
            case 'smart_suggestion':
                await this.showSmartSuggestion(interaction);
                break;
            case 'code_analysis':
                await this.performCodeAnalysis(interaction);
                break;
            case 'claude_review':
                await this.performClaudeReview(interaction);
                break;
            default:
                console.log(`🔄 執行默認操作: ${decision}`);
        }
    }

    private async showSmartSuggestion(interaction: UserInteraction): Promise<void> {
        // 顯示智能建議
        const recommendations = await this.getRecommendations();
        if (recommendations.length > 0) {
            console.log('💡 顯示智能建議:', recommendations[0].title);
        }
    }

    private async performCodeAnalysis(interaction: UserInteraction): Promise<void> {
        // 執行代碼分析
        if (interaction.context.selectedText) {
            await this.analyzeWithClaude(interaction.context.selectedText, 'analysis');
        }
    }

    private async performClaudeReview(interaction: UserInteraction): Promise<void> {
        // 執行 Claude 審查
        if (interaction.context.selectedText) {
            await this.analyzeWithClaude(interaction.context.selectedText, 'review');
        }
    }

    private getUserId(): string {
        // 獲取用戶 ID（可以是匿名 ID）
        let userId = this.context.globalState.get('user_id') as string;
        if (!userId) {
            userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            this.context.globalState.update('user_id', userId);
        }
        return userId;
    }

    private generateId(): string {
        return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // 公共 API
    isReady(): boolean {
        return this.isInitialized;
    }

    getVersion(): string {
        return '1.0.0';
    }

    getFeatures(): string[] {
        return this.roleService.getFeatureConfigs().map(f => f.name);
    }

    hasPermission(resource: string, action: string): boolean {
        return this.roleService.hasPermission(resource, action);
    }

    canAccessFeature(featureName: string): boolean {
        return this.roleService.canAccessFeature(featureName);
    }
}

