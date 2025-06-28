# SmartUI 权限管理系统完整部署指南

## 📋 目录

1. [系统概述](#系统概述)
2. [架构设计](#架构设计)
3. [部署步骤](#部署步骤)
4. [权限配置](#权限配置)
5. [前端集成](#前端集成)
6. [后端集成](#后端集成)
7. [测试验证](#测试验证)
8. [运维监控](#运维监控)
9. [故障排除](#故障排除)
10. [安全最佳实践](#安全最佳实践)

## 🎯 系统概述

SmartUI 权限管理系统是一个完整的基于角色的访问控制（RBAC）解决方案，专为 SmartUI 智能界面系统设计。系统支持三种用户角色，提供细粒度的权限控制，并保持原有紫色主题界面不变。

### 核心特性

- **统一前端界面**: 保持原有紫色主题，通过不同 API Key 区分角色
- **三级角色系统**: 管理员、开发者、用户
- **智能权限控制**: 基于功能的细粒度权限管理
- **文件管理界面**: 新增完整的文件管理功能
- **Claude Code 整合**: 将代码分析能力整合到 AICore 上下文中
- **审计日志**: 完整的操作记录和权限检查日志
- **高性能缓存**: 使用 Redis 提升权限检查性能

### 角色权限概览

| 角色 | API Key 前缀 | 主要权限 | 使用场景 |
|------|-------------|----------|----------|
| 管理员 | `admin_` | 完全权限 | 系统管理、代码审核 |
| 开发者 | `dev_` | 开发权限 | 代码编辑、插件连接 |
| 用户 | `user_` | 基础权限 | 文本输入、文件管理 |

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    SmartUI 前端应用                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   权限管理模块   │ │   文件管理界面   │ │   原有功能模块   │ │
│  │  - 角色识别     │ │  - 文件浏览器   │ │  - GitHub浏览   │ │
│  │  - 权限验证     │ │  - 文件上传     │ │  - 代码编辑器   │ │
│  │  - 功能控制     │ │  - 权限控制     │ │  - 智能聊天     │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端服务层                                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │  权限管理 MCP   │ │   AICore 服务   │ │   文件管理服务   │ │
│  │  - API Key验证  │ │  - Claude Code  │ │  - 文件CRUD     │ │
│  │  - 权限检查     │ │  - 智能分析     │ │  - 权限控制     │ │
│  │  - 审计日志     │ │  - 上下文处理   │ │  - 版本管理     │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据存储层                                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   Redis 缓存    │ │   文件系统      │ │   日志存储      │ │
│  │  - 权限缓存     │ │  - 项目文件     │ │  - 访问日志     │ │
│  │  - 会话数据     │ │  - 上传文件     │ │  - 操作记录     │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 权限流程图

```
用户访问 → API Key验证 → 角色识别 → 权限检查 → 功能访问/拒绝
    │           │           │           │
    │           │           │           └── 记录审计日志
    │           │           └── 缓存权限信息
    │           └── 验证Key有效性
    └── 获取Authorization Header
```

## 🚀 部署步骤

### 第一步：环境准备

#### 1.1 系统要求
- **操作系统**: Ubuntu 22.04 或更高版本
- **Node.js**: 20.18.0 或更高版本
- **Python**: 3.11.0 或更高版本
- **Redis**: 7.0 或更高版本（可选）

#### 1.2 安装依赖
```bash
# 安装 Node.js 依赖
cd /path/to/smartui
npm install

# 安装 Python 依赖
cd /path/to/aicore0624/PowerAutomation/components/smartui_permission_mcp
pip install flask flask-cors redis

# 安装 Redis（如果需要缓存功能）
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 第二步：配置权限管理系统

#### 2.1 配置 API Keys
在 `PowerAutomation/components/smartui_permission_mcp/main.py` 中确认 API Key 配置：

```python
API_KEY_ROLES = {
    'admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U': 'admin',
    'dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg': 'developer',
    'user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k': 'user'
}
```

#### 2.2 配置 Redis 连接
```python
# 在 main.py 中配置 Redis
def init_redis(self):
    try:
        self.redis_client = redis.Redis(
            host='localhost',  # Redis 服务器地址
            port=6379,         # Redis 端口
            db=1,              # 数据库编号
            decode_responses=True
        )
        self.redis_client.ping()
        logger.info("Redis连接成功")
    except Exception as e:
        logger.warning(f"Redis连接失败: {e}")
        self.redis_client = None
```

### 第三步：启动服务

#### 3.1 启动权限管理 MCP
```bash
cd /path/to/aicore0624/PowerAutomation/components/smartui_permission_mcp
python main.py
```

服务将在 `http://0.0.0.0:8081` 启动。

#### 3.2 启动 AICore 服务
```bash
cd /path/to/aicore0624
# 根据具体的 AICore 启动脚本
python PowerAutomation/core/enhanced_aicore3.py
```

#### 3.3 启动前端应用
```bash
cd /path/to/smartui
npm run dev
```

### 第四步：验证部署

#### 4.1 健康检查
```bash
# 检查权限管理服务
curl http://localhost:8081/health

# 检查 AICore 服务
curl http://localhost:8080/health
```

#### 4.2 权限验证测试
```bash
# 验证管理员 API Key
curl -X POST http://localhost:8081/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"api_key": "admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U"}'

# 验证开发者 API Key
curl -X POST http://localhost:8081/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"api_key": "dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg"}'
```

## ⚙️ 权限配置

### 角色权限详细配置

#### 管理员权限 (Admin)
```javascript
const adminPermissions = [
  // 代码管理
  'code_review', 'code_modify', 'code_delete',
  
  // 目录管理
  'directory_manage', 'project_create', 'project_delete',
  
  // 用户管理
  'user_manage', 'system_config',
  
  // 文件管理
  'file_manage_full', 'file_upload', 'file_download', 'file_delete',
  
  // 系统管理
  'github_manage', 'audit_view', 'cache_manage', 'system_monitor',
  
  // 聊天功能
  'chat_unlimited'
]
```

#### 开发者权限 (Developer)
```javascript
const developerPermissions = [
  // 代码操作
  'code_view', 'code_edit', 'code_analyze',
  
  // 文件操作
  'file_create', 'file_upload', 'file_download', 'file_manage_limited',
  
  // 开发工具
  'github_browse', 'plugin_connect', 'debug_access',
  
  // 项目访问
  'project_view',
  
  // 聊天功能
  'chat_basic'
]
```

#### 用户权限 (User)
```javascript
const userPermissions = [
  // 基础操作
  'text_input', 'file_download',
  
  // 只读访问
  'code_view_readonly', 'project_view_readonly',
  
  // 文件管理
  'file_manage_basic',
  
  // 聊天功能
  'chat_basic'
]
```

### 权限检查示例

#### 前端权限检查
```jsx
// 使用权限守卫组件
<PermissionGuard permission="code_edit">
  <CodeEditor />
</PermissionGuard>

// 使用权限 Hook
const { hasPermission } = usePermissions()
if (hasPermission('file_delete')) {
  // 显示删除按钮
}
```

#### 后端权限检查
```python
# 使用权限装饰器
@require_permission('file_upload')
def upload_file():
    # 文件上传逻辑
    pass

# 使用多权限检查
@require_permissions(['code_view', 'code_analyze'], require_all=False)
def analyze_code():
    # 代码分析逻辑
    pass
```

## 🎨 前端集成

### 权限管理 Hook 集成

#### 1. 安装权限提供者
```jsx
// App.jsx
import { PermissionProvider } from './hooks/usePermissions'

function App() {
  return (
    <PermissionProvider>
      <AppContent />
    </PermissionProvider>
  )
}
```

#### 2. 使用权限检查
```jsx
// 在组件中使用权限
import { usePermissions, PermissionGuard } from '../hooks/usePermissions'

function MyComponent() {
  const { hasPermission, userRole, roleInfo } = usePermissions()
  
  return (
    <div>
      {/* 条件渲染 */}
      {hasPermission('code_edit') && (
        <button>编辑代码</button>
      )}
      
      {/* 权限守卫 */}
      <PermissionGuard permission="file_delete">
        <button>删除文件</button>
      </PermissionGuard>
      
      {/* 角色信息 */}
      <div>当前角色: {roleInfo?.name}</div>
    </div>
  )
}
```

### 文件管理界面集成

#### 1. 文件管理组件使用
```jsx
import FileManager from './components/FileManager'

function App() {
  return (
    <div>
      {/* 其他组件 */}
      <FileManager />
    </div>
  )
}
```

#### 2. 权限控制的文件操作
```jsx
// FileManager.jsx 中的权限控制示例
<PermissionGuard permission="file_upload">
  <FileUpload />
</PermissionGuard>

<PermissionGuard permission="file_delete" showMessage={false}>
  <button onClick={handleDelete}>删除</button>
</PermissionGuard>
```

### Claude Code 整合

#### 1. 移除独立分析按钮
原有的 "Claude Code 分析" 按钮已被移除，分析功能整合到智能对话中。

#### 2. 自动分析集成
```jsx
// 在消息处理中自动启用代码分析
const handleSendMessage = async () => {
  const requestContext = {
    message: prompt,
    selectedFile: selectedFile,
    enableCodeAnalysis: true,  // 自动启用
    analysisMode: 'integrated' // 整合模式
  }
  
  const response = await mcpService.processMessage(requestContext)
  // 分析结果自动融入到响应中
}
```

## 🔧 后端集成

### 权限管理 MCP 部署

#### 1. 服务配置
```python
# main.py 配置示例
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 启动配置
if __name__ == '__main__':
    logger.info("启动 SmartUI 权限管理 MCP")
    app.run(host='0.0.0.0', port=8081, debug=False)
```

#### 2. 权限中间件
```python
# 权限检查中间件
@app.before_request
def check_permissions():
    # 获取 API Key
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # 验证权限
    if not permission_manager.check_permission(api_key, required_permission):
        return jsonify({'error': '权限不足'}), 403
```

### AICore 服务整合

#### 1. Claude Code 整合配置
```python
# 在 AICore 服务中整合 Claude Code
def process_message(context):
    if context.get('enableCodeAnalysis'):
        # 自动启用代码分析
        analysis_result = claude_code_analyzer.analyze(context)
        
        # 将分析结果融入响应
        response = integrate_analysis(response, analysis_result)
    
    return response
```

#### 2. 权限验证集成
```python
# 在 AICore 中验证权限
def verify_permissions(api_key, required_permissions):
    response = requests.post(
        'http://localhost:8081/api/auth/check',
        headers={'Authorization': f'Bearer {api_key}'},
        json={'permission': required_permissions}
    )
    return response.json().get('has_permission', False)
```

## ✅ 测试验证

### 功能测试清单

#### 1. 权限验证测试
- [ ] 管理员 API Key 验证
- [ ] 开发者 API Key 验证  
- [ ] 用户 API Key 验证
- [ ] 无效 API Key 拒绝
- [ ] 权限不足时的正确响应

#### 2. 界面功能测试
- [ ] 登录界面显示正确
- [ ] 角色标识显示正确
- [ ] 权限控制的按钮显示/隐藏
- [ ] 文件管理界面功能正常
- [ ] 紫色主题保持不变

#### 3. 文件管理测试
- [ ] 文件上传功能
- [ ] 文件下载功能
- [ ] 文件删除权限控制
- [ ] 文件重命名功能
- [ ] 目录创建功能

#### 4. Claude Code 整合测试
- [ ] 代码分析自动整合到对话
- [ ] 分析结果正确显示
- [ ] 200K tokens 上下文处理
- [ ] 缓存功能正常

### 自动化测试脚本

#### 权限测试脚本
```bash
#!/bin/bash
# test_permissions.sh

echo "测试权限管理系统..."

# 测试管理员权限
echo "测试管理员权限..."
curl -X POST http://localhost:8081/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"api_key": "admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U"}' \
  | jq '.authenticated'

# 测试开发者权限
echo "测试开发者权限..."
curl -X POST http://localhost:8081/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"api_key": "dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg"}' \
  | jq '.authenticated'

# 测试用户权限
echo "测试用户权限..."
curl -X POST http://localhost:8081/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"api_key": "user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k"}' \
  | jq '.authenticated'

echo "权限测试完成"
```

## 📊 运维监控

### 系统监控指标

#### 1. 权限管理服务监控
- **响应时间**: API 调用响应时间
- **成功率**: 权限验证成功率
- **错误率**: 权限拒绝和错误率
- **并发数**: 同时处理的请求数

#### 2. Redis 缓存监控
- **连接状态**: Redis 连接健康状态
- **缓存命中率**: 权限缓存命中率
- **内存使用**: Redis 内存使用情况
- **键过期**: 缓存键的过期情况

#### 3. 审计日志监控
- **日志量**: 每日访问日志数量
- **异常访问**: 权限拒绝事件统计
- **用户活跃度**: 各角色用户活跃情况
- **功能使用**: 各功能的使用频率

### 监控脚本示例

#### 健康检查脚本
```bash
#!/bin/bash
# health_check.sh

echo "检查 SmartUI 权限管理系统健康状态..."

# 检查权限管理服务
echo "检查权限管理服务..."
if curl -f http://localhost:8081/health > /dev/null 2>&1; then
    echo "✅ 权限管理服务正常"
else
    echo "❌ 权限管理服务异常"
fi

# 检查 AICore 服务
echo "检查 AICore 服务..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ AICore 服务正常"
else
    echo "❌ AICore 服务异常"
fi

# 检查 Redis 连接
echo "检查 Redis 连接..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 连接正常"
else
    echo "❌ Redis 连接异常"
fi

echo "健康检查完成"
```

### 日志分析

#### 访问日志分析
```python
# log_analyzer.py
import json
import redis
from datetime import datetime, timedelta

def analyze_access_logs(days=7):
    """分析访问日志"""
    r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
    
    stats = {
        'total_requests': 0,
        'by_role': {},
        'by_action': {},
        'permission_denied': 0
    }
    
    for day_offset in range(days):
        date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y%m%d')
        pattern = f"access_log:{date}:*"
        keys = r.keys(pattern)
        
        for key in keys:
            log_data = r.get(key)
            if log_data:
                log = json.loads(log_data)
                stats['total_requests'] += 1
                
                # 按角色统计
                role = log.get('role', 'unknown')
                stats['by_role'][role] = stats['by_role'].get(role, 0) + 1
                
                # 按操作统计
                action = log.get('action', 'unknown')
                stats['by_action'][action] = stats['by_action'].get(action, 0) + 1
                
                # 权限拒绝统计
                if log.get('result') == 'permission_denied':
                    stats['permission_denied'] += 1
    
    return stats

if __name__ == '__main__':
    stats = analyze_access_logs()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. API Key 验证失败
**问题**: 用户无法登录，提示 API Key 无效

**排查步骤**:
```bash
# 检查 API Key 配置
grep -n "API_KEY_ROLES" /path/to/smartui_permission_mcp/main.py

# 验证 API Key 格式
echo "admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U" | wc -c
```

**解决方案**:
- 确认 API Key 完整且无多余字符
- 检查配置文件中的 API Key 映射
- 重启权限管理服务

#### 2. Redis 连接失败
**问题**: 权限缓存不工作，性能下降

**排查步骤**:
```bash
# 检查 Redis 服务状态
sudo systemctl status redis-server

# 测试 Redis 连接
redis-cli ping

# 检查端口占用
netstat -tlnp | grep 6379
```

**解决方案**:
```bash
# 启动 Redis 服务
sudo systemctl start redis-server

# 重启 Redis 服务
sudo systemctl restart redis-server

# 检查 Redis 配置
sudo nano /etc/redis/redis.conf
```

#### 3. 权限检查失败
**问题**: 用户有权限但仍被拒绝访问

**排查步骤**:
```bash
# 检查权限配置
curl -X GET http://localhost:8081/api/auth/permissions \
  -H "Authorization: Bearer your_api_key"

# 检查特定权限
curl -X POST http://localhost:8081/api/auth/check \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"permission": "code_edit"}'
```

**解决方案**:
- 检查权限配置是否正确
- 清除 Redis 缓存重新验证
- 检查权限装饰器使用是否正确

#### 4. 文件上传失败
**问题**: 文件上传时提示权限不足

**排查步骤**:
```bash
# 检查文件上传权限
curl -X POST http://localhost:8081/api/auth/check \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"permission": "file_upload"}'

# 检查文件大小限制
curl -X POST http://localhost:8081/api/files/upload \
  -H "Authorization: Bearer your_api_key" \
  -F "files=@test.txt"
```

**解决方案**:
- 确认用户具有 `file_upload` 权限
- 检查文件大小是否超出限制
- 检查磁盘空间是否充足

### 日志调试

#### 启用详细日志
```python
# 在 main.py 中启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 或者在启动时设置环境变量
export FLASK_DEBUG=1
python main.py
```

#### 查看实时日志
```bash
# 查看权限管理服务日志
tail -f /var/log/smartui_permission.log

# 查看 Redis 日志
tail -f /var/log/redis/redis-server.log

# 查看系统日志
journalctl -u smartui-permission -f
```

## 🔒 安全最佳实践

### API Key 安全

#### 1. API Key 管理
- **定期轮换**: 建议每 90 天轮换一次 API Key
- **安全存储**: 使用环境变量或密钥管理系统
- **访问控制**: 限制 API Key 的访问范围
- **监控使用**: 监控 API Key 的使用情况

#### 2. API Key 轮换流程
```bash
# 1. 生成新的 API Key
python -c "import secrets; print('admin_' + secrets.token_urlsafe(32))"

# 2. 更新配置文件
# 3. 通知用户更新
# 4. 监控旧 Key 使用情况
# 5. 禁用旧 Key
```

### 网络安全

#### 1. HTTPS 配置
```nginx
# Nginx 配置示例
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 2. 防火墙配置
```bash
# 只允许必要的端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8081/tcp  # 不直接暴露内部端口
sudo ufw enable
```

### 权限安全

#### 1. 最小权限原则
- 用户只获得完成任务所需的最小权限
- 定期审查和调整权限分配
- 实施权限分离和职责分离

#### 2. 权限审计
```python
# 权限审计脚本
def audit_permissions():
    """审计权限分配"""
    for api_key, role in API_KEY_ROLES.items():
        permissions = ROLE_PERMISSIONS[role]['permissions']
        print(f"角色 {role}: {len(permissions)} 个权限")
        
        # 检查是否有过多权限
        if len(permissions) > 15:  # 阈值可调整
            print(f"⚠️  角色 {role} 权限过多，建议审查")
```

### 数据安全

#### 1. 敏感数据保护
```python
# 敏感数据脱敏
def mask_api_key(api_key):
    """脱敏 API Key"""
    if len(api_key) > 8:
        return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
    return '*' * len(api_key)
```

#### 2. 数据备份
```bash
#!/bin/bash
# backup_script.sh

# 备份 Redis 数据
redis-cli --rdb /backup/redis_$(date +%Y%m%d).rdb

# 备份配置文件
cp /path/to/config/* /backup/config_$(date +%Y%m%d)/

# 备份日志文件
tar -czf /backup/logs_$(date +%Y%m%d).tar.gz /var/log/smartui/
```

---

**文档版本**: 1.0.0  
**最后更新**: 2025-06-28  
**维护团队**: SmartUI 开发团队  
**联系方式**: smartui-support@example.com

