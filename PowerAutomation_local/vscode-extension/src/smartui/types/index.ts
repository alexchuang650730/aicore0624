/**
 * SmartUI Fusion 類型定義
 * 整合 AG-UI 協議、Stagewise 調試、LiveKit 通信的核心類型
 */

// 用戶角色枚舉
export enum UserRole {
    ADMIN = 'admin',
    DEVELOPER = 'developer', 
    USER = 'user'
}

// AG-UI 協議相關類型
export interface AGUIEvent {
    type: string;
    source: string;
    target: string;
    data: any;
    timestamp: number;
}

export interface AGUIComponent {
    id: string;
    type: string;
    props: Record<string, any>;
    state: Record<string, any>;
    children?: AGUIComponent[];
}

// Stagewise 調試相關類型
export interface StagewiseDebugInfo {
    componentId: string;
    elementType: string;
    properties: Record<string, any>;
    performance: {
        renderTime: number;
        updateTime: number;
        memoryUsage: number;
    };
    interactions: UserInteraction[];
}

// LiveKit 實時通信類型
export interface LiveKitMessage {
    messageId: string;
    type: 'state_sync' | 'user_action' | 'system_update';
    payload: any;
    sender: string;
    timestamp: number;
}

// 用戶交互類型
export interface UserInteraction {
    id: string;
    type: 'click' | 'input' | 'scroll' | 'hover' | 'keypress';
    element: string;
    timestamp: number;
    context: Record<string, any>;
    role: UserRole;
}

// 用戶行為分析結果
export interface UserBehaviorAnalysis {
    userId: string;
    role: UserRole;
    patterns: {
        mostUsedFeatures: string[];
        averageSessionTime: number;
        preferredLayout: string;
        efficiency: number; // 0-1
    };
    preferences: {
        theme: string;
        language: string;
        shortcuts: Record<string, string>;
    };
    recommendations: Recommendation[];
}

// 推薦建議
export interface Recommendation {
    id: string;
    type: 'feature' | 'shortcut' | 'layout' | 'workflow';
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
    action?: () => void;
}

// 決策引擎結果
export interface DecisionResult {
    decision: string;
    confidence: number; // 0-1
    reasoning: string[];
    alternatives: string[];
    context: Record<string, any>;
}

// SmartUI 狀態
export interface SmartUIState {
    currentRole: UserRole;
    userPreferences: UserPreferences;
    uiLayout: UILayoutState;
    analysisResults: AnalysisResult[];
    systemStatus: SystemStatus;
    activeComponents: AGUIComponent[];
    debugInfo?: StagewiseDebugInfo[];
}

// 用戶偏好設置
export interface UserPreferences {
    role: UserRole;
    theme: 'light' | 'dark' | 'auto';
    language: string;
    layout: {
        sidebarWidth: number;
        panelHeight: number;
        showMinimap: boolean;
    };
    features: {
        autoSave: boolean;
        smartSuggestions: boolean;
        realTimeAnalysis: boolean;
    };
    shortcuts: Record<string, string>;
}

// UI 布局狀態
export interface UILayoutState {
    activeView: string;
    visiblePanels: string[];
    componentStates: Record<string, any>;
    responsiveBreakpoint: 'mobile' | 'tablet' | 'desktop';
}

// 分析結果
export interface AnalysisResult {
    id: string;
    type: 'requirement' | 'code' | 'performance' | 'quality';
    content: string;
    result: any;
    confidence: number;
    timestamp: number;
    role: UserRole;
}

// 系統狀態
export interface SystemStatus {
    health: 'healthy' | 'warning' | 'error';
    performance: {
        cpu: number;
        memory: number;
        responseTime: number;
    };
    services: {
        claude: 'connected' | 'disconnected' | 'error';
        mcp: 'connected' | 'disconnected' | 'error';
        livekit: 'connected' | 'disconnected' | 'error';
    };
    lastUpdate: number;
}

// Claude SDK 相關類型
export interface ClaudeRequest {
    id: string;
    type: 'analysis' | 'generation' | 'review' | 'explanation';
    content: string;
    role: UserRole;
    context: Record<string, any>;
}

export interface ClaudeResponse {
    id: string;
    requestId: string;
    success: boolean;
    result?: any;
    error?: string;
    processingTime: number;
    confidence?: number;
}

// 角色配置
export interface RoleConfig {
    role: UserRole;
    apiKey: string;
    permissions: Permission[];
    uiConfig: UIConfig;
    features: FeatureConfig[];
}

export interface Permission {
    resource: string;
    actions: string[];
}

export interface UIConfig {
    theme: string;
    layout: string;
    visibleComponents: string[];
    defaultView: string;
}

export interface FeatureConfig {
    name: string;
    enabled: boolean;
    config: Record<string, any>;
}

// 事件類型
export type SmartUIEvent = 
    | { type: 'ROLE_CHANGED'; payload: { newRole: UserRole; oldRole: UserRole } }
    | { type: 'USER_ACTION'; payload: UserInteraction }
    | { type: 'ANALYSIS_COMPLETE'; payload: AnalysisResult }
    | { type: 'SYSTEM_STATUS_UPDATE'; payload: SystemStatus }
    | { type: 'PREFERENCE_UPDATED'; payload: Partial<UserPreferences> }
    | { type: 'COMPONENT_MOUNTED'; payload: { componentId: string; component: AGUIComponent } }
    | { type: 'COMPONENT_UNMOUNTED'; payload: { componentId: string } }
    | { type: 'LIVEKIT_MESSAGE'; payload: LiveKitMessage };

// 智能組件接口
export interface SmartComponent {
    id: string;
    type: string;
    render(role: UserRole, context: any): any;
    handleEvent(event: SmartUIEvent): void;
    updateFromAnalysis(analysis: AnalysisResult): void;
    getDebugInfo(): StagewiseDebugInfo;
}

// 服務接口
export interface SmartUIService {
    initialize(): Promise<boolean>;
    destroy(): Promise<void>;
    getStatus(): SystemStatus;
}

export interface DecisionEngine extends SmartUIService {
    makeDecision(context: any, options: string[]): Promise<DecisionResult>;
    learn(interaction: UserInteraction, outcome: any): void;
}

export interface UserAnalyzer extends SmartUIService {
    analyzeUser(userId: string): Promise<UserBehaviorAnalysis>;
    trackInteraction(interaction: UserInteraction): void;
    getRecommendations(userId: string): Promise<Recommendation[]>;
}

export interface ClaudeService extends SmartUIService {
    sendRequest(request: ClaudeRequest): Promise<ClaudeResponse>;
    getApiKey(role: UserRole): string;
}

export interface LiveKitService extends SmartUIService {
    connect(): Promise<boolean>;
    disconnect(): Promise<void>;
    sendMessage(message: LiveKitMessage): Promise<void>;
    onMessage(callback: (message: LiveKitMessage) => void): void;
}

