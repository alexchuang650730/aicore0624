import { useState, useEffect, useCallback } from 'react'

const useAuth = () => {
  const [authRequest, setAuthRequest] = useState(null)
  const [isAuthModalVisible, setIsAuthModalVisible] = useState(false)
  const [authHistory, setAuthHistory] = useState([])

  // 监听认证请求
  useEffect(() => {
    const handleAuthRequest = (event) => {
      const { detail } = event
      if (detail && detail.type === 'auth_request') {
        setAuthRequest(detail)
        setIsAuthModalVisible(true)
      }
    }

    // 监听自定义事件
    window.addEventListener('auth_request', handleAuthRequest)
    
    // 监听来自HITL MCP的认证请求
    const checkForAuthRequests = async () => {
      try {
        const response = await fetch('/api/auth/check', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.has_pending_request) {
            setAuthRequest(data.request)
            setIsAuthModalVisible(true)
          }
        }
      } catch (error) {
        console.error('检查认证请求失败:', error)
      }
    }

    // 定期检查认证请求
    const interval = setInterval(checkForAuthRequests, 2000)

    return () => {
      window.removeEventListener('auth_request', handleAuthRequest)
      clearInterval(interval)
    }
  }, [])

  // 提交认证信息
  const submitAuth = useCallback(async (credentials) => {
    if (!authRequest) {
      throw new Error('没有待处理的认证请求')
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001'}/api/auth/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          request_id: authRequest.request_id,
          credentials: credentials
        })
      })

      const result = await response.json()

      if (result.success) {
        // 记录认证历史
        setAuthHistory(prev => [...prev, {
          id: authRequest.request_id,
          auth_type: authRequest.auth_type,
          timestamp: new Date().toISOString(),
          status: 'completed'
        }])

        // 关闭模态框
        setIsAuthModalVisible(false)
        setAuthRequest(null)

        // 触发成功事件
        window.dispatchEvent(new CustomEvent('auth_success', {
          detail: {
            request_id: authRequest.request_id,
            auth_type: authRequest.auth_type
          }
        }))

        return result
      } else {
        throw new Error(result.error || '提交认证信息失败')
      }
    } catch (error) {
      console.error('提交认证信息失败:', error)
      throw error
    }
  }, [authRequest])

  // 取消认证
  const cancelAuth = useCallback(async () => {
    if (!authRequest) {
      return
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001'}/api/auth/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          request_id: authRequest.request_id
        })
      })

      const result = await response.json()

      if (result.success) {
        // 记录认证历史
        setAuthHistory(prev => [...prev, {
          id: authRequest.request_id,
          auth_type: authRequest.auth_type,
          timestamp: new Date().toISOString(),
          status: 'cancelled'
        }])
      }
    } catch (error) {
      console.error('取消认证请求失败:', error)
    } finally {
      // 无论成功失败都关闭模态框
      setIsAuthModalVisible(false)
      setAuthRequest(null)

      // 触发取消事件
      window.dispatchEvent(new CustomEvent('auth_cancelled', {
        detail: {
          request_id: authRequest?.request_id,
          auth_type: authRequest?.auth_type
        }
      }))
    }
  }, [authRequest])

  // 手动触发认证请求（用于测试）
  const triggerAuthRequest = useCallback((authType, context = {}) => {
    const mockRequest = {
      type: 'auth_request',
      auth_type: authType,
      title: `需要${authType}认证`,
      description: `请提供${authType}认证信息`,
      fields: getFieldsForAuthType(authType),
      security_level: 'high',
      context: context,
      request_id: `test_${authType}_${Date.now()}`
    }

    setAuthRequest(mockRequest)
    setIsAuthModalVisible(true)
  }, [])

  // 获取认证历史
  const getAuthHistory = useCallback(() => {
    return authHistory
  }, [authHistory])

  // 清除认证历史
  const clearAuthHistory = useCallback(() => {
    setAuthHistory([])
  }, [])

  return {
    authRequest,
    isAuthModalVisible,
    authHistory,
    submitAuth,
    cancelAuth,
    triggerAuthRequest,
    getAuthHistory,
    clearAuthHistory
  }
}

// 根据认证类型获取字段配置
const getFieldsForAuthType = (authType) => {
  const fieldConfigs = {
    'manus_login': [
      {
        name: 'email',
        type: 'email',
        label: '邮箱地址',
        placeholder: '请输入Manus账户邮箱',
        required: true,
        validation: 'email'
      },
      {
        name: 'password',
        type: 'password',
        label: '密码',
        placeholder: '请输入Manus账户密码',
        required: true,
        validation: 'required'
      }
    ],
    'github_token': [
      {
        name: 'token',
        type: 'password',
        label: 'GitHub个人访问令牌',
        placeholder: 'github_pat_...',
        required: true,
        validation: 'required'
      }
    ],
    'ec2_pem_key': [
      {
        name: 'pem_content',
        type: 'textarea',
        label: 'PEM私钥内容',
        placeholder: '-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----',
        required: true,
        validation: 'required'
      },
      {
        name: 'key_name',
        type: 'text',
        label: '密钥名称',
        placeholder: '例如: my-ec2-key',
        required: true,
        validation: 'required'
      },
      {
        name: 'server_ip',
        type: 'text',
        label: '服务器IP',
        placeholder: '例如: 18.212.49.136',
        required: false,
        validation: 'ip'
      },
      {
        name: 'username',
        type: 'text',
        label: '用户名',
        placeholder: '例如: ec2-user',
        required: false,
        validation: 'optional'
      }
    ],
    'anthropic_api_key': [
      {
        name: 'api_key',
        type: 'password',
        label: 'Anthropic API密钥',
        placeholder: 'sk-ant-...',
        required: true,
        validation: 'required'
      }
    ]
  }

  return fieldConfigs[authType] || []
}

export default useAuth

