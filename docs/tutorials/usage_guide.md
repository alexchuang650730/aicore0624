# 🚀 簡化Agent架構 - 使用指南

## 📋 概述

簡化Agent架構是基於Kimi-Researcher理念設計的統一AI決策系統，旨在替代複雜的Product-Workflow-Adapter三層架構，提供更高效、更易維護的解決方案。

## 🏗️ 架構組件

### 核心組件
- **Agent Core**: 統一的AI決策中心
- **Tool Registry**: 工具發現和管理系統
- **Action Executor**: 統一執行引擎
- **Configuration**: 統一配置管理

### 目錄結構
```
simplified_agent/
├── core/
│   └── agent_core.py          # Agent核心
├── tools/
│   └── tool_registry.py       # 工具註冊系統
├── actions/
│   └── action_executor.py     # 執行引擎
├── config/
│   └── config.py             # 配置管理
├── docs/
│   ├── architecture_design.md # 架構設計文檔
│   └── usage_guide.md        # 使用指南
└── examples/
    └── example_usage.py      # 使用示例
```

## 🚀 快速開始

### 1. 基本使用

```python
import asyncio
from core.agent_core import AgentCore, AgentRequest, Priority
from tools.tool_registry import ToolRegistry
from actions.action_executor import ActionExecutor
from config.config import get_config

async def main():
    # 獲取配置
    config = get_config('development')
    
    # 創建組件
    tool_registry = ToolRegistry(config.TOOL_REGISTRY)
    action_executor = ActionExecutor(config.ACTION_EXECUTOR)
    agent_core = AgentCore(config.AGENT_CORE)
    
    # 設置依賴
    agent_core.set_dependencies(tool_registry, action_executor)
    action_executor.set_tool_registry(tool_registry)
    
    # 初始化
    await tool_registry.initialize()
    
    # 創建請求
    request = AgentRequest(
        id="demo_001",
        type="analysis",
        content="請分析系統運行狀態並提供優化建議",
        priority=Priority.HIGH
    )
    
    # 處理請求
    response = await agent_core.process_request(request)
    
    print(f"Response: {response.result}")
    print(f"Status: {response.status}")
    print(f"Execution time: {response.execution_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 工廠模式使用

```python
from simplified_agent_factory import create_simplified_agent

async def quick_start():
    # 使用工廠函數快速創建
    agent = await create_simplified_agent('development')
    
    # 直接使用
    response = await agent.process("監控系統狀態")
    print(response)
```

## 🔧 配置說明

### 環境配置

支持三種環境配置：
- **development**: 開發環境
- **production**: 生產環境  
- **testing**: 測試環境

```python
from config.config import get_config

# 獲取開發環境配置
dev_config = get_config('development')

# 獲取生產環境配置
prod_config = get_config('production')
```

### 環境變量覆蓋

支持通過環境變量覆蓋配置：

```bash
export AGENT_ENV=production
export AGENT_NAME=my_agent
export AGENT_LOG_LEVEL=DEBUG
export AGENT_MAX_WORKERS=20
export AGENT_TIMEOUT=300
```

### 主要配置項

```python
# Agent Core配置
AGENT_CORE = {
    'max_concurrent_requests': 50,
    'request_timeout': 300,
    'history_limit': 1000,
    'performance_tracking': True
}

# Tool Registry配置
TOOL_REGISTRY = {
    'auto_discovery': True,
    'discovery_interval': 300,
    'health_check_interval': 60
}

# Action Executor配置
ACTION_EXECUTOR = {
    'max_workers': 10,
    'max_concurrent_tasks': 20,
    'default_timeout': 30
}
```

## 🛠️ 工具管理

### 自動發現工具

系統會自動發現以下類型的工具：
- **MCP服務**: 基於HTTP的MCP服務
- **HTTP API**: RESTful API服務
- **Python模塊**: 本地Python工具
- **Shell命令**: 系統命令工具

### 手動註冊工具

```python
from tools.tool_registry import ToolInfo, ToolType, ToolCapability

# 創建工具信息
tool_info = ToolInfo(
    id="custom_tool",
    name="Custom Tool",
    type=ToolType.PYTHON_MODULE,
    description="自定義工具",
    version="1.0.0",
    capabilities=[
        ToolCapability(
            name="custom_processing",
            description="自定義處理能力",
            input_types=["text"],
            output_types=["json"]
        )
    ]
)

# 註冊工具
await tool_registry.register_tool(tool_info)
```

### 工具查詢

```python
# 獲取所有可用工具
available_tools = await tool_registry.get_available_tools()

# 根據能力查找工具
monitoring_tools = await tool_registry.find_tools_by_capability('monitoring')

# 根據標籤查找工具
mcp_tools = await tool_registry.find_tools_by_tag('mcp')

# 獲取工具詳細信息
tool_info = await tool_registry.get_tool_info('mcp_operations_workflow_mcp')
```

## ⚡ 執行模式

### 並行執行 (默認)

```python
from actions.action_executor import ExecutionMode

