# SmartUI 快速启动指南

## 🚀 快速开始

欢迎使用 PowerAutomation 3.0.2 + SmartUI 智能界面系统！本指南将帮助您快速启动和使用整合后的系统。

## 📋 系统要求

### 基础环境
- **Node.js**: 20.18.0+
- **Python**: 3.11+
- **Redis**: 6.0+ (可选，用于缓存)
- **Git**: 2.0+

### 推荐配置
- **内存**: 8GB+
- **存储**: 10GB+ 可用空间
- **网络**: 稳定的互联网连接

## 🛠️ 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/alexchuang650730/aicore0624.git
cd aicore0624
```

### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

### 3. 安装 SmartUI 前端依赖
```bash
cd powerautomation_web/smartui
pnpm install
# 或者使用 npm
npm install
```

### 4. 配置环境变量
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

基本配置示例：
```env
# AICore 配置
AICORE_HOST=localhost
AICORE_PORT=8080

# Redis 配置 (可选)
REDIS_URL=redis://localhost:6379

# Claude Code SDK 配置
CLAUDE_API_KEY=your_claude_api_key

# GitHub 配置
GITHUB_TOKEN=your_github_token
```

## 🚀 启动服务

### 方式一：分别启动 (推荐开发环境)

#### 1. 启动 AICore 后端服务
```bash
# 在项目根目录
cd PowerAutomation
python -m core.aicore3
```

#### 2. 启动 SmartUI 前端服务
```bash
# 新开终端窗口
cd powerautomation_web/smartui
pnpm dev
# 或者
npm run dev
```

### 方式二：Docker 容器启动 (推荐生产环境)

```bash
# 在项目根目录
cd deployment/smartui
docker-compose up -d
```

## 🌐 访问系统

### 开发环境
- **SmartUI 前端**: http://localhost:3000
- **AICore 后端**: http://localhost:8080
- **API 文档**: http://localhost:8080/docs

### 生产环境 (Docker)
- **完整系统**: http://localhost (通过 Nginx 代理)

## 🎯 核心功能使用

### 1. GitHub 文件浏览器

1. 在 SmartUI 界面中点击 "GitHub Explorer"
2. 输入仓库地址 (例如: `alexchuang650730/aicore0624`)
3. 浏览文件树，点击文件查看内容
4. 支持在线编辑和保存

### 2. 智能代码编辑器

1. 在文件浏览器中选择代码文件
2. 自动启动代码编辑器
3. 享受语法高亮和智能提示
4. 使用 Ctrl+S 保存更改

### 3. Claude Code 分析

1. 选择要分析的代码文件
2. 点击 "Analyze with Claude"
3. 获得详细的代码分析报告
4. 查看优化建议和潜在问题

### 4. 智能聊天助手

1. 在界面右侧找到聊天窗口
2. 输入您的问题或需求
3. 享受 200K tokens 上下文分析
4. 获得智能的回答和建议

## 🔧 高级配置

### MCP 服务配置

编辑 `PowerAutomation/config/enhanced_config.py`：

```python
MCP_CONFIG = {
    "host": "localhost",
    "port": 8080,
    "max_connections": 100,
    "timeout": 30,
    "retry_attempts": 3
}
```

### SmartUI 前端配置

编辑 `powerautomation_web/smartui/vite.config.js`：

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
```

### Redis 缓存配置

```python
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": None,
    "max_connections": 20
}
```

## 🐛 故障排除

### 常见问题

#### 1. MCP 连接失败
```bash
# 检查 AICore 服务状态
curl http://localhost:8080/health

# 检查端口占用
netstat -tulpn | grep 8080
```

#### 2. 前端构建失败
```bash
# 清理依赖
cd powerautomation_web/smartui
rm -rf node_modules package-lock.json
pnpm install

# 或者
npm cache clean --force
npm install
```

#### 3. Redis 连接问题
```bash
# 检查 Redis 服务
redis-cli ping

# 启动 Redis (如果未启动)
redis-server
```

#### 4. 权限问题
```bash
# 确保文件权限正确
chmod +x deployment/smartui/deploy_to_cloud.sh
```

### 日志查看

#### AICore 日志
```bash
tail -f PowerAutomation/logs/aicore.log
```

#### SmartUI 日志
```bash
# 开发环境
# 日志会直接显示在终端

# 生产环境 (Docker)
docker logs smartui-container
```

#### Nginx 日志 (生产环境)
```bash
docker logs nginx-container
```

## 📊 性能优化

### 1. 缓存优化
- 启用 Redis 缓存以提升响应速度
- 配置合适的缓存过期时间
- 监控缓存命中率

### 2. 前端优化
- 启用代码分割和懒加载
- 压缩静态资源
- 使用 CDN 加速

### 3. 后端优化
- 调整 MCP 连接池大小
- 优化数据库查询
- 启用 gzip 压缩

## 🔒 安全配置

### 1. API 安全
```python
# 启用 API 密钥验证
API_SECURITY = {
    "enable_auth": True,
    "api_key_header": "X-API-Key",
    "rate_limit": "100/hour"
}
```

### 2. CORS 配置
```python
CORS_CONFIG = {
    "allow_origins": ["http://localhost:3000"],
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["*"]
}
```

### 3. HTTPS 配置 (生产环境)
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... 其他配置
}
```

## 📈 监控和维护

### 1. 健康检查
```bash
# 检查所有服务状态
curl http://localhost:8080/health
curl http://localhost:3000/health
```

### 2. 性能监控
- 监控 CPU 和内存使用率
- 跟踪 API 响应时间
- 监控错误率和异常

### 3. 日志轮转
```bash
# 配置日志轮转
logrotate /etc/logrotate.d/smartui
```

## 🆘 获取帮助

### 文档资源
- **完整文档**: `docs/smartui/SMARTUI_INTEGRATION_GUIDE.md`
- **API 文档**: http://localhost:8080/docs
- **架构文档**: `docs/smartui/claude_code_enhanced_architecture.md`

### 社区支持
- **GitHub Issues**: https://github.com/alexchuang650730/aicore0624/issues
- **技术讨论**: 查看项目 Wiki

### 联系方式
如有紧急问题，请查看项目文档或提交 GitHub Issue。

## 🎉 开始使用

现在您已经完成了 SmartUI 的设置，可以开始探索以下功能：

1. 🔍 **浏览 GitHub 仓库** - 直接在界面中浏览和编辑代码
2. 🤖 **AI 代码分析** - 使用 Claude Code SDK 分析代码质量
3. 💬 **智能对话** - 与 AI 助手进行技术讨论
4. ⚡ **高性能缓存** - 享受快速的响应体验

祝您使用愉快！🚀

---

**PowerAutomation 3.0.2 + SmartUI** - 让智能开发触手可及！

