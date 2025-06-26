// 新功能模块
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

// 文件管理模块
class FileManager {
  constructor() {
    this.uploadDir = '/tmp/powerautomation_uploads';
    this.maxFileSize = 10 * 1024 * 1024; // 10MB
    this.allowedTypes = [
      'text/plain',
      'application/json',
      'text/csv',
      'application/pdf',
      'image/jpeg',
      'image/png',
      'image/gif'
    ];
    this.files = new Map(); // 文件元数据存储
  }

  // 初始化上传目录
  async initialize() {
    try {
      await fs.mkdir(this.uploadDir, { recursive: true });
      console.log('文件管理器初始化成功');
    } catch (error) {
      console.error('文件管理器初始化失败:', error);
    }
  }

  // 验证文件
  validateFile(file) {
    const errors = [];

    if (!file) {
      errors.push('文件不能为空');
      return { valid: false, errors };
    }

    if (file.size > this.maxFileSize) {
      errors.push(`文件大小超过限制 (${this.maxFileSize / 1024 / 1024}MB)`);
    }

    if (!this.allowedTypes.includes(file.mimetype)) {
      errors.push(`不支持的文件类型: ${file.mimetype}`);
    }

    // 检查文件名
    if (!/^[a-zA-Z0-9._-]+$/.test(file.originalname)) {
      errors.push('文件名包含非法字符');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  // 保存文件
  async saveFile(file, userId) {
    const validation = this.validateFile(file);
    if (!validation.valid) {
      throw new Error(validation.errors.join(', '));
    }

    const fileId = crypto.randomUUID();
    const fileName = `${fileId}_${file.originalname}`;
    const filePath = path.join(this.uploadDir, fileName);

    try {
      await fs.writeFile(filePath, file.buffer);

      const metadata = {
        id: fileId,
        originalName: file.originalname,
        fileName,
        filePath,
        size: file.size,
        mimetype: file.mimetype,
        userId,
        uploadedAt: new Date().toISOString(),
        downloads: 0,
        lastAccessed: null
      };

      this.files.set(fileId, metadata);
      return metadata;
    } catch (error) {
      throw new Error(`文件保存失败: ${error.message}`);
    }
  }

  // 获取文件
  async getFile(fileId, userId) {
    const metadata = this.files.get(fileId);
    if (!metadata) {
      throw new Error('文件不存在');
    }

    // 检查权限（用户只能访问自己的文件，管理员可以访问所有文件）
    if (metadata.userId !== userId && userId !== 'admin') {
      throw new Error('无权限访问此文件');
    }

    try {
      const content = await fs.readFile(metadata.filePath);
      
      // 更新访问记录
      metadata.downloads++;
      metadata.lastAccessed = new Date().toISOString();
      
      return {
        metadata,
        content
      };
    } catch (error) {
      throw new Error(`文件读取失败: ${error.message}`);
    }
  }

  // 删除文件
  async deleteFile(fileId, userId) {
    const metadata = this.files.get(fileId);
    if (!metadata) {
      throw new Error('文件不存在');
    }

    // 检查权限
    if (metadata.userId !== userId && userId !== 'admin') {
      throw new Error('无权限删除此文件');
    }

    try {
      await fs.unlink(metadata.filePath);
      this.files.delete(fileId);
      return true;
    } catch (error) {
      throw new Error(`文件删除失败: ${error.message}`);
    }
  }

  // 获取用户文件列表
  getUserFiles(userId) {
    const userFiles = Array.from(this.files.values())
      .filter(file => file.userId === userId || userId === 'admin')
      .map(file => ({
        id: file.id,
        originalName: file.originalName,
        size: file.size,
        mimetype: file.mimetype,
        uploadedAt: file.uploadedAt,
        downloads: file.downloads,
        lastAccessed: file.lastAccessed
      }));

    return {
      files: userFiles,
      total: userFiles.length,
      totalSize: userFiles.reduce((sum, file) => sum + file.size, 0)
    };
  }

  // 获取文件统计
  getFileStats() {
    const allFiles = Array.from(this.files.values());
    const totalSize = allFiles.reduce((sum, file) => sum + file.size, 0);
    const typeStats = {};

    allFiles.forEach(file => {
      typeStats[file.mimetype] = (typeStats[file.mimetype] || 0) + 1;
    });

    return {
      totalFiles: allFiles.length,
      totalSize,
      averageSize: allFiles.length > 0 ? Math.round(totalSize / allFiles.length) : 0,
      typeDistribution: typeStats,
      recentUploads: allFiles
        .sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt))
        .slice(0, 10)
    };
  }
}

