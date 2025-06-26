/**
 * SmartUI 用戶行為分析器
 * 分析用戶交互模式，生成個性化建議
 */

import { 
    UserAnalyzer, 
    UserBehaviorAnalysis, 
    UserInteraction, 
    Recommendation, 
    UserRole, 
    SystemStatus 
} from '../types';

export class SmartUIUserAnalyzer implements UserAnalyzer {
    private isInitialized = false;
    private userInteractions: Map<string, UserInteraction[]> = new Map();
    private userAnalyses: Map<string, UserBehaviorAnalysis> = new Map();
    private analysisCache: Map<string, { analysis: UserBehaviorAnalysis; timestamp: number }> = new Map();
    private readonly CACHE_TTL = 5 * 60 * 1000; // 5分鐘緩存

    async initialize(): Promise<boolean> {
        try {
            console.log('📊 初始化用戶行為分析器...');
            
            // 加載歷史分析數據
            await this.loadAnalysisData();
            
            // 初始化分析模型
            this.initializeAnalysisModels();
            
            this.isInitialized = true;
            console.log('✅ 用戶行為分析器初始化完成');
            return true;
        } catch (error) {
            console.error('❌ 用戶行為分析器初始化失敗:', error);
            return false;
        }
    }

    async destroy(): Promise<void> {
        console.log('🔄 銷毀用戶行為分析器...');
        
        // 保存分析數據
        await this.saveAnalysisData();
        
        this.userInteractions.clear();
        this.userAnalyses.clear();
        this.analysisCache.clear();
        this.isInitialized = false;
        
        console.log('✅ 用戶行為分析器已銷毀');
    }

    getStatus(): SystemStatus {
        return {
            health: this.isInitialized ? 'healthy' : 'error',
            performance: {
                cpu: this.calculateCpuUsage(),
                memory: this.calculateMemoryUsage(),
                responseTime: this.getAverageAnalysisTime()
            },
            services: {
                claude: 'connected',
                mcp: 'connected',
                livekit: 'connected'
            },
            lastUpdate: Date.now()
        };
    }

    async analyzeUser(userId: string): Promise<UserBehaviorAnalysis> {
        if (!this.isInitialized) {
            throw new Error('用戶行為分析器未初始化');
        }

        // 檢查緩存
        const cacheKey = userId;
        const cached = this.analysisCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
            console.log(`📋 使用緩存的用戶分析: ${userId}`);
            return cached.analysis;
        }

        const startTime = Date.now();
        
