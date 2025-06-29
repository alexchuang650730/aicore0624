# 部署管理 MCP (Deployment MCP)

PowerAutomation 系统的统一部署管理组件，负责协调 EC2 主平台与本地环境的分布式部署。

## 🏗️ 架构概述

```
EC2 主平台部署
       ↓
远程部署协调器 (Remote Deployment Coordinator)
       ↓
触发本地环境部署 (SSH/HTTP API/Webhook)
       ↓
本地 init_aicore.sh 执行
       ↓
验证分布式系统状态
```

## 📁 组件结构

```
deployment_mcp/
├── main.py                           # 主要的部署 MCP 组件
├── remote_deployment_coordinator.py  # 远程部署协调器
├── ec2_deployment_trigger.py         # EC2 部署触发器
├── remote_environments.json          # 远程环境配置
└── README.md                         # 本文档
```

## 🚀 核心功能

### 1. 远程部署协调器 (Remote Deployment Coordinator)

负责协调整个分布式部署流程：

- **EC2 主平台部署**: 部署 PowerAutomation 主平台到云端
- **本地环境触发**: 通过多种方式触发本地环境初始化
- **状态监控**: 实时监控所有环境的部署状态
- **健康检查**: 验证分布式系统的整体健康状态

### 2. EC2 部署触发器 (EC2 Deployment Trigger)

在 EC2 部署完成后自动执行：

- **环境配置加载**: 从配置文件加载所有注册的本地环境
- **批量触发**: 并行触发多个本地环境的部署
- **结果汇总**: 收集和展示所有环境的部署结果

### 3. 多种连接方式

支持多种方式连接和触发本地环境：

- **SSH**: 通过 SSH 直接执行远程命令
- **HTTP API**: 通过 REST API 触发部署
- **Webhook**: 通过 Webhook 通知本地环境

## ⚙️ 配置说明

### 远程环境配置 (remote_environments.json)

```json
{
  "environments": [
    {
      "environment_id": "mac_local_001",
      "environment_type": "mac_local",
      "connection_method": "ssh",
      "host": "192.168.1.100",
      "port": 22,
      "username": "alexchuang",
      "ssh_key_path": "/home/ubuntu/.ssh/id_rsa",
      "init_script_path": "./init_aicore.sh",
      "health_check_url": "http://localhost:8081/health",
      "timeout": 300
    }
  ]
}
```

### 配置参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `environment_id` | string | ✅ | 环境唯一标识符 |
| `environment_type` | enum | ✅ | 环境类型 (mac_local, windows_local, linux_local) |
| `connection_method` | enum | ✅ | 连接方式 (ssh, http_api, webhook) |
| `host` | string | ✅ | 目标主机地址 |
| `port` | integer | ✅ | 连接端口 |
| `username` | string | SSH时必需 | SSH 用户名 |
| `ssh_key_path` | string | SSH时必需 | SSH 私钥路径 |
| `api_token` | string | HTTP API时必需 | API 认证令牌 |
| `init_script_path` | string | ❌ | 初始化脚本路径 (默认: ./init_aicore.sh) |
| `health_check_url` | string | ❌ | 健康检查 URL |
| `timeout` | integer | ❌ | 超时时间 (默认: 300秒) |

## 🔧 使用方法

### 1. 在 EC2 部署脚本中集成

在您的 EC2 部署脚本的最后添加：

```bash
#!/bin/bash
# EC2 部署脚本

# ... EC2 部署逻辑 ...

# 部署完成后触发本地环境
echo "🚀 PowerAutomation 主平台部署完成，触发本地环境..."

# 设置环境变量
export EC2_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
export EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
export DEPLOYMENT_VERSION="v1.0.0"

# 执行触发器
cd /path/to/PowerAutomation/components/deployment_mcp
python3 ec2_deployment_trigger.py

echo "✅ 分布式部署协调完成"
```

### 2. 直接使用协调器

