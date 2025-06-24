# 🔄 統一MCP協同框架設計

## 🎯 **問題分析**

當前MCP組件間存在的協同問題：

### ❌ **硬編碼依賴問題**
```python
# 當前的硬編碼方式
class WorkflowRecorder:
    def __init__(self):
        self.replay_parser = ReplayDataParser()  # 硬編碼依賴
        self.rl_srt = SimplifiedRLSRTAdapter()   # 硬編碼依賴
        self.log_manager = EnhancedInteractionLogManager()  # 硬編碼依賴
```

### 🔍 **核心問題**
1. **緊耦合**: 組件間直接依賴，難以替換和測試
2. **配置困難**: 無法動態配置組件組合
3. **擴展性差**: 添加新MCP需要修改現有代碼
4. **循環依賴**: 組件間可能形成循環引用
5. **版本衝突**: 不同組件可能需要不同版本的依賴

## 🏗️ **統一MCP協同框架**

### 1. **MCP服務註冊中心**
```python
# -*- coding: utf-8 -*-
"""
MCP服務註冊中心 - 統一管理所有MCP組件
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

class MCPServiceType(Enum):
    """MCP服務類型"""
    DATA_PROCESSOR = "data_processor"      # 數據處理器
    LEARNING_ENGINE = "learning_engine"    # 學習引擎
    RECORDER = "recorder"                  # 錄製器
    CLASSIFIER = "classifier"              # 分類器
    EXECUTOR = "executor"                  # 執行器
    ANALYZER = "analyzer"                  # 分析器
    ADAPTER = "adapter"                    # 適配器

class MCPCapability(Enum):
    """MCP能力標識"""
    # 數據處理能力
    PARSE_REPLAY_DATA = "parse_replay_data"
    PROCESS_WORKFLOW = "process_workflow"
    EXTRACT_FEATURES = "extract_features"
    STANDARDIZE_DATA = "standardize_data"
    
    # 學習能力
    PATTERN_RECOGNITION = "pattern_recognition"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    RECOMMENDATION = "recommendation"
    FEEDBACK_PROCESSING = "feedback_processing"
    
    # 錄製能力
    WORKFLOW_RECORDING = "workflow_recording"
    SESSION_MANAGEMENT = "session_management"
    QUALITY_ASSESSMENT = "quality_assessment"
    
    # 分類能力
    INTELLIGENT_CLASSIFICATION = "intelligent_classification"
    QUALITY_EVALUATION = "quality_evaluation"
    PATTERN_IDENTIFICATION = "pattern_identification"

@dataclass
class MCPServiceInfo:
    """MCP服務信息"""
    service_id: str
    service_name: str
    service_type: MCPServiceType
    capabilities: List[MCPCapability]
    version: str
    description: str
    instance: Any = None
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    status: str = "inactive"
    
class MCPServiceInterface(ABC):
    """MCP服務統一接口"""
    
    @abstractmethod
    def get_service_info(self) -> MCPServiceInfo:
        """獲取服務信息"""
        pass
    
    @abstractmethod
    async def initialize(self, registry: 'MCPServiceRegistry') -> bool:
        """初始化服務"""
        pass
    
    @abstractmethod
    async def process_request(self, request_type: str, data: Any, context: Dict[str, Any] = None) -> Any:
        """處理請求"""
        pass
    
    @abstractmethod
    async def handle_event(self, event_type: str, event_data: Any) -> None:
        """處理事件"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """關閉服務"""
        pass

class MCPServiceRegistry:
    """MCP服務註冊中心"""
    
    def __init__(self):
        self.services: Dict[str, MCPServiceInfo] = {}
        self.capability_map: Dict[MCPCapability, List[str]] = {}
        self.event_bus = MCPEventBus()
        self.dependency_resolver = MCPDependencyResolver()
        self.logger = logging.getLogger(__name__)
    
    def register_service(self, service: MCPServiceInterface) -> bool:
        """註冊MCP服務"""
        try:
            service_info = service.get_service_info()
            service_info.instance = service
            
            # 檢查服務ID唯一性
            if service_info.service_id in self.services:
                self.logger.warning(f"服務 {service_info.service_id} 已存在，將被覆蓋")
            
            # 註冊服務
            self.services[service_info.service_id] = service_info
            
            # 更新能力映射
            for capability in service_info.capabilities:
                if capability not in self.capability_map:
                    self.capability_map[capability] = []
                self.capability_map[capability].append(service_info.service_id)
            
            self.logger.info(f"✅ 服務註冊成功: {service_info.service_name} ({service_info.service_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 服務註冊失敗: {e}")
            return False
    
    def unregister_service(self, service_id: str) -> bool:
        """註銷MCP服務"""
        try:
            if service_id not in self.services:
                self.logger.warning(f"服務 {service_id} 不存在")
                return False
            
            service_info = self.services[service_id]
            
            # 從能力映射中移除
            for capability in service_info.capabilities:
                if capability in self.capability_map:
                    self.capability_map[capability].remove(service_id)
                    if not self.capability_map[capability]:
                        del self.capability_map[capability]
            
            # 移除服務
            del self.services[service_id]
            
            self.logger.info(f"✅ 服務註銷成功: {service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 服務註銷失敗: {e}")
            return False
    
    def get_services_by_capability(self, capability: MCPCapability) -> List[MCPServiceInfo]:
        """根據能力獲取服務列表"""
        service_ids = self.capability_map.get(capability, [])
        return [self.services[sid] for sid in service_ids if sid in self.services]
    
    def get_service(self, service_id: str) -> Optional[MCPServiceInfo]:
        """獲取指定服務"""
        return self.services.get(service_id)
    
    async def initialize_all_services(self) -> Dict[str, bool]:
        """初始化所有服務"""
        results = {}
        
        # 解析依賴順序
        init_order = self.dependency_resolver.resolve_dependencies(self.services)
        
        for service_id in init_order:
            service_info = self.services[service_id]
            try:
                success = await service_info.instance.initialize(self)
                service_info.status = "active" if success else "failed"
                results[service_id] = success
                
                if success:
                    self.logger.info(f"✅ 服務初始化成功: {service_info.service_name}")
                else:
                    self.logger.error(f"❌ 服務初始化失敗: {service_info.service_name}")
                    
            except Exception as e:
                self.logger.error(f"❌ 服務初始化異常: {service_info.service_name} - {e}")
                service_info.status = "error"
                results[service_id] = False
        
        return results
    
    async def request_service(self, capability: MCPCapability, request_type: str, 
                            data: Any, context: Dict[str, Any] = None) -> Any:
        """請求具有指定能力的服務"""
        services = self.get_services_by_capability(capability)
        
        if not services:
            raise ValueError(f"沒有找到具有能力 {capability.value} 的服務")
        
        # 選擇最佳服務（可以根據負載、性能等因素選擇）
        best_service = self._select_best_service(services, request_type)
        
        if not best_service or best_service.status != "active":
            raise RuntimeError(f"沒有可用的服務處理請求: {capability.value}")
        
        try:
            result = await best_service.instance.process_request(request_type, data, context)
            
            # 發布事件
            await self.event_bus.publish_event("service_request_completed", {
                "service_id": best_service.service_id,
                "capability": capability.value,
                "request_type": request_type,
                "success": True
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"服務請求失敗: {best_service.service_id} - {e}")
            
            # 發布錯誤事件
            await self.event_bus.publish_event("service_request_failed", {
                "service_id": best_service.service_id,
                "capability": capability.value,
                "request_type": request_type,
                "error": str(e)
            })
            
            raise
    
    def _select_best_service(self, services: List[MCPServiceInfo], request_type: str) -> Optional[MCPServiceInfo]:
        """選擇最佳服務"""
        # 簡單策略：選擇第一個活躍的服務
        # 可以擴展為更複雜的負載均衡策略
        for service in services:
            if service.status == "active":
                return service
        return None
    
    def get_service_status(self) -> Dict[str, Any]:
        """獲取所有服務狀態"""
        return {
            "total_services": len(self.services),
            "active_services": len([s for s in self.services.values() if s.status == "active"]),
            "capabilities": len(self.capability_map),
            "services": {
                sid: {
                    "name": info.service_name,
                    "type": info.service_type.value,
                    "status": info.status,
                    "capabilities": [c.value for c in info.capabilities]
                }
                for sid, info in self.services.items()
            }
        }

class MCPEventBus:
    """MCP事件總線"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """訂閱事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """取消訂閱"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    async def publish_event(self, event_type: str, event_data: Any) -> None:
        """發布事件"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, event_data)
                    else:
                        callback(event_type, event_data)
                except Exception as e:
                    self.logger.error(f"事件處理失敗: {event_type} - {e}")

class MCPDependencyResolver:
    """MCP依賴解析器"""
    
    def resolve_dependencies(self, services: Dict[str, MCPServiceInfo]) -> List[str]:
        """解析服務依賴順序"""
        # 拓撲排序算法
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(service_id: str):
            if service_id in temp_visited:
                raise ValueError(f"檢測到循環依賴: {service_id}")
            
            if service_id not in visited:
                temp_visited.add(service_id)
                
                service_info = services.get(service_id)
                if service_info:
                    for dep in service_info.dependencies:
                        if dep in services:
                            visit(dep)
                
                temp_visited.remove(service_id)
                visited.add(service_id)
                result.append(service_id)
        
        for service_id in services:
            if service_id not in visited:
                visit(service_id)
        
        return result

# 全局註冊中心實例
mcp_registry = MCPServiceRegistry()
```

