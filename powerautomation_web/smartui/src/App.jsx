import { useState, useEffect } from 'react'
import GitHubFileExplorer from './components/GitHubFileExplorer'
import CodeEditor from './components/CodeEditor'
import FileManager from './components/FileManager'
import AuthModal from './components/AuthModal'
import mcpService from './services/mcpService'
import useAuth from './hooks/useAuth'
import './App.css'

// 角色权限配置
const ROLE_PERMISSIONS = {
  admin: {
    name: '管理员',
    color: 'text-red-400',
    badge: 'bg-red-500/20 text-red-400',
    permissions: [
      'code_review', 'code_modify', 'directory_manage', 
      'code_delete', 'user_manage', 'system_config',
      'file_manage_full', 'github_manage', 'chat_unlimited',
      'file_upload', 'file_download', 'file_delete',
      'project_create', 'project_delete'
    ]
  },
  developer: {
    name: '開發者',
    color: 'text-blue-400',
    badge: 'bg-blue-500/20 text-blue-400',
    permissions: [
      'code_view', 'code_edit', 'file_create', 'chat_basic',
      'github_browse', 'plugin_connect', 'file_manage_limited',
      'file_upload', 'file_download', 'project_view'
    ]
  },
  user: {
    name: '用戶',
    color: 'text-green-400',
    badge: 'bg-green-500/20 text-green-400',
    permissions: [
      'text_input', 'file_manage_basic', 'code_view_readonly',
      'chat_basic', 'file_download'
    ]
  }
}

// API Key到角色的映射
const API_KEY_ROLES = {
  'admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U': 'admin',
  'dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg': 'developer',
  'user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k': 'user'
}

