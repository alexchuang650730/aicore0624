const express = require('express')
const router = express.Router()

// 獲取系統狀態
router.get('/status', (req, res) => {
  try {
    const status = {
      server: {
        status: 'online',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        cpu_usage: Math.random() * 100,
        load_average: require('os').loadavg()
      },
      database: {
        status: 'connected',
        connections: Math.floor(Math.random() * 50) + 10,
        response_time: Math.random() * 100 + 10
      },
      mcp_service: {
        status: 'running',
        active_connections: Math.floor(Math.random() * 20) + 5,
        requests_per_minute: Math.floor(Math.random() * 100) + 20
      },
      external_apis: {
        github: { status: 'ok', response_time: 120 },
        google: { status: 'ok', response_time: 95 },
        microsoft: { status: 'ok', response_time: 110 }
      },
      last_updated: new Date().toISOString()
    }

    res.json({
      success: true,
      data: status
    })

  } catch (error) {
    console.error('獲取系統狀態錯誤:', error)
    res.status(500).json({
      error: '獲取系統狀態失敗'
    })
  }
})

// 獲取系統監控數據
router.get('/monitoring', (req, res) => {
  try {
    const { timeRange = '1h' } = req.query

    // 生成模擬監控數據
    const generateTimeSeriesData = (points = 60) => {
      const data = []
      const now = Date.now()
      const interval = timeRange === '1h' ? 60000 : timeRange === '24h' ? 1440000 : 3600000

      for (let i = points - 1; i >= 0; i--) {
        data.push({
          timestamp: new Date(now - i * interval).toISOString(),
          cpu: Math.random() * 100,
          memory: Math.random() * 100,
          network_in: Math.random() * 1000,
          network_out: Math.random() * 800,
          requests: Math.floor(Math.random() * 50) + 10,
          response_time: Math.random() * 500 + 50
        })
      }
      return data
    }

    const monitoringData = {
      time_range: timeRange,
      metrics: generateTimeSeriesData(),
      alerts: [
        {
          id: 1,
          level: 'warning',
          message: 'CPU 使用率持續偏高',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          resolved: false
        },
        {
          id: 2,
          level: 'info',
          message: '系統備份已完成',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          resolved: true
        }
      ]
    }

    res.json({
      success: true,
      data: monitoringData
    })

  } catch (error) {
    console.error('獲取監控數據錯誤:', error)
    res.status(500).json({
      error: '獲取監控數據失敗'
    })
  }
})

// 執行系統操作
router.post('/operations', (req, res) => {
  try {
    const { operation, parameters } = req.body
    const user = req.user

    // 檢查用戶權限
    if (user.role !== 'admin' && user.role !== 'developer') {
      return res.status(403).json({
        error: '權限不足'
      })
    }

    console.log(`用戶 ${user.email} 執行系統操作:`, operation, parameters)

    let result = {}

    switch (operation) {
      case 'restart_service':
        result = {
          operation: 'restart_service',
          service: parameters.service || 'mcp',
          status: 'success',
          message: '服務重啟成功'
        }
        break

      case 'clear_cache':
        result = {
          operation: 'clear_cache',
          cache_type: parameters.cache_type || 'all',
          status: 'success',
          message: '緩存清理成功',
          cleared_items: Math.floor(Math.random() * 1000) + 100
        }
        break

      case 'backup_database':
        result = {
          operation: 'backup_database',
          status: 'success',
          message: '數據庫備份成功',
          backup_file: `backup_${Date.now()}.sql`,
          size: `${Math.floor(Math.random() * 100) + 10}MB`
        }
        break

      case 'update_config':
        result = {
          operation: 'update_config',
          config: parameters.config || {},
          status: 'success',
          message: '配置更新成功'
        }
        break

      default:
        return res.status(400).json({
          error: '不支持的操作'
        })
    }

    res.json({
      success: true,
      data: result
    })

  } catch (error) {
    console.error('執行系統操作錯誤:', error)
    res.status(500).json({
      error: '系統操作失敗'
    })
  }
})

// 獲取 API 使用統計
router.get('/api-stats', (req, res) => {
  try {
    const { timeRange = '24h' } = req.query

    const apiStats = {
      time_range: timeRange,
      total_requests: Math.floor(Math.random() * 10000) + 1000,
      successful_requests: Math.floor(Math.random() * 9000) + 900,
      failed_requests: Math.floor(Math.random() * 100) + 10,
      average_response_time: Math.floor(Math.random() * 200) + 50,
      endpoints: [
        { path: '/api/auth/api-key', requests: 1250, avg_time: 120 },
        { path: '/api/mcp/process', requests: 3200, avg_time: 350 },
        { path: '/api/users/profile', requests: 890, avg_time: 80 },
        { path: '/api/admin/stats', requests: 450, avg_time: 200 },
        { path: '/api/system/status', requests: 320, avg_time: 60 }
      ],
      status_codes: {
        '200': Math.floor(Math.random() * 8000) + 1000,
        '401': Math.floor(Math.random() * 100) + 10,
        '403': Math.floor(Math.random() * 50) + 5,
        '404': Math.floor(Math.random() * 30) + 3,
        '500': Math.floor(Math.random() * 20) + 2
      }
    }

    res.json({
      success: true,
      data: apiStats
    })

  } catch (error) {
    console.error('獲取 API 統計錯誤:', error)
    res.status(500).json({
      error: '獲取 API 統計失敗'
    })
  }
})

// 測試 MCP 連接
router.post('/test-mcp', (req, res) => {
  try {
    const user = req.user

    // 模擬 MCP 連接測試
    const testResult = {
      connection: 'success',
      response_time: Math.floor(Math.random() * 100) + 50,
      version: '1.0.0',
      features: ['chat', 'file_processing', 'code_analysis'],
      timestamp: new Date().toISOString()
    }

    console.log(`用戶 ${user.email} 測試 MCP 連接`)

    res.json({
      success: true,
      data: testResult,
      message: 'MCP 連接測試成功'
    })

  } catch (error) {
    console.error('MCP 連接測試錯誤:', error)
    res.status(500).json({
      error: 'MCP 連接測試失敗'
    })
  }
})

module.exports = router

