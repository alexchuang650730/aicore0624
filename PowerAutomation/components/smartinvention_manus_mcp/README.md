# SmartInvention Manus Mode MCP

SmartInvention Manus模式MCP - 专为精确对话任务编排及任务规划分析设计的增强版MCP组件。

## 功能特性

### 1. 文件Checkin状态管理
- **自动检测文件checkin状态**：checked_in, pending, modified, unknown
- **文件哈希追踪**：监控文件变更
- **待处理更改识别**：自动识别需要处理的文件修改
- **状态汇总报告**：提供详细的checkin状态统计

### 2. Agent目录管理
- **自动创建Agent目录结构**：为每个任务和Agent创建独立目录
- **对话记录存储**：完整保存Agent的对话历史
- **修改记录追踪**：记录Agent的所有修改操作
- **Agent注册管理**：维护Agent的注册信息和状态

### 3. SmartUI集成接口
- **智能问题分类**：自动识别问题类型并路由到相应处理器
- **实时响应生成**：基于实际数据生成智能响应
- **多类型问题支持**：任务状态、文件checkin、对话历史、Agent信息等
- **RESTful API**：提供标准的HTTP接口供SmartUI调用

## 核心组件

### SmartinventionManusModeMCP
增强版SmartInvention MCP主类，继承自原有的SmartinventionAdapterMCP，添加了Manus模式特有功能。

**主要方法：**
- `get_latest_tasks_with_checkin()` - 获取最新任务及checkin状态
- `save_tasks_complete_history()` - 保存完整任务历史
- `get_checkin_summary()` - 获取checkin状态汇总
- `get_agent_summary()` - 获取Agent状态汇总

### FileCheckinManager
文件checkin状态管理器，负责检查和追踪文件的checkin状态。

**核心功能：**
- 文件状态检测算法
- checkin记录持久化存储
- 状态变更历史追踪
- 批量状态检查优化

### AgentDirectoryManager
Agent目录管理器，负责创建和维护Agent的工作目录结构。

**目录结构：**
```
/tmp/smartinvention_agents/
├── task_{task_id}/
│   └── agent_{agent_id}/
│       ├── agent_config.json
│       ├── conversations/
│       ├── modifications/
│       ├── files/
│       └── logs/
```

### SmartUIResponseGenerator
SmartUI响应生成器，提供智能问答和响应生成功能。

**支持的问题类型：**
- 任务状态查询
- 文件checkin状态
- 对话历史检索
- Agent信息查询
- 修改记录追踪
- 标准合规检查

## API接口

### HTTP端点

#### `/health`
- **方法**: GET
- **描述**: 健康检查
- **响应**: 服务状态信息

#### `/api/smartui-question`
- **方法**: POST
- **描述**: 处理SmartUI问题
- **请求体**:
  ```json
  {
    "question": "最新的5个任务状态如何？",
    "context": {}
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "question": "最新的5个任务状态如何？",
    "category": "task_status",
    "data": {...},
    "answer": "最新的5个任务是：...",
    "timestamp": "2025-01-01T00:00:00"
  }
  ```

#### `/api/manus-status`
- **方法**: GET
- **描述**: 获取Manus模式整体状态
- **响应**: 任务、checkin、Agent的汇总状态

#### `/api/initialize-mcp`
- **方法**: POST
- **描述**: 初始化MCP实例
- **响应**: 初始化结果

## 使用方法

### 1. 启动服务
```bash
python3 smartui_manus_integration.py
```

### 2. 初始化MCP
```python
from smartinvention_mcp_enhanced import SmartinventionManusModeMCP

config = {
    "manus": {
        "base_url": "https://manus.im",
        "app_url": "https://manus.im/app/oXk20YJhBI530ArzGBJEJC",
        "auto_login": True
    }
}

mcp = SmartinventionManusModeMCP(config)
await mcp.initialize()
```

### 3. 获取任务checkin状态
```python
result = await mcp.handle_request("get_latest_tasks_with_checkin", {"limit": 5})
tasks = result.get("tasks", [])
```

### 4. 保存完整历史
```python
result = await mcp.handle_request("save_tasks_complete_history", {})
```

### 5. SmartUI问答
```bash
curl -X POST http://localhost:5003/api/smartui-question \
  -H "Content-Type: application/json" \
  -d '{"question": "最新任务的文件checkin状态如何？"}'
```

## 数据模型

### FileCheckinStatus
```python
@dataclass
class FileCheckinStatus:
    file_path: str
    file_name: str
    task_id: str
    checkin_status: str  # 'checked_in', 'pending', 'modified', 'unknown'
    last_modified: datetime
    file_hash: str
    checkin_user: Optional[str] = None
    checkin_time: Optional[datetime] = None
    pending_changes: List[str] = field(default_factory=list)
```

### AgentInfo
```python
@dataclass
class AgentInfo:
    agent_id: str
    agent_name: str
    agent_type: str  # 'human', 'ai', 'system'
    task_id: str
    created_at: datetime
    last_active: datetime
    conversation_count: int = 0
    modification_count: int = 0
```

## 配置说明

### MCP配置
```python
config = {
    "manus": {
        "base_url": "https://manus.im",
        "app_url": "https://manus.im/app/oXk20YJhBI530ArzGBJEJC",
        "login_email": "your_email",
        "login_password": "your_password",
        "auto_login": True
    }
}
```

### 存储配置
- **Checkin数据**: `/tmp/smartinvention_checkin/`
- **Agent目录**: `/tmp/smartinvention_agents/`
- **日志文件**: 标准Python logging

## 依赖要求

```
flask>=2.0.0
flask-cors>=3.0.0
aiohttp>=3.8.0
aiofiles>=0.8.0
asyncio
```

## 版本信息

- **版本**: 3.0.0 - Manus Mode
- **作者**: Manus AI
- **日期**: 2025-01-01
- **基于**: SmartInvention MCP 2.x

## 更新日志

### v3.0.0 - Manus Mode (2025-01-01)
- ✅ 新增文件checkin状态管理
- ✅ 新增Agent目录管理系统
- ✅ 新增SmartUI集成接口
- ✅ 新增智能问题分类和响应生成
- ✅ 新增RESTful API支持
- ✅ 增强数据持久化存储
- ✅ 优化异步处理性能

## 许可证

本项目遵循MIT许可证。

## 支持

如有问题或建议，请联系Manus AI团队。

