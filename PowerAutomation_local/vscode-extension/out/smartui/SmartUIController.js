"use strict";
/**
 * SmartUI 主控制器
 * 整合所有 SmartUI 組件和服務
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SmartUIController = void 0;
const types_1 = require("./types");
const DecisionEngine_1 = require("./core/DecisionEngine");
const UserAnalyzer_1 = require("./core/UserAnalyzer");
const ClaudeService_1 = require("./services/ClaudeService");
const RoleService_1 = require("./services/RoleService");
class SmartUIController {
    constructor(context) {
        this.context = context;
        this.isInitialized = false;
        this.eventListeners = new Map();
        // 初始化狀態
        this.state = {
            currentRole: types_1.UserRole.USER,
            userPreferences: {
                role: types_1.UserRole.USER,
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
        this.decisionEngine = new DecisionEngine_1.SmartUIDecisionEngine();
        this.userAnalyzer = new UserAnalyzer_1.SmartUIUserAnalyzer();
        this.claudeService = new ClaudeService_1.SmartUIClaudeService();
        this.roleService = new RoleService_1.SmartUIRoleService();
    }
    async initialize() {
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
        }
        catch (error) {
            console.error('❌ SmartUI 控制器初始化失敗:', error);
            return false;
        }
    }
    async destroy() {
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
    getState() {
        return { ...this.state };
    }
    updateState(updates) {
        this.state = { ...this.state, ...updates };
        console.log('📊 SmartUI 狀態已更新');
    }
    // 角色管理
    getCurrentRole() {
        return this.state.currentRole;
    }
    async switchRole(newRole) {
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
        }
        catch (error) {
            console.error('❌ 角色切換失敗:', error);
            return false;
        }
    }
    // 用戶交互處理
    async handleUserInteraction(interaction) {
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
        }
        catch (error) {
            console.error('❌ 處理用戶交互失敗:', error);
        }
    }
    // 智能決策
    async makeSmartDecision(interaction) {
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
        }
        catch (error) {
            console.error('❌ 智能決策失敗:', error);
        }
    }
    // Claude 分析
    async analyzeWithClaude(content, type) {
        try {
            console.log(`🤖 Claude 分析: ${type}`);
            const request = {
                id: this.generateId(),
                type: type,
                content,
                role: this.state.currentRole,
                context: {
                    timestamp: Date.now(),
                    view: this.state.uiLayout.activeView
                }
            };
            const response = await this.claudeService.sendRequest(request);
            if (response.success) {
                const analysisResult = {
                    id: this.generateId(),
                    type: type,
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
        }
        catch (error) {
            console.error('❌ Claude 分析失敗:', error);
            return null;
        }
    }
    // 獲取用戶分析
    async getUserAnalysis() {
        try {
            const userId = this.getUserId();
            return await this.userAnalyzer.analyzeUser(userId);
        }
        catch (error) {
            console.error('❌ 獲取用戶分析失敗:', error);
            return null;
        }
    }
    // 獲取推薦
    async getRecommendations() {
        try {
            const userId = this.getUserId();
            return await this.userAnalyzer.getRecommendations(userId);
        }
        catch (error) {
            console.error('❌ 獲取推薦失敗:', error);
            return [];
        }
    }
    // 系統狀態更新
    async updateSystemStatus() {
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
                    mcp: 'connected',
                    livekit: 'connected' // 假設 LiveKit 服務正常
                },
                lastUpdate: Date.now()
            };
            // 觸發狀態更新事件
            this.emitEvent({
                type: 'SYSTEM_STATUS_UPDATE',
                payload: this.state.systemStatus
            });
        }
        catch (error) {
            console.error('❌ 更新系統狀態失敗:', error);
        }
    }
    // 事件管理
    addEventListener(eventType, listener) {
        if (!this.eventListeners.has(eventType)) {
            this.eventListeners.set(eventType, []);
        }
        this.eventListeners.get(eventType).push(listener);
    }
    removeEventListener(eventType, listener) {
        const listeners = this.eventListeners.get(eventType);
        if (listeners) {
            const index = listeners.indexOf(listener);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }
    emitEvent(event) {
        const listeners = this.eventListeners.get(event.type) || [];
        listeners.forEach(listener => {
            try {
                listener(event);
            }
            catch (error) {
                console.error('事件監聽器錯誤:', error);
            }
        });
    }
    // 私有方法
    setupEventListeners() {
        // 監聽角色服務事件
        this.roleService.addEventListener((event) => {
            this.emitEvent(event);
        });
        console.log('📡 事件監聽器設置完成');
    }
    async loadUserState() {
        try {
            // 從 VS Code 存儲中加載用戶狀態
            const savedState = this.context.globalState.get('smartui_state');
            if (savedState) {
                this.state = { ...this.state, ...savedState };
                console.log('📖 用戶狀態加載完成');
            }
        }
        catch (error) {
            console.warn('⚠️ 無法加載用戶狀態，使用默認設置');
        }
    }
    async saveUserState() {
        try {
            await this.context.globalState.update('smartui_state', {
                currentRole: this.state.currentRole,
                userPreferences: this.state.userPreferences,
                uiLayout: this.state.uiLayout
            });
            console.log('💾 用戶狀態保存完成');
        }
        catch (error) {
            console.error('❌ 保存用戶狀態失敗:', error);
        }
    }
    getRecentActions() {
        // 獲取最近的用戶操作
        return this.state.analysisResults
            .slice(-10)
            .map(result => ({
            type: result.type,
            timestamp: result.timestamp
        }));
    }
    getSessionDuration() {
        // 計算會話持續時間
        const startTime = this.context.globalState.get('session_start_time') || Date.now();
        return Date.now() - startTime;
    }
    getAvailableOptions(interaction) {
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
    async executeDecision(decision, interaction) {
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
    async showSmartSuggestion(interaction) {
        // 顯示智能建議
        const recommendations = await this.getRecommendations();
        if (recommendations.length > 0) {
            console.log('💡 顯示智能建議:', recommendations[0].title);
        }
    }
    async performCodeAnalysis(interaction) {
        // 執行代碼分析
        if (interaction.context.selectedText) {
            await this.analyzeWithClaude(interaction.context.selectedText, 'analysis');
        }
    }
    async performClaudeReview(interaction) {
        // 執行 Claude 審查
        if (interaction.context.selectedText) {
            await this.analyzeWithClaude(interaction.context.selectedText, 'review');
        }
    }
    getUserId() {
        // 獲取用戶 ID（可以是匿名 ID）
        let userId = this.context.globalState.get('user_id');
        if (!userId) {
            userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            this.context.globalState.update('user_id', userId);
        }
        return userId;
    }
    generateId() {
        return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    // 公共 API
    isReady() {
        return this.isInitialized;
    }
    getVersion() {
        return '1.0.0';
    }
    getFeatures() {
        return this.roleService.getFeatureConfigs().map(f => f.name);
    }
    hasPermission(resource, action) {
        return this.roleService.hasPermission(resource, action);
    }
    canAccessFeature(featureName) {
        return this.roleService.canAccessFeature(featureName);
    }
}
exports.SmartUIController = SmartUIController;
//# sourceMappingURL=SmartUIController.js.map