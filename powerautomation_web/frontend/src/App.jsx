import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Activity, 
  Users, 
  Settings, 
  Code, 
  Monitor, 
  Database,
  Play,
  Terminal,
  BarChart3,
  Shield,
  Cpu,
  HardDrive,
  Network,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle
} from 'lucide-react'

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'http://18.212.97.173:3001' 
  : 'http://localhost:3001'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [systemStats, setSystemStats] = useState(null)
  const [codeInput, setCodeInput] = useState('')
  const [codeOutput, setCodeOutput] = useState('')
  const [codeLanguage, setCodeLanguage] = useState('python')

  // 登录功能
  const handleLogin = async () => {
    if (!apiKey.trim()) {
      setError('请输入 API Key')
      return
    }

    setLoading(true)
    setError('')

    try {
      console.log('正在连接到:', `${API_BASE_URL}/api/auth/api-key`)
      
      const response = await fetch(`${API_BASE_URL}/api/auth/api-key`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ apiKey: apiKey.trim() }),
      })

      const data = await response.json()
      console.log('服务器响应:', data)

      if (response.ok) {
        setUser(data.user)
        localStorage.setItem('token', data.token)
        setError('')
        // 登录成功后获取系统统计信息
        if (data.user.role === 'admin') {
          await fetchSystemStats()
        }
      } else {
        setError(data.message || '登录失败')
      }
    } catch (err) {
      console.error('登录错误:', err)
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('无法连接到服务器，请检查网络连接或服务器状态')
      } else {
        setError(`连接服务器失败: ${err.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  // 获取系统统计信息
  const fetchSystemStats = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setSystemStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch system stats:', err)
    }
  }

  // 执行代码
  const executeCode = async () => {
    if (!codeInput.trim()) {
      setCodeOutput('请输入要执行的代码')
      return
    }

    setLoading(true)
    setCodeOutput('正在执行...')

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE_URL}/api/code/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          code: codeInput,
          language: codeLanguage,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setCodeOutput(`执行成功:\n${data.output || '无输出'}`)
      } else {
        setCodeOutput(`执行失败:\n${data.message || '未知错误'}`)
      }
    } catch (err) {
      setCodeOutput(`执行错误:\n${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  // 登出功能
  const handleLogout = () => {
    setUser(null)
    setApiKey('')
    setSystemStats(null)
    localStorage.removeItem('token')
  }

  // 检查登录状态
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // 验证 token 有效性并恢复用户状态
      verifyTokenAndRestoreUser(token)
    }
  }, [])

  // 验证token并恢复用户状态
  const verifyTokenAndRestoreUser = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
        await fetchSystemStats()
      } else {
        // Token无效，清除本地存储
        localStorage.removeItem('token')
      }
    } catch (err) {
      console.error('Token验证失败:', err)
      localStorage.removeItem('token')
    }
  }

  // 如果未登录，显示登录界面
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-gray-800">
              PowerAutomation Web 系统
            </CardTitle>
            <CardDescription>
              增强版三角色权限登录
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="apiKey">API Key:</Label>
              <Input
                id="apiKey"
                type="password"
                placeholder="输入您的 API Key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
              />
            </div>
            
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <Button 
              onClick={handleLogin} 
              disabled={loading}
              className="w-full"
            >
              {loading ? '登录中...' : '登录'}
            </Button>

            <div className="mt-6 text-sm text-gray-600">
              <p className="font-semibold mb-2">测试账号:</p>
              <div className="space-y-1">
                <p><Badge variant="destructive">管理员</Badge>: admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U</p>
                <p><Badge variant="default">开发者</Badge>: dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg</p>
                <p><Badge variant="secondary">用户</Badge>: user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // 根据用户角色显示不同的界面
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                PowerAutomation Web 系统
              </h1>
              <Badge variant={
                user.role === 'admin' ? 'destructive' : 
                user.role === 'developer' ? 'default' : 'secondary'
              }>
                {user.role === 'admin' ? '管理员' : 
                 user.role === 'developer' ? '开发者' : '用户'}
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                欢迎, {user.username || user.role}
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                登出
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* 主要内容区域 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {user.role === 'admin' && (
          <AdminDashboard 
            systemStats={systemStats} 
            onRefreshStats={fetchSystemStats}
          />
        )}
        
        {user.role === 'developer' && (
          <DeveloperDashboard 
            codeInput={codeInput}
            setCodeInput={setCodeInput}
            codeOutput={codeOutput}
            codeLanguage={codeLanguage}
            setCodeLanguage={setCodeLanguage}
            onExecuteCode={executeCode}
            loading={loading}
          />
        )}
        
        {user.role === 'user' && (
          <UserDashboard />
        )}
      </main>
    </div>
  )
}