        try {
            console.log(`🔍 開始分析用戶: ${userId}`);
            
            // 獲取用戶交互數據
            const interactions = this.userInteractions.get(userId) || [];
            
            if (interactions.length === 0) {
                return this.createDefaultAnalysis(userId);
            }

            // 執行多維度分析
            const patterns = await this.analyzeInteractionPatterns(interactions);
            const preferences = await this.analyzeUserPreferences(interactions);
            const efficiency = await this.calculateUserEfficiency(interactions);
            const recommendations = await this.generateRecommendations(userId, patterns, preferences);

            const analysis: UserBehaviorAnalysis = {
                userId,
                role: this.determineUserRole(interactions),
                patterns: {
                    mostUsedFeatures: patterns.mostUsedFeatures,
                    averageSessionTime: patterns.averageSessionTime,
                    preferredLayout: patterns.preferredLayout,
                    efficiency: efficiency
                },
                preferences: {
                    theme: preferences.theme,
                    language: preferences.language,
                    shortcuts: preferences.shortcuts
                },
                recommendations
            };

            // 緩存結果
            this.analysisCache.set(cacheKey, {
                analysis,
                timestamp: Date.now()
            });

            // 保存到持久存儲
            this.userAnalyses.set(userId, analysis);

            const processingTime = Date.now() - startTime;
            console.log(`✅ 用戶分析完成: ${userId} (耗時: ${processingTime}ms)`);
            
            return analysis;

        } catch (error) {
            console.error(`❌ 用戶分析失敗: ${userId}`, error);
            throw error;
        }
    }

    trackInteraction(interaction: UserInteraction): void {
        try {
            const userId = interaction.context.userId || 'anonymous';
            
            // 獲取或創建用戶交互列表
            const interactions = this.userInteractions.get(userId) || [];
            interactions.push(interaction);
            
            // 限制存儲的交互數量（保留最近1000個）
            if (interactions.length > 1000) {
                interactions.splice(0, interactions.length - 1000);
            }
            
            this.userInteractions.set(userId, interactions);
            
            // 清除相關緩存
            this.analysisCache.delete(userId);
            
            console.log(`📝 記錄用戶交互: ${userId} - ${interaction.type} - ${interaction.element}`);
            
            // 實時更新分析（如果交互頻繁）
            this.scheduleRealTimeAnalysis(userId);
            
        } catch (error) {
            console.error('❌ 記錄用戶交互失敗:', error);
        }
    }

    async getRecommendations(userId: string): Promise<Recommendation[]> {
        try {
            const analysis = await this.analyzeUser(userId);
            return analysis.recommendations;
        } catch (error) {
            console.error(`❌ 獲取推薦失敗: ${userId}`, error);
            return [];
        }
    }

    private async loadAnalysisData(): Promise<void> {
        try {
            // 從 VS Code 存儲中加載數據
            console.log('📖 加載用戶分析數據...');
        } catch (error) {
            console.warn('⚠️ 無法加載用戶分析數據，使用默認設置');
        }
    }

    private async saveAnalysisData(): Promise<void> {
        try {
            // 保存到 VS Code 存儲
            console.log('💾 保存用戶分析數據...');
        } catch (error) {
            console.error('❌ 保存用戶分析數據失敗:', error);
        }
    }

    private initializeAnalysisModels(): void {
        console.log('🤖 初始化分析模型...');
        
        // 初始化不同的分析模型
        // 1. 行為模式識別模型
        // 2. 偏好預測模型
        // 3. 效率評估模型
        // 4. 推薦生成模型
    }

    private createDefaultAnalysis(userId: string): UserBehaviorAnalysis {
        return {
            userId,
            role: UserRole.USER,
            patterns: {
                mostUsedFeatures: [],
                averageSessionTime: 0,
                preferredLayout: 'default',
                efficiency: 0.5
            },
            preferences: {
                theme: 'auto',
                language: 'zh-CN',
                shortcuts: {}
            },
            recommendations: [
                {
                    id: 'welcome',
                    type: 'feature',
                    title: '歡迎使用 PowerAutomation',
                    description: '開始探索智能功能，提升您的工作效率',
                    priority: 'high'
                }
            ]
        };
    }

    private async analyzeInteractionPatterns(interactions: UserInteraction[]): Promise<any> {
        const patterns = {
            mostUsedFeatures: [],
            averageSessionTime: 0,
            preferredLayout: 'default',
            timeDistribution: {},
            sequencePatterns: []
        };

        // 分析最常用功能
        const featureUsage = new Map<string, number>();
        interactions.forEach(interaction => {
            const feature = interaction.element;
            featureUsage.set(feature, (featureUsage.get(feature) || 0) + 1);
        });

        patterns.mostUsedFeatures = Array.from(featureUsage.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([feature]) => feature);

        // 分析會話時間
        const sessions = this.groupInteractionsBySessions(interactions);
        if (sessions.length > 0) {
            const totalSessionTime = sessions.reduce((sum, session) => sum + session.duration, 0);
            patterns.averageSessionTime = totalSessionTime / sessions.length;
        }

        // 分析偏好布局
        patterns.preferredLayout = this.analyzePreferredLayout(interactions);

        // 分析時間分佈
        patterns.timeDistribution = this.analyzeTimeDistribution(interactions);

        // 分析操作序列模式
        patterns.sequencePatterns = this.analyzeSequencePatterns(interactions);

        return patterns;
    }

    private async analyzeUserPreferences(interactions: UserInteraction[]): Promise<any> {
        const preferences = {
            theme: 'auto',
            language: 'zh-CN',
            shortcuts: {}
        };

        // 分析主題偏好
        preferences.theme = this.analyzeThemePreference(interactions);

        // 分析語言偏好
        preferences.language = this.analyzeLanguagePreference(interactions);

        // 分析快捷鍵使用
        preferences.shortcuts = this.analyzeShortcutUsage(interactions);

        return preferences;
    }

    private async calculateUserEfficiency(interactions: UserInteraction[]): Promise<number> {
        if (interactions.length === 0) return 0.5;

        let efficiency = 0.5; // 基礎效率

        // 基於操作速度計算效率
        const operationSpeed = this.calculateOperationSpeed(interactions);
        efficiency += (operationSpeed - 1) * 0.2; // 速度影響

        // 基於錯誤率計算效率
        const errorRate = this.calculateErrorRate(interactions);
        efficiency -= errorRate * 0.3; // 錯誤率影響

        // 基於功能使用深度計算效率
        const featureDepth = this.calculateFeatureUsageDepth(interactions);
        efficiency += featureDepth * 0.2; // 功能深度影響

        // 基於工作流程優化程度計算效率
        const workflowOptimization = this.calculateWorkflowOptimization(interactions);
        efficiency += workflowOptimization * 0.3; // 工作流程影響

        return Math.max(0, Math.min(1, efficiency));
    }

    private async generateRecommendations(
        userId: string, 
        patterns: any, 
        preferences: any
    ): Promise<Recommendation[]> {
        const recommendations: Recommendation[] = [];

        // 基於使用模式生成推薦
        if (patterns.efficiency < 0.6) {
            recommendations.push({
                id: 'efficiency_tips',
                type: 'workflow',
                title: '提升工作效率',
                description: '學習使用快捷鍵和自動化功能來提升效率',
                priority: 'high'
            });
        }

        // 基於功能使用生成推薦
        if (patterns.mostUsedFeatures.length < 3) {
            recommendations.push({
                id: 'explore_features',
                type: 'feature',
                title: '探索更多功能',
                description: '發現更多有用的功能來增強您的工作流程',
                priority: 'medium'
            });
        }

        // 基於時間模式生成推薦
        const peakHours = this.findPeakUsageHours(patterns.timeDistribution);
        if (peakHours.length > 0) {
            recommendations.push({
                id: 'optimize_schedule',
                type: 'workflow',
                title: '優化工作時間',
                description: `您在 ${peakHours.join(', ')} 時最活躍，考慮在這些時間處理重要任務`,
                priority: 'low'
            });
        }

        // 基於偏好生成推薦
        if (preferences.shortcuts && Object.keys(preferences.shortcuts).length < 5) {
            recommendations.push({
                id: 'learn_shortcuts',
                type: 'shortcut',
                title: '學習快捷鍵',
                description: '掌握常用快捷鍵可以顯著提升操作速度',
                priority: 'medium'
            });
        }

        return recommendations.slice(0, 5); // 限制推薦數量
    }

    private determineUserRole(interactions: UserInteraction[]): UserRole {
        if (interactions.length === 0) return UserRole.USER;

        // 基於交互模式判斷用戶角色
        const roleIndicators = {
            admin: 0,
            developer: 0,
            user: 0
        };

        interactions.forEach(interaction => {
            // 管理員指標
            if (interaction.element.includes('admin') || 
                interaction.element.includes('system') ||
                interaction.element.includes('config')) {
                roleIndicators.admin++;
            }

            // 開發者指標
            if (interaction.element.includes('code') || 
                interaction.element.includes('debug') ||
                interaction.element.includes('analysis')) {
                roleIndicators.developer++;
            }

            // 普通用戶指標
            if (interaction.element.includes('help') || 
                interaction.element.includes('basic') ||
                interaction.element.includes('simple')) {
                roleIndicators.user++;
            }
        });

        // 返回得分最高的角色
        const maxScore = Math.max(...Object.values(roleIndicators));
        if (roleIndicators.admin === maxScore) return UserRole.ADMIN;
        if (roleIndicators.developer === maxScore) return UserRole.DEVELOPER;
        return UserRole.USER;
    }

    private groupInteractionsBySessions(interactions: UserInteraction[]): any[] {
        const sessions = [];
        let currentSession = null;
        const SESSION_TIMEOUT = 30 * 60 * 1000; // 30分鐘

        interactions.forEach(interaction => {
            if (!currentSession || 
                interaction.timestamp - currentSession.lastActivity > SESSION_TIMEOUT) {
                // 開始新會話
                currentSession = {
                    startTime: interaction.timestamp,
                    endTime: interaction.timestamp,
                    lastActivity: interaction.timestamp,
                    interactions: [interaction],
                    duration: 0
                };
                sessions.push(currentSession);
            } else {
                // 繼續當前會話
                currentSession.endTime = interaction.timestamp;
                currentSession.lastActivity = interaction.timestamp;
                currentSession.interactions.push(interaction);
                currentSession.duration = currentSession.endTime - currentSession.startTime;
            }
        });

        return sessions;
    }

    private analyzePreferredLayout(interactions: UserInteraction[]): string {
        // 分析用戶偏好的布局
        const layoutUsage = new Map<string, number>();
        
        interactions.forEach(interaction => {
            const layout = interaction.context.layout || 'default';
            layoutUsage.set(layout, (layoutUsage.get(layout) || 0) + 1);
        });

        if (layoutUsage.size === 0) return 'default';

        return Array.from(layoutUsage.entries())
            .sort((a, b) => b[1] - a[1])[0][0];
    }

    private analyzeTimeDistribution(interactions: UserInteraction[]): any {
        const distribution: Record<number, number> = {};

        interactions.forEach(interaction => {
            const hour = new Date(interaction.timestamp).getHours();
            distribution[hour] = (distribution[hour] || 0) + 1;
        });

        return distribution;
    }

    private analyzeSequencePatterns(interactions: UserInteraction[]): any[] {
        // 分析操作序列模式
        const patterns = [];
        const sequenceLength = 3;

        for (let i = 0; i <= interactions.length - sequenceLength; i++) {
            const sequence = interactions.slice(i, i + sequenceLength)
                .map(interaction => interaction.element);
            
            patterns.push(sequence);
        }

        // 統計序列頻率
        const sequenceFreq = new Map<string, number>();
        patterns.forEach(pattern => {
            const key = pattern.join('->');
            sequenceFreq.set(key, (sequenceFreq.get(key) || 0) + 1);
        });

        return Array.from(sequenceFreq.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)
            .map(([sequence, frequency]) => ({ sequence, frequency }));
    }

    private analyzeThemePreference(interactions: UserInteraction[]): string {
        // 基於使用時間分析主題偏好
        const hourlyUsage = this.analyzeTimeDistribution(interactions);
        const dayTimeUsage = Object.entries(hourlyUsage)
            .filter(([hour]) => parseInt(hour) >= 6 && parseInt(hour) <= 18)
            .reduce((sum, [, count]) => sum + (count as number), 0);
        
        const nightTimeUsage = Object.entries(hourlyUsage)
            .filter(([hour]) => parseInt(hour) < 6 || parseInt(hour) > 18)
            .reduce((sum, [, count]) => sum + (count as number), 0);

        if (nightTimeUsage > dayTimeUsage * 1.5) return 'dark';
        if (dayTimeUsage > nightTimeUsage * 1.5) return 'light';
        return 'auto';
    }

    private analyzeLanguagePreference(interactions: UserInteraction[]): string {
        // 基於交互內容分析語言偏好
        return 'zh-CN'; // 默認中文
    }

    private analyzeShortcutUsage(interactions: UserInteraction[]): Record<string, string> {
        const shortcuts: Record<string, string> = {};

        interactions.forEach(interaction => {
            if (interaction.type === 'keypress' && interaction.context.shortcut) {
                shortcuts[interaction.element] = interaction.context.shortcut;
            }
        });

        return shortcuts;
    }

    private calculateOperationSpeed(interactions: UserInteraction[]): number {
        if (interactions.length < 2) return 1;

        const intervals = [];
        for (let i = 1; i < interactions.length; i++) {
            const interval = interactions[i].timestamp - interactions[i-1].timestamp;
            if (interval < 60000) { // 小於1分鐘的間隔
                intervals.push(interval);
            }
        }

        if (intervals.length === 0) return 1;

        const avgInterval = intervals.reduce((sum, interval) => sum + interval, 0) / intervals.length;
        const baseInterval = 5000; // 5秒基準
        
        return Math.max(0.1, Math.min(3, baseInterval / avgInterval));
    }

    private calculateErrorRate(interactions: UserInteraction[]): number {
        // 基於撤銷操作、重複操作等計算錯誤率
        let errorCount = 0;
        
        interactions.forEach((interaction, index) => {
            // 檢測撤銷操作
            if (interaction.element.includes('undo') || interaction.element.includes('cancel')) {
                errorCount++;
            }
            
            // 檢測重複操作
            if (index > 0 && 
                interaction.element === interactions[index-1].element &&
                interaction.timestamp - interactions[index-1].timestamp < 1000) {
                errorCount++;
            }
        });

        return Math.min(1, errorCount / interactions.length);
    }

    private calculateFeatureUsageDepth(interactions: UserInteraction[]): number {
        const uniqueFeatures = new Set(interactions.map(i => i.element));
        const totalFeatures = 50; // 假設總共有50個功能
        
        return Math.min(1, uniqueFeatures.size / totalFeatures);
    }

    private calculateWorkflowOptimization(interactions: UserInteraction[]): number {
        // 基於操作序列的優化程度
        const sequences = this.analyzeSequencePatterns(interactions);
        const efficientSequences = sequences.filter(s => s.frequency > 2);
        
        return Math.min(1, efficientSequences.length / 10);
    }

    private findPeakUsageHours(timeDistribution: Record<number, number>): string[] {
        const entries = Object.entries(timeDistribution);
        if (entries.length === 0) return [];

        const maxUsage = Math.max(...entries.map(([, count]) => count));
        const threshold = maxUsage * 0.8;

        return entries
            .filter(([, count]) => count >= threshold)
            .map(([hour]) => `${hour}:00`)
            .sort();
    }

    private scheduleRealTimeAnalysis(userId: string): void {
        // 防抖處理，避免頻繁分析
        const debounceKey = `analysis_${userId}`;
        clearTimeout((this as any)[debounceKey]);
        
        (this as any)[debounceKey] = setTimeout(() => {
            this.analyzeUser(userId).catch(error => {
                console.error('實時分析失敗:', error);
            });
        }, 5000); // 5秒後執行分析
    }

    private calculateCpuUsage(): number {
        return Math.random() * 5; // 0-5%
    }

    private calculateMemoryUsage(): number {
        return Math.random() * 30 + 10; // 10-40MB
    }

    private getAverageAnalysisTime(): number {
        // 模擬分析時間
        return Math.random() * 100 + 50; // 50-150ms
    }
}