### 2. **動態MCP適配器**
```python
# -*- coding: utf-8 -*-
"""
動態MCP適配器 - 讓現有MCP組件無縫接入統一框架
"""

class WorkflowRecorderMCPAdapter(MCPServiceInterface):
    """Workflow Recorder MCP適配器"""
    
    def __init__(self, workflow_recorder_instance=None):
        self.workflow_recorder = workflow_recorder_instance or WorkflowRecorder()
        self.registry = None
    
    def get_service_info(self) -> MCPServiceInfo:
        return MCPServiceInfo(
            service_id="workflow_recorder",
            service_name="Workflow Recorder",
            service_type=MCPServiceType.RECORDER,
            capabilities=[
                MCPCapability.WORKFLOW_RECORDING,
                MCPCapability.SESSION_MANAGEMENT,
                MCPCapability.QUALITY_ASSESSMENT
            ],
            version="1.0.0",
            description="工作流錄製和會話管理服務",
            dependencies=[],  # 無硬編碼依賴
            provides=["workflow_data", "session_data", "quality_metrics"]
        )
    
    async def initialize(self, registry: MCPServiceRegistry) -> bool:
        """初始化服務"""
        try:
            self.registry = registry
            
            # 訂閱相關事件
            registry.event_bus.subscribe("replay_data_processed", self._handle_replay_data)
            registry.event_bus.subscribe("learning_feedback", self._handle_learning_feedback)
            
            return True
        except Exception as e:
            logging.error(f"Workflow Recorder 初始化失敗: {e}")
            return False
    
    async def process_request(self, request_type: str, data: Any, context: Dict[str, Any] = None) -> Any:
        """處理請求"""
        if request_type == "start_recording":
            return await self._start_recording(data, context)
        elif request_type == "stop_recording":
            return await self._stop_recording(data, context)
        elif request_type == "get_session_data":
            return await self._get_session_data(data, context)
        else:
            raise ValueError(f"不支持的請求類型: {request_type}")
    
    async def handle_event(self, event_type: str, event_data: Any) -> None:
        """處理事件"""
        if event_type == "replay_data_processed":
            await self._integrate_replay_data(event_data)
        elif event_type == "learning_feedback":
            await self._apply_learning_feedback(event_data)
    
    async def shutdown(self) -> None:
        """關閉服務"""
        # 清理資源
        pass
    
    async def _start_recording(self, data: Any, context: Dict[str, Any]) -> Any:
        """開始錄製"""
        session = await self.workflow_recorder.start_recording(**data)
        
        # 發布事件
        await self.registry.event_bus.publish_event("recording_started", {
            "session_id": session.session_id,
            "session_name": session.session_name,
            "workflow_type": session.workflow_type
        })
        
        return session
    
    async def _stop_recording(self, data: Any, context: Dict[str, Any]) -> Any:
        """停止錄製"""
        session = await self.workflow_recorder.stop_recording()
        
        if session and session.status == RecordingStatus.COMPLETED:
            # 自動請求數據處理服務
            try:
                session_data = self.workflow_recorder.export_session_data(session.session_id)
                
                # 請求Replay數據解析
                if session_data:
                    await self.registry.request_service(
                        MCPCapability.PARSE_REPLAY_DATA,
                        "parse_workflow_data",
                        session_data,
                        {"source": "workflow_recorder", "session_id": session.session_id}
                    )
                
            except Exception as e:
                logging.error(f"自動數據處理失敗: {e}")
        
        return session
    
    async def _handle_replay_data(self, event_type: str, event_data: Any) -> None:
        """處理Replay數據事件"""
        # 整合Replay數據到工作流分析中
        pass
    
    async def _integrate_replay_data(self, event_data: Any) -> None:
        """整合Replay數據"""
        # 將Replay分析結果整合到工作流質量評估中
        pass

class ReplayDataParserMCPAdapter(MCPServiceInterface):
    """Replay Data Parser MCP適配器"""
    
    def __init__(self, parser_instance=None):
        self.parser = parser_instance or ReplayDataParser()
        self.classifier = IntelligentReplayClassifier()
        self.registry = None
    
    def get_service_info(self) -> MCPServiceInfo:
        return MCPServiceInfo(
            service_id="replay_data_parser",
            service_name="Replay Data Parser",
            service_type=MCPServiceType.DATA_PROCESSOR,
            capabilities=[
                MCPCapability.PARSE_REPLAY_DATA,
                MCPCapability.EXTRACT_FEATURES,
                MCPCapability.INTELLIGENT_CLASSIFICATION
            ],
            version="1.0.0",
            description="Replay數據解析和智能分類服務",
            dependencies=[],
            provides=["parsed_replay_data", "classification_result", "feature_data"]
        )
    
    async def initialize(self, registry: MCPServiceRegistry) -> bool:
        """初始化服務"""
        try:
            self.registry = registry
            
            # 訂閱工作流錄製事件
            registry.event_bus.subscribe("recording_completed", self._handle_recording_completed)
            
            return True
        except Exception as e:
            logging.error(f"Replay Data Parser 初始化失敗: {e}")
            return False
    
    async def process_request(self, request_type: str, data: Any, context: Dict[str, Any] = None) -> Any:
        """處理請求"""
        if request_type == "parse_replay_data":
            return await self._parse_replay_data(data, context)
        elif request_type == "parse_workflow_data":
            return await self._parse_workflow_data(data, context)
        elif request_type == "classify_data":
            return await self._classify_data(data, context)
        else:
            raise ValueError(f"不支持的請求類型: {request_type}")
    
    async def handle_event(self, event_type: str, event_data: Any) -> None:
        """處理事件"""
        if event_type == "recording_completed":
            await self._process_recording_data(event_data)
    
    async def shutdown(self) -> None:
        """關閉服務"""
        pass
    
    async def _parse_replay_data(self, data: Any, context: Dict[str, Any]) -> Any:
        """解析Replay數據"""
        parsed_data = await self.parser.parse_replay_data(data)
        classification_result = self.classifier.classify_and_learn(parsed_data)
        
        # 發布解析完成事件
        await self.registry.event_bus.publish_event("replay_data_processed", {
            "parsed_data": parsed_data,
            "classification": classification_result,
            "context": context
        })
        
        # 自動請求學習服務
        try:
            await self.registry.request_service(
                MCPCapability.PATTERN_RECOGNITION,
                "learn_from_data",
                {
                    "parsed_data": parsed_data,
                    "classification": classification_result
                },
                context
            )
        except Exception as e:
            logging.error(f"自動學習請求失敗: {e}")
        
        return {
            "parsed_data": parsed_data,
            "classification": classification_result
        }
    
    async def _parse_workflow_data(self, data: Any, context: Dict[str, Any]) -> Any:
        """解析工作流數據"""
        # 將工作流數據轉換為Replay格式進行處理
        replay_format_data = self._convert_workflow_to_replay_format(data)
        return await self._parse_replay_data(replay_format_data, context)
    
    def _convert_workflow_to_replay_format(self, workflow_data: Any) -> Any:
        """將工作流數據轉換為Replay格式"""
        # 實現格式轉換邏輯
        return workflow_data

class RLSRTAdapterMCPAdapter(MCPServiceInterface):
    """RL SRT Adapter MCP適配器"""
    
    def __init__(self, rl_srt_instance=None):
        self.rl_srt = rl_srt_instance or SimplifiedRLSRTAdapter()
        self.registry = None
    
    def get_service_info(self) -> MCPServiceInfo:
        return MCPServiceInfo(
            service_id="rl_srt_adapter",
            service_name="RL SRT Adapter",
            service_type=MCPServiceType.LEARNING_ENGINE,
            capabilities=[
                MCPCapability.PATTERN_RECOGNITION,
                MCPCapability.STRATEGY_OPTIMIZATION,
                MCPCapability.RECOMMENDATION,
                MCPCapability.FEEDBACK_PROCESSING
            ],
            version="1.0.0",
            description="強化學習策略優化和推薦服務",
            dependencies=[],
            provides=["learning_insights", "recommendations", "strategy_updates"]
        )
    
    async def initialize(self, registry: MCPServiceRegistry) -> bool:
        """初始化服務"""
        try:
            self.registry = registry
            
            # 訂閱數據處理事件
            registry.event_bus.subscribe("replay_data_processed", self._handle_processed_data)
            registry.event_bus.subscribe("workflow_completed", self._handle_workflow_feedback)
            
            return True
        except Exception as e:
            logging.error(f"RL SRT Adapter 初始化失敗: {e}")
            return False
    
    async def process_request(self, request_type: str, data: Any, context: Dict[str, Any] = None) -> Any:
        """處理請求"""
        if request_type == "learn_from_data":
            return await self._learn_from_data(data, context)
        elif request_type == "get_recommendation":
            return await self._get_recommendation(data, context)
        elif request_type == "process_feedback":
            return await self._process_feedback(data, context)
        else:
            raise ValueError(f"不支持的請求類型: {request_type}")
    
    async def handle_event(self, event_type: str, event_data: Any) -> None:
        """處理事件"""
        if event_type == "replay_data_processed":
            await self._learn_from_processed_data(event_data)
        elif event_type == "workflow_completed":
            await self._process_workflow_feedback(event_data)
    
    async def shutdown(self) -> None:
        """關閉服務"""
        pass
    
    async def _learn_from_data(self, data: Any, context: Dict[str, Any]) -> Any:
        """從數據中學習"""
        learning_result = self.rl_srt.process_training_data(data)
        
        # 發布學習完成事件
        await self.registry.event_bus.publish_event("learning_completed", {
            "learning_result": learning_result,
            "context": context
        })
        
        return learning_result
    
    async def _get_recommendation(self, data: Any, context: Dict[str, Any]) -> Any:
        """獲取推薦"""
        recommendation = self.rl_srt.recommend_action(data)
        
        # 發布推薦事件
        await self.registry.event_bus.publish_event("recommendation_generated", {
            "recommendation": recommendation,
            "context": context
        })
        
        return recommendation
```

