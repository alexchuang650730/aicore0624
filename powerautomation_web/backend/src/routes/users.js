const express = require('express')
const router = express.Router()

// 獲取當前用戶信息
router.get('/profile', (req, res) => {
  try {
    const user = req.user

    res.json({
      success: true,
      data: {
        user: {
          id: user.id,
          email: user.email,
          role: user.role,
          permissions: user.permissions,
          profile: {
            name: user.name || '用戶',
            avatar: user.avatar || null,
            created_at: user.created_at || new Date().toISOString(),
            last_login: new Date().toISOString()
          }
        }
      }
    })

  } catch (error) {
    console.error('獲取用戶信息錯誤:', error)
    res.status(500).json({
      error: '獲取用戶信息失敗'
    })
  }
})

// 更新用戶資料
router.put('/profile', (req, res) => {
  try {
    const { name, avatar } = req.body
    const user = req.user

    // 這裡應該更新數據庫
    console.log(`用戶 ${user.id} 更新資料:`, { name, avatar })

    res.json({
      success: true,
      data: {
        user: {
          ...user,
          name: name || user.name,
          avatar: avatar || user.avatar
        }
      },
      message: '用戶資料更新成功'
    })

  } catch (error) {
    console.error('更新用戶資料錯誤:', error)
    res.status(500).json({
      error: '更新用戶資料失敗'
    })
  }
})

// 獲取用戶統計
router.get('/stats', (req, res) => {
  try {
    const user = req.user

    const mockStats = {
      total_sessions: Math.floor(Math.random() * 100) + 10,
      total_requests: Math.floor(Math.random() * 1000) + 50,
      total_credits_used: Math.floor(Math.random() * 500) + 20,
      remaining_credits: Math.floor(Math.random() * 1000) + 100,
      last_activity: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
      subscription: user.role === 'developer' ? 'Pro' : 'Basic',
      usage_this_month: {
        requests: Math.floor(Math.random() * 200) + 10,
        credits: Math.floor(Math.random() * 100) + 5
      }
    }

    res.json({
      success: true,
      data: mockStats
    })

  } catch (error) {
    console.error('獲取用戶統計錯誤:', error)
    res.status(500).json({
      error: '獲取用戶統計失敗'
    })
  }
})

// 獲取用戶活動歷史
router.get('/activities', (req, res) => {
  try {
    const { page = 1, limit = 20 } = req.query
    const user = req.user

    const mockActivities = [
      {
        id: 1,
        type: 'login',
        description: '用戶登錄',
        timestamp: new Date(Date.now() - 60000).toISOString(),
        details: { ip: '192.168.1.100', device: 'Chrome/Windows' }
      },
      {
        id: 2,
        type: 'api_request',
        description: 'API 請求處理',
        timestamp: new Date(Date.now() - 120000).toISOString(),
        details: { endpoint: '/api/mcp/process', status: 'success' }
      },
      {
        id: 3,
        type: 'file_upload',
        description: '文件上傳',
        timestamp: new Date(Date.now() - 180000).toISOString(),
        details: { filename: 'document.pdf', size: '2.5MB' }
      },
      {
        id: 4,
        type: 'profile_update',
        description: '更新個人資料',
        timestamp: new Date(Date.now() - 240000).toISOString(),
        details: { fields: ['name', 'avatar'] }
      },
      {
        id: 5,
        type: 'chat',
        description: '聊天對話',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        details: { messages: 5, duration: '10分鐘' }
      }
    ]

    // 分頁
    const startIndex = (page - 1) * limit
    const endIndex = startIndex + parseInt(limit)
    const paginatedActivities = mockActivities.slice(startIndex, endIndex)

    res.json({
      success: true,
      data: {
        activities: paginatedActivities,
        pagination: {
          current_page: parseInt(page),
          per_page: parseInt(limit),
          total: mockActivities.length,
          total_pages: Math.ceil(mockActivities.length / limit)
        }
      }
    })

  } catch (error) {
    console.error('獲取用戶活動錯誤:', error)
    res.status(500).json({
      error: '獲取用戶活動失敗'
    })
  }
})

module.exports = router