// 通知系统模块
class NotificationSystem {
  constructor() {
    this.notifications = new Map();
    this.subscriptions = new Map(); // 用户订阅
    this.templates = new Map();
    this.initializeTemplates();
  }

  // 初始化通知模板
  initializeTemplates() {
    this.templates.set('welcome', {
      title: '欢迎使用 PowerAutomation',
      body: '您已成功登录系统，开始探索强大的自动化功能吧！',
      type: 'info',
      priority: 'normal'
    });

    this.templates.set('security_alert', {
      title: '安全警告',
      body: '检测到异常登录活动，请检查您的账户安全',
      type: 'warning',
      priority: 'high'
    });

    this.templates.set('system_maintenance', {
      title: '系统维护通知',
      body: '系统将在 {time} 进行维护，预计持续 {duration}',
      type: 'info',
      priority: 'normal'
    });

    this.templates.set('task_completed', {
      title: '任务完成',
      body: '您的任务 "{taskName}" 已成功完成',
      type: 'success',
      priority: 'normal'
    });

    this.templates.set('error_occurred', {
      title: '系统错误',
      body: '系统遇到错误: {error}',
      type: 'error',
      priority: 'high'
    });
  }

  // 创建通知
  createNotification(userId, templateId, variables = {}, customOptions = {}) {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`通知模板不存在: ${templateId}`);
    }

    const notificationId = crypto.randomUUID();
    let body = template.body;

    // 替换变量
    Object.entries(variables).forEach(([key, value]) => {
      body = body.replace(new RegExp(`{${key}}`, 'g'), value);
    });

    const notification = {
      id: notificationId,
      userId,
      title: customOptions.title || template.title,
      body,
      type: customOptions.type || template.type,
      priority: customOptions.priority || template.priority,
      read: false,
      createdAt: new Date().toISOString(),
      readAt: null,
      data: customOptions.data || {}
    };

    this.notifications.set(notificationId, notification);
    return notification;
  }

  // 发送通知
  async sendNotification(userId, templateId, variables = {}, customOptions = {}) {
    try {
      const notification = this.createNotification(userId, templateId, variables, customOptions);
      
      // 这里可以集成实际的推送服务
      console.log(`[NOTIFICATION] 发送给用户 ${userId}: ${notification.title}`);
      
      return notification;
    } catch (error) {
      console.error('发送通知失败:', error);
      throw error;
    }
  }

  // 获取用户通知
  getUserNotifications(userId, options = {}) {
    const { unreadOnly = false, limit = 50, offset = 0 } = options;
    
    let userNotifications = Array.from(this.notifications.values())
      .filter(n => n.userId === userId);

    if (unreadOnly) {
      userNotifications = userNotifications.filter(n => !n.read);
    }

    // 按创建时间倒序排列
    userNotifications.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

    const total = userNotifications.length;
    const notifications = userNotifications.slice(offset, offset + limit);

    return {
      notifications,
      total,
      unread: userNotifications.filter(n => !n.read).length,
      hasMore: offset + limit < total
    };
  }

  // 标记通知为已读
  markAsRead(notificationId, userId) {
    const notification = this.notifications.get(notificationId);
    if (!notification) {
      throw new Error('通知不存在');
    }

    if (notification.userId !== userId) {
      throw new Error('无权限操作此通知');
    }

    notification.read = true;
    notification.readAt = new Date().toISOString();
    return notification;
  }

  // 标记所有通知为已读
  markAllAsRead(userId) {
    let count = 0;
    this.notifications.forEach(notification => {
      if (notification.userId === userId && !notification.read) {
        notification.read = true;
        notification.readAt = new Date().toISOString();
        count++;
      }
    });
    return count;
  }

  // 删除通知
  deleteNotification(notificationId, userId) {
    const notification = this.notifications.get(notificationId);
    if (!notification) {
      throw new Error('通知不存在');
    }

    if (notification.userId !== userId) {
      throw new Error('无权限删除此通知');
    }

    this.notifications.delete(notificationId);
    return true;
  }

  // 获取通知统计
  getNotificationStats(userId = null) {
    let notifications = Array.from(this.notifications.values());
    
    if (userId) {
      notifications = notifications.filter(n => n.userId === userId);
    }

    const stats = {
      total: notifications.length,
      unread: notifications.filter(n => !n.read).length,
      byType: {},
      byPriority: {},
      recent: notifications
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        .slice(0, 5)
    };

    notifications.forEach(n => {
      stats.byType[n.type] = (stats.byType[n.type] || 0) + 1;
      stats.byPriority[n.priority] = (stats.byPriority[n.priority] || 0) + 1;
    });

    return stats;
  }
}