### 3. **配置驅動的組件組合**
```python
# -*- coding: utf-8 -*-
"""
配置驅動的MCP組合管理器
"""

class MCPCompositionManager:
    """MCP組合管理器"""
    
    def __init__(self, registry: MCPServiceRegistry):
        self.registry = registry
        self.compositions: Dict[str, MCPComposition] = {}
        self.logger = logging.getLogger(__name__)
    
    def load_composition_config(self, config_path: str) -> None:
        """從配置文件加載組合配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for comp_config in config.get('compositions', []):
            composition = MCPComposition.from_config(comp_config, self.registry)
            self.compositions[composition.name] = composition
    
    async def execute_composition(self, composition_name: str, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """執行組合流程"""
        if composition_name not in self.compositions:
            raise ValueError(f"組合 {composition_name} 不存在")
        
        composition = self.compositions[composition_name]
        return await composition.execute(input_data, context)

@dataclass
class MCPCompositionStep:
    """組合步驟"""
    step_id: str
    service_capability: MCPCapability
    request_type: str
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    condition: Optional[str] = None
    parallel: bool = False

class MCPComposition:
    """MCP組合"""
    
    def __init__(self, name: str, description: str, steps: List[MCPCompositionStep], registry: MCPServiceRegistry):
        self.name = name
        self.description = description
        self.steps = steps
        self.registry = registry
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def from_config(cls, config: Dict[str, Any], registry: MCPServiceRegistry) -> 'MCPComposition':
        """從配置創建組合"""
        steps = []
        for step_config in config.get('steps', []):
            step = MCPCompositionStep(
                step_id=step_config['step_id'],
                service_capability=MCPCapability(step_config['capability']),
                request_type=step_config['request_type'],
                input_mapping=step_config.get('input_mapping', {}),
                output_mapping=step_config.get('output_mapping', {}),
                condition=step_config.get('condition'),
                parallel=step_config.get('parallel', False)
            )
            steps.append(step)
        
        return cls(
            name=config['name'],
            description=config['description'],
            steps=steps,
            registry=registry
        )
    
    async def execute(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """執行組合流程"""
        context = context or {}
        execution_context = {
            'input': input_data,
            'results': {},
            'context': context
        }
        
        for step in self.steps:
            try:
                # 檢查條件
                if step.condition and not self._evaluate_condition(step.condition, execution_context):
                    self.logger.info(f"跳過步驟 {step.step_id}: 條件不滿足")
                    continue
                
                # 準備輸入數據
                step_input = self._prepare_step_input(step, execution_context)
                
                # 執行步驟
                result = await self.registry.request_service(
                    step.service_capability,
                    step.request_type,
                    step_input,
                    context
                )
                
                # 處理輸出
                self._process_step_output(step, result, execution_context)
                
                self.logger.info(f"✅ 步驟 {step.step_id} 執行成功")
                
            except Exception as e:
                self.logger.error(f"❌ 步驟 {step.step_id} 執行失敗: {e}")
                raise
        
        return execution_context['results']
    
    def _prepare_step_input(self, step: MCPCompositionStep, execution_context: Dict[str, Any]) -> Any:
        """準備步驟輸入"""
        if not step.input_mapping:
            return execution_context['input']
        
        step_input = {}
        for target_key, source_path in step.input_mapping.items():
            value = self._get_value_by_path(source_path, execution_context)
            step_input[target_key] = value
        
        return step_input
    
    def _process_step_output(self, step: MCPCompositionStep, result: Any, execution_context: Dict[str, Any]) -> None:
        """處理步驟輸出"""
        execution_context['results'][step.step_id] = result
        
        if step.output_mapping:
            for target_path, source_key in step.output_mapping.items():
                if isinstance(result, dict) and source_key in result:
                    self._set_value_by_path(target_path, result[source_key], execution_context)
    
    def _get_value_by_path(self, path: str, context: Dict[str, Any]) -> Any:
        """根據路徑獲取值"""
        keys = path.split('.')
        value = context
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def _set_value_by_path(self, path: str, value: Any, context: Dict[str, Any]) -> None:
        """根據路徑設置值"""
        keys = path.split('.')
        target = context
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """評估條件"""
        # 簡單的條件評估，可以擴展為更複雜的表達式解析
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
```

