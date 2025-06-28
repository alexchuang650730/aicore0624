import React, { useState, useEffect } from 'react'
import { usePermissions } from '../hooks/usePermissions'

const AuthModal = ({ authRequest, onSubmit, onCancel, isVisible }) => {
  const { hasPermission } = usePermissions()
  const [formData, setFormData] = useState({})
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (authRequest && authRequest.fields) {
      // 初始化表单数据
      const initialData = {}
      authRequest.fields.forEach(field => {
        initialData[field.name] = ''
      })
      setFormData(initialData)
      setErrors({})
    }
  }, [authRequest])

  const validateField = (field, value) => {
    switch (field.validation) {
      case 'email':
        return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(value) ? null : '请输入有效的邮箱地址'
      case 'required':
        return value.trim() ? null : '此字段为必填项'
      case 'ip':
        return /^(\\d{1,3}\\.){3}\\d{1,3}$/.test(value) ? null : '请输入有效的IP地址'
      case 'optional':
        return null
      default:
        return field.required && !value.trim() ? '此字段为必填项' : null
    }
  }

  const handleInputChange = (fieldName, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }))

    // 清除错误
    if (errors[fieldName]) {
      setErrors(prev => ({
        ...prev,
        [fieldName]: null
      }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    // 验证表单
    const newErrors = {}
    if (authRequest && authRequest.fields) {
      authRequest.fields.forEach(field => {
        if (field.required || formData[field.name]) {
          const error = validateField(field, formData[field.name])
          if (error) {
            newErrors[field.name] = error
          }
        }
      })
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      setIsSubmitting(false)
      return
    }

    try {
      await onSubmit(formData)
    } catch (error) {
      console.error('提交认证信息失败:', error)
      setErrors({ general: '提交失败，请重试' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const getSecurityIcon = (level) => {
    switch (level) {
      case 'high': return '🔒'
      case 'medium': return '🔐'
      case 'low': return '🔓'
      default: return '🔒'
    }
  }

  const getAuthTypeIcon = (authType) => {
    const icons = {
      'manus_login': '🌐',
      'github_token': '🐙',
      'ec2_pem_key': '🔑',
      'anthropic_api_key': '🤖',
      'openai_api_key': '🧠',
      'redis_password': '🗄️',
      'database_password': '💾'
    }
    return icons[authType] || '🔐'
  }

  if (!isVisible || !authRequest) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4 border border-purple-500/30 max-h-[90vh] overflow-y-auto">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{getAuthTypeIcon(authRequest.auth_type)}</span>
            <div>
              <h3 className="text-lg font-semibold text-white">{authRequest.title}</h3>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <span>{getSecurityIcon(authRequest.security_level)}</span>
                <span>安全级别: {authRequest.security_level}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 描述 */}
        <div className="mb-4 p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
          <p className="text-sm text-purple-200">{authRequest.description}</p>
          {authRequest.context && (
            <div className="mt-2 text-xs text-gray-400">
              {authRequest.context.purpose && (
                <div>用途: {authRequest.context.purpose}</div>
              )}
              {authRequest.context.platform && (
                <div>平台: {authRequest.context.platform}</div>
              )}
              {authRequest.context.service && (
                <div>服务: {authRequest.context.service}</div>
              )}
              {authRequest.context.repository && (
                <div>仓库: {authRequest.context.repository}</div>
              )}
            </div>
          )}
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {authRequest.fields && authRequest.fields.map(field => (
            <div key={field.name}>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                {field.label}
                {field.required && <span className="text-red-400 ml-1">*</span>}
              </label>
              
              {field.type === 'textarea' ? (
                <textarea
                  value={formData[field.name] || ''}
                  onChange={(e) => handleInputChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  className={`w-full px-3 py-2 bg-gray-700 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-vertical min-h-[100px] ${
                    errors[field.name] ? 'border-red-500' : 'border-gray-600'
                  }`}
                  required={field.required}
                />
              ) : (
                <input
                  type={field.type}
                  value={formData[field.name] || ''}
                  onChange={(e) => handleInputChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  className={`w-full px-3 py-2 bg-gray-700 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 ${
                    errors[field.name] ? 'border-red-500' : 'border-gray-600'
                  }`}
                  required={field.required}
                />
              )}
              
              {errors[field.name] && (
                <p className="mt-1 text-sm text-red-400">{errors[field.name]}</p>
              )}
            </div>
          ))}

          {/* 通用错误信息 */}
          {errors.general && (
            <div className="p-3 bg-red-500/10 rounded-lg border border-red-500/20">
              <p className="text-sm text-red-400">{errors.general}</p>
            </div>
          )}

          {/* 安全提示 */}
          <div className="p-3 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
            <div className="flex items-start gap-2">
              <span className="text-yellow-400">⚠️</span>
              <div className="text-xs text-yellow-200">
                <div className="font-medium">安全提示:</div>
                <div>• 认证信息仅用于当前操作，不会永久存储</div>
                <div>• 系统会在操作完成后自动清除敏感信息</div>
                <div>• 请确保在安全的网络环境中输入认证信息</div>
                <div>• 如有疑问，请联系系统管理员</div>
              </div>
            </div>
          </div>

          {/* 按钮 */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors disabled:opacity-50"
              disabled={isSubmitting}
            >
              取消
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>提交中...</span>
                </div>
              ) : (
                '确认提交'
              )}
            </button>
          </div>
        </form>

        {/* 请求ID（调试用） */}
        {process.env.NODE_ENV === 'development' && authRequest.request_id && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <p className="text-xs text-gray-500">
              Request ID: {authRequest.request_id}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AuthModal

