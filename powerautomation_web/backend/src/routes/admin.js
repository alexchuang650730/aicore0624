const express = require('express')
const router = express.Router()

// 模擬數據
const mockUsers = [
  { id: 1, name: 'John Doe', email: 'john@example.com', credits: 1200, status: 'active', role: 'developer', created_at: '2024-01-15' },
  { id: 2, name: 'Alice Smith', email: 'alice@example.com', credits: 320, status: 'active', role: 'user', created_at: '2024-02-20' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', credits: 1300, status: 'active', role: 'developer', created_at: '2024-03-10' },
  { id: 4, name: 'Carol Williams', email: 'carol@example.com', credits: 2300, status: 'inactive', role: 'user', created_at: '2024-01-05' },
  { id: 5, name: 'David Brown', email: 'david@example.com', credits: 850, status: 'active', role: 'user', created_at: '2024-04-12' },
]

const mockSystemStats = {
  totalUsers: 1247,
  activeUsers: 892,
  totalRequests: 15420,
  systemUptime: '99.9%',
  serverLoad: '45%',
  memoryUsage: '62%',
  diskUsage: '78%',
  lastUpdated: new Date().toISOString()
}

const mockUsageData = [
  { name: '1月', value: 400, users: 120, requests: 2400 },
  { name: '2月', value: 300, users: 150, requests: 1800 },
  { name: '3月', value: 600, users: 200, requests: 3600 },
  { name: '4月', value: 800, users: 280, requests: 4800 },
  { name: '5月', value: 1000, users: 350, requests: 6000 },
  { name: '6月', value: 1200, users: 420, requests: 7200 },
]

// 獲取系統統計
router.get('/stats', (req, res) => {
  try {
    res.json({
      success: true,
      data: {
        ...mockSystemStats,
        growth: {
          users: '+12%',
          requests: '+25%',
          revenue: '+18%'
        }
      }
    })
  } catch (error) {
    console.error('獲取系統統計錯誤:', error)
    res.status(500).json({
      error: '獲取統計數據失敗'
    })
  }
})

// 獲取使用量趨勢
router.get('/usage-trends', (req, res) => {
  try {
    res.json({
      success: true,
      data: mockUsageData
    })
  } catch (error) {
    console.error('獲取使用量趨勢錯誤:', error)
    res.status(500).json({
      error: '獲取趨勢數據失敗'
    })
  }
})

// 獲取用戶列表
router.get('/users', (req, res) => {
  try {
    const { page = 1, limit = 10, role, status, search } = req.query
    
    let filteredUsers = [...mockUsers]

    // 角色過濾
    if (role && role !== 'all') {
      filteredUsers = filteredUsers.filter(user => user.role === role)
    }

    // 狀態過濾
    if (status && status !== 'all') {
      filteredUsers = filteredUsers.filter(user => user.status === status)
    }

    // 搜索過濾
    if (search) {
      const searchLower = search.toLowerCase()
      filteredUsers = filteredUsers.filter(user => 
        user.name.toLowerCase().includes(searchLower) ||
        user.email.toLowerCase().includes(searchLower)
      )
    }

    // 分頁
    const startIndex = (page - 1) * limit
    const endIndex = startIndex + parseInt(limit)
    const paginatedUsers = filteredUsers.slice(startIndex, endIndex)

    res.json({
      success: true,
      data: {
        users: paginatedUsers,
        pagination: {
          current_page: parseInt(page),
          per_page: parseInt(limit),
          total: filteredUsers.length,
          total_pages: Math.ceil(filteredUsers.length / limit)
        }
      }
    })

  } catch (error) {
    console.error('獲取用戶列表錯誤:', error)
    res.status(500).json({
      error: '獲取用戶列表失敗'
    })
  }
})

// 獲取單個用戶詳情
router.get('/users/:id', (req, res) => {
  try {
    const { id } = req.params
    const user = mockUsers.find(u => u.id === parseInt(id))

    if (!user) {
      return res.status(404).json({
        error: '用戶不存在'
      })
    }

    // 添加額外的用戶詳情
    const userDetails = {
      ...user,
      last_login: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      total_sessions: Math.floor(Math.random() * 100) + 10,
      total_requests: Math.floor(Math.random() * 1000) + 50,
      subscription: user.role === 'developer' ? 'Pro' : 'Basic'
    }

    res.json({
      success: true,
      data: userDetails
    })

  } catch (error) {
    console.error('獲取用戶詳情錯誤:', error)
    res.status(500).json({
      error: '獲取用戶詳情失敗'
    })
  }
})

// 更新用戶信息
router.put('/users/:id', (req, res) => {
  try {
    const { id } = req.params
    const { name, email, role, status, credits } = req.body

    const userIndex = mockUsers.findIndex(u => u.id === parseInt(id))
    if (userIndex === -1) {
      return res.status(404).json({
        error: '用戶不存在'
      })
    }

    // 更新用戶信息
    if (name) mockUsers[userIndex].name = name
    if (email) mockUsers[userIndex].email = email
    if (role) mockUsers[userIndex].role = role
    if (status) mockUsers[userIndex].status = status
    if (credits !== undefined) mockUsers[userIndex].credits = credits

    res.json({
      success: true,
      data: mockUsers[userIndex],
      message: '用戶信息更新成功'
    })

  } catch (error) {
    console.error('更新用戶信息錯誤:', error)
    res.status(500).json({
      error: '更新用戶信息失敗'
    })
  }
})

// 刪除用戶
router.delete('/users/:id', (req, res) => {
  try {
    const { id } = req.params
    const userIndex = mockUsers.findIndex(u => u.id === parseInt(id))

    if (userIndex === -1) {
      return res.status(404).json({
        error: '用戶不存在'
      })
    }

    const deletedUser = mockUsers.splice(userIndex, 1)[0]

    res.json({
      success: true,
      data: deletedUser,
      message: '用戶刪除成功'
    })

  } catch (error) {
    console.error('刪除用戶錯誤:', error)
    res.status(500).json({
      error: '刪除用戶失敗'
    })
  }
})

// 批量操作用戶
router.post('/users/batch', (req, res) => {
  try {
    const { action, userIds } = req.body

    if (!action || !userIds || !Array.isArray(userIds)) {
      return res.status(400).json({
        error: '請提供有效的操作和用戶ID列表'
      })
    }

    const affectedUsers = mockUsers.filter(user => userIds.includes(user.id))

    switch (action) {
      case 'activate':
        affectedUsers.forEach(user => user.status = 'active')
        break
      case 'deactivate':
        affectedUsers.forEach(user => user.status = 'inactive')
        break
      case 'delete':
        userIds.forEach(id => {
          const index = mockUsers.findIndex(u => u.id === id)
          if (index !== -1) mockUsers.splice(index, 1)
        })
        break
      default:
        return res.status(400).json({
          error: '不支持的操作'
        })
    }

    res.json({
      success: true,
      data: {
        action,
        affected_count: affectedUsers.length
      },
      message: `批量${action}操作完成`
    })

  } catch (error) {
    console.error('批量操作錯誤:', error)
    res.status(500).json({
      error: '批量操作失敗'
    })
  }
})

// 獲取系統配置
router.get('/config', (req, res) => {
  try {
    const config = {
      ui_configs: {
        community: {
          name: 'Community版',
          nodes: ['code'],
          color: 'green',
          features: ['基礎編碼', '開源透明'],
          enabled: true
        },
        personal: {
          name: 'Personal版',
          nodes: ['code', 'test', 'deploy'],
          color: 'blue',
          features: ['編碼實現', '測試驗證', '部署發布', '隱私雲同步'],
          enabled: true
        },
        enterprise: {
          name: 'Enterprise版',
          nodes: ['analysis', 'design', 'code', 'test', 'deploy', 'monitor'],
          color: 'purple',
          features: ['需求分析', '架構設計', '編碼實現', '測試驗證', '部署發布', '監控運維'],
          enabled: true
        }
      },
      system_settings: {
        max_users: 10000,
        rate_limit: 100,
        session_timeout: '7d',
        debug_mode: false,
        maintenance_mode: false
      }
    }

    res.json({
      success: true,
      data: config
    })

  } catch (error) {
    console.error('獲取系統配置錯誤:', error)
    res.status(500).json({
      error: '獲取系統配置失敗'
    })
  }
})

// 更新系統配置
router.put('/config', (req, res) => {
  try {
    const { ui_configs, system_settings } = req.body

    // 這裡應該保存到數據庫
    console.log('更新系統配置:', { ui_configs, system_settings })

    res.json({
      success: true,
      message: '系統配置更新成功'
    })

  } catch (error) {
    console.error('更新系統配置錯誤:', error)
    res.status(500).json({
      error: '更新系統配置失敗'
    })
  }
})

// 獲取系統日誌
router.get('/logs', (req, res) => {
  try {
    const { level = 'all', limit = 100 } = req.query

    const mockLogs = [
      { id: 1, level: 'info', message: '用戶登錄成功', timestamp: new Date().toISOString(), user: 'john@example.com' },
      { id: 2, level: 'warning', message: '磁盤使用率達到 80%', timestamp: new Date(Date.now() - 60000).toISOString() },
      { id: 3, level: 'error', message: 'API 請求失敗', timestamp: new Date(Date.now() - 120000).toISOString(), details: 'Connection timeout' },
      { id: 4, level: 'info', message: '系統備份完成', timestamp: new Date(Date.now() - 180000).toISOString() },
      { id: 5, level: 'info', message: '新用戶註冊', timestamp: new Date(Date.now() - 240000).toISOString(), user: 'alice@example.com' },
    ]

    let filteredLogs = mockLogs
    if (level !== 'all') {
      filteredLogs = mockLogs.filter(log => log.level === level)
    }

    res.json({
      success: true,
      data: filteredLogs.slice(0, parseInt(limit))
    })

  } catch (error) {
    console.error('獲取系統日誌錯誤:', error)
    res.status(500).json({
      error: '獲取系統日誌失敗'
    })
  }
})

module.exports = router

