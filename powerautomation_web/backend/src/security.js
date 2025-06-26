// 安全配置模块
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class SecurityManager {
  constructor() {
    this.securityEvents = [];
    this.blockedIPs = new Set();
    this.suspiciousActivities = new Map();
    this.maxFailedAttempts = 5;
    this.blockDuration = 15 * 60 * 1000; // 15分钟
  }

  // 记录安全事件
  logSecurityEvent(type, ip, details = {}) {
    const event = {
      id: crypto.randomUUID(),
      type,
      ip,
      timestamp: new Date().toISOString(),
      details,
      severity: this.getSeverityLevel(type)
    };

    this.securityEvents.push(event);
    
    // 保持最近1000个事件
    if (this.securityEvents.length > 1000) {
      this.securityEvents.shift();
    }

    // 检查是否需要阻止IP
    this.checkSuspiciousActivity(ip, type);

    console.log(`[SECURITY] ${type}: ${ip} - ${JSON.stringify(details)}`);
    return event;
  }

  // 获取严重级别
  getSeverityLevel(type) {
    const severityMap = {
      'failed_login': 'medium',
      'invalid_token': 'medium',
      'rate_limit_exceeded': 'high',
      'suspicious_request': 'high',
      'sql_injection_attempt': 'critical',
      'xss_attempt': 'critical',
      'unauthorized_access': 'high'
    };
    return severityMap[type] || 'low';
  }

  // 检查可疑活动
  checkSuspiciousActivity(ip, type) {
    if (!this.suspiciousActivities.has(ip)) {
      this.suspiciousActivities.set(ip, {
        failedAttempts: 0,
        lastAttempt: Date.now(),
        events: []
      });
    }

    const activity = this.suspiciousActivities.get(ip);
    activity.events.push({ type, timestamp: Date.now() });
    
    // 清理旧事件（超过1小时）
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    activity.events = activity.events.filter(e => e.timestamp > oneHourAgo);

    // 检查失败登录次数
    if (type === 'failed_login') {
      activity.failedAttempts++;
      activity.lastAttempt = Date.now();

      if (activity.failedAttempts >= this.maxFailedAttempts) {
        this.blockIP(ip, 'Too many failed login attempts');
      }
    }

    // 检查短时间内的多种可疑活动
    const recentEvents = activity.events.filter(e => e.timestamp > Date.now() - 5 * 60 * 1000);
    if (recentEvents.length > 10) {
      this.blockIP(ip, 'Suspicious activity pattern detected');
    }
  }

  // 阻止IP
  blockIP(ip, reason) {
    this.blockedIPs.add(ip);
    this.logSecurityEvent('ip_blocked', ip, { reason });

    // 自动解除阻止
    setTimeout(() => {
      this.unblockIP(ip);
    }, this.blockDuration);
  }

  // 解除IP阻止
  unblockIP(ip) {
    this.blockedIPs.delete(ip);
    this.logSecurityEvent('ip_unblocked', ip);
  }

  // 检查IP是否被阻止
  isIPBlocked(ip) {
    return this.blockedIPs.has(ip);
  }

  // 获取安全统计
  getSecurityStats() {
    const now = Date.now();
    const last24h = now - 24 * 60 * 60 * 1000;
    const recentEvents = this.securityEvents.filter(e => new Date(e.timestamp).getTime() > last24h);

    const eventsByType = {};
    const eventsBySeverity = {};

    recentEvents.forEach(event => {
      eventsByType[event.type] = (eventsByType[event.type] || 0) + 1;
      eventsBySeverity[event.severity] = (eventsBySeverity[event.severity] || 0) + 1;
    });

    return {
      totalEvents: recentEvents.length,
      blockedIPs: this.blockedIPs.size,
      suspiciousIPs: this.suspiciousActivities.size,
      eventsByType,
      eventsBySeverity,
      recentEvents: recentEvents.slice(-10),
      lastUpdated: new Date().toISOString()
    };
  }

  // 输入验证
  validateInput(input, type) {
    const patterns = {
      apiKey: /^[a-zA-Z0-9_-]{40,}$/,
      username: /^[a-zA-Z0-9_]{3,20}$/,
      email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      code: /^[\s\S]{1,10000}$/, // 代码长度限制
      language: /^[a-zA-Z]{2,10}$/
    };

    if (!patterns[type]) {
      return { valid: false, error: 'Unknown validation type' };
    }

    if (!patterns[type].test(input)) {
      return { valid: false, error: `Invalid ${type} format` };
    }

    // 检查恶意内容
    const maliciousPatterns = [
      /<script/i,
      /javascript:/i,
      /on\w+\s*=/i,
      /union\s+select/i,
      /drop\s+table/i,
      /delete\s+from/i,
      /insert\s+into/i,
      /update\s+set/i
    ];

    for (const pattern of maliciousPatterns) {
      if (pattern.test(input)) {
        return { valid: false, error: 'Potentially malicious content detected' };
      }
    }

    return { valid: true };
  }

  // 生成安全报告
  generateSecurityReport() {
    const stats = this.getSecurityStats();
    const report = {
      reportId: crypto.randomUUID(),
      generatedAt: new Date().toISOString(),
      period: '24 hours',
      summary: {
        totalSecurityEvents: stats.totalEvents,
        blockedIPs: stats.blockedIPs,
        suspiciousActivities: stats.suspiciousIPs,
        highSeverityEvents: stats.eventsBySeverity.high || 0,
        criticalEvents: stats.eventsBySeverity.critical || 0
      },
      details: stats,
      recommendations: this.getSecurityRecommendations(stats)
    };

    return report;
  }

  // 获取安全建议
  getSecurityRecommendations(stats) {
    const recommendations = [];

    if (stats.eventsBySeverity.critical > 0) {
      recommendations.push({
        priority: 'high',
        message: '检测到严重安全事件，建议立即检查系统日志',
        action: 'review_critical_events'
      });
    }

    if (stats.blockedIPs > 10) {
      recommendations.push({
        priority: 'medium',
        message: '大量IP被阻止，考虑加强防护措施',
        action: 'enhance_protection'
      });
    }

    if (stats.eventsByType.failed_login > 50) {
      recommendations.push({
        priority: 'medium',
        message: '登录失败次数较多，建议启用双因素认证',
        action: 'enable_2fa'
      });
    }

    if (recommendations.length === 0) {
      recommendations.push({
        priority: 'low',
        message: '系统安全状态良好',
        action: 'maintain_monitoring'
      });
    }

    return recommendations;
  }
}

