# -*- coding: utf-8 -*-
"""
簡化Agent工廠函數和使用示例
Simplified Agent Factory and Usage Examples
"""

import asyncio
import logging
from typing import Dict, Any, Optional

# 導入核心組件
from core.agent_core import AgentCore, AgentRequest, AgentResponse, Priority
from tools.tool_registry import ToolRegistry
from actions.action_executor import ActionExecutor, ExecutionMode
from config.config import get_config, apply_env_overrides, validate_config

logger = logging.getLogger(__name__)

class SimplifiedAgent:
    """
    簡化Agent包裝類
    提供更簡潔的使用接口
    """
    
    def __init__(self, agent_core: AgentCore, tool_registry: ToolRegistry, action_executor: ActionExecutor):
        self.agent_core = agent_core
        self.tool_registry = tool_registry
        self.action_executor = action_executor
        self._request_counter = 0
    
    async def process(self, content: str, request_type: str = "general", priority: Priority = Priority.MEDIUM, **kwargs) -> Dict[str, Any]:
        """
        簡化的處理接口
        
        Args:
            content: 請求內容
            request_type: 請求類型
            priority: 優先級
            **kwargs: 其他參數
        
        Returns:
            處理結果字典
        """
        self._request_counter += 1
        request_id = f"req_{self._request_counter}_{int(asyncio.get_event_loop().time())}"
        
        request = AgentRequest(
            id=request_id,
            type=request_type,
            content=content,
            priority=priority,
            context=kwargs.get('context', {}),
            timeout=kwargs.get('timeout', 300),
            metadata=kwargs.get('metadata', {})
        )
        
        response = await self.agent_core.process_request(request)
        
        return {
            'success': response.status.value == 'completed',
            'result': response.result,
            'error': response.error,
            'execution_time': response.execution_time,
            'tools_used': response.tools_used,
            'confidence': response.confidence,
            'request_id': request_id
        }
    
    async def analyze(self, content: str, **kwargs) -> Dict[str, Any]:
        """分析請求的快捷方法"""
        return await self.process(content, "analysis", **kwargs)
    
    async def monitor(self, content: str, **kwargs) -> Dict[str, Any]:
        """監控請求的快捷方法"""
        return await self.process(content, "monitoring", **kwargs)
    
    async def workflow(self, content: str, **kwargs) -> Dict[str, Any]:
        """工作流請求的快捷方法"""
        return await self.process(content, "workflow", **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """獲取Agent狀態"""
        return {
            'agent_status': self.agent_core.get_status(),
            'tool_registry_stats': self.tool_registry.get_registry_stats(),
            'executor_stats': self.action_executor.get_executor_stats()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """執行健康檢查"""
        await self.tool_registry.health_check_all()
        
        status = self.get_status()
        
        return {
            'healthy': status['agent_status']['health'] == 'healthy',
            'available_tools': status['tool_registry_stats']['available_tools'],
            'total_tools': status['tool_registry_stats']['total_tools'],
            'success_rate': status['executor_stats']['success_rate']
        }

async def create_PowerAutomation(env: str = 'development', config_overrides: Dict[str, Any] = None) -> SimplifiedAgent:
    """
    工廠函數：創建簡化Agent實例
    
    Args:
        env: 環境名稱 (development, production, testing)
        config_overrides: 配置覆蓋
    
    Returns:
        SimplifiedAgent實例
    """
    logger.info(f"Creating simplified agent for environment: {env}")
    
    # 獲取配置
    config = get_config(env)
    config = apply_env_overrides(config)
    
    # 應用配置覆蓋
    if config_overrides:
        for key, value in config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    # 驗證配置
    if not validate_config(config):
        raise ValueError("Invalid configuration")
    
    # 設置日誌
    logging.basicConfig(
        level=getattr(logging, config.LOGGING['level']),
        format=config.LOGGING['format']
    )
    
    # 創建核心組件
    tool_registry = ToolRegistry(config.TOOL_REGISTRY)
    action_executor = ActionExecutor(config.ACTION_EXECUTOR)
    agent_core = AgentCore(config.AGENT_CORE)
    
    # 設置依賴關係
    agent_core.set_dependencies(tool_registry, action_executor)
    action_executor.set_tool_registry(tool_registry)
    
    # 初始化組件
    await tool_registry.initialize()
    
    logger.info("Simplified agent created successfully")
    
    return SimplifiedAgent(agent_core, tool_registry, action_executor)

# 使用示例
async def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 創建Agent
    agent = await create_PowerAutomation('development')
    
    # 基本處理
    result = await agent.process("請分析當前系統狀態")
    print(f"處理結果: {result['success']}")
    print(f"執行時間: {result['execution_time']:.2f}s")
    print(f"使用工具: {result['tools_used']}")
    
    # 使用快捷方法
    analysis_result = await agent.analyze("分析運營數據趨勢")
    print(f"分析結果: {analysis_result['result']}")
    
    monitor_result = await agent.monitor("檢查服務健康狀態")
    print(f"監控結果: {monitor_result['result']}")

async def example_advanced_usage():
    """高級使用示例"""
    print("\n=== 高級使用示例 ===")
    
    # 使用配置覆蓋
    config_overrides = {
        'ACTION_EXECUTOR': {
            'max_workers': 5,
            'default_timeout': 60
        }
    }
    
    agent = await create_PowerAutomation('development', config_overrides)
    
    # 帶上下文的處理
    result = await agent.process(
        content="優化數據庫性能",
        request_type="optimization",
        priority=Priority.HIGH,
        context={
            'database_type': 'postgresql',
            'current_load': 'high'
        },
        metadata={
            'user_id': 'admin',
            'department': 'ops'
        },
        timeout=120
    )
    
    print(f"優化結果: {result}")

async def example_monitoring_and_health():
    """監控和健康檢查示例"""
    print("\n=== 監控和健康檢查示例 ===")
    
    agent = await create_PowerAutomation('development')
    
    # 獲取狀態
    status = agent.get_status()
    print(f"Agent狀態: {status['agent_status']['health']}")
    print(f"可用工具數: {status['tool_registry_stats']['available_tools']}")
    print(f"執行成功率: {status['executor_stats']['success_rate']:.2%}")
    
    # 健康檢查
    health = await agent.health_check()
    print(f"系統健康: {health['healthy']}")
    print(f"工具可用性: {health['available_tools']}/{health['total_tools']}")

async def example_batch_processing():
    """批量處理示例"""
    print("\n=== 批量處理示例 ===")
    
    agent = await create_PowerAutomation('development')
    
    # 批量請求
    requests = [
        "分析CPU使用率",
        "檢查記憶體狀態", 
        "監控磁碟空間",
        "檢查網絡連接",
        "分析日誌錯誤"
    ]
    
    # 並發處理
    tasks = [agent.monitor(req) for req in requests]
    results = await asyncio.gather(*tasks)
    
    print("批量處理結果:")
    for i, result in enumerate(results):
        print(f"  {i+1}. {requests[i]}: {'成功' if result['success'] else '失敗'}")

async def example_error_handling():
    """錯誤處理示例"""
    print("\n=== 錯誤處理示例 ===")
    
    agent = await create_PowerAutomation('development')
    
    try:
        # 模擬可能失敗的請求
        result = await agent.process(
            content="執行不存在的操作",
            request_type="invalid_type",
            timeout=5  # 短超時
        )
        
        if not result['success']:
            print(f"請求失敗: {result['error']}")
        else:
            print(f"請求成功: {result['result']}")
            
    except Exception as e:
        print(f"異常處理: {e}")

async def example_custom_workflow():
    """自定義工作流示例"""
    print("\n=== 自定義工作流示例 ===")
    
    agent = await create_PowerAutomation('development')
    
    # 複雜的工作流請求
    workflow_content = """
    請執行以下工作流:
    1. 檢查系統資源使用情況
    2. 分析當前運行的服務狀態
    3. 識別潛在的性能瓶頸
    4. 提供優化建議
    5. 生成詳細報告
    """
    
    result = await agent.workflow(
        content=workflow_content,
        context={
            'workflow_type': 'system_optimization',
            'priority': 'high',
            'report_format': 'detailed'
        }
    )
    
    print(f"工作流執行結果:")
    print(f"  成功: {result['success']}")
    print(f"  執行時間: {result['execution_time']:.2f}s")
    print(f"  置信度: {result['confidence']:.2%}")
    print(f"  使用工具: {', '.join(result['tools_used'])}")

# 主函數
async def main():
    """主函數 - 運行所有示例"""
    print("🚀 簡化Agent架構 - 使用示例")
    print("=" * 50)
    
    try:
        await example_basic_usage()
        await example_advanced_usage()
        await example_monitoring_and_health()
        await example_batch_processing()
        await example_error_handling()
        await example_custom_workflow()
        
        print("\n✅ 所有示例執行完成!")
        
    except Exception as e:
        print(f"\n❌ 示例執行失敗: {e}")
        logger.exception("Example execution failed")

if __name__ == "__main__":
    # 運行示例
    asyncio.run(main())