### 4. **配置文件示例**
```json
{
  "compositions": [
    {
      "name": "workflow_recording_to_learning",
      "description": "從工作流錄製到學習的完整流程",
      "steps": [
        {
          "step_id": "parse_workflow",
          "capability": "parse_replay_data",
          "request_type": "parse_workflow_data",
          "input_mapping": {
            "workflow_data": "input.session_data"
          },
          "output_mapping": {
            "parsed_data": "results.parse_workflow.parsed_data",
            "classification": "results.parse_workflow.classification"
          }
        },
        {
          "step_id": "learn_patterns",
          "capability": "pattern_recognition",
          "request_type": "learn_from_data",
          "input_mapping": {
            "training_data": "results.parse_workflow.parsed_data",
            "classification": "results.parse_workflow.classification"
          },
          "output_mapping": {
            "learning_insights": "results.learn_patterns.learning_result"
          }
        },
        {
          "step_id": "generate_recommendation",
          "capability": "recommendation",
          "request_type": "get_recommendation",
          "input_mapping": {
            "context": "context.task_context"
          },
          "condition": "results.learn_patterns.learning_result.confidence_score > 0.7"
        }
      ]
    },
    {
      "name": "replay_analysis_pipeline",
      "description": "Replay數據分析管道",
      "steps": [
        {
          "step_id": "parse_replay",
          "capability": "parse_replay_data",
          "request_type": "parse_replay_data",
          "input_mapping": {
            "replay_url": "input.replay_url"
          }
        },
        {
          "step_id": "classify_replay",
          "capability": "intelligent_classification",
          "request_type": "classify_data",
          "input_mapping": {
            "data": "results.parse_replay.parsed_data"
          }
        },
        {
          "step_id": "extract_patterns",
          "capability": "pattern_recognition",
          "request_type": "learn_from_data",
          "input_mapping": {
            "data": "results.parse_replay.parsed_data",
            "classification": "results.classify_replay.classification"
          },
          "parallel": true
        }
      ]
    }
  ]
}
```

