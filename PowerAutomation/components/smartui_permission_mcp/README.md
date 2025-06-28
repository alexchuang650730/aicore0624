# SmartUI 权限管理 MCP

## 概述

SmartUI 权限管理 MCP 是一个基于角色的权限验证和管理系统，为 SmartUI 前端应用提供完整的权限控制功能。

## 功能特性

### 🔐 权限管理
- **三级角色系统**: 管理员、开发者、用户
- **细粒度权限控制**: 支持功能级别的权限验证
- **API Key 认证**: 基于预定义 API Key 的身份验证
- **权限缓存**: 使用 Redis 缓存提升性能

### 📊 审计日志
- **访问记录**: 记录所有 API 访问和权限检查
- **操作追踪**: 跟踪用户操作和系统变更
- **日志查询**: 支持管理员查询访问日志
- **数据保留**: 日志数据保留 7 天

### 🛡️ 安全特性
- **权限装饰器**: 简化权限检查实现
- **多权限验证**: 支持同时检查多个权限
- **IP 地址记录**: 记录访问来源 IP
- **用户代理跟踪**: 记录客户端信息

## 角色权限配置

### 管理员 (Admin)
- **API Key**: `admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U`
- **权限范围**: 完全访问权限
- **主要功能**:
  - 代码审核和修改
  - 目录结构管理
  - 用户管理
  - 系统配置
  - 审计日志查看
  - 缓存管理

### 开发者 (Developer)
- **API Key**: `dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg`
- **权限范围**: 开发功能权限
- **主要功能**:
  - 代码查看和编辑
  - 文件创建和管理
  - GitHub 浏览
  - 插件连接
  - 代码分析
  - 调试访问

### 用户 (User)
- **API Key**: `user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k`
- **权限范围**: 基础使用权限
- **主要功能**:
  - 文字输入
  - 基础文件管理
  - 只读代码查看
  - 基础聊天功能
  - 文件下载

## API 接口

### 认证接口

#### 验证 API Key
```http
POST /api/auth/verify
Content-Type: application/json

{
  "api_key": "your_api_key_here"
}
```

#### 获取用户权限
```http
GET /api/auth/permissions
Authorization: Bearer your_api_key_here
```

#### 检查特定权限
```http
POST /api/auth/check
Authorization: Bearer your_api_key_here
Content-Type: application/json

{
  "permission": "code_edit"
}
```

### 文件管理接口

#### 文件上传
```http
POST /api/files/upload
Authorization: Bearer your_api_key_here
Content-Type: multipart/form-data

files: [file1, file2, ...]
```

#### 文件删除
```http
DELETE /api/files/delete
Authorization: Bearer your_api_key_here
Content-Type: application/json

{
  "file_path": "/path/to/file"
}
```

### 代码分析接口

#### 代码分析
```http
POST /api/code/analyze
Authorization: Bearer your_api_key_here
Content-Type: application/json

{
  "code_content": "your_code_here"
}
```

### 管理接口

#### 获取访问日志
```http
GET /api/admin/logs?days=7
Authorization: Bearer admin_api_key_here
```

#### 获取用户列表
```http
GET /api/admin/users
Authorization: Bearer admin_api_key_here
```

#### 系统状态
```http
GET /api/system/status
Authorization: Bearer admin_api_key_here
```

## 权限装饰器使用

### 单权限检查
```python
@require_permission('code_edit')
def edit_code():
    # 需要 code_edit 权限
    pass
```

### 多权限检查
```python
@require_permissions(['code_view', 'code_analyze'], require_all=False)
def view_or_analyze():
    # 需要 code_view 或 code_analyze 权限之一
    pass

@require_permissions(['admin_access', 'system_config'], require_all=True)
def admin_config():
    # 需要同时具备两个权限
    pass
```

## 部署配置

### 环境要求
- Python 3.8+
- Flask
- Redis (可选，用于缓存)
- flask-cors

### 安装依赖
```bash
pip install flask flask-cors redis
```

### 启动服务
```bash
python main.py
```

服务将在 `http://0.0.0.0:8081` 上启动。

### Redis 配置
如果使用 Redis 缓存，请确保 Redis 服务运行在 `localhost:6379`。

## 配置文件

### 权限配置
权限配置直接在 `main.py` 中定义，包括：
- API Key 到角色的映射
- 角色权限定义
- Redis 连接配置

### 日志配置
- 访问日志存储在 Redis 中
- 日志保留期为 7 天
- 支持按日期查询日志

## 安全注意事项

### API Key 安全
- API Key 应保密存储
- 建议定期轮换 API Key
- 生产环境中应使用更复杂的 Key

### 权限设计
- 遵循最小权限原则
- 定期审查权限分配
- 监控异常访问行为

### 网络安全
- 建议使用 HTTPS
- 配置防火墙规则
- 限制访问来源 IP

## 监控和维护

### 日志监控
- 定期检查访问日志
- 监控权限拒绝事件
- 分析用户行为模式

### 性能监控
- 监控 API 响应时间
- 检查 Redis 连接状态
- 监控系统资源使用

### 故障排除
- 检查 Redis 连接
- 验证 API Key 配置
- 查看应用日志

## 扩展开发

### 添加新权限
1. 在 `ROLE_PERMISSIONS` 中添加权限
2. 更新相关角色的权限列表
3. 在需要的接口上添加权限检查

### 添加新角色
1. 在 `API_KEY_ROLES` 中添加新的 API Key
2. 在 `ROLE_PERMISSIONS` 中定义角色权限
3. 更新前端权限配置

### 自定义权限逻辑
可以扩展 `PermissionManager` 类来实现更复杂的权限逻辑，如：
- 基于时间的权限
- 基于资源的权限
- 动态权限分配

---

**版本**: 1.0.0  
**最后更新**: 2025-06-28  
**维护团队**: SmartUI 开发团队

