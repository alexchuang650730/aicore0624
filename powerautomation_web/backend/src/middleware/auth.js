const jwt = require('jsonwebtoken')

const JWT_SECRET = process.env.JWT_SECRET || 'powerautomation_secret_key_2024'

const authMiddleware = (req, res, next) => {
  try {
    // 獲取 Authorization header
    const authHeader = req.headers.authorization

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: '請提供認證令牌',
        code: 'NO_TOKEN'
      })
    }

    // 提取 token
    const token = authHeader.substring(7)

    // 驗證 token
    const decoded = jwt.verify(token, JWT_SECRET)

    // 將用戶信息添加到請求對象
    req.user = {
      id: decoded.id,
      email: decoded.email,
      role: decoded.role,
      permissions: decoded.permissions || []
    }

    next()

  } catch (error) {
    console.error('認證中間件錯誤:', error)

    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        error: '無效的認證令牌',
        code: 'INVALID_TOKEN'
      })
    }

    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: '認證令牌已過期',
        code: 'TOKEN_EXPIRED'
      })
    }

    return res.status(401).json({
      error: '認證失敗',
      code: 'AUTH_FAILED'
    })
  }
}

module.exports = authMiddleware

