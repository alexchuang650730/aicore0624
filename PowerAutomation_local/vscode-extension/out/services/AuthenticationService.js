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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthenticationService = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
class AuthenticationService {
    constructor(context) {
        this._currentUser = null;
        this._isAuthenticated = false;
        this._authProviders = [
            // 用戶登錄方式
            {
                id: 'github',
                name: 'GitHub 登錄',
                icon: '🐙',
                color: '#24292e',
                description: '使用 GitHub 帳號登錄',
                category: 'user'
            },
            {
                id: 'google',
                name: 'Google 登錄',
                icon: '🔍',
                color: '#db4437',
                description: '使用 Google 帳號登錄',
                category: 'user'
            },
            {
                id: 'microsoft',
                name: 'Microsoft 登錄',
                icon: '🪟',
                color: '#00a1f1',
                description: '使用 Microsoft 帳號登錄',
                category: 'user'
            },
            {
                id: 'email',
                name: '郵箱登錄',
                icon: '📧',
                color: '#007bff',
                description: '使用郵箱和密碼登錄',
                category: 'user'
            },
            // 高級用戶登錄方式
            {
                id: 'apikey',
                name: 'API Key 登錄',
                icon: '🔑',
                color: '#ff6b35',
                description: '使用 API Key 登錄（開發者/管理員）',
                category: 'advanced'
            }
        ];
        this._context = context;
        this._loadStoredUser();
    }
    // 獲取用戶類型從 API Key
    _getUserTypeFromApiKey(apiKey) {
        if (apiKey.startsWith('admin_'))
            return 'admin';
        if (apiKey.startsWith('dev_'))
            return 'developer';
        if (apiKey.startsWith('user_'))
            return 'user';
        throw new Error('無效的 API Key 格式');
    }
    // 獲取界面類型
    _getInterfaceType(userType) {
        return userType === 'user' ? 'user' : 'advanced';
    }
    // 獲取角色權限
    _getRolePermissions(userType) {
        const permissions = {
            admin: [
                'all-features',
                'user-management',
                'server-management',
                'system-config',
                'analytics',
                'debug-tools',
                'api-access',
                'advanced-chat',
                'file-management',
                'history',
                'team-management',
                'custom-integration'
            ],
            developer: [
                'api-access',
                'debug-tools',
                'advanced-chat',
                'local-mode',
                'smartinvention',
                'code-analysis',
                'file-management',
                'history',
                'advanced-settings'
            ],
            user: [
                'basic-chat',
                'file-management',
                'history',
                'basic-settings'
            ]
        };
        return permissions[userType] || permissions.user;
    }
    // 登錄方法
    async login(provider, credentials) {
        try {
            let user;
            switch (provider) {
                case 'apikey':
                    user = await this._loginWithApiKey(credentials.apiKey, credentials.endpoint);
                    break;
                case 'github':
                case 'google':
                case 'microsoft':
                    user = await this._loginWithOAuth(provider);
                    break;
                case 'email':
                    user = await this._loginWithEmail(credentials.email, credentials.password);
                    break;
                default:
                    throw new Error(`不支援的登錄方式: ${provider}`);
            }
            this._currentUser = user;
            this._isAuthenticated = true;
            // 保存用戶信息
            await this._saveUser(user);
            // 設置 VS Code 上下文
            await vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', true);
            await vscode.commands.executeCommand('setContext', 'powerautomation.userType', user.userType);
            await vscode.commands.executeCommand('setContext', 'powerautomation.interfaceType', user.interfaceType);
            return user;
        }
        catch (error) {
            throw new Error(`登錄失敗: ${error}`);
        }
    }
    // API Key 登錄
    async _loginWithApiKey(apiKey, endpoint) {
        // 驗證 API Key 格式
        const userType = this._getUserTypeFromApiKey(apiKey);
        const interfaceType = this._getInterfaceType(userType);
        // 如果提供了端點，測試連接
        if (endpoint) {
            try {
                const response = await axios_1.default.post(`${endpoint}/api/auth/verify`, {}, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`
                    }
                });
                if (response.status !== 200) {
                    throw new Error('API Key驗證失敗');
                }
                const userData = response.data;
                return {
                    id: userData.id || `${userType}_${apiKey.slice(-8)}`,
                    username: userData.username || this._getDefaultUsername(userType),
                    email: userData.email || this._getDefaultEmail(userType),
                    avatar: userData.avatar,
                    provider: 'apikey',
                    subscription: userData.subscription || this._getDefaultSubscription(userType),
                    userType: userType,
                    role: userType,
                    credits: userData.credits || this._getDefaultCredits(userType),
                    lastLogin: new Date(),
                    permissions: this._getRolePermissions(userType),
                    interfaceType: interfaceType
                };
            }
            catch (error) {
                throw new Error(`API Key驗證失敗: ${error}`);
            }
        }
        else {
            // 本地模式
            return {
                id: `${userType}_${apiKey.slice(-8)}`,
                username: this._getDefaultUsername(userType),
                email: this._getDefaultEmail(userType),
                provider: 'apikey',
                subscription: this._getDefaultSubscription(userType),
                userType: userType,
                role: userType,
                credits: this._getDefaultCredits(userType),
                lastLogin: new Date(),
                permissions: this._getRolePermissions(userType),
                interfaceType: interfaceType
            };
        }
    }
    // OAuth 登錄（用戶界面）
    async _loginWithOAuth(provider) {
        // 模擬 OAuth 登錄，實際應該打開瀏覽器進行 OAuth 流程
        const userId = await this._generateUserId();
        return {
            id: userId,
            username: `${provider}_user`,
            email: `user@${provider}.com`,
            provider: provider,
            subscription: 'free',
            userType: 'user',
            role: 'user',
            credits: 1000,
            lastLogin: new Date(),
            permissions: this._getRolePermissions('user'),
            interfaceType: 'user'
        };
    }
    // 郵箱登錄（用戶界面）
    async _loginWithEmail(email, password) {
        // 模擬郵箱登錄驗證
        if (!email || !password) {
            throw new Error('請輸入郵箱和密碼');
        }
        const userId = await this._generateUserId();
        return {
            id: userId,
            username: email.split('@')[0],
            email: email,
            provider: 'email',
            subscription: 'free',
            userType: 'user',
            role: 'user',
            credits: 1000,
            lastLogin: new Date(),
            permissions: this._getRolePermissions('user'),
            interfaceType: 'user'
        };
    }
    // 生成用戶 ID 和對應的 user_ API Key
    async _generateUserId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 18);
        return `user_${timestamp}_${random}`;
    }
    // 獲取默認用戶名
    _getDefaultUsername(userType) {
        const names = {
            admin: 'System Administrator',
            developer: 'Developer',
            user: 'User'
        };
        return names[userType];
    }
    // 獲取默認郵箱
    _getDefaultEmail(userType) {
        const emails = {
            admin: 'admin@powerautomation.ai',
            developer: 'developer@powerautomation.ai',
            user: 'user@powerautomation.ai'
        };
        return emails[userType];
    }
    // 獲取默認訂閱
    _getDefaultSubscription(userType) {
        const subscriptions = {
            admin: 'enterprise',
            developer: 'pro',
            user: 'free'
        };
        return subscriptions[userType];
    }
    // 獲取默認積分
    _getDefaultCredits(userType) {
        const credits = {
            admin: 999999,
            developer: 10000,
            user: 1000
        };
        return credits[userType];
    }
    // 登出
    async logout() {
        this._currentUser = null;
        this._isAuthenticated = false;
        // 清除存儲的用戶信息
        await this._context.secrets.delete('powerautomation.user');
        // 清除 VS Code 上下文
        await vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', false);
        await vscode.commands.executeCommand('setContext', 'powerautomation.userType', undefined);
        await vscode.commands.executeCommand('setContext', 'powerautomation.interfaceType', undefined);
    }
    // 檢查是否已認證
    isAuthenticated() {
        return this._isAuthenticated && this._currentUser !== null;
    }
    // 獲取當前用戶
    getCurrentUser() {
        return this._currentUser;
    }
    // 獲取用戶類型
    getUserType() {
        return this._currentUser?.userType || null;
    }
    // 獲取界面類型
    getInterfaceType() {
        return this._currentUser?.interfaceType || null;
    }
    // 獲取用戶角色
    getUserRole() {
        return this._currentUser?.role || null;
    }
    // 檢查權限
    hasPermission(permission) {
        if (!this._currentUser)
            return false;
        return this._currentUser.permissions.includes(permission) ||
            this._currentUser.permissions.includes('all-features');
    }
    // 獲取認證提供者
    getAuthProviders(category) {
        if (category) {
            return this._authProviders.filter(provider => provider.category === category);
        }
        return this._authProviders;
    }
    // 獲取 UI 配置
    getUIConfiguration() {
        if (!this._currentUser) {
            return {
                sidebar: [],
                features: [],
                theme: 'default',
                layout: 'minimal',
                interfaceType: 'user'
            };
        }
        const { userType, interfaceType } = this._currentUser;
        if (interfaceType === 'advanced') {
            return {
                sidebar: ['dashboard', 'chat', 'repository', 'debug', 'management'],
                features: this._currentUser.permissions,
                theme: 'professional',
                layout: 'advanced',
                interfaceType: 'advanced'
            };
        }
        else {
            return {
                sidebar: ['chat', 'files', 'history'],
                features: this._currentUser.permissions,
                theme: 'simple',
                layout: 'minimal',
                interfaceType: 'user'
            };
        }
    }
    // 保存用戶信息
    async _saveUser(user) {
        await this._context.secrets.store('powerautomation.user', JSON.stringify(user));
    }
    // 加載存儲的用戶信息
    async _loadStoredUser() {
        try {
            const storedUser = await this._context.secrets.get('powerautomation.user');
            if (storedUser) {
                this._currentUser = JSON.parse(storedUser);
                this._isAuthenticated = true;
                // 設置 VS Code 上下文
                await vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', true);
                await vscode.commands.executeCommand('setContext', 'powerautomation.userType', this._currentUser?.userType);
                await vscode.commands.executeCommand('setContext', 'powerautomation.interfaceType', this._currentUser?.interfaceType);
            }
        }
        catch (error) {
            console.error('加載用戶信息失敗:', error);
        }
    }
    // 發送手機驗證碼
    async sendPhoneVerificationCode(phone) {
        // 模擬發送驗證碼
        console.log(`發送驗證碼到 ${phone}`);
    }
    // 重置密碼
    async resetPassword(email) {
        // 模擬重置密碼
        console.log(`發送重置密碼郵件到 ${email}`);
    }
}
exports.AuthenticationService = AuthenticationService;
//# sourceMappingURL=AuthenticationService.js.map