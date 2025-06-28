// MCP服务 - 生产环境配置
class MCPService {
  constructor() {
    // 生产环境后端URL
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'https://y0h0i3cyzmop.manus.space/api'
    this.backendURL = import.meta.env.VITE_BACKEND_URL || 'https://y0h0i3cyzmop.manus.space'
    this.connected = false
    this.contextCapacity = '200K'
    
    console.log('🚀 SmartUI MCP Service 初始化')
    console.log('📡 后端API:', this.baseURL)
    console.log('🔗 后端服务:', this.backendURL)
  }

  // 检查连接状态
  async checkConnection() {
    try {
      const response = await fetch(`${this.backendURL}/health`, {
        method: 'GET',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      this.connected = response.ok
      const data = await response.json()
      
      return {
        connected: this.connected,
        status: response.status,
        message: this.connected ? 'SmartUI 权限管理系统连接成功' : '连接失败',
        service: data.service || 'unknown',
        version: data.version || '1.0.0'
      }
    } catch (error) {
      this.connected = false
      return {
        connected: false,
        status: 'error',
        message: `连接失败: ${error.message}`,
        service: 'smartui-permission-backend',
        version: '1.0.0'
      }
    }
  }

  // 处理消息 - 整合Claude Code分析到AICore上下文
  async processMessage(context) {
    try {
      const {
        message,
        selectedFile,
        repository,
        chatHistory,
        enableCodeAnalysis = true,
        contextCapacity = '200K',
        analysisMode = 'integrated'
      } = context

      // 构建分析请求
      const payload = {
        context: {
          // 基础上下文
          user_role: this.getUserRole(),
          repository: repository,
          selected_file: selectedFile,
          chat_history: chatHistory,
          
          // Claude Code 整合配置
          enable_code_analysis: enableCodeAnalysis,
          context_capacity: contextCapacity,
          analysis_mode: analysisMode,
          
          // 智能分析选项
          auto_analyze_code: true,
          deep_context_understanding: true,
          generate_recommendations: true,
          
          // 请求内容
          message: message,
          
          // 功能标志
          use_claude_code: true,
          integrate_smartinvention: true,
          enable_caching: true
        },
        
        // 元数据
        timestamp: new Date().toISOString(),
        session_id: this.getSessionId(),
        tokens_used: 0
      }

      // 发送到后端代码分析端点
      const response = await fetch(`${this.baseURL}/code/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getApiKey()}`,
          'X-Context-Capacity': contextCapacity,
          'X-Analysis-Mode': analysisMode
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(`HTTP ${response.status}: ${errorData.error || response.statusText}`)
      }

      const result = await response.json()
      
      // 处理响应，提取整合的分析结果
      return this.processResponse(result)
      
    } catch (error) {
      console.error('MCP处理失败:', error)
      
      // 返回错误响应
      return {
        content: `❌ **处理失败**\n\n错误信息: ${error.message}\n\n请检查网络连接或API权限。`,
        error: true,
        timestamp: new Date().toISOString(),
        service: 'smartui-permission-backend'
      }
    }
  }

  // 处理后端响应
  processResponse(result) {
    const {
      response,
      claude_code_analysis,
      recommendations,
      tokens_used,
      processing_time,
      cache_hit,
      system_type
    } = result

    // 构建整合的响应
    let content = response || '智能分析完成'
    
    // 如果有Claude Code分析结果，自然地整合到响应中
    if (claude_code_analysis) {
      const analysis = claude_code_analysis
      
      // 将分析结果自然地融入到响应中
      if (analysis.summary) {
        content += `\n\n## 🧠 智能分析\n${analysis.summary}`
      }
      
      if (analysis.key_findings && analysis.key_findings.length > 0) {
        content += `\n\n### 关键发现：\n`
        analysis.key_findings.forEach((finding, idx) => {
          content += `${idx + 1}. ${finding}\n`
        })
      }
      
      if (analysis.quality_score) {
        content += `\n### 代码质量评分：${analysis.quality_score}/10`
      }
    }

    // 添加智能建议
    if (recommendations && recommendations.length > 0) {
      content += `\n\n## 💡 智能建议\n`
      recommendations.slice(0, 3).forEach((rec, idx) => {
        content += `${idx + 1}. ${rec}\n`
      })
    }

    // 添加性能信息
    const perfInfo = []
    if (processing_time) perfInfo.push(`处理时间: ${processing_time}`)
    if (tokens_used) perfInfo.push(`Tokens: ${tokens_used}`)
    if (cache_hit !== undefined) perfInfo.push(`缓存: ${cache_hit ? '命中' : '未命中'}`)
    if (system_type) perfInfo.push(`系统: ${system_type}`)
    
    if (perfInfo.length > 0) {
      content += `\n\n---\n*${perfInfo.join(' | ')}*`
    }

    return {
      content,
      codeAnalysis: claude_code_analysis,
      recommendations,
      tokens: tokens_used || 0,
      processing_time,
      cache_hit,
      system_type: system_type || 'SmartUI + AICore + Claude Code SDK',
      timestamp: new Date().toISOString()
    }
  }

  // 验证API Key
  async verifyApiKey(apiKey) {
    try {
      const response = await fetch(`${this.baseURL}/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ api_key: apiKey })
      })

      if (response.ok) {
        return await response.json()
      }
      
      return { authenticated: false, error: 'API Key验证失败' }
    } catch (error) {
      return { authenticated: false, error: error.message }
    }
  }

  // 获取用户权限
  async getUserPermissions(apiKey) {
    try {
      const response = await fetch(`${this.baseURL}/auth/permissions`, {
        headers: {
          'Authorization': `Bearer ${apiKey}`
        }
      })

      if (response.ok) {
        return await response.json()
      }
      
      return { permissions: [], role: null }
    } catch (error) {
      console.error('获取权限失败:', error)
      return { permissions: [], role: null }
    }
  }

  // 检查特定权限
  async checkPermission(permission, apiKey = null) {
    try {
      const key = apiKey || this.getApiKey()
      const response = await fetch(`${this.baseURL}/auth/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${key}`
        },
        body: JSON.stringify({ permission })
      })

      if (response.ok) {
        const result = await response.json()
        return result.has_permission
      }
      
      return false
    } catch (error) {
      console.error('权限检查失败:', error)
      return false
    }
  }

  // 获取用户角色
  getUserRole() {
    const apiKey = this.getApiKey()
    
    if (apiKey.startsWith('admin_')) return 'admin'
    if (apiKey.startsWith('dev_')) return 'developer'
    if (apiKey.startsWith('user_')) return 'user'
    
    return 'guest'
  }

  // 获取API Key
  getApiKey() {
    return localStorage.getItem('smartui_api_key') || ''
  }

  // 设置API Key
  setApiKey(apiKey) {
    localStorage.setItem('smartui_api_key', apiKey)
  }

  // 获取会话ID
  getSessionId() {
    let sessionId = localStorage.getItem('smartui_session_id')
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('smartui_session_id', sessionId)
    }
    return sessionId
  }

  // 获取系统状态
  async getSystemStatus() {
    try {
      const response = await fetch(`${this.baseURL}/system/status`)
      
      if (response.ok) {
        return await response.json()
      }
      
      return {
        status: 'error',
        message: '无法获取系统状态'
      }
    } catch (error) {
      return {
        status: 'error',
        message: error.message
      }
    }
  }

  // 文件上传
  async uploadFiles(files) {
    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      const response = await fetch(`${this.baseURL}/files/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getApiKey()}`
        },
        body: formData
      })

      return await response.json()
    } catch (error) {
      return { error: error.message }
    }
  }

  // 删除文件
  async deleteFile(filePath) {
    try {
      const response = await fetch(`${this.baseURL}/files/delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getApiKey()}`
        },
        body: JSON.stringify({ file_path: filePath })
      })

      return await response.json()
    } catch (error) {
      return { error: error.message }
    }
  }

  // 获取访问日志（管理员权限）
  async getAccessLogs(days = 7) {
    try {
      const response = await fetch(`${this.baseURL}/admin/logs?days=${days}`, {
        headers: {
          'Authorization': `Bearer ${this.getApiKey()}`
        }
      })

      if (response.ok) {
        return await response.json()
      }
      
      return { logs: [], total: 0 }
    } catch (error) {
      console.error('获取日志失败:', error)
      return { logs: [], total: 0 }
    }
  }

  // 获取用户列表（管理员权限）
  async getUsers() {
    try {
      const response = await fetch(`${this.baseURL}/admin/users`, {
        headers: {
          'Authorization': `Bearer ${this.getApiKey()}`
        }
      })

      if (response.ok) {
        return await response.json()
      }
      
      return { users: [] }
    } catch (error) {
      console.error('获取用户列表失败:', error)
      return { users: [] }
    }
  }
}

// 创建单例实例
const mcpService = new MCPService()

export default mcpService