// 任务调度模块
class TaskScheduler {
  constructor() {
    this.tasks = new Map();
    this.runningTasks = new Map();
    this.taskHistory = [];
    this.maxHistorySize = 1000;
  }

  // 创建任务
  createTask(name, schedule, action, options = {}) {
    const taskId = crypto.randomUUID();
    const task = {
      id: taskId,
      name,
      schedule, // cron 表达式或间隔时间
      action, // 要执行的函数
      options: {
        enabled: true,
        maxRetries: 3,
        timeout: 30000, // 30秒
        ...options
      },
      createdAt: new Date().toISOString(),
      lastRun: null,
      nextRun: this.calculateNextRun(schedule),
      runCount: 0,
      failCount: 0,
      status: 'scheduled'
    };

    this.tasks.set(taskId, task);
    return task;
  }

  // 计算下次运行时间
  calculateNextRun(schedule) {
    if (typeof schedule === 'number') {
      // 间隔时间（毫秒）
      return new Date(Date.now() + schedule).toISOString();
    } else if (typeof schedule === 'string') {
      // 简单的 cron 表达式解析（实际应用中应使用专业的 cron 库）
      const now = new Date();
      if (schedule === '0 0 * * *') { // 每天午夜
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(0, 0, 0, 0);
        return tomorrow.toISOString();
      } else if (schedule === '0 * * * *') { // 每小时
        const nextHour = new Date(now);
        nextHour.setHours(nextHour.getHours() + 1, 0, 0, 0);
        return nextHour.toISOString();
      } else if (schedule === '*/5 * * * *') { // 每5分钟
        const next5Min = new Date(now);
        next5Min.setMinutes(Math.ceil(next5Min.getMinutes() / 5) * 5, 0, 0);
        return next5Min.toISOString();
      }
    }
    
    // 默认1小时后
    return new Date(Date.now() + 60 * 60 * 1000).toISOString();
  }