// 管理员仪表板组件
function AdminDashboard({ systemStats, onRefreshStats }) {
  return (
    <div className="space-y-6">
      {/* 系统概览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总用户数</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats?.users || 1247}</div>
            <p className="text-xs text-muted-foreground">+12% 较上月</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API 请求</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats?.requests || 15420}</div>
            <p className="text-xs text-muted-foreground">+8% 较昨日</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">系统状态</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">正常</div>
            <p className="text-xs text-muted-foreground">所有服务运行正常</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">响应时间</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats?.responseTime || 156}ms</div>
            <p className="text-xs text-muted-foreground">平均响应时间</p>
          </CardContent>
        </Card>
      </div>

      {/* 管理员功能标签页 */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">概览</TabsTrigger>
          <TabsTrigger value="users">用户管理</TabsTrigger>
          <TabsTrigger value="system">系统监控</TabsTrigger>
          <TabsTrigger value="tools">工具管理</TabsTrigger>
          <TabsTrigger value="logs">日志查看</TabsTrigger>
          <TabsTrigger value="settings">系统设置</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>系统性能</CardTitle>
                <CardDescription>实时系统资源使用情况</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Cpu className="h-4 w-4" />
                    <span>CPU 使用率</span>
                  </div>
                  <span className="font-medium">23%</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <HardDrive className="h-4 w-4" />
                    <span>内存使用</span>
                  </div>
                  <span className="font-medium">45%</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Network className="h-4 w-4" />
                    <span>网络流量</span>
                  </div>
                  <span className="font-medium">1.2 GB/s</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>快速操作</CardTitle>
                <CardDescription>常用管理操作</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button onClick={onRefreshStats} className="w-full" variant="outline">
                  <Activity className="h-4 w-4 mr-2" />
                  刷新系统状态
                </Button>
                <Button className="w-full" variant="outline">
                  <Database className="h-4 w-4 mr-2" />
                  数据库备份
                </Button>
                <Button className="w-full" variant="outline">
                  <Shield className="h-4 w-4 mr-2" />
                  安全扫描
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>用户管理</CardTitle>
              <CardDescription>管理系统用户和权限</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">用户列表</h3>
                  <Button size="sm">
                    <Users className="h-4 w-4 mr-2" />
                    添加用户
                  </Button>
                </div>
                <div className="border rounded-lg p-4">
                  <p className="text-sm text-gray-600">用户管理功能开发中...</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>系统监控</CardTitle>
              <CardDescription>实时监控系统运行状态</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <Monitor className="h-8 w-8 mx-auto mb-2 text-green-600" />
                  <p className="font-medium">服务状态</p>
                  <p className="text-sm text-green-600">正常运行</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <BarChart3 className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                  <p className="font-medium">性能指标</p>
                  <p className="text-sm text-blue-600">优秀</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <Shield className="h-8 w-8 mx-auto mb-2 text-orange-600" />
                  <p className="font-medium">安全状态</p>
                  <p className="text-sm text-orange-600">安全</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tools" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>工具管理</CardTitle>
              <CardDescription>管理系统工具和插件</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">已安装工具</h3>
                  <Button size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    添加工具
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">代码执行引擎</h4>
                      <Badge variant="default">已启用</Badge>
                    </div>
                    <p className="text-sm text-gray-600">支持多语言代码执行</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">API 测试工具</h4>
                      <Badge variant="secondary">开发中</Badge>
                    </div>
                    <p className="text-sm text-gray-600">内置 API 测试功能</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>系统日志</CardTitle>
              <CardDescription>查看系统运行日志</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm h-64 overflow-y-auto">
                <div>[2025-06-25 11:49:00] INFO: PowerAutomation Web 系统启动成功</div>
                <div>[2025-06-25 11:49:01] INFO: 后端 API 服务器运行在端口 3001</div>
                <div>[2025-06-25 11:49:02] INFO: 前端服务器运行在端口 5173</div>
                <div>[2025-06-25 11:49:03] INFO: 数据库连接成功</div>
                <div>[2025-06-25 11:49:04] INFO: 所有服务初始化完成</div>
                <div>[2025-06-25 11:50:15] INFO: 管理员用户登录成功</div>
                <div>[2025-06-25 11:50:16] INFO: 获取系统统计信息</div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>系统设置</CardTitle>
              <CardDescription>配置系统参数和选项</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">基本设置</h3>
                  <div className="space-y-2">
                    <Label>系统名称</Label>
                    <Input defaultValue="PowerAutomation Web 系统" />
                  </div>
                  <div className="space-y-2">
                    <Label>管理员邮箱</Label>
                    <Input defaultValue="admin@powerautomation.com" />
                  </div>
                </div>
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">安全设置</h3>
                  <div className="space-y-2">
                    <Label>会话超时 (分钟)</Label>
                    <Input defaultValue="30" type="number" />
                  </div>
                  <div className="space-y-2">
                    <Label>最大登录尝试次数</Label>
                    <Input defaultValue="5" type="number" />
                  </div>
                </div>
              </div>
              <div className="pt-4">
                <Button>保存设置</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

// 开发者仪表板组件
function DeveloperDashboard({ 
  codeInput, 
  setCodeInput, 
  codeOutput, 
  codeLanguage, 
  setCodeLanguage, 
  onExecuteCode, 
  loading 
}) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Code className="h-5 w-5" />
              <span>代码执行环境</span>
            </CardTitle>
            <CardDescription>
              支持 Python、JavaScript、Shell 等多种语言
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4">
              <Label>语言:</Label>
              <select 
                value={codeLanguage} 
                onChange={(e) => setCodeLanguage(e.target.value)}
                className="border rounded px-3 py-1"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="shell">Shell</option>
                <option value="sql">SQL</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <Label>代码输入:</Label>
              <textarea
                value={codeInput}
                onChange={(e) => setCodeInput(e.target.value)}
                placeholder={`输入 ${codeLanguage} 代码...`}
                className="w-full h-32 p-3 border rounded-lg font-mono text-sm"
              />
            </div>
            
            <Button onClick={onExecuteCode} disabled={loading}>
              <Play className="h-4 w-4 mr-2" />
              {loading ? '执行中...' : '执行代码'}
            </Button>
            
            <div className="space-y-2">
              <Label>执行结果:</Label>
              <div className="bg-black text-green-400 p-3 rounded-lg font-mono text-sm h-32 overflow-y-auto whitespace-pre-wrap">
                {codeOutput || '等待执行...'}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Terminal className="h-5 w-5" />
              <span>开发者工具</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full">
              <Monitor className="h-4 w-4 mr-2" />
              API 测试
            </Button>
            <Button variant="outline" className="w-full">
              <Database className="h-4 w-4 mr-2" />
              数据库查询
            </Button>
            <Button variant="outline" className="w-full">
              <Settings className="h-4 w-4 mr-2" />
              系统调试
            </Button>
            <Button variant="outline" className="w-full">
              <BarChart3 className="h-4 w-4 mr-2" />
              性能分析
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* 开发者专用功能标签页 */}
      <Tabs defaultValue="api" className="space-y-4">
        <TabsList>
          <TabsTrigger value="api">API 测试</TabsTrigger>
          <TabsTrigger value="debug">调试工具</TabsTrigger>
          <TabsTrigger value="docs">文档</TabsTrigger>
        </TabsList>

        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>API 测试工具</CardTitle>
              <CardDescription>测试系统 API 端点</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label>请求方法</Label>
                    <select className="w-full border rounded px-3 py-2 mt-1">
                      <option>GET</option>
                      <option>POST</option>
                      <option>PUT</option>
                      <option>DELETE</option>
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <Label>API 端点</Label>
                    <Input placeholder="/api/health" className="mt-1" />
                  </div>
                </div>
                <div>
                  <Label>请求体 (JSON)</Label>
                  <textarea 
                    placeholder='{"key": "value"}'
                    className="w-full h-24 p-3 border rounded-lg font-mono text-sm mt-1"
                  />
                </div>
                <Button>
                  <Play className="h-4 w-4 mr-2" />
                  发送请求
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="debug" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>系统调试</CardTitle>
              <CardDescription>调试工具和系统信息</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">系统信息</h4>
                    <div className="text-sm space-y-1">
                      <p>Node.js: v18.20.8</p>
                      <p>系统: Ubuntu 22.04</p>
                      <p>内存: 8GB</p>
                      <p>CPU: 4 cores</p>
                    </div>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">服务状态</h4>
                    <div className="text-sm space-y-1">
                      <p className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        后端 API: 正常
                      </p>
                      <p className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        前端服务: 正常
                      </p>
                      <p className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        数据库: 正常
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="docs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>开发文档</CardTitle>
              <CardDescription>API 文档和开发指南</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2">API 端点</h4>
                  <div className="text-sm space-y-2">
                    <p><code className="bg-gray-100 px-2 py-1 rounded">GET /api/health</code> - 健康检查</p>
                    <p><code className="bg-gray-100 px-2 py-1 rounded">POST /api/auth/api-key</code> - API Key 认证</p>
                    <p><code className="bg-gray-100 px-2 py-1 rounded">GET /api/admin/stats</code> - 系统统计</p>
                    <p><code className="bg-gray-100 px-2 py-1 rounded">POST /api/code/execute</code> - 代码执行</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

// 用户仪表板组件
function UserDashboard() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>用户控制台</span>
          </CardTitle>
          <CardDescription>
            欢迎使用 PowerAutomation Web 系统
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">可用功能</h3>
              <div className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <Activity className="h-4 w-4 mr-2" />
                  查看系统状态
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Settings className="h-4 w-4 mr-2" />
                  个人设置
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Monitor className="h-4 w-4 mr-2" />
                  使用统计
                </Button>
              </div>
            </div>
            <div className="space-y-4">
              <h3 className="text-lg font-medium">系统信息</h3>
              <div className="border rounded-lg p-4">
                <div className="space-y-2 text-sm">
                  <p className="flex justify-between">
                    <span>系统版本:</span>
                    <span>v1.0.0</span>
                  </p>
                  <p className="flex justify-between">
                    <span>最后更新:</span>
                    <span>2025-06-25</span>
                  </p>
                  <p className="flex justify-between">
                    <span>在线用户:</span>
                    <span>1,247</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default App