// 高级监控模块
class AdvancedMonitor {
  constructor() {
    this.metrics = {
      requests: [],
      errors: [],
      performance: [],
      resources: [],
      users: []
    };
    this.alerts = [];
    this.thresholds = {
      responseTime: 1000, // ms
      errorRate: 5, // %
      cpuUsage: 80, // %
      memoryUsage: 85, // %
      diskUsage: 90 // %
    };
  }

  // 记录请求指标
  recordRequest(req, res, responseTime) {
    const metric = {
      timestamp: Date.now(),
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      responseTime,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      size: res.get('Content-Length') || 0
    };

    this.metrics.requests.push(metric);
    this.checkThresholds(metric);
    this.cleanOldMetrics();
  }

  // 记录错误
  recordError(error, req = null) {
    const errorMetric = {
      timestamp: Date.now(),
      message: error.message,
      stack: error.stack,
      url: req ? req.url : null,
      method: req ? req.method : null,
      ip: req ? req.ip : null,
      severity: this.getErrorSeverity(error)
    };

    this.metrics.errors.push(errorMetric);
    this.generateAlert('error', errorMetric);
  }

  // 记录性能指标
  recordPerformance() {
    const performance = {
      timestamp: Date.now(),
      cpu: this.getCPUUsage(),
      memory: this.getMemoryUsage(),
      disk: this.getDiskUsage(),
      network: this.getNetworkStats(),
      activeConnections: this.getActiveConnections()
    };

    this.metrics.performance.push(performance);
    this.checkResourceThresholds(performance);
  }

  // 获取CPU使用率（模拟）
  getCPUUsage() {
    return {
      usage: Math.random() * 30 + 15,
      cores: 4,
      loadAverage: [
        Math.random() * 2,
        Math.random() * 2,
        Math.random() * 2
      ]
    };
  }

  // 获取内存使用情况（模拟）
  getMemoryUsage() {
    const total = 8 * 1024 * 1024 * 1024; // 8GB
    const used = total * (Math.random() * 0.3 + 0.4); // 40-70%
    
    return {
      total,
      used,
      free: total - used,
      usage: (used / total * 100).toFixed(2)
    };
  }

