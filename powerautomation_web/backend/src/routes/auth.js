const express = require('express')
const jwt = require('jsonwebtoken')
const bcrypt = require('bcryptjs')
const router = express.Router()

const JWT_SECRET = process.env.JWT_SECRET || 'powerautomation_secret_key_2024'

// 模擬用戶數據庫
const users = new Map()
const apiKeys = new Map()

// 初始化一些測試數據
const initTestData = () => {
  // 管理員
  apiKeys.set('admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U', {
    id: 'admin_1',
    name: '系統管理員',
    email: 'admin@powerautomation.com',
    role: 'admin',
    permissions: ['all'],
    created_at: new Date().toISOString()
  })

  // 開發者
  apiKeys.set('dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg', {
    id: 'dev_1',
    name: '開發者',
    email: 'developer@powerautomation.com',
    role: 'developer',
    permissions: ['mcp_access', 'debug_tools', 'api_access', 'advanced_features'],
    created_at: new Date().toISOString()
  })

  // 用戶
  apiKeys.set('user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k', {
    id: 'user_1',
    name: '測試用戶',
    email: 'user@powerautomation.com',
    role: 'user',
    permissions: ['basic_chat', 'file_upload', 'history_view'],
    created_at: new Date().toISOString()
  })

  // 郵箱用戶
  users.set('user@example.com', {
    id: 'email_user_1',
    name: '郵箱用戶',
    email: 'user@example.com',
    password: bcrypt.hashSync('password123', 10),
    role: 'user',
    permissions: ['basic_chat', 'file_upload', 'history_view'],
    created_at: new Date().toISOString()
  })
}

initTestData()

// 檢測 API Key 類型
const detectKeyType = (key) => {
  if (key.startsWith('admin_')) return 'admin'
  if (key.startsWith('dev_')) return 'developer'
  if (key.startsWith('user_')) return 'user'
  return null
}

// 生成 JWT Token
const generateToken = (user) => {
  return jwt.sign(
    {
      id: user.id,
      email: user.email,
      role: user.role,
      permissions: user.permissions
    },
    JWT_SECRET,
    { expiresIn: '7d' }
  )
}

// API Key 登錄
router.post('/api-key', async (req, res) => {
  try {
    const { apiKey } = req.body

    if (!apiKey) {
      return res.status(400).json({
        error: '請提供 API Key'
      })
    }

    // 檢查 API Key 是否存在
    const user = apiKeys.get(apiKey)
    if (!user) {
      return res.status(401).json({
        error: 'API Key 無效'
      })
    }

    // 檢查 Key 類型是否匹配
    const keyType = detectKeyType(apiKey)
    if (keyType !== user.role) {
      return res.status(401).json({
        error: 'API Key 類型不匹配'
      })
    }

    // 生成 JWT Token
    const token = generateToken(user)

    // 記錄登錄
    console.log(`${user.role} 登錄成功: ${user.name} (${user.email})`)

    res.json({
      success: true,
      data: {
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role,
          permissions: user.permissions
        },
        token,
        expires_in: '7d'
      }
    })

  } catch (error) {
    console.error('API Key 登錄錯誤:', error)
    res.status(500).json({
      error: '登錄失敗'
    })
  }
})

// 郵箱密碼登錄
router.post('/email', async (req, res) => {
  try {
    const { email, password } = req.body

    if (!email || !password) {
      return res.status(400).json({
        error: '請提供郵箱和密碼'
      })
    }

    // 查找用戶
    const user = users.get(email)
    if (!user) {
      return res.status(401).json({
        error: '郵箱或密碼錯誤'
      })
    }

    // 驗證密碼
    const isValidPassword = await bcrypt.compare(password, user.password)
    if (!isValidPassword) {
      return res.status(401).json({
        error: '郵箱或密碼錯誤'
      })
    }

    // 生成用戶 API Key（如果沒有的話）
    let userApiKey = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // 生成 JWT Token
    const token = generateToken(user)

    // 記錄登錄
    console.log(`用戶郵箱登錄成功: ${user.name} (${user.email})`)

    res.json({
      success: true,
      data: {
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role,
          permissions: user.permissions,
          api_key: userApiKey
        },
        token,
        expires_in: '7d'
      }
    })

  } catch (error) {
    console.error('郵箱登錄錯誤:', error)
    res.status(500).json({
      error: '登錄失敗'
    })
  }
})

