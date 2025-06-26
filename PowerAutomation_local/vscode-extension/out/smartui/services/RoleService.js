"use strict";
/**
 * SmartUI 角色管理服務
 * 管理用戶角色、權限和配置
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SmartUIRoleService = void 0;
const types_1 = require("../types");
class SmartUIRoleService {
    constructor() {
        this.isInitialized = false;
        this.currentRole = types_1.UserRole.USER;
        this.roleConfigs = new Map();
        this.eventListeners = [];
    }
    async initialize() {
        try {
            console.log('👥 初始化角色管理服務...');
            // 初始化角色配置
            this.initializeRoleConfigs();
            // 加載用戶偏好
            await this.loadUserPreferences();
            this.isInitialized = true;
            console.log('✅ 角色管理服務初始化完成');
            return true;
        }
        catch (error) {
            console.error('❌ 角色管理服務初始化失敗:', error);
            return false;
        }
    }
    async destroy() {
        console.log('🔄 銷毀角色管理服務...');
        // 保存用戶偏好
        await this.saveUserPreferences();
        this.roleConfigs.clear();
        this.eventListeners = [];
        this.isInitialized = false;
        console.log('✅ 角色管理服務已銷毀');
    }
    getStatus() {
        return {
            health: this.isInitialized ? 'healthy' : 'error',
            performance: {
                cpu: 1,
                memory: 5,
                responseTime: 10
            },
            services: {
                claude: 'connected',
                mcp: 'connected',
                livekit: 'connected'
            },
            lastUpdate: Date.now()
        };
    }
    // 角色管理方法
    getCurrentRole() {
        return this.currentRole;
    }
    async switchRole(newRole) {
        if (!this.isInitialized) {
            throw new Error('角色管理服務未初始化');
        }
        if (!this.roleConfigs.has(newRole)) {
            throw new Error(`未知角色: ${newRole}`);
        }
        const oldRole = this.currentRole;
        this.currentRole = newRole;
        console.log(`🔄 角色切換: ${oldRole} → ${newRole}`);
        // 觸發角色切換事件
        this.emitEvent({
            type: 'ROLE_CHANGED',
            payload: { newRole, oldRole }
        });
        // 保存角色偏好
        await this.saveRolePreference(newRole);
        return true;
    }
    getRoleConfig(role) {
        const targetRole = role || this.currentRole;
        return this.roleConfigs.get(targetRole);
    }
    getAllRoles() {
        return Array.from(this.roleConfigs.keys());
    }
    // 權限檢查
    hasPermission(resource, action, role) {
        const targetRole = role || this.currentRole;
        const config = this.roleConfigs.get(targetRole);
        if (!config)
            return false;
        return config.permissions.some(permission => permission.resource === resource &&
            permission.actions.includes(action));
    }
    getPermissions(role) {
        const targetRole = role || this.currentRole;
        const config = this.roleConfigs.get(targetRole);
        return config?.permissions || [];
    }
    // UI 配置
    getUIConfig(role) {
        const targetRole = role || this.currentRole;
        const config = this.roleConfigs.get(targetRole);
        return config?.uiConfig;
    }
    getVisibleComponents(role) {
        const uiConfig = this.getUIConfig(role);
        return uiConfig?.visibleComponents || [];
    }
    getDefaultView(role) {
        const uiConfig = this.getUIConfig(role);
        return uiConfig?.defaultView || 'dashboard';
    }
    // 功能配置
    getFeatureConfigs(role) {
        const targetRole = role || this.currentRole;
        const config = this.roleConfigs.get(targetRole);
        return config?.features || [];
    }
    isFeatureEnabled(featureName, role) {
        const features = this.getFeatureConfigs(role);
        const feature = features.find(f => f.name === featureName);
        return feature?.enabled || false;
    }
    getFeatureConfig(featureName, role) {
        const features = this.getFeatureConfigs(role);
        const feature = features.find(f => f.name === featureName);
        return feature?.config || {};
    }
    // API Key 管理
    getApiKey(role) {
        const targetRole = role || this.currentRole;
        const config = this.roleConfigs.get(targetRole);
        return config?.apiKey || '';
    }
    // 事件管理
    addEventListener(listener) {
        this.eventListeners.push(listener);
    }
    removeEventListener(listener) {
        const index = this.eventListeners.indexOf(listener);
        if (index > -1) {
            this.eventListeners.splice(index, 1);
        }
    }
    emitEvent(event) {
        this.eventListeners.forEach(listener => {
            try {
                listener(event);
            }
            catch (error) {
                console.error('事件監聽器錯誤:', error);
            }
        });
    }
    // 角色特定的方法
    getAdminFeatures() {
        return [
            'system_monitor',
            'user_management',
            'global_settings',
            'performance_analytics',
            'security_audit',
            'backup_restore',
            'log_viewer',
            'service_control'
        ];
    }
    getDeveloperFeatures() {
        return [
            'code_analysis',
            'claude_integration',
            'debugging_tools',
            'project_management',
            'api_testing',
            'documentation_generator',
            'performance_profiler',
            'collaboration_tools',
            'requirement_analysis',
            'architecture_design'
        ];
    }
    getUserFeatures() {
        return [
            'basic_chat',
            'simple_analysis',
            'help_system',
            'tutorials',
            'basic_settings',
            'feedback_system'
        ];
    }
    initializeRoleConfigs() {
        // Admin 角色配置
        this.roleConfigs.set(types_1.UserRole.ADMIN, {
            role: types_1.UserRole.ADMIN,
            apiKey: 'admin_pth4jG-nVjvGaTZA2URN7SyHu-o7wBaeLOYbMrLMKkc',
            permissions: [
                { resource: 'system', actions: ['read', 'write', 'delete', 'admin'] },
                { resource: 'users', actions: ['read', 'write', 'delete', 'manage'] },
                { resource: 'settings', actions: ['read', 'write', 'admin'] },
                { resource: 'logs', actions: ['read', 'write', 'delete'] },
                { resource: 'services', actions: ['read', 'write', 'restart', 'stop'] }
            ],
            uiConfig: {
                theme: 'admin-dark',
                layout: 'admin-dashboard',
                visibleComponents: [
                    'system-monitor',
                    'user-management',
                    'service-control',
                    'performance-analytics',
                    'security-panel',
                    'log-viewer',
                    'backup-restore',
                    'global-settings'
                ],
                defaultView: 'system-dashboard'
            },
            features: [
                { name: 'system_monitor', enabled: true, config: { refreshInterval: 5000 } },
                { name: 'user_management', enabled: true, config: { bulkOperations: true } },
                { name: 'global_settings', enabled: true, config: { advancedMode: true } },
                { name: 'performance_analytics', enabled: true, config: { realTime: true } },
                { name: 'security_audit', enabled: true, config: { autoScan: true } },
                { name: 'backup_restore', enabled: true, config: { autoBackup: true } },
                { name: 'log_viewer', enabled: true, config: { logLevel: 'debug' } },
                { name: 'service_control', enabled: true, config: { restartPermission: true } }
            ]
        });
        // Developer 角色配置
        this.roleConfigs.set(types_1.UserRole.DEVELOPER, {
            role: types_1.UserRole.DEVELOPER,
            apiKey: 'dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso',
            permissions: [
                { resource: 'code', actions: ['read', 'write', 'analyze', 'generate'] },
                { resource: 'projects', actions: ['read', 'write', 'create', 'manage'] },
                { resource: 'claude', actions: ['read', 'write', 'analyze'] },
                { resource: 'debugging', actions: ['read', 'write', 'execute'] },
                { resource: 'documentation', actions: ['read', 'write', 'generate'] }
            ],
            uiConfig: {
                theme: 'developer-blue',
                layout: 'developer-workspace',
                visibleComponents: [
                    'code-analyzer',
                    'claude-assistant',
                    'project-manager',
                    'debugging-tools',
                    'api-tester',
                    'documentation-generator',
                    'performance-profiler',
                    'collaboration-panel',
                    'requirement-analyzer',
                    'architecture-designer'
                ],
                defaultView: 'development-dashboard'
            },
            features: [
                { name: 'code_analysis', enabled: true, config: { realTimeAnalysis: true } },
                { name: 'claude_integration', enabled: true, config: { advancedFeatures: true } },
                { name: 'debugging_tools', enabled: true, config: { breakpoints: true } },
                { name: 'project_management', enabled: true, config: { gitIntegration: true } },
                { name: 'api_testing', enabled: true, config: { autoGenerate: true } },
                { name: 'documentation_generator', enabled: true, config: { autoUpdate: true } },
                { name: 'performance_profiler', enabled: true, config: { detailedMetrics: true } },
                { name: 'collaboration_tools', enabled: true, config: { realTimeSync: true } },
                { name: 'requirement_analysis', enabled: true, config: { aiAssisted: true } },
                { name: 'architecture_design', enabled: true, config: { visualDesigner: true } }
            ]
        });
        // User 角色配置
        this.roleConfigs.set(types_1.UserRole.USER, {
            role: types_1.UserRole.USER,
            apiKey: 'user_RcmKEIPfGCQrA6sSohzn5NDXYMsS5mkyP9jPhM3llTw',
            permissions: [
                { resource: 'chat', actions: ['read', 'write'] },
                { resource: 'analysis', actions: ['read', 'basic'] },
                { resource: 'help', actions: ['read'] },
                { resource: 'settings', actions: ['read', 'write'] },
                { resource: 'feedback', actions: ['write'] }
            ],
            uiConfig: {
                theme: 'user-friendly',
                layout: 'simple-interface',
                visibleComponents: [
                    'basic-chat',
                    'simple-analyzer',
                    'help-center',
                    'tutorials',
                    'basic-settings',
                    'feedback-form'
                ],
                defaultView: 'user-dashboard'
            },
            features: [
                { name: 'basic_chat', enabled: true, config: { simpleMode: true } },
                { name: 'simple_analysis', enabled: true, config: { guidedMode: true } },
                { name: 'help_system', enabled: true, config: { interactive: true } },
                { name: 'tutorials', enabled: true, config: { stepByStep: true } },
                { name: 'basic_settings', enabled: true, config: { simplified: true } },
                { name: 'feedback_system', enabled: true, config: { anonymous: true } }
            ]
        });
        console.log('🎭 角色配置初始化完成');
    }
    async loadUserPreferences() {
        try {
            // 從 VS Code 存儲中加載用戶偏好
            // 這裡可以從 globalState 加載
            console.log('📖 加載用戶偏好...');
        }
        catch (error) {
            console.warn('⚠️ 無法加載用戶偏好，使用默認設置');
        }
    }
    async saveUserPreferences() {
        try {
            // 保存到 VS Code 存儲
            console.log('💾 保存用戶偏好...');
        }
        catch (error) {
            console.error('❌ 保存用戶偏好失敗:', error);
        }
    }
    async saveRolePreference(role) {
        try {
            // 保存當前角色偏好
            console.log(`💾 保存角色偏好: ${role}`);
        }
        catch (error) {
            console.error('❌ 保存角色偏好失敗:', error);
        }
    }
    // 角色驗證
    validateRole(role) {
        return Object.values(types_1.UserRole).includes(role);
    }
    // 獲取角色顯示名稱
    getRoleDisplayName(role) {
        const displayNames = {
            [types_1.UserRole.ADMIN]: '系統管理員',
            [types_1.UserRole.DEVELOPER]: '開發者',
            [types_1.UserRole.USER]: '用戶'
        };
        return displayNames[role] || role;
    }
    // 獲取角色描述
    getRoleDescription(role) {
        const descriptions = {
            [types_1.UserRole.ADMIN]: '擁有完整的系統管理權限，可以管理用戶、監控系統性能、配置全局設置',
            [types_1.UserRole.DEVELOPER]: '專為開發者和產品經理設計，提供代碼分析、項目管理、AI 輔助開發等功能',
            [types_1.UserRole.USER]: '為最終用戶提供簡化的界面和基礎功能，注重易用性和用戶體驗'
        };
        return descriptions[role] || '';
    }
    // 獲取角色圖標
    getRoleIcon(role) {
        const icons = {
            [types_1.UserRole.ADMIN]: '👑',
            [types_1.UserRole.DEVELOPER]: '👨‍💻',
            [types_1.UserRole.USER]: '👤'
        };
        return icons[role] || '👤';
    }
    // 角色能力檢查
    canAccessFeature(featureName, role) {
        const targetRole = role || this.currentRole;
        const features = this.getFeatureConfigs(targetRole);
        return features.some(f => f.name === featureName && f.enabled);
    }
    canPerformAction(resource, action, role) {
        return this.hasPermission(resource, action, role);
    }
    // 獲取角色統計信息
    getRoleStats() {
        return {
            totalRoles: this.roleConfigs.size,
            currentRole: this.currentRole,
            availableFeatures: this.getFeatureConfigs().length,
            permissions: this.getPermissions().length,
            visibleComponents: this.getVisibleComponents().length
        };
    }
}
exports.SmartUIRoleService = SmartUIRoleService;
//# sourceMappingURL=RoleService.js.map