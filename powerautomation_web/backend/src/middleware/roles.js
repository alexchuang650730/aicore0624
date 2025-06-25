// 角色權限中間件
const roleMiddleware = (allowedRoles = []) => {
  return (req, res, next) => {
    try {
      // 檢查用戶是否已認證
      if (!req.user) {
        return res.status(401).json({
          error: '用戶未認證',
          code: 'NOT_AUTHENTICATED'
        })
      }

      const userRole = req.user.role

      // 檢查用戶角色是否在允許的角色列表中
      if (!allowedRoles.includes(userRole)) {
        return res.status(403).json({
          error: '權限不足',
          code: 'INSUFFICIENT_PERMISSIONS',
          required_roles: allowedRoles,
          user_role: userRole
        })
      }

      next()

    } catch (error) {
      console.error('角色權限中間件錯誤:', error)
      return res.status(500).json({
        error: '權限檢查失敗',
        code: 'PERMISSION_CHECK_FAILED'
      })
    }
  }
}

// 權限檢查中間件
const permissionMiddleware = (requiredPermissions = []) => {
  return (req, res, next) => {
    try {
      // 檢查用戶是否已認證
      if (!req.user) {
        return res.status(401).json({
          error: '用戶未認證',
          code: 'NOT_AUTHENTICATED'
        })
      }

      const userPermissions = req.user.permissions || []

      // 管理員擁有所有權限
      if (req.user.role === 'admin' || userPermissions.includes('all')) {
        return next()
      }

      // 檢查用戶是否擁有所需的權限
      const hasPermission = requiredPermissions.every(permission => 
        userPermissions.includes(permission)
      )

      if (!hasPermission) {
        return res.status(403).json({
          error: '權限不足',
          code: 'INSUFFICIENT_PERMISSIONS',
          required_permissions: requiredPermissions,
          user_permissions: userPermissions
        })
      }

      next()

    } catch (error) {
      console.error('權限檢查中間件錯誤:', error)
      return res.status(500).json({
        error: '權限檢查失敗',
        code: 'PERMISSION_CHECK_FAILED'
      })
    }
  }
}

// 角色權限配置
const ROLE_PERMISSIONS = {
  admin: [
    'all', // 管理員擁有所有權限
    'user_management',
    'system_config',
    'data_analysis',
    'server_management',
    'mcp_access',
    'debug_tools',
    'api_access',
    'advanced_features',
    'basic_chat',
    'file_upload',
    'history_view'
  ],
  developer: [
    'mcp_access',
    'debug_tools',
    'api_access',
    'advanced_features',
    'basic_chat',
    'file_upload',
    'history_view'
  ],
  user: [
    'basic_chat',
    'file_upload',
    'history_view'
  ]
}

// 檢查角色是否擁有特定權限
const hasRolePermission = (role, permission) => {
  const rolePermissions = ROLE_PERMISSIONS[role] || []
  return rolePermissions.includes(permission) || rolePermissions.includes('all')
}

// 獲取角色的所有權限
const getRolePermissions = (role) => {
  return ROLE_PERMISSIONS[role] || []
}

module.exports = {
  roleMiddleware,
  permissionMiddleware,
  hasRolePermission,
  getRolePermissions,
  ROLE_PERMISSIONS
}

