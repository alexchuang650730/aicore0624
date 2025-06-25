import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  User, 
  Code, 
  Shield, 
  Github, 
  Mail, 
  Key, 
  LogIn,
  Settings,
  BarChart3,
  Users,
  Activity,
  Zap
} from 'lucide-react'
import './App.css'

// API 配置 - 直接使用後端 URL
const API_BASE_URL = 'http://localhost:3001'

// API 請求函數
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  }

  try {
    const response = await fetch(url, config)
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`)
    }
    
    return data
  } catch (error) {
    console.error('API 請求錯誤:', error)
    throw error
  }
}

function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [loginMode, setLoginMode] = useState('user') // 'user' | 'advanced'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // 檢查本地存儲的登錄狀態
  useEffect(() => {
    const savedUser = localStorage.getItem('powerautomation_user')
    const savedToken = localStorage.getItem('powerautomation_token')
    if (savedUser && savedToken) {
      try {
        setCurrentUser(JSON.parse(savedUser))
      } catch (e) {
        localStorage.removeItem('powerautomation_user')
        localStorage.removeItem('powerautomation_token')
      }
    }
  }, [])

  // 真實的登錄函數
  const handleLogin = async (credentials) => {
    setLoading(true)
    setError('')
    
    try {
      let response = null
      
      if (credentials.type === 'api_key') {
        response = await apiRequest('/api/auth/api-key', {
          method: 'POST',
          body: JSON.stringify({ apiKey: credentials.apiKey })
        })
      } else if (credentials.type === 'oauth') {
        // 模擬 OAuth 登錄（實際應用中會跳轉到 OAuth 提供商）
        response = await apiRequest('/api/auth/oauth/github', {
          method: 'POST',
          body: JSON.stringify({ provider: credentials.provider })
        })
      } else if (credentials.type === 'email') {
        response = await apiRequest('/api/auth/email', {
          method: 'POST',
          body: JSON.stringify({ 
            email: credentials.email, 
            password: credentials.password 
          })
        })
      }
      
      if (response && response.success) {
        const { user, token } = response.data
        setCurrentUser(user)
        localStorage.setItem('powerautomation_user', JSON.stringify(user))
        localStorage.setItem('powerautomation_token', token)
      } else {
        throw new Error('登錄失敗')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // 登出函數
  const handleLogout = () => {
    setCurrentUser(null)
    localStorage.removeItem('powerautomation_user')
    localStorage.removeItem('powerautomation_token')
  }

  // 如果已登錄，顯示儀表板
  if (currentUser) {
    return <Dashboard user={currentUser} onLogout={handleLogout} />
  }

  // 登錄界面
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 text-white rounded-full mb-4">
            <Zap className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">PowerAutomation</h1>
          <p className="text-gray-600">智能編程助手 - 三角色權限系統</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>選擇登錄方式</CardTitle>
            <CardDescription>
              請選擇您的使用方式來訪問 PowerAutomation 系統
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={loginMode} onValueChange={setLoginMode}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="user" className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  用戶模式
                </TabsTrigger>
                <TabsTrigger value="advanced" className="flex items-center gap-2">
                  <Code className="w-4 h-4" />
                  高級模式
                </TabsTrigger>
              </TabsList>

              <TabsContent value="user" className="space-y-4">
                <UserLoginForm onLogin={handleLogin} loading={loading} />
              </TabsContent>

              <TabsContent value="advanced" className="space-y-4">
                <AdvancedLoginForm onLogin={handleLogin} loading={loading} />
              </TabsContent>
            </Tabs>

            {error && (
              <Alert className="mt-4 border-red-200 bg-red-50">
                <AlertDescription className="text-red-700">
                  {error}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// 用戶登錄表單
function UserLoginForm({ onLogin, loading }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleOAuthLogin = (provider) => {
    onLogin({ type: 'oauth', provider })
  }

  const handleEmailLogin = (e) => {
    e.preventDefault()
    if (email && password) {
      onLogin({ type: 'email', email, password })
    }
  }

  return (
    <div className="space-y-4">
      <div className="text-center">
        <Badge variant="secondary" className="mb-4">
          <User className="w-3 h-3 mr-1" />
          普通用戶登錄
        </Badge>
        <p className="text-sm text-gray-600 mb-4">
          使用 OAuth 或郵箱密碼登錄，系統將自動為您生成用戶 API Key
        </p>
      </div>

      {/* OAuth 登錄 */}
      <div className="space-y-2">
        <Button 
          variant="outline" 
          className="w-full" 
          onClick={() => handleOAuthLogin('github')}
          disabled={loading}
        >
          <Github className="w-4 h-4 mr-2" />
          使用 GitHub 登錄
        </Button>
        <Button 
          variant="outline" 
          className="w-full" 
          onClick={() => handleOAuthLogin('google')}
          disabled={loading}
        >
          <Mail className="w-4 h-4 mr-2" />
          使用 Google 登錄
        </Button>
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-2 text-gray-500">或</span>
        </div>
      </div>

      {/* 郵箱登錄 */}
      <form onSubmit={handleEmailLogin} className="space-y-3">
        <div>
          <Label htmlFor="email">郵箱地址</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
          />
        </div>
        <div>
          <Label htmlFor="password">密碼</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
        </div>
        <Button type="submit" className="w-full" disabled={loading}>
          <LogIn className="w-4 h-4 mr-2" />
          {loading ? '登錄中...' : '郵箱登錄'}
        </Button>
      </form>
    </div>
  )
}

// 高級用戶登錄表單
function AdvancedLoginForm({ onLogin, loading }) {
  const [apiKey, setApiKey] = useState('')

  const handleApiKeyLogin = (e) => {
    e.preventDefault()
    if (apiKey.trim()) {
      onLogin({ type: 'api_key', apiKey: apiKey.trim() })
    }
  }

  const getKeyTypeInfo = () => {
    if (apiKey.startsWith('admin_')) {
      return { type: '管理員', color: 'bg-red-100 text-red-700', icon: Shield }
    } else if (apiKey.startsWith('dev_')) {
      return { type: '開發者', color: 'bg-orange-100 text-orange-700', icon: Code }
    } else if (apiKey.startsWith('user_')) {
      return { type: '用戶', color: 'bg-blue-100 text-blue-700', icon: User }
    }
    return null
  }

  const keyInfo = getKeyTypeInfo()

  return (
    <div className="space-y-4">
      <div className="text-center">
        <Badge variant="secondary" className="mb-4">
          <Key className="w-3 h-3 mr-1" />
          API Key 登錄
        </Badge>
        <p className="text-sm text-gray-600 mb-4">
          適用於開發者和管理員，請輸入您的專用 API Key
        </p>
      </div>

      <form onSubmit={handleApiKeyLogin} className="space-y-4">
        <div>
          <Label htmlFor="apiKey">API Key</Label>
          <Input
            id="apiKey"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="admin_xxx... 或 dev_xxx..."
            required
          />
          {keyInfo && (
            <div className={`mt-2 p-2 rounded-md ${keyInfo.color} flex items-center gap-2`}>
              <keyInfo.icon className="w-4 h-4" />
              <span className="text-sm font-medium">檢測到 {keyInfo.type} Key</span>
            </div>
          )}
        </div>

        <Button type="submit" className="w-full" disabled={loading || !apiKey.trim()}>
          <Key className="w-4 h-4 mr-2" />
          {loading ? '驗證中...' : 'API Key 登錄'}
        </Button>
      </form>

      <div className="text-xs text-gray-500 space-y-1">
        <p>• <strong>admin_</strong> 開頭：系統管理員權限</p>
        <p>• <strong>dev_</strong> 開頭：開發者權限</p>
        <p>• <strong>user_</strong> 開頭：普通用戶權限</p>
      </div>
    </div>
  )
}

// 儀表板組件
function Dashboard({ user, onLogout }) {
  const [systemStats, setSystemStats] = useState(null)
  const [loading, setLoading] = useState(false)

  // 獲取系統統計數據
  useEffect(() => {
    const fetchSystemStats = async () => {
      if (user.role === 'admin') {
        setLoading(true)
        try {
          const token = localStorage.getItem('powerautomation_token')
          const response = await apiRequest('/api/admin/stats', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          if (response.success) {
            setSystemStats(response.data)
          }
        } catch (error) {
          console.error('獲取系統統計失敗:', error)
        } finally {
          setLoading(false)
        }
      }
    }

    fetchSystemStats()
  }, [user.role])

  const getRoleColor = () => {
    switch (user.role) {
      case 'admin': return 'bg-red-100 text-red-700 border-red-200'
      case 'developer': return 'bg-orange-100 text-orange-700 border-orange-200'
      default: return 'bg-blue-100 text-blue-700 border-blue-200'
    }
  }

  const getRoleIcon = () => {
    switch (user.role) {
      case 'admin': return Shield
      case 'developer': return Code
      default: return User
    }
  }

  const RoleIcon = getRoleIcon()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 頂部導航 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">PowerAutomation</h1>
            </div>
            
            <div className="flex items-center gap-4">
              <Badge className={getRoleColor()}>
                <RoleIcon className="w-3 h-3 mr-1" />
                {user.role === 'admin' ? '管理員' : user.role === 'developer' ? '開發者' : '用戶'}
              </Badge>
              <div className="flex items-center gap-2">
                <span className="text-2xl">
                  {user.role === 'admin' ? '👑' : user.role === 'developer' ? '👨‍💻' : '👤'}
                </span>
                <span className="text-sm font-medium text-gray-700">{user.name}</span>
              </div>
              <Button variant="outline" size="sm" onClick={onLogout}>
                登出
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* 主要內容 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* 用戶信息卡片 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                用戶信息
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p><strong>姓名:</strong> {user.name}</p>
                <p><strong>郵箱:</strong> {user.email}</p>
                <p><strong>角色:</strong> {user.role}</p>
                <p><strong>ID:</strong> {user.id}</p>
              </div>
            </CardContent>
          </Card>

          {/* 權限信息卡片 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                權限信息
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {user.permissions.map((permission, index) => (
                  <Badge key={index} variant="secondary" className="mr-1 mb-1">
                    {permission}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 系統狀態卡片 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                系統狀態
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>MCP 連接:</span>
                  <Badge className="bg-green-100 text-green-700">正常</Badge>
                </div>
                <div className="flex justify-between">
                  <span>API 狀態:</span>
                  <Badge className="bg-green-100 text-green-700">運行中</Badge>
                </div>
                {systemStats && (
                  <>
                    <div className="flex justify-between">
                      <span>在線用戶:</span>
                      <span>{systemStats.activeUsers}</span>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 管理員專用功能 */}
          {user.role === 'admin' && (
            <Card className="md:col-span-2 lg:col-span-3">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  管理員控制台
                  {loading && <span className="text-sm text-gray-500">(載入中...)</span>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button variant="outline" className="h-20 flex flex-col gap-2">
                    <Users className="w-6 h-6" />
                    用戶管理
                    {systemStats && <span className="text-xs">{systemStats.totalUsers} 用戶</span>}
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col gap-2">
                    <BarChart3 className="w-6 h-6" />
                    數據分析
                    {systemStats && <span className="text-xs">{systemStats.totalRequests} 請求</span>}
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col gap-2">
                    <Settings className="w-6 h-6" />
                    系統配置
                    {systemStats && <span className="text-xs">運行時間 {systemStats.systemUptime}</span>}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 開發者專用功能 */}
          {user.role === 'developer' && (
            <Card className="md:col-span-2 lg:col-span-3">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  開發者工具
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button variant="outline" className="h-20 flex flex-col gap-2">
                    <Key className="w-6 h-6" />
                    API 訪問
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col gap-2">
                    <Activity className="w-6 h-6" />
                    調試工具
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col gap-2">
                    <Settings className="w-6 h-6" />
                    服務器管理
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}

export default App