# 並行執行多個工具
result = await action_executor.execute(
    request=request,
    tools=['tool1', 'tool2', 'tool3'],
    mode=ExecutionMode.PARALLEL
)
```

### 順序執行

```python
# 順序執行工具
result = await action_executor.execute(
    request=request,
    tools=['tool1', 'tool2', 'tool3'],
    mode=ExecutionMode.SEQUENTIAL
)
```

### 管道執行

```python
# 管道執行（前一個工具的輸出作為下一個工具的輸入）
result = await action_executor.execute(
    request=request,
    tools=['preprocessor', 'analyzer', 'formatter'],
    mode=ExecutionMode.PIPELINE
)
```

## 📊 監控和統計

### Agent狀態監控

```python
# 獲取Agent狀態
status = agent_core.get_status()
print(f"Active tasks: {status['active_tasks']}")
print(f"Total processed: {status['total_processed']}")
print(f"Performance metrics: {status['performance_metrics']}")
```

### 工具註冊統計

```python
# 獲取工具註冊統計
stats = tool_registry.get_registry_stats()
print(f"Total tools: {stats['total_tools']}")
print(f"Available tools: {stats['available_tools']}")
print(f"Type distribution: {stats['type_distribution']}")
```

### 執行器統計

```python
# 獲取執行器統計
stats = action_executor.get_executor_stats()
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Average execution time: {stats['average_execution_time']:.2f}s")
```

## 🔍 調試和故障排除

### 日誌配置

```python
import logging

# 設置日誌級別
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 健康檢查

```python
# 檢查所有工具健康狀態
await tool_registry.health_check_all()

# 檢查單個工具
is_healthy = await tool_registry.health_check_tool('mcp_operations_workflow_mcp')
```

### 錯誤處理

```python
try:
    response = await agent_core.process_request(request)
    if response.status == TaskStatus.FAILED:
        print(f"Request failed: {response.error}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🎯 最佳實踐

### 1. 請求設計

```python
# 好的請求設計
request = AgentRequest(
    id="unique_id",
    type="specific_type",  # 明確的類型
    content="清晰的需求描述",
    context={"key": "value"},  # 提供上下文
    priority=Priority.HIGH,
    timeout=300
)
```

### 2. 錯誤處理

```python
# 完整的錯誤處理
try:
    response = await agent_core.process_request(request)
    
    if response.status == TaskStatus.COMPLETED:
        # 處理成功結果
        result = response.result
    elif response.status == TaskStatus.FAILED:
        # 處理失敗情況
        logger.error(f"Request failed: {response.error}")
    else:
        # 處理其他狀態
        logger.warning(f"Unexpected status: {response.status}")
        
except asyncio.TimeoutError:
    logger.error("Request timeout")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### 3. 性能優化

```python
# 使用適當的執行模式
if tools_are_independent:
    mode = ExecutionMode.PARALLEL  # 並行執行
elif tools_have_dependencies:
    mode = ExecutionMode.PIPELINE  # 管道執行
else:
    mode = ExecutionMode.SEQUENTIAL  # 順序執行

# 設置合理的超時時間
request.timeout = estimated_execution_time * 2
```

### 4. 監控和維護

```python
# 定期檢查系統狀態
async def health_check():
    agent_status = agent_core.get_status()
    registry_stats = tool_registry.get_registry_stats()
    executor_stats = action_executor.get_executor_stats()
    
    # 記錄關鍵指標
    logger.info(f"Agent health: {agent_status['health']}")
    logger.info(f"Available tools: {registry_stats['available_tools']}")
    logger.info(f"Success rate: {executor_stats['success_rate']:.2%}")

# 定期執行健康檢查
asyncio.create_task(health_check())
```

## 🔄 遷移指南

### 從三層架構遷移

1. **識別現有功能**
   - Product Layer → Agent Core的需求分析
   - Workflow Layer → Tool Registry的工具選擇
   - Adapter Layer → Action Executor的執行邏輯

2. **重構步驟**
   ```python
   # 原來的三層調用
   product_result = await product_layer.analyze(request)
   workflow_result = await workflow_layer.select_components(product_result)
   adapter_result = await adapter_layer.execute(workflow_result)
   
   # 簡化為單一調用
   response = await agent_core.process_request(request)
   ```

3. **工具適配**
   - 將現有MCP服務註冊到Tool Registry
   - 將現有API包裝為統一工具接口
   - 遷移現有業務邏輯到Action Executor

## 📚 API參考

### AgentCore

- `process_request(request: AgentRequest) -> AgentResponse`
- `get_status() -> Dict[str, Any]`
- `get_task_history(limit: int) -> List[Dict[str, Any]]`

### ToolRegistry

- `initialize() -> None`
- `register_tool(tool_info: ToolInfo) -> None`
- `get_available_tools() -> List[str]`
- `find_tools_by_capability(capability: str) -> List[str]`
- `health_check_all() -> None`

### ActionExecutor

- `execute(request, tools: List[str], mode: ExecutionMode) -> Dict[str, Any]`
- `get_executor_stats() -> Dict[str, Any]`

## 🤝 貢獻指南

1. Fork項目
2. 創建功能分支
3. 提交更改
4. 創建Pull Request

## 📄 許可證

MIT License

---

**簡化Agent架構 - 讓AI系統更簡單、更高效！** 🚀