// OAuth 登錄（模擬）
router.post('/oauth/:provider', async (req, res) => {
  try {
    const { provider } = req.params
    const { code, state } = req.body

    // 模擬 OAuth 處理
    const mockUser = {
      id: `oauth_${provider}_${Date.now()}`,
      name: `${provider} 用戶`,
      email: `user@${provider}.com`,
      role: 'user',
      permissions: ['basic_chat', 'file_upload', 'history_view'],
      provider: provider,
      created_at: new Date().toISOString()
    }

    // 生成用戶 API Key
    const userApiKey = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // 生成 JWT Token
    const token = generateToken(mockUser)

    // 記錄登錄
    console.log(`${provider} OAuth 登錄成功: ${mockUser.name} (${mockUser.email})`)

    res.json({
      success: true,
      data: {
        user: {
          ...mockUser,
          api_key: userApiKey
        },
        token,
        expires_in: '7d'
      }
    })

  } catch (error) {
    console.error('OAuth 登錄錯誤:', error)
    res.status(500).json({
      error: 'OAuth 登錄失敗'
    })
  }
})

// 驗證 Token
router.post('/verify', async (req, res) => {
  try {
    const { token } = req.body

    if (!token) {
      return res.status(400).json({
        error: '請提供認證令牌'
      })
    }

    // 驗證 JWT Token
    const decoded = jwt.verify(token, JWT_SECRET)

    res.json({
      success: true,
      data: {
        user: {
          id: decoded.id,
          email: decoded.email,
          role: decoded.role,
          permissions: decoded.permissions
        },
        valid: true
      }
    })

  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        error: '無效的認證令牌'
      })
    }
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: '認證令牌已過期'
      })
    }

    console.error('Token 驗證錯誤:', error)
    res.status(500).json({
      error: 'Token 驗證失敗'
    })
  }
})

// 刷新 Token
router.post('/refresh', async (req, res) => {
  try {
    const { token } = req.body

    if (!token) {
      return res.status(400).json({
        error: '請提供認證令牌'
      })
    }

    // 驗證舊 Token（忽略過期）
    const decoded = jwt.verify(token, JWT_SECRET, { ignoreExpiration: true })

    // 生成新 Token
    const newToken = generateToken({
      id: decoded.id,
      email: decoded.email,
      role: decoded.role,
      permissions: decoded.permissions
    })

    res.json({
      success: true,
      data: {
        token: newToken,
        expires_in: '7d'
      }
    })

  } catch (error) {
    console.error('Token 刷新錯誤:', error)
    res.status(401).json({
      error: 'Token 刷新失敗'
    })
  }
})

// 登出
router.post('/logout', (req, res) => {
  // 在實際應用中，這裡可以將 Token 加入黑名單
  res.json({
    success: true,
    message: '登出成功'
  })
})

// 獲取用戶信息（需要認證）
router.get('/me', async (req, res) => {
  try {
    const authHeader = req.headers.authorization
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: '請提供認證令牌'
      })
    }

    const token = authHeader.substring(7)
    const decoded = jwt.verify(token, JWT_SECRET)

    res.json({
      success: true,
      data: {
        user: {
          id: decoded.id,
          email: decoded.email,
          role: decoded.role,
          permissions: decoded.permissions
        }
      }
    })

  } catch (error) {
    console.error('獲取用戶信息錯誤:', error)
    res.status(401).json({
      error: '認證失敗'
    })
  }
})

module.exports = router

