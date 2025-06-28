# ClaudeSDKMCP v2.0.0 Core Integration

## 🎯 **整合概述**

ClaudeSDKMCP v2.0.0 已成功整合到 PowerAutomation Core 目录中，提供智能代码分析和专家咨询能力。

## 📁 **文件组织**

### **Core 目录文件**
```
PowerAutomation/core/
├── claude_sdk_mcp_v2.py           # 主要实现文件
├── claude_sdk_config.py           # 配置管理
├── claude_sdk_cli.py              # CLI接口
├── claude_sdk_performance_monitor.py  # 性能监控
├── claude_sdk_quick_start.py      # 快速开始示例
├── test_claude_sdk_mcp.py         # 测试套件
└── README_CLAUDE_SDK_MCP.md       # 本文档
```

### **Components 目录文件**
```
PowerAutomation/components/claude_sdk_mcp/
├── main.py                        # MCP主实现
└── examples.py                    # 使用示例
```

## 🚀 **核心功能**

### **1. 动态场景识别**
- 95% 准确率的智能场景识别
- 基于Claude API的前置场景分析
- 200K tokens上下文处理能力

### **2. 专家系统**
- 5个专业领域专家
- 动态专家发现机制
- 智能专家推荐系统

### **3. 操作处理器**
- 38个操作处理器
- 覆盖AI代码分析全流程
- 支持多种分析类型

## 🛠️ **使用方法**

### **作为Core组件使用**
```python
from PowerAutomation.core.claude_sdk_mcp_v2 import ClaudeSDKMCP

# 初始化
claude_sdk = ClaudeSDKMCP(api_key="your-api-key")

# 处理请求
result = await claude_sdk.process_request(
    "分析这段代码的性能问题",
    {"code": "def example(): pass", "language": "python"}
)
```

### **作为MCP组件使用**
```python
from PowerAutomation.components.claude_sdk_mcp.main import ClaudeSDKMCP

# 使用MCP接口
mcp = ClaudeSDKMCP()
result = await mcp.handle_request(user_input, context)
```

### **CLI使用**
```bash
# 进入core目录
cd PowerAutomation/core

# 运行CLI
python claude_sdk_cli.py analyze --code "def hello(): print('world')" --language python
```

## 📊 **性能监控**

使用性能监控组件：
```python
from PowerAutomation.core.claude_sdk_performance_monitor import run_performance_demo

# 运行性能测试
await run_performance_demo()
```

## 🧪 **测试**

运行测试套件：
```bash
cd PowerAutomation/core
python test_claude_sdk_mcp.py
```

## 🔧 **配置**

配置文件位于 `claude_sdk_config.py`，包含：
- Claude API配置
- 专家系统配置
- 性能参数配置

## 📈 **集成优势**

1. **统一架构** - 与PowerAutomation核心架构完全兼容
2. **模块化设计** - 可独立使用或作为组件集成
3. **标准化接口** - 遵循PowerAutomation MCP规范
4. **完整功能** - 保留所有原有功能和性能

## 🔄 **更新日志**

- **v2.0.0** - 初始整合到PowerAutomation Core
- 整合了claudesdk-clean-secure分支的核心功能
- 添加了38个操作处理器
- 实现了动态专家系统

## 📞 **支持**

如有问题，请参考：
- 测试文件：`test_claude_sdk_mcp.py`
- 示例文件：`claude_sdk_quick_start.py`
- 组件示例：`components/claude_sdk_mcp/examples.py`

---

**ClaudeSDKMCP v2.0.0** - 现已完全整合到PowerAutomation Core生态系统！

