import * as vscode from 'vscode';

export interface UserProfile {
    id: string;
    username: string;
    email: string;
    avatar?: string;
    provider: 'email' | 'github' | 'google' | 'microsoft' | 'phone' | 'apikey';
    subscription: 'free' | 'pro' | 'enterprise';
    credits: number;
    lastLogin: Date;
}

export interface AuthProvider {
    id: string;
    name: string;
    icon: string;
    color: string;
    description: string;
}

export class AuthenticationService {
    private _currentUser: UserProfile | null = null;
    private _isAuthenticated: boolean = false;
    private _authProviders: AuthProvider[] = [
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

    constructor() {
        this._loadStoredAuth();
    }

    public async login(provider: string, credentials: any): Promise<UserProfile> {
        try {
            let user: UserProfile;

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
        } catch (error) {
            throw new Error(`登錄失敗: ${error}`);
        }
    }

    public async register(provider: string, userData: any): Promise<UserProfile> {
        try {
            let user: UserProfile;

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
        } catch (error) {
            throw new Error(`註冊失敗: ${error}`);
        }
    }

    public async logout(): Promise<void> {
        this._currentUser = null;
        this._isAuthenticated = false;
        this._clearStoredAuth();
        vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', false);
    }

    public getCurrentUser(): UserProfile | null {
        return this._currentUser;
    }

    public isAuthenticated(): boolean {
        return this._isAuthenticated;
    }

    public getAuthProviders(): AuthProvider[] {
        return this._authProviders;
    }

    private async _loginWithEmail(email: string, password: string): Promise<UserProfile> {
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

    private async _loginWithGitHub(): Promise<UserProfile> {
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

    private async _loginWithGoogle(): Promise<UserProfile> {
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

    private async _loginWithMicrosoft(): Promise<UserProfile> {
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
        } catch (error) {
            throw new Error('Microsoft登錄失敗');
        }
    }

    private async _loginWithPhone(phone: string, code: string): Promise<UserProfile> {
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

    private async _loginWithApiKey(apiKey: string): Promise<UserProfile> {
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

    private async _registerWithEmail(userData: any): Promise<UserProfile> {
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

    private async _registerWithGitHub(): Promise<UserProfile> {
        return this._loginWithGitHub();
    }

    private async _registerWithGoogle(): Promise<UserProfile> {
        return this._loginWithGoogle();
    }

    private async _registerWithMicrosoft(): Promise<UserProfile> {
        return this._loginWithMicrosoft();
    }

    private async _registerWithPhone(userData: any): Promise<UserProfile> {
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

    private _loadStoredAuth(): void {
        try {
            const stored = vscode.workspace.getConfiguration('powerautomation').get('storedAuth');
            if (stored) {
                const authData = JSON.parse(stored as string);
                this._currentUser = authData.user;
                this._isAuthenticated = authData.authenticated;
                
                if (this._isAuthenticated) {
                    vscode.commands.executeCommand('setContext', 'powerautomation.authenticated', true);
                }
            }
        } catch (error) {
            console.error('Failed to load stored auth:', error);
        }
    }

    private _saveAuth(): void {
        try {
            const authData = {
                user: this._currentUser,
                authenticated: this._isAuthenticated,
                timestamp: new Date().toISOString()
            };
            
            vscode.workspace.getConfiguration('powerautomation')
                .update('storedAuth', JSON.stringify(authData), vscode.ConfigurationTarget.Global);
        } catch (error) {
            console.error('Failed to save auth:', error);
        }
    }

    private _clearStoredAuth(): void {
        try {
            vscode.workspace.getConfiguration('powerautomation')
                .update('storedAuth', undefined, vscode.ConfigurationTarget.Global);
        } catch (error) {
            console.error('Failed to clear stored auth:', error);
        }
    }

    private _delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    public async sendPhoneVerificationCode(phone: string): Promise<void> {
        // 模擬發送驗證碼
        await this._delay(500);
        console.log(`驗證碼已發送到 ${phone}`);
    }

    public async resetPassword(email: string): Promise<void> {
        // 模擬重置密碼
        await this._delay(800);
        console.log(`密碼重置郵件已發送到 ${email}`);
    }

    public async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
        if (!this._currentUser) {
            throw new Error('用戶未登錄');
        }

        this._currentUser = { ...this._currentUser, ...updates };
        this._saveAuth();
        return this._currentUser;
    }

    public async getSubscriptionInfo(): Promise<any> {
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

    private _getSubscriptionFeatures(plan: string): string[] {
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

