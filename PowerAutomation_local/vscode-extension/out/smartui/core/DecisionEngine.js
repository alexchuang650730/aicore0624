"use strict";
/**
 * SmartUI 決策引擎
 * 基於用戶行為、角色和上下文做出智能決策
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SmartUIDecisionEngine = void 0;
const types_1 = require("../types");
class SmartUIDecisionEngine {
    constructor() {
        this.isInitialized = false;
        this.learningData = new Map();
        this.decisionHistory = [];
        this.userPatterns = new Map();
    }
    async initialize() {
        try {
            console.log('🧠 初始化 SmartUI 決策引擎...');
            // 加載歷史學習數據
            await this.loadLearningData();
            // 初始化決策策略
            this.initializeDecisionStrategies();
            this.isInitialized = true;
            console.log('✅ SmartUI 決策引擎初始化完成');
            return true;
        }
        catch (error) {
            console.error('❌ SmartUI 決策引擎初始化失敗:', error);
            return false;
        }
    }
    async destroy() {
        console.log('🔄 銷毀 SmartUI 決策引擎...');
        // 保存學習數據
        await this.saveLearningData();
        this.learningData.clear();
        this.decisionHistory = [];
        this.userPatterns.clear();
        this.isInitialized = false;
        console.log('✅ SmartUI 決策引擎已銷毀');
    }
    getStatus() {
        return {
            health: this.isInitialized ? 'healthy' : 'error',
            performance: {
                cpu: this.calculateCpuUsage(),
                memory: this.calculateMemoryUsage(),
                responseTime: this.getAverageResponseTime()
            },
            services: {
                claude: 'connected',
                mcp: 'connected',
                livekit: 'connected'
            },
            lastUpdate: Date.now()
        };
    }
    async makeDecision(context, options) {
        if (!this.isInitialized) {
            throw new Error('決策引擎未初始化');
        }
        const startTime = Date.now();
        try {
            // 分析上下文
            const contextAnalysis = this.analyzeContext(context);
            // 獲取用戶模式
            const userPattern = this.getUserPattern(context.userId, context.role);
            // 應用決策策略
            const decision = await this.applyDecisionStrategies(contextAnalysis, userPattern, options);
            // 計算信心度
            const confidence = this.calculateConfidence(decision, contextAnalysis);
            // 生成推理過程
            const reasoning = this.generateReasoning(decision, contextAnalysis, userPattern);
            // 生成替代方案
            const alternatives = this.generateAlternatives(options, decision);
            const result = {
                decision,
                confidence,
                reasoning,
                alternatives,
                context: {
                    ...contextAnalysis,
                    processingTime: Date.now() - startTime,
                    timestamp: Date.now()
                }
            };
            // 記錄決策歷史
            this.decisionHistory.push(result);
            console.log(`🎯 決策完成: ${decision} (信心度: ${confidence.toFixed(2)})`);
            return result;
        }
        catch (error) {
            console.error('❌ 決策過程出錯:', error);
            throw error;
        }
    }
    learn(interaction, outcome) {
        try {
            const key = this.generateLearningKey(interaction);
            // 更新學習數據
            const existingData = this.learningData.get(key) || {
                interactions: [],
                outcomes: [],
                patterns: {}
            };
            existingData.interactions.push(interaction);
            existingData.outcomes.push(outcome);
            // 分析模式
            existingData.patterns = this.analyzeInteractionPatterns(existingData.interactions);
            this.learningData.set(key, existingData);
            // 更新用戶模式
            this.updateUserPattern(interaction.context.userId, interaction);
            console.log(`📚 學習完成: ${key}`);
        }
        catch (error) {
            console.error('❌ 學習過程出錯:', error);
        }
    }
    async loadLearningData() {
        try {
            // 從 VS Code 存儲中加載數據
            // 這裡可以從 globalState 或文件系統加載
            console.log('📖 加載學習數據...');
        }
        catch (error) {
            console.warn('⚠️ 無法加載學習數據，使用默認設置');
        }
    }
    async saveLearningData() {
        try {
            // 保存到 VS Code 存儲
            console.log('💾 保存學習數據...');
        }
        catch (error) {
            console.error('❌ 保存學習數據失敗:', error);
        }
    }
    initializeDecisionStrategies() {
        console.log('🎯 初始化決策策略...');
        // 初始化不同的決策策略
        // 1. 基於規則的策略
        // 2. 基於機器學習的策略
        // 3. 基於用戶行為的策略
        // 4. 基於角色的策略
        // 5. 混合策略
    }
    analyzeContext(context) {
        return {
            role: context.role || types_1.UserRole.USER,
            currentView: context.currentView || 'unknown',
            recentActions: context.recentActions || [],
            timeOfDay: new Date().getHours(),
            sessionDuration: context.sessionDuration || 0,
            complexity: this.calculateContextComplexity(context)
        };
    }
    getUserPattern(userId, role) {
        const key = `${userId}_${role}`;
        return this.userPatterns.get(key) || {
            preferredFeatures: [],
            averageSessionTime: 0,
            commonWorkflows: [],
            efficiency: 0.5
        };
    }
    async applyDecisionStrategies(contextAnalysis, userPattern, options) {
        // 策略 1: 基於角色的決策
        const roleBasedScore = this.calculateRoleBasedScore(contextAnalysis.role, options);
        // 策略 2: 基於用戶模式的決策
        const patternBasedScore = this.calculatePatternBasedScore(userPattern, options);
        // 策略 3: 基於上下文的決策
        const contextBasedScore = this.calculateContextBasedScore(contextAnalysis, options);
        // 策略 4: 基於時間的決策
        const timeBasedScore = this.calculateTimeBasedScore(contextAnalysis.timeOfDay, options);
        // 綜合評分
        const scores = options.map(option => {
            const totalScore = roleBasedScore[option] * 0.3 +
                patternBasedScore[option] * 0.3 +
                contextBasedScore[option] * 0.25 +
                timeBasedScore[option] * 0.15;
            return { option, score: totalScore };
        });
        // 選擇最高分的選項
        scores.sort((a, b) => b.score - a.score);
        return scores[0].option;
    }
    calculateConfidence(decision, contextAnalysis) {
        // 基於多個因素計算信心度
        let confidence = 0.5; // 基礎信心度
        // 基於上下文複雜度調整
        confidence += (1 - contextAnalysis.complexity) * 0.2;
        // 基於歷史決策成功率調整
        const historicalSuccess = this.getHistoricalSuccessRate(decision);
        confidence += historicalSuccess * 0.3;
        return Math.min(Math.max(confidence, 0), 1);
    }
    generateReasoning(decision, contextAnalysis, userPattern) {
        const reasoning = [];
        reasoning.push(`基於用戶角色 ${contextAnalysis.role} 的特點`);
        reasoning.push(`考慮當前視圖 ${contextAnalysis.currentView} 的上下文`);
        reasoning.push(`參考用戶的歷史使用模式`);
        if (contextAnalysis.complexity > 0.7) {
            reasoning.push('檢測到複雜操作場景，優先推薦簡化方案');
        }
        if (userPattern.efficiency < 0.5) {
            reasoning.push('基於用戶效率較低，推薦輔助功能');
        }
        return reasoning;
    }
    generateAlternatives(options, selectedDecision) {
        return options.filter(option => option !== selectedDecision).slice(0, 2);
    }
    calculateContextComplexity(context) {
        let complexity = 0;
        // 基於最近操作數量
        complexity += Math.min(context.recentActions?.length || 0, 10) / 10 * 0.3;
        // 基於會話持續時間
        complexity += Math.min(context.sessionDuration || 0, 3600) / 3600 * 0.3;
        // 基於當前視圖複雜度
        const viewComplexity = this.getViewComplexity(context.currentView);
        complexity += viewComplexity * 0.4;
        return Math.min(complexity, 1);
    }
    getViewComplexity(view) {
        const complexityMap = {
            'dashboard': 0.8,
            'editor': 0.6,
            'settings': 0.7,
            'chat': 0.4,
            'repository': 0.5
        };
        return complexityMap[view] || 0.5;
    }
    calculateRoleBasedScore(role, options) {
        const scores = {};
        options.forEach(option => {
            switch (role) {
                case types_1.UserRole.ADMIN:
                    scores[option] = this.getAdminPreference(option);
                    break;
                case types_1.UserRole.DEVELOPER:
                    scores[option] = this.getDeveloperPreference(option);
                    break;
                case types_1.UserRole.USER:
                    scores[option] = this.getUserPreference(option);
                    break;
                default:
                    scores[option] = 0.5;
            }
        });
        return scores;
    }
    calculatePatternBasedScore(userPattern, options) {
        const scores = {};
        options.forEach(option => {
            // 基於用戶偏好特徵計算分數
            const preferenceScore = userPattern.preferredFeatures.includes(option) ? 0.8 : 0.3;
            const efficiencyBonus = userPattern.efficiency * 0.2;
            scores[option] = preferenceScore + efficiencyBonus;
        });
        return scores;
    }
    calculateContextBasedScore(contextAnalysis, options) {
        const scores = {};
        options.forEach(option => {
            let score = 0.5;
            // 基於當前視圖調整分數
            if (this.isOptionRelevantToView(option, contextAnalysis.currentView)) {
                score += 0.3;
            }
            // 基於複雜度調整分數
            if (contextAnalysis.complexity > 0.7 && this.isSimpleOption(option)) {
                score += 0.2;
            }
            scores[option] = Math.min(score, 1);
        });
        return scores;
    }
    calculateTimeBasedScore(hour, options) {
        const scores = {};
        options.forEach(option => {
            let score = 0.5;
            // 基於時間調整分數
            if (hour >= 9 && hour <= 17) {
                // 工作時間，偏好效率工具
                if (this.isEfficiencyTool(option)) {
                    score += 0.2;
                }
            }
            else {
                // 非工作時間，偏好簡單功能
                if (this.isSimpleOption(option)) {
                    score += 0.2;
                }
            }
            scores[option] = score;
        });
        return scores;
    }
    getHistoricalSuccessRate(decision) {
        const relevantDecisions = this.decisionHistory.filter(d => d.decision === decision);
        if (relevantDecisions.length === 0)
            return 0.5;
        const avgConfidence = relevantDecisions.reduce((sum, d) => sum + d.confidence, 0) / relevantDecisions.length;
        return avgConfidence;
    }
    generateLearningKey(interaction) {
        return `${interaction.role}_${interaction.type}_${interaction.element}`;
    }
    analyzeInteractionPatterns(interactions) {
        // 分析交互模式
        const patterns = {
            frequency: {},
            sequences: [],
            timing: {}
        };
        // 計算頻率
        interactions.forEach(interaction => {
            const key = `${interaction.type}_${interaction.element}`;
            patterns.frequency[key] = (patterns.frequency[key] || 0) + 1;
        });
        return patterns;
    }
    updateUserPattern(userId, interaction) {
        const key = `${userId}_${interaction.role}`;
        const pattern = this.userPatterns.get(key) || {
            preferredFeatures: [],
            averageSessionTime: 0,
            commonWorkflows: [],
            efficiency: 0.5
        };
        // 更新偏好特徵
        if (!pattern.preferredFeatures.includes(interaction.element)) {
            pattern.preferredFeatures.push(interaction.element);
        }
        this.userPatterns.set(key, pattern);
    }
    calculateCpuUsage() {
        // 模擬 CPU 使用率計算
        return Math.random() * 10; // 0-10%
    }
    calculateMemoryUsage() {
        // 模擬內存使用率計算
        return Math.random() * 50 + 20; // 20-70MB
    }
    getAverageResponseTime() {
        if (this.decisionHistory.length === 0)
            return 0;
        const totalTime = this.decisionHistory.reduce((sum, decision) => {
            return sum + (decision.context.processingTime || 0);
        }, 0);
        return totalTime / this.decisionHistory.length;
    }
    getAdminPreference(option) {
        const adminPreferences = {
            'system_monitor': 0.9,
            'user_management': 0.8,
            'settings': 0.7,
            'logs': 0.8,
            'performance': 0.9
        };
        return adminPreferences[option] || 0.3;
    }
    getDeveloperPreference(option) {
        const devPreferences = {
            'code_analysis': 0.9,
            'debugging': 0.8,
            'testing': 0.7,
            'documentation': 0.6,
            'collaboration': 0.7
        };
        return devPreferences[option] || 0.4;
    }
    getUserPreference(option) {
        const userPreferences = {
            'simple_interface': 0.9,
            'help': 0.8,
            'basic_features': 0.8,
            'tutorials': 0.7
        };
        return userPreferences[option] || 0.5;
    }
    isOptionRelevantToView(option, view) {
        const relevanceMap = {
            'dashboard': ['overview', 'status', 'quick_actions'],
            'editor': ['code_analysis', 'formatting', 'suggestions'],
            'chat': ['send_message', 'clear_history', 'settings'],
            'settings': ['preferences', 'configuration', 'reset']
        };
        return relevanceMap[view]?.includes(option) || false;
    }
    isSimpleOption(option) {
        const simpleOptions = ['help', 'basic_features', 'simple_interface', 'tutorials'];
        return simpleOptions.includes(option);
    }
    isEfficiencyTool(option) {
        const efficiencyTools = ['shortcuts', 'automation', 'batch_operations', 'quick_actions'];
        return efficiencyTools.includes(option);
    }
}
exports.SmartUIDecisionEngine = SmartUIDecisionEngine;
//# sourceMappingURL=DecisionEngine.js.map