  // 获取磁盘使用情况（模拟）
  getDiskUsage() {
    const total = 100 * 1024 * 1024 * 1024; // 100GB
    const used = total * (Math.random() * 0.3 + 0.5); // 50-80%
    
    return {
      total,
      used,
      free: total - used,
      usage: (used / total * 100).toFixed(2)
    };
  }

  // 获取网络统计（模拟）
  getNetworkStats() {
    return {
      bytesIn: Math.floor(Math.random() * 1000000) + 500000,
      bytesOut: Math.floor(Math.random() * 800000) + 300000,
      packetsIn: Math.floor(Math.random() * 10000) + 5000,
      packetsOut: Math.floor(Math.random() * 8000) + 3000,
      connectionsActive: Math.floor(Math.random() * 50) + 20
    };
  }

  // 获取活跃连接数（模拟）
  getActiveConnections() {
    return Math.floor(Math.random() * 100) + 50;
  }

  // 检查阈值
  checkThresholds(metric) {
    if (metric.responseTime > this.thresholds.responseTime) {
      this.generateAlert('slow_response', {
        responseTime: metric.responseTime,
        url: metric.url,
        threshold: this.thresholds.responseTime
      });
    }
  }

  // 检查资源阈值
  checkResourceThresholds(performance) {
    if (performance.cpu.usage > this.thresholds.cpuUsage) {
      this.generateAlert('high_cpu', {
        usage: performance.cpu.usage,
        threshold: this.thresholds.cpuUsage
      });
    }

    if (parseFloat(performance.memory.usage) > this.thresholds.memoryUsage) {
      this.generateAlert('high_memory', {
        usage: performance.memory.usage,
        threshold: this.thresholds.memoryUsage
      });
    }

    if (parseFloat(performance.disk.usage) > this.thresholds.diskUsage) {
      this.generateAlert('high_disk', {
        usage: performance.disk.usage,
        threshold: this.thresholds.diskUsage
      });
    }
  }

  // 生成告警
  generateAlert(type, data) {
    const alert = {
      id: crypto.randomUUID(),
      type,
      severity: this.getAlertSeverity(type),
      message: this.getAlertMessage(type, data),
      data,
      timestamp: new Date().toISOString(),
      acknowledged: false
    };

    this.alerts.push(alert);
    console.log(`[ALERT] ${alert.severity.toUpperCase()}: ${alert.message}`);

    // 保持最近100个告警
    if (this.alerts.length > 100) {
      this.alerts.shift();
    }
  }

  // 获取告警严重级别
  getAlertSeverity(type) {
    const severityMap = {
      'error': 'high',
      'slow_response': 'medium',
      'high_cpu': 'medium',
      'high_memory': 'high',
      'high_disk': 'high',
      'security_breach': 'critical'
    };
    return severityMap[type] || 'low';
  }

  // 获取告警消息
  getAlertMessage(type, data) {
    const messageMap = {
      'error': `系统错误: ${data.message}`,
      'slow_response': `响应时间过慢: ${data.responseTime}ms (阈值: ${data.threshold}ms)`,
      'high_cpu': `CPU使用率过高: ${data.usage}% (阈值: ${data.threshold}%)`,
      'high_memory': `内存使用率过高: ${data.usage}% (阈值: ${data.threshold}%)`,
      'high_disk': `磁盘使用率过高: ${data.usage}% (阈值: ${data.threshold}%)`,
      'security_breach': '检测到安全威胁'
    };
    return messageMap[type] || '未知告警类型';
  }

  // 获取错误严重级别
  getErrorSeverity(error) {
    if (error.message.includes('ECONNREFUSED') || error.message.includes('timeout')) {
      return 'high';
    }
    if (error.message.includes('validation') || error.message.includes('unauthorized')) {
      return 'medium';
    }
    return 'low';
  }

  // 清理旧指标
  cleanOldMetrics() {
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    
    this.metrics.requests = this.metrics.requests.filter(m => m.timestamp > oneHourAgo);
    this.metrics.errors = this.metrics.errors.filter(m => m.timestamp > oneHourAgo);
    this.metrics.performance = this.metrics.performance.filter(m => m.timestamp > oneHourAgo);
  }

