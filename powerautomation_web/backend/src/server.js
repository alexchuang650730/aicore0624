const express = require('express')
const cors = require('cors')
const helmet = require('helmet')
const rateLimit = require('express-rate-limit')
const jwt = require('jsonwebtoken')
const bcrypt = require('bcryptjs')
const { createServer } = require('http')
const { Server } = require('socket.io')

// 導入路由
const authRoutes = require('./routes/auth')
const userRoutes = require('./routes/users')
const adminRoutes = require('./routes/admin')
const systemRoutes = require('./routes/system')

// 導入中間件
const authMiddleware = require('./middleware/auth')
const { roleMiddleware } = require('./middleware/roles')

const app = express()
const server = createServer(app)
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
})

// 基本配置
const PORT = process.env.PORT || 3001
const JWT_SECRET = process.env.JWT_SECRET || 'powerautomation_secret_key_2024'

// 安全中間件
app.use(helmet({
  contentSecurityPolicy: false, // 開發環境下禁用 CSP
}))

// CORS 配置
app.use(cors({
  origin: true, // 允許所有來源
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}))

// 速率限制
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分鐘
  max: 100, // 限制每個 IP 100 次請求
  message: {
    error: '請求過於頻繁，請稍後再試'
  }
})
app.use('/api/', limiter)

// 解析中間件
app.use(express.json({ limit: '10mb' }))
app.use(express.urlencoded({ extended: true, limit: '10mb' }))

// 請求日誌
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`)
  next()
})

// 健康檢查
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    service: 'PowerAutomation Web API'
  })
})

// API 路由
app.use('/api/auth', authRoutes)
app.use('/api/users', authMiddleware, userRoutes)
app.use('/api/admin', authMiddleware, roleMiddleware(['admin']), adminRoutes)
app.use('/api/system', authMiddleware, roleMiddleware(['admin', 'developer']), systemRoutes)

// PowerAutomation MCP 集成端點
app.post('/api/mcp/process', authMiddleware, async (req, res) => {
  try {
    const { request, context } = req.body
    const user = req.user

    // 檢查用戶權限
    if (!user.permissions.includes('mcp_access')) {
      return res.status(403).json({
        error: '無權限訪問 MCP 服務'
      })
    }

    // 模擬 MCP 處理
    const response = {
      id: Date.now(),
      user_id: user.id,
      request: request,
      response: `處理完成：${request}`,
      timestamp: new Date().toISOString(),
      processing_time: Math.random() * 1000 + 500
    }

    // 廣播給管理員（如果需要）
    if (user.role === 'admin') {
      io.emit('mcp_request', {
        user: user.name,
        request: request,
        timestamp: response.timestamp
      })
    }

    res.json({
      success: true,
      data: response
    })

  } catch (error) {
    console.error('MCP 處理錯誤:', error)
    res.status(500).json({
      error: 'MCP 服務處理失敗'
    })
  }
})

// WebSocket 連接處理
io.on('connection', (socket) => {
  console.log('用戶連接:', socket.id)

  socket.on('join_room', (data) => {
    const { userId, role } = data
    socket.join(`user_${userId}`)
    socket.join(`role_${role}`)
    console.log(`用戶 ${userId} (${role}) 加入房間`)
  })

  socket.on('disconnect', () => {
    console.log('用戶斷開連接:', socket.id)
  })
})

// 錯誤處理中間件
app.use((err, req, res, next) => {
  console.error('服務器錯誤:', err)
  
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({ error: '無效的認證令牌' })
  }
  
  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({ error: '認證令牌已過期' })
  }
  
  res.status(500).json({
    error: '服務器內部錯誤',
    message: process.env.NODE_ENV === 'development' ? err.message : '請聯繫管理員'
  })
})

// 404 處理
app.use('*', (req, res) => {
  res.status(404).json({
    error: '接口不存在',
    path: req.originalUrl
  })
})

// 啟動服務器
server.listen(PORT, '0.0.0.0', () => {
  console.log(`
🚀 PowerAutomation Web API 服務器已啟動
📍 地址: http://localhost:${PORT}
🌐 環境: ${process.env.NODE_ENV || 'development'}
⏰ 時間: ${new Date().toLocaleString()}
  `)
})

// 優雅關閉
process.on('SIGTERM', () => {
  console.log('收到 SIGTERM 信號，正在關閉服務器...')
  server.close(() => {
    console.log('服務器已關閉')
    process.exit(0)
  })
})

process.on('SIGINT', () => {
  console.log('收到 SIGINT 信號，正在關閉服務器...')
  server.close(() => {
    console.log('服務器已關閉')
    process.exit(0)
  })
})

module.exports = { app, server, io }

