# PowerAutomation 一键部署系统

## 🎯 概述

PowerAutomation 一键部署系统实现了从 EC2 主平台到本地环境的完全自动化部署协调。通过整合 `fully_integrated_system.py` 和 `deployment_mcp` 组件，现在可以真正实现一键触发整个 PowerAutomation 生态系统的部署。

## 🏗️ 系统架构

```
EC2 主平台 (fully_integrated_system_with_deployment.py)
    ↓ 一键部署 API
部署协调器 (deployment_mcp)
    ↓ SSH/HTTP/Webhook
本地环境 (init_aicore.sh)
    ↓ 启动
PowerAutomation_local + AIWeb + SmartUI
```

## 🚀 快速开始

### 1. 启动主平台系统

```bash
# 在 EC2 或本地测试环境中
cd aicore0624
./start_one_click_deployment_system.sh
```

### 2. 配置部署环境

编辑 `PowerAutomation/components/deployment_mcp/remote_environments.json`:

```json
{
  "environments": [
    {
      "environment_id": "your_mac_local",
      "environment_type": "mac_local",
      "connection_method": "ssh",
      "host": "你的Mac IP地址",
      "port": 22,
      "username": "你的用户名",
      "ssh_key_path": "/path/to/your/ssh/key",
      "init_script_path": "./init_aicore.sh",
      "working_directory": "/path/to/aicore0624",
      "health_check_url": "http://你的Mac IP:8081/health",
      "timeout": 300
    }
  ]
}
```

### 3. 触发一键部署

#### 方法 1: 使用 API

```bash
# 获取 API Key (从启动日志中获取)
API_KEY="admin_xxxxxxxxxx"

# 触发一键部署
curl -X POST http://localhost:8080/api/deployment/one-click \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"target_environments": ["your_mac_local"]}'
```

#### 方法 2: 使用测试脚本

```bash
# 运行完整测试
python3 one_click_deployment_test.py
```

## 📋 API 端点

### 部署管理

| 端点 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/deployment/one-click` | POST | 触发一键部署 | Admin/Developer |
| `/api/deployment/status` | GET | 获取部署状态 | All |
| `/api/deployment/history` | GET | 获取部署历史 | Admin/Developer |
| `/api/deployment/environments` | GET | 获取环境配置 | Admin/Developer |
| `/api/deployment/test-connection` | POST | 测试部署连接 | Admin/Developer |

### 系统管理

| 端点 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/system/status` | GET | 系统状态 | All |
| `/api/system/health` | GET | 健康检查 | Public |
| `/api/keys` | GET | API Key 管理 | Admin |

## 🔧 配置说明

### 环境配置参数

- **environment_id**: 环境唯一标识符
- **environment_type**: 环境类型 (mac_local, windows_local, linux_local, docker)
- **connection_method**: 连接方式 (ssh, http_api, webhook)
- **host**: 目标主机地址
- **port**: 连接端口
- **username**: SSH 用户名
- **ssh_key_path**: SSH 私钥路径
- **init_script_path**: 初始化脚本路径 (通常是 ./init_aicore.sh)
- **working_directory**: 工作目录
- **health_check_url**: 健康检查 URL
- **timeout**: 超时时间 (秒)

### 连接方式详解

#### SSH 连接
```json
{
  "connection_method": "ssh",
  "host": "192.168.1.100",
  "port": 22,
  "username": "alexchuang",
  "ssh_key_path": "/home/ubuntu/.ssh/id_rsa"
}
```

#### HTTP API 连接
```json
{
  "connection_method": "http_api",
  "host": "localhost",
  "port": 8082,
  "api_endpoint": "http://localhost:8082/api/deploy"
}
```

#### Webhook 连接
```json
{
  "connection_method": "webhook",
  "webhook_url": "http://localhost:8083/webhook/deploy"
}
```

## 🔑 API Key 管理

系统启动时会自动生成三种类型的 API Key：

- **Admin Key**: `admin_xxxxxxxxxx` - 完全访问权限
- **Developer Key**: `dev_xxxxxxxxxx` - 开发者权限
- **User Key**: `user_xxxxxxxxxx` - 只读权限

API Key 在启动日志中显示，请妥善保存。

## 📊 部署流程