```python
import asyncio
from remote_deployment_coordinator import (
    RemoteDeploymentCoordinator,
    RemoteEnvironmentConfig,
    RemoteEnvironmentType
)

async def deploy_distributed_system():
    coordinator = RemoteDeploymentCoordinator()
    
    # 注册本地环境
    mac_config = RemoteEnvironmentConfig(
        environment_id="mac_local_001",
        environment_type=RemoteEnvironmentType.MAC_LOCAL,
        connection_method="ssh",
        host="192.168.1.100",
        port=22,
        username="alexchuang",
        ssh_key_path="/path/to/ssh/key",
        init_script_path="./init_aicore.sh"
    )
    
    coordinator.register_remote_environment(mac_config)
    
    # 执行协调部署
    result = await coordinator.coordinate_deployment(
        coordination_id="deploy_001",
        ec2_deployment_config={"instance_type": "t3.medium"},
        target_environments=["mac_local_001"]
    )
    
    print(f"部署状态: {result.status.value}")

# 运行
asyncio.run(deploy_distributed_system())
```

### 3. 配置本地环境

在本地环境中，确保：

1. **SSH 访问**: 配置 SSH 密钥认证
2. **脚本权限**: 确保 `init_aicore.sh` 有执行权限
3. **网络连通**: 确保 EC2 可以访问本地环境

```bash
# 在本地环境中
chmod +x init_aicore.sh

# 测试 SSH 连接 (从 EC2)
ssh -i /path/to/key user@local-host "echo 'SSH connection test'"
```

## 📊 部署流程

### 完整的分布式部署流程

1. **EC2 主平台部署**
   - 部署 PowerAutomation 主平台到 EC2
   - 启动核心 MCP 服务
   - 验证主平台状态

2. **触发本地环境**
   - 读取远程环境配置
   - 并行触发所有注册的本地环境
   - 执行 `init_aicore.sh` 脚本

3. **本地环境初始化**
   - 启动 PowerAutomation_local (MCP 适配器)
   - 启动 AIWeb & SmartUI 组件
   - 连接到 EC2 主平台

4. **分布式验证**
   - 检查所有环境的健康状态
   - 验证 EC2 与本地环境的连通性
   - 确认整个系统正常运行

### 部署状态流转

```
PENDING → EC2_DEPLOYING → EC2_COMPLETED → LOCAL_TRIGGERING → 
LOCAL_DEPLOYING → LOCAL_COMPLETED → COMPLETED
```

## 🔍 监控和日志

### 部署状态查询

```python
# 查询活跃的协调任务
active_coordinations = coordinator.list_active_coordinations()

# 获取特定协调的状态
status = coordinator.get_coordination_status("deploy_001")

# 查看历史记录
history = coordinator.get_coordination_history(limit=10)
```

### 日志输出

部署过程中会输出详细的日志信息：

```
🚀 开始协调部署: deploy_20250629_001
📡 阶段1: 部署 PowerAutomation 主平台到 EC2
✅ EC2 主平台部署完成
💻 阶段2: 触发本地环境部署
🔗 触发远程环境: mac_local_001
✅ mac_local_001 部署成功
🔍 阶段3: 验证整体部署状态
🎉 所有环境部署成功完成
⏱️ 总耗时: 45.67 秒
```

## 🛠️ 故障排除

### 常见问题

1. **SSH 连接失败**
   ```
   错误: SSH 连接超时
   解决: 检查网络连通性、SSH 密钥配置、防火墙设置
   ```

2. **本地脚本执行失败**
   ```
   错误: init_aicore.sh 执行失败
   解决: 检查脚本权限、依赖环境、路径配置
   ```

3. **健康检查失败**
   ```
   错误: 健康检查 URL 无响应
   解决: 确认服务已启动、端口开放、URL 配置正确
   ```

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 安全考虑

1. **SSH 密钥管理**: 使用专用的部署密钥，定期轮换
2. **网络安全**: 限制 SSH 访问来源，使用 VPN 或专用网络
3. **API 认证**: 使用强密码的 API 令牌，启用 HTTPS
4. **权限控制**: 使用最小权限原则，避免使用 root 用户

## 📈 扩展性

### 添加新的连接方式

1. 在 `RemoteEnvironmentConfig` 中添加新的连接方法
2. 在 `RemoteDeploymentCoordinator` 中实现对应的触发逻辑
3. 更新配置文件格式和文档

### 支持更多环境类型

1. 扩展 `RemoteEnvironmentType` 枚举
2. 添加特定环境的处理逻辑
3. 更新配置验证和文档

## 🤝 贡献指南

1. 遵循 PowerAutomation MCP 组织规范
2. 所有 MCP 通信通过中央协调器进行
3. 保持向后兼容性
4. 添加充分的测试和文档

---

**PowerAutomation Team**  
*让分布式部署变得简单而可靠*