  // 执行任务
  async executeTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task || !task.options.enabled) {
      return;
    }

    if (this.runningTasks.has(taskId)) {
      console.log(`任务 ${task.name} 正在运行中，跳过此次执行`);
      return;
    }

    const execution = {
      id: crypto.randomUUID(),
      taskId,
      startTime: new Date().toISOString(),
      endTime: null,
      status: 'running',
      result: null,
      error: null
    };

    this.runningTasks.set(taskId, execution);
    task.status = 'running';
    task.lastRun = execution.startTime;

    try {
      console.log(`开始执行任务: ${task.name}`);
      
      // 设置超时
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('任务执行超时')), task.options.timeout);
      });

      // 执行任务
      const result = await Promise.race([
        task.action(),
        timeoutPromise
      ]);

      execution.result = result;
      execution.status = 'completed';
      task.runCount++;
      task.status = 'scheduled';
      
      console.log(`任务 ${task.name} 执行成功`);
      
    } catch (error) {
      execution.error = error.message;
      execution.status = 'failed';
      task.failCount++;
      task.status = 'failed';
      
      console.error(`任务 ${task.name} 执行失败:`, error);
      
      // 重试逻辑
      if (task.failCount < task.options.maxRetries) {
        task.status = 'scheduled';
        console.log(`任务 ${task.name} 将在5分钟后重试`);
        task.nextRun = new Date(Date.now() + 5 * 60 * 1000).toISOString();
      }
    } finally {
      execution.endTime = new Date().toISOString();
      this.runningTasks.delete(taskId);
      
      // 记录执行历史
      this.taskHistory.push(execution);
      if (this.taskHistory.length > this.maxHistorySize) {
        this.taskHistory.shift();
      }
      
      // 计算下次运行时间
      if (task.status === 'scheduled') {
        task.nextRun = this.calculateNextRun(task.schedule);
      }
    }
  }

  // 启动调度器
  start() {
    console.log('任务调度器启动');
    
    // 每分钟检查一次待执行的任务
    this.schedulerInterval = setInterval(() => {
      this.checkAndExecuteTasks();
    }, 60 * 1000);
  }

  // 停止调度器
  stop() {
    if (this.schedulerInterval) {
      clearInterval(this.schedulerInterval);
      this.schedulerInterval = null;
      console.log('任务调度器停止');
    }
  }

  // 检查并执行待执行的任务
  checkAndExecuteTasks() {
    const now = new Date();
    
    this.tasks.forEach(task => {
      if (task.options.enabled && 
          task.status === 'scheduled' && 
          task.nextRun && 
          new Date(task.nextRun) <= now) {
        this.executeTask(task.id);
      }
    });
  }

  // 获取任务列表
  getTasks() {
    return Array.from(this.tasks.values()).map(task => ({
      ...task,
      isRunning: this.runningTasks.has(task.id)
    }));
  }

  // 获取任务详情
  getTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error('任务不存在');
    }

    const executions = this.taskHistory
      .filter(h => h.taskId === taskId)
      .sort((a, b) => new Date(b.startTime) - new Date(a.startTime))
      .slice(0, 10);

    return {
      ...task,
      isRunning: this.runningTasks.has(taskId),
      recentExecutions: executions
    };
  }

  // 启用/禁用任务
  toggleTask(taskId, enabled) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error('任务不存在');
    }

    task.options.enabled = enabled;
    task.status = enabled ? 'scheduled' : 'disabled';
    
    if (enabled) {
      task.nextRun = this.calculateNextRun(task.schedule);
    } else {
      task.nextRun = null;
    }

    return task;
  }

  // 删除任务
  deleteTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error('任务不存在');
    }

    // 如果任务正在运行，不能删除
    if (this.runningTasks.has(taskId)) {
      throw new Error('任务正在运行中，无法删除');
    }

    this.tasks.delete(taskId);
    return true;
  }

  // 获取调度器统计
  getSchedulerStats() {
    const tasks = Array.from(this.tasks.values());
    const runningTasks = Array.from(this.runningTasks.values());
    
    return {
      totalTasks: tasks.length,
      enabledTasks: tasks.filter(t => t.options.enabled).length,
      runningTasks: runningTasks.length,
      failedTasks: tasks.filter(t => t.status === 'failed').length,
      totalExecutions: this.taskHistory.length,
      successfulExecutions: this.taskHistory.filter(h => h.status === 'completed').length,
      failedExecutions: this.taskHistory.filter(h => h.status === 'failed').length,
      averageExecutionTime: this.calculateAverageExecutionTime(),
      nextScheduledTask: this.getNextScheduledTask()
    };
  }

  // 计算平均执行时间
  calculateAverageExecutionTime() {
    const completedExecutions = this.taskHistory.filter(h => 
      h.status === 'completed' && h.startTime && h.endTime
    );

    if (completedExecutions.length === 0) return 0;

    const totalTime = completedExecutions.reduce((sum, execution) => {
      const duration = new Date(execution.endTime) - new Date(execution.startTime);
      return sum + duration;
    }, 0);

    return Math.round(totalTime / completedExecutions.length);
  }

  // 获取下一个计划执行的任务
  getNextScheduledTask() {
    const scheduledTasks = Array.from(this.tasks.values())
      .filter(t => t.options.enabled && t.nextRun)
      .sort((a, b) => new Date(a.nextRun) - new Date(b.nextRun));

    return scheduledTasks.length > 0 ? scheduledTasks[0] : null;
  }
}

module.exports = {
  FileManager,
  NotificationSystem,
  TaskScheduler
};

