const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const { createServer } = require('http');
const { Server } = require('socket.io');

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'powerautomation-secret-key-2025';

// 安全中间件
app.use(helmet());

// CORS 配置
app.use(cors({
  origin: "*",
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// 速率限制
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100 // 限制每个 IP 100 个请求
});
app.use('/api/', limiter);

// 解析 JSON
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// 模拟用户数据库
const users = {
  'admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U': {
    id: 1,
    username: 'admin',
    role: 'admin',
    permissions: ['all']
  },
  'dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg': {
    id: 2,
    username: 'developer',
    role: 'developer',
    permissions: ['mcp_access', 'debug_tools', 'api_access', 'code_execution']
  },
  'user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k': {
    id: 3,
    username: 'user',
    role: 'user',
    permissions: ['basic_chat', 'file_upload', 'view_history']
  }
};

// 权限配置
const rolePermissions = {
  admin: ['all'],
  developer: ['mcp_access', 'debug_tools', 'api_access', 'code_execution', 'system_monitor'],
  user: ['basic_chat', 'file_upload', 'view_history']
};

// JWT 认证中间件
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: '访问令牌缺失' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ message: '访问令牌无效' });
    }
    req.user = user;
    next();
  });
};

// 权限检查中间件
const requirePermission = (permission) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ message: '未认证' });
    }

    const userPermissions = rolePermissions[req.user.role] || [];
    
    if (userPermissions.includes('all') || userPermissions.includes(permission)) {
      next();
    } else {
      res.status(403).json({ message: '权限不足' });
    }
  };
};

// 角色检查中间件
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ message: '未认证' });
    }

    if (roles.includes(req.user.role)) {
      next();
    } else {
      res.status(403).json({ message: '角色权限不足' });
    }
  };
};

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'PowerAutomation Web API',
    version: '1.0.0'
  });
});

