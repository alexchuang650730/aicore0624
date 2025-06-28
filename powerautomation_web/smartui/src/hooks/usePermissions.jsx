import { useState, useEffect, createContext, useContext } from 'react'

// 权限上下文
const PermissionContext = createContext()

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

// 权限管理Hook
export const usePermissions = () => {
  const context = useContext(PermissionContext)
  if (!context) {
    throw new Error('usePermissions must be used within a PermissionProvider')
  }
  return context
}

// 权限提供者组件
export const PermissionProvider = ({ children }) => {
  const [apiKey, setApiKey] = useState(localStorage.getItem('smartui_api_key') || '')
  const [userRole, setUserRole] = useState(null)
  const [roleInfo, setRoleInfo] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // 初始化权限
  useEffect(() => {
    if (apiKey) {
      const role = API_KEY_ROLES[apiKey]
      if (role) {
        setUserRole(role)
        setRoleInfo(ROLE_PERMISSIONS[role])
        setIsAuthenticated(true)
        localStorage.setItem('smartui_api_key', apiKey)
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

  // 检查权限
  const hasPermission = (permission) => {
    if (!roleInfo) return false
    return roleInfo.permissions.includes(permission)
  }

  // 检查多个权限（需要全部满足）
  const hasAllPermissions = (permissions) => {
    return permissions.every(permission => hasPermission(permission))
  }

  // 检查多个权限（满足其中一个即可）
  const hasAnyPermission = (permissions) => {
    return permissions.some(permission => hasPermission(permission))
  }

  // 登录
  const login = (key) => {
    setApiKey(key)
  }

  // 登出
  const logout = () => {
    setApiKey('')
    setUserRole(null)
    setRoleInfo(null)
    setIsAuthenticated(false)
    localStorage.removeItem('smartui_api_key')
  }

  const value = {
    apiKey,
    userRole,
    roleInfo,
    isAuthenticated,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    login,
    logout
  }

  return (
    <PermissionContext.Provider value={value}>
      {children}
    </PermissionContext.Provider>
  )
}

// 权限守卫组件
export const PermissionGuard = ({ 
  permission, 
  permissions, 
  requireAll = true,
  children, 
  fallback = null,
  showMessage = true 
}) => {
  const { hasPermission, hasAllPermissions, hasAnyPermission } = usePermissions()

  let hasAccess = false

  if (permission) {
    hasAccess = hasPermission(permission)
  } else if (permissions) {
    hasAccess = requireAll 
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions)
  }

  if (!hasAccess) {
    if (fallback) return fallback
    if (showMessage) {
      return (
        <div className="flex items-center justify-center p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <div className="text-center">
            <div className="text-red-400 mb-2">🔒</div>
            <div className="text-red-400 text-sm">權限不足</div>
            <div className="text-gray-400 text-xs mt-1">
              您沒有執行此操作的權限
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  return children
}

// 角色标识组件
export const RoleBadge = ({ className = "" }) => {
  const { roleInfo, isAuthenticated } = usePermissions()

  if (!isAuthenticated || !roleInfo) return null

  return (
    <div className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${roleInfo.badge} ${className}`}>
      <div className="w-2 h-2 bg-current rounded-full mr-1.5"></div>
      {roleInfo.name}
    </div>
  )
}

// 登录组件
export const LoginForm = ({ onLogin }) => {
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
              type="password"
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="請輸入您的 API Key"
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
            <div>• 開發者：開發權限</div>
            <div>• 用戶：基礎權限</div>
          </div>
        </div>
      </div>
    </div>
  )
}

