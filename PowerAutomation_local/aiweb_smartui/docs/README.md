# AIWeb + SmartUI 组件

PowerAutomation Local 的 AIWeb 和 SmartUI AI-First IDE 组件。

## 📖 组件简介

这是 PowerAutomation Local 系统中的 AIWeb + SmartUI 组件，提供：

- **AIWeb前端**：简洁的Web入口平台，一键连接SmartUI
- **SmartUI前端**：AI-First IDE界面
- **SmartUI MCP后端**：遵循PowerAutomation MCP规范的后端服务

## 🏗️ 目录结构

```
aiweb_smartui/
├── frontend/
│   ├── aiweb/              # AIWeb前端
│   │   └── index.html
│   └── smartui/            # SmartUI前端
│       └── index.html
├── backend/
│   └── smartui_mcp.py      # SmartUI MCP后端服务
├── config/
│   └── requirements.txt    # Python依赖
├── docs/
│   └── README.md          # 本文档
├── logs/                  # 运行日志（自动创建）
├── venv/                  # Python虚拟环境（自动创建）
├── start_aiweb_smartui.sh # 启动脚本
└── stop_aiweb_smartui.sh  # 停止脚本
```

## 🚀 快速开始

### 启动服务
```bash
# 在PowerAutomation_local/aiweb_smartui目录中执行
./start_aiweb_smartui.sh
```

### 停止服务
```bash
./stop_aiweb_smartui.sh
```

### 访问服务
- **AIWeb入口**：http://localhost:8081
- **SmartUI IDE**：http://localhost:3000
- **后端API**：http://localhost:5001

## 🔧 技术规范

### MCP规范遵循
- 遵循PowerAutomation MCP组织规范
- 文件名包含`_mcp`后缀
- 提供独立的CLI接口
- 支持工具注册规范

### 端口配置
- **AIWeb前端**：8081
- **SmartUI前端**：3000
- **SmartUI MCP后端**：5001 (避免macOS AirPlay端口冲突)

### 依赖管理
- 使用独立的Python虚拟环境
- 最小化依赖：flask, flask-cors, requests

## 🔗 与PowerAutomation Local集成

### 目录组织
- 严格遵循PowerAutomation目录与文件组织规范
- 作为独立组件集成到PowerAutomation_local中
- 避免随意新增目录或文件

### MCP通信
- 通过PowerAutomation的中央协调器进行MCP间通信
- 不采用直接互传的方式
- 支持工具注册和管理

## 📊 日志管理

### 日志文件
- `logs/smartui_backend.log` - SmartUI MCP后端日志
- `logs/smartui_frontend.log` - SmartUI前端日志
- `logs/aiweb_frontend.log` - AIWeb前端日志
- `logs/pip_install.log` - 依赖安装日志

### 查看日志
```bash
# 查看所有日志
tail -f logs/*.log

# 查看特定服务日志
tail -f logs/smartui_backend.log
```

## 🛠️ 开发指南

### 添加新功能
1. 遵循PowerAutomation MCP规范
2. 在工具表中注册新工具
3. 通过中央协调器进行通信
4. 更新相关文档

### 测试
```bash
# 健康检查
curl http://localhost:5001/health

# MCP信息
curl http://localhost:5001/api/mcp/info
```

## 🔄 更新和维护

### 更新依赖
```bash
# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r config/requirements.txt --upgrade

# 退出虚拟环境
deactivate
```

### 重启服务
```bash
./stop_aiweb_smartui.sh
./start_aiweb_smartui.sh
```

## 📞 支持

如有问题：
1. 查看日志文件
2. 检查服务状态
3. 参考PowerAutomation Local主文档
4. 提交Issue到aicore0624仓库

---

**PowerAutomation Local - AIWeb & SmartUI 组件**