## 🚀 **使用示例**

### 1. **註冊所有MCP服務**
```python
# 初始化註冊中心
registry = MCPServiceRegistry()

# 註冊服務
workflow_adapter = WorkflowRecorderMCPAdapter()
replay_adapter = ReplayDataParserMCPAdapter()
rl_srt_adapter = RLSRTAdapterMCPAdapter()

registry.register_service(workflow_adapter)
registry.register_service(replay_adapter)
registry.register_service(rl_srt_adapter)

# 初始化所有服務
await registry.initialize_all_services()
```

### 2. **配置驅動的組合執行**
```python
# 加載組合配置
composition_manager = MCPCompositionManager(registry)
composition_manager.load_composition_config('mcp_compositions.json')

# 執行工作流錄製到學習的完整流程
result = await composition_manager.execute_composition(
    "workflow_recording_to_learning",
    {"session_data": workflow_session_data},
    {"task_context": {"task_type": "form_filling"}}
)
```

### 3. **動態服務請求**
```python
# 動態請求具有特定能力的服務
parsed_data = await registry.request_service(
    MCPCapability.PARSE_REPLAY_DATA,
    "parse_replay_data",
    {"replay_url": "https://manus.im/share/..."}
)

# 自動學習
learning_result = await registry.request_service(
    MCPCapability.PATTERN_RECOGNITION,
    "learn_from_data",
    parsed_data
)

# 獲取推薦
recommendation = await registry.request_service(
    MCPCapability.RECOMMENDATION,
    "get_recommendation",
    {"task_type": "form_filling", "complexity": "medium"}
)
```

## 🎯 **核心優勢**

### ✅ **解決的問題**
1. **消除硬編碼依賴**: 通過服務註冊和能力匹配
2. **動態組合**: 通過配置文件定義組合流程
3. **鬆耦合**: 組件間通過事件總線通信
4. **可擴展**: 新組件只需實現統一接口
5. **可測試**: 每個組件可獨立測試
6. **可配置**: 運行時動態調整組合

### 🔄 **事件驅動協同**
- **自動觸發**: 一個組件完成後自動觸發下游組件
- **異步處理**: 支持並行和異步執行
- **錯誤隔離**: 單個組件失敗不影響整體系統
- **監控友好**: 完整的事件追蹤和日誌

### 📊 **配置驅動**
- **靈活組合**: 通過JSON配置定義不同的處理流程
- **條件執行**: 支持條件判斷和分支邏輯
- **數據映射**: 靈活的輸入輸出數據映射
- **運行時調整**: 無需重啟即可調整組合邏輯

**🎊 這個統一框架讓所有MCP組件能夠動態協同，完全消除硬編碼依賴！**