// API Key 认证端点
app.post('/api/auth/api-key', (req, res) => {
  try {
    const { apiKey } = req.body;

    if (!apiKey) {
      return res.status(400).json({ message: 'API Key 是必需的' });
    }

    const user = users[apiKey];
    if (!user) {
      return res.status(401).json({ message: '无效的 API Key' });
    }

    // 生成 JWT token
    const token = jwt.sign(
      { 
        id: user.id, 
        username: user.username, 
        role: user.role,
        permissions: user.permissions
      },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.json({
      message: '登录成功',
      token,
      user: {
        id: user.id,
        username: user.username,
        role: user.role,
        permissions: user.permissions
      }
    });

  } catch (error) {
    console.error('API Key 认证错误:', error);
    res.status(500).json({ message: '服务器内部错误' });
  }
});

// 管理员统计端点
app.get('/api/admin/stats', authenticateToken, requireRole(['admin']), (req, res) => {
  try {
    const stats = {
      users: 1247,
      requests: 15420,
      responseTime: 156,
      uptime: '99.9%',
      systemStatus: 'healthy',
      activeConnections: 42,
      cpuUsage: 23,
      memoryUsage: 45,
      diskUsage: 67,
      networkTraffic: '1.2 GB/s',
      lastUpdated: new Date().toISOString()
    };

    res.json(stats);
  } catch (error) {
    console.error('获取统计信息错误:', error);
    res.status(500).json({ message: '获取统计信息失败' });
  }
});

// 用户管理端点
app.get('/api/admin/users', authenticateToken, requireRole(['admin']), (req, res) => {
  try {
    const userList = Object.values(users).map(user => ({
      id: user.id,
      username: user.username,
      role: user.role,
      permissions: user.permissions,
      lastLogin: new Date().toISOString(),
      status: 'active'
    }));

    res.json({
      users: userList,
      total: userList.length
    });
  } catch (error) {
    console.error('获取用户列表错误:', error);
    res.status(500).json({ message: '获取用户列表失败' });
  }
});

// 系统监控端点
app.get('/api/system/monitor', authenticateToken, requirePermission('system_monitor'), (req, res) => {
  try {
    const monitoring = {
      services: [
        { name: 'API Server', status: 'running', port: 3001, uptime: '2h 15m' },
        { name: 'Frontend Server', status: 'running', port: 5173, uptime: '2h 15m' },
        { name: 'Database', status: 'running', port: 5432, uptime: '2h 15m' }
      ],
      performance: {
        cpu: { usage: 23, cores: 4 },
        memory: { usage: 45, total: '8GB', used: '3.6GB' },
        disk: { usage: 67, total: '100GB', used: '67GB' },
        network: { inbound: '1.2 MB/s', outbound: '0.8 MB/s' }
      },
      logs: [
        { timestamp: new Date().toISOString(), level: 'INFO', message: 'System running normally' },
        { timestamp: new Date(Date.now() - 60000).toISOString(), level: 'INFO', message: 'User authentication successful' },
        { timestamp: new Date(Date.now() - 120000).toISOString(), level: 'INFO', message: 'API request processed' }
      ]
    };

    res.json(monitoring);
  } catch (error) {
    console.error('获取监控信息错误:', error);
    res.status(500).json({ message: '获取监控信息失败' });
  }
});

// 代码执行端点
app.post('/api/code/execute', authenticateToken, requirePermission('code_execution'), (req, res) => {
  try {
    const { code, language } = req.body;

    if (!code || !language) {
      return res.status(400).json({ message: '代码和语言参数是必需的' });
    }

    // 模拟代码执行（实际应用中需要安全的沙盒环境）
    let output = '';
    let success = true;

    switch (language) {
      case 'python':
        if (code.includes('print')) {
          output = '代码执行成功！\nHello, PowerAutomation!';
        } else {
          output = '代码执行完成，无输出';
        }
        break;
      case 'javascript':
        if (code.includes('console.log')) {
          output = '代码执行成功！\nHello, PowerAutomation!';
        } else {
          output = '代码执行完成，无输出';
        }
        break;
      case 'shell':
        output = '$ ' + code + '\n命令执行成功';
        break;
      case 'sql':
        output = 'Query executed successfully\nRows affected: 1';
        break;
      default:
        success = false;
        output = '不支持的编程语言';
    }

    res.json({
      success,
      output,
      language,
      executionTime: Math.random() * 1000 + 100, // 模拟执行时间
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('代码执行错误:', error);
    res.status(500).json({ 
      success: false,
      message: '代码执行失败',
      error: error.message 
    });
  }
});

// 工具管理端点
app.get('/api/tools', authenticateToken, requirePermission('mcp_access'), (req, res) => {
  try {
    const tools = [
      {
        id: 1,
        name: 'Code Execution Engine',
        description: '多语言代码执行引擎',
        status: 'active',
        version: '1.0.0',
        capabilities: ['python', 'javascript', 'shell', 'sql']
      },
      {
        id: 2,
        name: 'API Testing Tool',
        description: 'RESTful API 测试工具',
        status: 'development',
        version: '0.9.0',
        capabilities: ['http_requests', 'response_validation', 'load_testing']
      },
      {
        id: 3,
        name: 'System Monitor',
        description: '系统性能监控工具',
        status: 'active',
        version: '1.2.0',
        capabilities: ['cpu_monitoring', 'memory_tracking', 'disk_analysis']
      }
    ];

    res.json({
      tools,
      total: tools.length,
      active: tools.filter(t => t.status === 'active').length
    });
  } catch (error) {
    console.error('获取工具列表错误:', error);
    res.status(500).json({ message: '获取工具列表失败' });
  }
});

// 刷新工具注册表
app.post('/api/tools/refresh', authenticateToken, requirePermission('mcp_access'), (req, res) => {
  try {
    // 模拟工具刷新过程
    setTimeout(() => {
      res.json({
        message: '工具注册表刷新成功',
        refreshed: 3,
        timestamp: new Date().toISOString()
      });
    }, 1000);
  } catch (error) {
    console.error('刷新工具注册表错误:', error);
    res.status(500).json({ message: '刷新工具注册表失败' });
  }
});

// 系统日志端点
app.get('/api/logs', authenticateToken, requireRole(['admin', 'developer']), (req, res) => {
  try {
    const logs = [
      { timestamp: new Date().toISOString(), level: 'INFO', message: 'PowerAutomation Web 系统启动成功' },
      { timestamp: new Date(Date.now() - 60000).toISOString(), level: 'INFO', message: '后端 API 服务器运行在端口 3001' },
      { timestamp: new Date(Date.now() - 120000).toISOString(), level: 'INFO', message: '前端服务器运行在端口 5173' },
      { timestamp: new Date(Date.now() - 180000).toISOString(), level: 'INFO', message: '数据库连接成功' },
      { timestamp: new Date(Date.now() - 240000).toISOString(), level: 'INFO', message: '所有服务初始化完成' },
      { timestamp: new Date(Date.now() - 300000).toISOString(), level: 'INFO', message: '管理员用户登录成功' },
      { timestamp: new Date(Date.now() - 360000).toISOString(), level: 'INFO', message: '获取系统统计信息' }
    ];

    res.json({
      logs,
      total: logs.length
    });
  } catch (error) {
    console.error('获取日志错误:', error);
    res.status(500).json({ message: '获取日志失败' });
  }
});

// API 测试端点
app.all('/api/test/*', authenticateToken, requirePermission('api_access'), (req, res) => {
  try {
    const endpoint = req.params[0];
    const method = req.method;
    const body = req.body;
    const query = req.query;

    res.json({
      message: 'API 测试成功',
      endpoint: `/api/test/${endpoint}`,
      method,
      body,
      query,
      timestamp: new Date().toISOString(),
      responseTime: Math.random() * 100 + 50
    });
  } catch (error) {
    console.error('API 测试错误:', error);
    res.status(500).json({ message: 'API 测试失败' });
  }
});

// 用户个人信息端点
app.get('/api/user/profile', authenticateToken, (req, res) => {
  try {
    const user = users[Object.keys(users).find(key => users[key].id === req.user.id)];
    
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    res.json({
      id: user.id,
      username: user.username,
      role: user.role,
      permissions: user.permissions,
      lastLogin: new Date().toISOString(),
      accountCreated: '2025-01-01T00:00:00.000Z'
    });
  } catch (error) {
    console.error('获取用户信息错误:', error);
    res.status(500).json({ message: '获取用户信息失败' });
  }
});

// WebSocket 连接处理
io.on('connection', (socket) => {
  console.log('用户连接:', socket.id);

  // 实时系统状态推送
  const statusInterval = setInterval(() => {
    socket.emit('system_status', {
      timestamp: new Date().toISOString(),
      cpu: Math.random() * 30 + 10,
      memory: Math.random() * 20 + 40,
      activeUsers: Math.floor(Math.random() * 10) + 35
    });
  }, 5000);

  socket.on('disconnect', () => {
    console.log('用户断开连接:', socket.id);
    clearInterval(statusInterval);
  });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error('服务器错误:', err);
  res.status(500).json({ 
    message: '服务器内部错误',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// 404 处理
app.use('*', (req, res) => {
  res.status(404).json({ message: '端点不存在' });
});

// 启动服务器
server.listen(PORT, '0.0.0.0', () => {
  console.log('🚀 PowerAutomation Web API 服務器已啟動');
  console.log(`📍 地址: http://localhost:${PORT}`);
  console.log(`🌐 環境: ${process.env.NODE_ENV || 'development'}`);
  console.log(`⏰ 時間: ${new Date().toLocaleString()}`);
});

module.exports = app;