  // 获取监控统计
  getMonitoringStats() {
    const now = Date.now();
    const oneHourAgo = now - 60 * 60 * 1000;
    
    const recentRequests = this.metrics.requests.filter(r => r.timestamp > oneHourAgo);
    const recentErrors = this.metrics.errors.filter(e => e.timestamp > oneHourAgo);
    const recentPerformance = this.metrics.performance.slice(-1)[0] || {};

    const avgResponseTime = recentRequests.length > 0
      ? recentRequests.reduce((sum, r) => sum + r.responseTime, 0) / recentRequests.length
      : 0;

    const errorRate = recentRequests.length > 0
      ? (recentErrors.length / recentRequests.length * 100)
      : 0;

    return {
      requests: {
        total: recentRequests.length,
        successful: recentRequests.filter(r => r.statusCode < 400).length,
        failed: recentRequests.filter(r => r.statusCode >= 400).length,
        averageResponseTime: Math.round(avgResponseTime)
      },
      errors: {
        total: recentErrors.length,
        rate: errorRate.toFixed(2),
        byType: this.groupErrorsByType(recentErrors)
      },
      performance: recentPerformance,
      alerts: {
        total: this.alerts.length,
        unacknowledged: this.alerts.filter(a => !a.acknowledged).length,
        bySeverity: this.groupAlertsBySeverity()
      },
      lastUpdated: new Date().toISOString()
    };
  }

  // 按类型分组错误
  groupErrorsByType(errors) {
    const grouped = {};
    errors.forEach(error => {
      const type = error.message.split(':')[0] || 'Unknown';
      grouped[type] = (grouped[type] || 0) + 1;
    });
    return grouped;
  }

  // 按严重级别分组告警
  groupAlertsBySeverity() {
    const grouped = {};
    this.alerts.forEach(alert => {
      grouped[alert.severity] = (grouped[alert.severity] || 0) + 1;
    });
    return grouped;
  }

  // 确认告警
  acknowledgeAlert(alertId) {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      alert.acknowledgedAt = new Date().toISOString();
      return true;
    }
    return false;
  }

  // 生成监控报告
  generateMonitoringReport() {
    const stats = this.getMonitoringStats();
    
    return {
      reportId: crypto.randomUUID(),
      generatedAt: new Date().toISOString(),
      period: '1 hour',
      summary: {
        totalRequests: stats.requests.total,
        averageResponseTime: stats.requests.averageResponseTime,
        errorRate: stats.errors.rate,
        systemHealth: this.calculateSystemHealth(stats)
      },
      details: stats,
      recommendations: this.getPerformanceRecommendations(stats)
    };
  }

  // 计算系统健康度
  calculateSystemHealth(stats) {
    let score = 100;
    
    // 响应时间影响
    if (stats.requests.averageResponseTime > 1000) score -= 20;
    else if (stats.requests.averageResponseTime > 500) score -= 10;
    
    // 错误率影响
    if (parseFloat(stats.errors.rate) > 5) score -= 30;
    else if (parseFloat(stats.errors.rate) > 2) score -= 15;
    
    // 告警影响
    if (stats.alerts.unacknowledged > 5) score -= 20;
    else if (stats.alerts.unacknowledged > 2) score -= 10;
    
    return Math.max(0, score);
  }

  // 获取性能建议
  getPerformanceRecommendations(stats) {
    const recommendations = [];
    
    if (stats.requests.averageResponseTime > 1000) {
      recommendations.push({
        priority: 'high',
        message: '平均响应时间过长，建议优化数据库查询和缓存策略',
        action: 'optimize_performance'
      });
    }
    
    if (parseFloat(stats.errors.rate) > 5) {
      recommendations.push({
        priority: 'high',
        message: '错误率过高，建议检查应用程序逻辑和错误处理',
        action: 'fix_errors'
      });
    }
    
    if (stats.alerts.unacknowledged > 5) {
      recommendations.push({
        priority: 'medium',
        message: '有多个未确认的告警，建议及时处理',
        action: 'acknowledge_alerts'
      });
    }
    
    if (recommendations.length === 0) {
      recommendations.push({
        priority: 'low',
        message: '系统性能良好，继续保持监控',
        action: 'maintain_monitoring'
      });
    }
    
    return recommendations;
  }
}

module.exports = {
  SecurityManager,
  AdvancedMonitor
};