// 登录组件
function LoginForm({ onLogin }) {
  const [inputKey, setInputKey] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!inputKey.trim()) {
      setError('請輸入 API Key')
      return
    }

    if (!API_KEY_ROLES[inputKey]) {
      setError('無效的 API Key')
      return
    }

    setError('')
    onLogin(inputKey)
  }

  const handleInputChange = (e) => {
    setInputKey(e.target.value)
    if (error) setError('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 flex items-center justify-center p-4">
      <div className="bg-gray-900/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-4xl mb-4">🧠</div>
          <h1 className="text-2xl font-bold text-white mb-2">SmartUI</h1>
          <p className="text-gray-400 text-sm">+ Claude Code SDK</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              API Key
            </label>
            <input
              type="text"
              value={inputKey}
              onChange={handleInputChange}
              className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="請輸入您的 API Key"
              autoComplete="off"
              spellCheck="false"
            />
            {error && (
              <p className="mt-2 text-sm text-red-400">{error}</p>
            )}
          </div>

          <button
            type="submit"
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
          >
            登入
          </button>
        </form>

        <div className="mt-8 text-xs text-gray-500">
          <div className="mb-2 font-medium">角色說明：</div>
          <div className="space-y-1">
            <div>• 管理員：完全權限</div>
            <div>• 開發者：開發權限（無審核、修改目录、删除原有代码权限）</div>
            <div>• 用戶：基礎權限（文字输入框和文件管理权限）</div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 主应用组件
function App() {
  const [apiKey, setApiKey] = useState(localStorage.getItem('smartui_api_key') || '')
  const [userRole, setUserRole] = useState(null)
  const [roleInfo, setRoleInfo] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [activeTab, setActiveTab] = useState('cascade')
  const [prompt, setPrompt] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [chatHistory, setChatHistory] = useState([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedRepository, setSelectedRepository] = useState('alexchuang650730/aicore0624')
  const [showEditor, setShowEditor] = useState(false)
  const [mcpConnected, setMcpConnected] = useState(false)
  const [mcpStatus, setMcpStatus] = useState('checking')

  // 认证管理Hook
  const {
    authRequest,
    isAuthModalVisible,
    authHistory,
    submitAuth,
    cancelAuth,
    triggerAuthRequest
  } = useAuth()

  // 初始化权限
  useEffect(() => {
    if (apiKey) {
      const role = API_KEY_ROLES[apiKey]
      if (role) {
        setUserRole(role)
        setRoleInfo(ROLE_PERMISSIONS[role])
        setIsAuthenticated(true)
        localStorage.setItem('smartui_api_key', apiKey)
        
        // 设置MCP服务的API Key
        mcpService.setApiKey(apiKey)
      } else {
        // 无效的API Key
        setUserRole(null)
        setRoleInfo(null)
        setIsAuthenticated(false)
        localStorage.removeItem('smartui_api_key')
      }
    } else {
      setIsAuthenticated(false)
    }
  }, [apiKey])

  // 初始化 MCP 連接
  useEffect(() => {
    if (isAuthenticated) {
      const initializeMCP = async () => {
        try {
          setMcpStatus('connecting')
          const connectionResult = await mcpService.checkConnection()
          
          if (connectionResult.connected) {
            setMcpConnected(true)
            setMcpStatus('connected')
            
            // 添加連接成功消息到聊天歷史
            const welcomeMessage = {
              id: Date.now(),
              type: 'assistant',
              content: `🎉 **AICore + Claude Code SDK 連接成功！**

✅ **連接狀態**: 已連接
🤖 **智能能力**: AICore 3.0 + Claude Code SDK 深度整合
⚡ **上下文能力**: 200K tokens 深度分析
🔄 **緩存加速**: 高性能緩存已啟用
🧠 **智能分析**: 代碼分析已整合到對話流程中
👤 **當前角色**: ${roleInfo?.name || '未知'}

**現在您可以直接使用完整的 AI 功能**：
- 智能代碼分析（自動整合到對話中）
- 深度上下文理解
- SmartInvention 任務管理
- 高性能緩存加速`,
              timestamp: new Date().toISOString()
            }
            
            setChatHistory([welcomeMessage])
          } else {
            setMcpConnected(false)
            setMcpStatus('disconnected')
          }
        } catch (error) {
          console.error('MCP初始化失败:', error)
          setMcpConnected(false)
          setMcpStatus('error')
        }
      }
      
      initializeMCP()
    }
  }, [isAuthenticated, roleInfo])

  // 检查权限
  const hasPermission = (permission) => {
    if (!roleInfo) return false
    return roleInfo.permissions.includes(permission)
  }

  // 登录处理
  const handleLogin = (key) => {
    setApiKey(key)
  }

  // 登出处理
  const handleLogout = () => {
    setApiKey('')
    setUserRole(null)
    setRoleInfo(null)
    setIsAuthenticated(false)
    localStorage.removeItem('smartui_api_key')
    setChatHistory([])
    setMcpConnected(false)
    setMcpStatus('checking')
  }

  // 处理消息发送
  const handleSendMessage = async () => {
    if (!currentMessage.trim() || isProcessing) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    }

    setChatHistory(prev => [...prev, userMessage])
    setCurrentMessage('')
    setIsProcessing(true)

    try {
      // 构建上下文
      const context = {
        message: currentMessage,
        selectedFile: selectedFile,
        repository: selectedRepository,
        chatHistory: chatHistory,
        enableCodeAnalysis: true,
        contextCapacity: '200K',
        analysisMode: 'integrated'
      }

      // 发送到MCP服务处理
      const result = await mcpService.processMessage(context)

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: result.content,
        timestamp: new Date().toISOString(),
        tokens: result.tokens,
        processing_time: result.processing_time,
        system_type: result.system_type
      }

      setChatHistory(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('消息处理失败:', error)
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `❌ **處理失敗**\n\n錯誤信息: ${error.message}\n\n請檢查網絡連接或API權限。`,
        timestamp: new Date().toISOString(),
        error: true
      }

      setChatHistory(prev => [...prev, errorMessage])
    } finally {
      setIsProcessing(false)
    }
  }

  // 如果未认证，显示登录界面
  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />
  }

  // 主界面
  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col">
      {/* 顶部导航栏 */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="text-2xl">🧠</div>
            <span className="text-lg font-semibold">SmartUI</span>
            <span className="text-sm text-purple-400">+ Claude Code SDK</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm text-green-400">200K Tokens</span>
            <span className="text-sm text-blue-400">AI 優先 IDE</span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* 角色标识 */}
          <div className={`px-2 py-1 rounded text-xs ${roleInfo?.badge}`}>
            {roleInfo?.name}
          </div>
          
          {/* 连接状态 */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              mcpStatus === 'connected' ? 'bg-green-400' : 
              mcpStatus === 'connecting' ? 'bg-yellow-400' : 'bg-red-400'
            }`}></div>
            <span className="text-xs text-gray-400">
              {mcpStatus === 'connected' ? 'Claude Code SDK 已連接' : 
               mcpStatus === 'connecting' ? '連接中...' : 'SmartInvention MCP 啟用'}
            </span>
          </div>

          <button
            onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-white"
          >
            登出
          </button>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex-1 flex">
        {/* 左侧面板 */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
          {/* 项目浏览器 */}
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm font-medium">📁 項目瀏覽器</span>
              <span className="text-xs text-green-400">GitHub 已連接</span>
            </div>
            
            <GitHubFileExplorer
              repository={selectedRepository}
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile}
              hasPermission={hasPermission}
            />
          </div>

          {/* 快速操作 */}
          {hasPermission('file_manage_basic') && (
            <div className="p-4 border-b border-gray-700">
              <div className="text-sm font-medium mb-3">快速操作</div>
              <div className="space-y-2">
                <button className="w-full text-left text-sm text-gray-400 hover:text-white p-2 rounded hover:bg-gray-700">
                  🔗 在 GitHub 中開啟
                </button>
                <button className="w-full text-left text-sm text-gray-400 hover:text-white p-2 rounded hover:bg-gray-700">
                  🆕 刷新檔案樹
                </button>
                <button className="w-full text-left text-sm text-gray-400 hover:text-white p-2 rounded hover:bg-gray-700">
                  📋 展開所有檔案夾
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 中央内容区域 */}
        <div className="flex-1 flex flex-col">
          {/* 标签栏 */}
          <div className="bg-gray-800 border-b border-gray-700 px-4 py-2">
            <div className="flex space-x-1">
              <button
                onClick={() => setActiveTab('cascade')}
                className={`px-4 py-2 text-sm rounded-t-lg ${
                  activeTab === 'cascade' 
                    ? 'bg-purple-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                ✨ Cascade 協作
              </button>
              <button
                onClick={() => setActiveTab('composer')}
                className={`px-4 py-2 text-sm rounded-t-lg ${
                  activeTab === 'composer' 
                    ? 'bg-purple-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                🎼 Composer ...
              </button>
              <button
                onClick={() => setActiveTab('preview')}
                className={`px-4 py-2 text-sm rounded-t-lg ${
                  activeTab === 'preview' 
                    ? 'bg-purple-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                👁️ 實時預覽
              </button>
              <button
                onClick={() => setActiveTab('terminal')}
                className={`px-4 py-2 text-sm rounded-t-lg ${
                  activeTab === 'terminal' 
                    ? 'bg-purple-600 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                💻 終端機
              </button>
              {hasPermission('file_manage_basic') && (
                <button
                  onClick={() => setActiveTab('files')}
                  className={`px-4 py-2 text-sm rounded-t-lg ${
                    activeTab === 'files' 
                      ? 'bg-purple-600 text-white' 
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  📁 文件管理
                </button>
              )}
            </div>
          </div>

          {/* 内容区域 */}
          <div className="flex-1 p-4">
            {activeTab === 'cascade' && (
              <div className="h-full flex flex-col">
                <div className="mb-4">
                  <h2 className="text-xl font-bold mb-2">✨ Cascade AI 協作</h2>
                  <p className="text-gray-400 text-sm">基於 200K tokens 上下文的深度代碼理解</p>
                </div>

                {/* 聊天区域 */}
                <div className="flex-1 bg-gray-800 rounded-lg p-4 mb-4 overflow-y-auto">
                  {chatHistory.length === 0 ? (
                    <div className="text-center text-gray-500 mt-8">
                      <div className="text-4xl mb-4">🤖</div>
                      <p>開始與 AI 對話，獲得智能代碼分析和建議</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {chatHistory.map((message) => (
                        <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-3xl p-3 rounded-lg ${
                            message.type === 'user' 
                              ? 'bg-purple-600 text-white' 
                              : 'bg-gray-700 text-gray-100'
                          }`}>
                            <div className="whitespace-pre-wrap">{message.content}</div>
                            {message.tokens && (
                              <div className="text-xs text-gray-400 mt-2">
                                Tokens: {message.tokens} | {message.processing_time} | {message.system_type}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* 输入区域 */}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                    className="flex-1 px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="描述您想要建構或分析的內容... (例如：'創建一個用戶認證的 React 組件，包含表單驗證')"
                    disabled={isProcessing}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={isProcessing || !currentMessage.trim()}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    {isProcessing ? '處理中...' : '發送'}
                  </button>
                </div>

                {/* 操作按钮 */}
                <div className="flex space-x-2 mt-4">
                  <button className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-gray-300 rounded">
                    💬 聊天模式
                  </button>
                  <button className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-gray-300 rounded">
                    🗑️ 清除歷史
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'files' && hasPermission('file_manage_basic') && (
              <FileManager 
                hasPermission={hasPermission}
                apiKey={apiKey}
              />
            )}

            {activeTab === 'composer' && (
              <div className="h-full flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <div className="text-4xl mb-4">🎼</div>
                  <p>Composer 功能開發中...</p>
                </div>
              </div>
            )}

            {activeTab === 'preview' && (
              <div className="h-full flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <div className="text-4xl mb-4">👁️</div>
                  <p>實時預覽功能開發中...</p>
                </div>
              </div>
            )}

            {activeTab === 'terminal' && (
              <div className="h-full flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <div className="text-4xl mb-4">💻</div>
                  <p>終端機功能開發中...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 底部状态栏 */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-2 text-xs text-gray-400">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span>🟢 Claude Code SDK 已連接</span>
            <span>200K Tokens 可用</span>
            <span>SmartInvention MCP 啟用</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>第 42 行，第 18 列</span>
            <span>UTF-8</span>
            <span>JavaScript</span>
          </div>
        </div>
      </div>

      {/* 认证模态框 */}
      <AuthModal
        authRequest={authRequest}
        onSubmit={submitAuth}
        onCancel={cancelAuth}
        isVisible={isAuthModalVisible}
      />
    </div>
  )
}

export default App