### 1. 准备阶段 (10%)
- 验证环境配置
- 检查连接状态
- 准备部署参数

### 2. 部署阶段 (30-70%)
- 连接到目标环境
- 执行 `init_aicore.sh`
- 监控执行状态

### 3. 验证阶段 (85-100%)
- 健康检查
- 服务状态验证
- 生成部署报告

## 🧪 测试功能

### 运行完整测试

```bash
python3 one_click_deployment_test.py
```

测试包括：
- ✅ 系统状态检查
- ✅ 环境配置验证
- ✅ 部署连接测试
- ✅ 一键部署触发
- ✅ 部署进度监控
- ✅ 部署历史查询

### 手动测试步骤

1. **启动系统**: `./start_one_click_deployment_system.sh`
2. **检查健康**: `curl http://localhost:8080/api/system/health`
3. **获取状态**: `curl -H "X-API-Key: YOUR_KEY" http://localhost:8080/api/system/status`
4. **触发部署**: 使用 POST 请求到 `/api/deployment/one-click`
5. **监控进度**: 定期查询 `/api/deployment/status`

## 🔍 故障排除

### 常见问题

#### 1. 部署组件不可用
```
❌ 部署协调组件导入失败
```
**解决方案**: 检查 `deployment_mcp` 目录是否存在，安装必要依赖

#### 2. SSH 连接失败
```
❌ SSH 部署异常: Authentication failed
```
**解决方案**: 检查 SSH 密钥路径、用户名、主机地址

#### 3. 脚本执行失败
```
❌ Script not found: ./init_aicore.sh
```
**解决方案**: 确保目标环境中存在 `init_aicore.sh` 脚本

#### 4. 健康检查失败
```
❌ 健康检查失败: Connection refused
```
**解决方案**: 确保目标服务已启动，端口可访问

### 调试模式

启用详细日志：
```bash
export LOG_LEVEL=DEBUG
./start_one_click_deployment_system.sh
```

## 📈 监控和日志

### 部署状态监控

```bash
# 实时监控部署状态
watch -n 5 'curl -s -H "X-API-Key: YOUR_KEY" http://localhost:8080/api/deployment/status | jq'
```

### 日志查看

部署日志包含在 API 响应中：
```json
{
  "logs": [
    "[2025-06-29 10:30:00] 🚀 开始一键部署流程",
    "[2025-06-29 10:30:05] 📡 触发遠程部署協調器...",
    "[2025-06-29 10:30:15] ✅ 遠程環境部署成功"
  ]
}
```

## 🔄 自动化部署

### 启动时自动部署

设置环境变量启用自动部署：
```bash
export AUTO_DEPLOY_ON_STARTUP=true
./start_one_click_deployment_system.sh
```

### 定时部署

使用 cron 定时触发部署：
```bash
# 每天凌晨2点自动部署
0 2 * * * curl -X POST -H "X-API-Key: YOUR_KEY" http://localhost:8080/api/deployment/one-click
```

## 🎯 最佳实践

### 1. 安全配置
- 使用 SSH 密钥而非密码
- 定期轮换 API Key
- 限制网络访问权限

### 2. 环境管理
- 为不同环境使用不同的配置
- 实施环境隔离策略
- 定期备份配置文件

### 3. 监控和告警
- 设置部署失败告警
- 监控系统资源使用
- 记录部署历史和性能指标

### 4. 故障恢复
- 准备回滚方案
- 测试灾难恢复流程
- 维护环境清单和联系信息

## 🚀 高级功能

### 并行部署

支持同时部署到多个环境：
```json
{
  "target_environments": [
    "mac_local_001",
    "mac_local_002",
    "linux_local_001"
  ]
}
```

### 条件部署

基于环境状态的智能部署：
- 自动跳过不健康的环境
- 重试失败的部署
- 渐进式部署策略

### 集成通知

支持多种通知方式：
- Slack Webhook
- 邮件通知
- 自定义 Webhook

## 📞 支持和反馈

如有问题或建议，请：
1. 查看日志文件
2. 运行测试脚本诊断
3. 检查网络连接和权限
4. 联系 PowerAutomation 团队

---

**PowerAutomation 一键部署系统 - 让部署变得简单而可靠！** 🎉

