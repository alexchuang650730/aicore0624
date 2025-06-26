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
exports.AuthenticationService = void 0;
const vscode = __importStar(require("vscode"));
class AuthenticationService {
    constructor() {
        this._currentUser = null;
        this._isAuthenticated = false;
        this._authProviders = [
            {
                id: 'email',
                name: '郵箱登錄',
                icon: '📧',
                color: '#4285f4',
                description: '使用郵箱和密碼登錄'
            },
            {
                id: 'github',
                name: 'GitHub',
                icon: '🐙',
                color: '#24292e',
                description: '使用GitHub帳號登錄'
            },
            {
                id: 'google',
                name: 'Google',
                icon: '🔍',
                color: '#db4437',
                description: '使用Google帳號登錄'
            },
            {
                id: 'microsoft',
                name: 'Microsoft',
                icon: '🪟',
                color: '#00a1f1',
                description: '使用Microsoft帳號登錄'
            },
            {
                id: 'phone',
                name: '手機號',
                icon: '📱',
                color: '#25d366',
                description: '使用手機號和驗證碼登錄'
            },
            {
                id: 'apikey',
                name: 'API Key',
                icon: '🔑',
                color: '#ff6b35',
                description: '使用API密鑰登錄（開發者）'
            }
        ];
        this._loadStoredAuth();
    }
    async login(provider, credentials) {
        try {
            let user;
            switch (provider) {
                case 'email':
                    user = await this._loginWithEmail(credentials.email, credentials.password);
                    break;
                case 'github':
                    user = await this._loginWithGitHub();
                    break;
                case 'google':
                    user = await this._loginWithGoogle();
                    break;
                case 'microsoft':
                    user = await this._loginWithMicrosoft();
                    break;
                case 'phone':
                    user = await this._loginWithPhone(credentials.phone, credentials.code);
                    break;
                case 'apikey':
                    user = await this._loginWithApiKey(credentials.apiKey);
                    break;
                default:
                    throw new Error('不支持的登錄方式');
            }
            this._currentUser = user;
            this._isAuthenticated = true;
            this._saveAuth();
            vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', true);
            return user;
        }
        catch (error) {
            throw new Error(`登錄失敗: ${error}`);
        }
    }
    async register(provider, userData) {
        try {
            let user;
            switch (provider) {
                case 'email':
                    user = await this._registerWithEmail(userData);
                    break;
                case 'github':
                    user = await this._registerWithGitHub();
                    break;
                case 'google':
                    user = await this._registerWithGoogle();
                    break;
                case 'microsoft':
                    user = await this._registerWithMicrosoft();
                    break;
                case 'phone':
                    user = await this._registerWithPhone(userData);
                    break;
                default:
                    throw new Error('不支持的註冊方式');
            }
            this._currentUser = user;
            this._isAuthenticated = true;
            this._saveAuth();
            vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', true);
            return user;
        }
        catch (error) {
            throw new Error(`註冊失敗: ${error}`);
        }
    }
    async logout() {
        this._currentUser = null;
        this._isAuthenticated = false;
        this._clearStoredAuth();
        vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', false);
    }
    getCurrentUser() {
        return this._currentUser;
    }
    isAuthenticated() {
        return this._isAuthenticated;
    }
    getAuthProviders() {
        return this._authProviders;
    }
    async _loginWithEmail(email, password) {
        // 模擬API調用
        await this._delay(1000);
        if (email === 'demo@powerautomation.ai' && password === 'demo123') {
            return {
                id: 'user_001',
                username: 'Demo User',
                email: email,
                avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=demo',
                provider: 'email',
                subscription: 'pro',
                credits: 2847,
                lastLogin: new Date()
            };
        }
        throw new Error('郵箱或密碼錯誤');
    }
    async _loginWithGitHub() {
        // 使用VSCode的GitHub認證
        const session = await vscode.authentication.getSession('github', ['user:email'], { createIfNone: true });
        return {
            id: `github_${session.account.id}`,
            username: session.account.label,
            email: session.account.id + '@github.local',
            avatar: `https://github.com/${session.account.label}.png`,
            provider: 'github',
            subscription: 'free',
            credits: 100,
            lastLogin: new Date()
        };
    }
    async _loginWithGoogle() {
        // 模擬Google OAuth流程
        await this._delay(1500);
        return {
            id: 'google_demo',
            username: 'Google User',
            email: 'user@gmail.com',
            avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=google',
            provider: 'google',
            subscription: 'free',
            credits: 50,
            lastLogin: new Date()
        };
    }
    async _loginWithMicrosoft() {
        // 使用VSCode的Microsoft認證
        try {
            const session = await vscode.authentication.getSession('microsoft', ['user.read'], { createIfNone: true });
            return {
                id: `microsoft_${session.account.id}`,
                username: session.account.label,
                email: session.account.id,
                avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=microsoft',
                provider: 'microsoft',
                subscription: 'free',
                credits: 100,
                lastLogin: new Date()
            };
        }
        catch (error) {
            throw new Error('Microsoft登錄失敗');
        }
    }
    async _loginWithPhone(phone, code) {
        // 模擬手機驗證
        await this._delay(800);
        if (code === '123456') {
            return {
                id: `phone_${phone}`,
                username: `用戶${phone.slice(-4)}`,
                email: `${phone}@phone.local`,
                provider: 'phone',
                subscription: 'free',
                credits: 20,
                lastLogin: new Date()
            };
        }
        throw new Error('驗證碼錯誤');
    }
    async _loginWithApiKey(apiKey) {
        // 模擬API Key驗證
        await this._delay(500);
        if (apiKey.startsWith('pa_') && apiKey.length === 32) {
            return {
                id: `api_${apiKey.slice(-8)}`,
                username: 'API User',
                email: 'api@powerautomation.ai',
                provider: 'apikey',
                subscription: 'enterprise',
                credits: 10000,
                lastLogin: new Date()
            };
        }
        throw new Error('無效的API Key');
    }
    async _registerWithEmail(userData) {
        await this._delay(1200);
        return {
            id: `user_${Date.now()}`,
            username: userData.username,
            email: userData.email,
            provider: 'email',
            subscription: 'free',
            credits: 100,
            lastLogin: new Date()
        };
    }
    async _registerWithGitHub() {
        return this._loginWithGitHub();
    }
    async _registerWithGoogle() {
        return this._loginWithGoogle();
    }
    async _registerWithMicrosoft() {
        return this._loginWithMicrosoft();
    }
    async _registerWithPhone(userData) {
        await this._delay(1000);
        return {
            id: `phone_${userData.phone}`,
            username: userData.username || `用戶${userData.phone.slice(-4)}`,
            email: `${userData.phone}@phone.local`,
            provider: 'phone',
            subscription: 'free',
            credits: 50,
            lastLogin: new Date()
        };
    }
    _loadStoredAuth() {
        try {
            const stored = vscode.workspace.getConfiguration('powerautomation').get('storedAuth');
            if (stored) {
                const authData = JSON.parse(stored);
                this._currentUser = authData.user;
                this._isAuthenticated = authData.authenticated;
                if (this._isAuthenticated) {
                    vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', true);
                }
            }
        }
        catch (error) {
            console.error('Failed to load stored auth:', error);
        }
    }
    _saveAuth() {
        try {
            const authData = {
                user: this._currentUser,
                authenticated: this._isAuthenticated,
                timestamp: new Date().toISOString()
            };
            vscode.workspace.getConfiguration('powerautomation')
                .update('storedAuth', JSON.stringify(authData), vscode.ConfigurationTarget.Global);
        }
        catch (error) {
            console.error('Failed to save auth:', error);
        }
    }
    _clearStoredAuth() {
        try {
            vscode.workspace.getConfiguration('powerautomation')
                .update('storedAuth', undefined, vscode.ConfigurationTarget.Global);
        }
        catch (error) {
            console.error('Failed to clear stored auth:', error);
        }
    }
    _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    async sendPhoneVerificationCode(phone) {
        // 模擬發送驗證碼
        await this._delay(500);
        console.log(`驗證碼已發送到 ${phone}`);
    }
    async resetPassword(email) {
        // 模擬重置密碼
        await this._delay(800);
        console.log(`密碼重置郵件已發送到 ${email}`);
    }
    async updateProfile(updates) {
        if (!this._currentUser) {
            throw new Error('用戶未登錄');
        }
        this._currentUser = { ...this._currentUser, ...updates };
        this._saveAuth();
        return this._currentUser;
    }
    async getSubscriptionInfo() {
        if (!this._currentUser) {
            throw new Error('用戶未登錄');
        }
        return {
            plan: this._currentUser.subscription,
            credits: this._currentUser.credits,
            features: this._getSubscriptionFeatures(this._currentUser.subscription),
            nextBilling: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
        };
    }
    _getSubscriptionFeatures(plan) {
        switch (plan) {
            case 'free':
                return ['基礎OCR', '100積分/月', '社區支持'];
            case 'pro':
                return ['高級OCR', '1000積分/月', '優先支持', 'API訪問'];
            case 'enterprise':
                return ['企業OCR', '無限積分', '專屬支持', '私有部署', '自定義集成'];
            default:
                return [];
        }
    }
}
exports.AuthenticationService = AuthenticationService;
//# sourceMappingURL=AuthenticationService.js.map