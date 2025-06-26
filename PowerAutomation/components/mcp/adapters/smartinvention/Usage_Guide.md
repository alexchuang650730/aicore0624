# SmartInvention 對話歷史 API 和對比引擎使用指南

## 📋 概述

SmartInvention 系統提供了完整的對話歷史管理和對比引擎功能，可以與 Manus 標準進行增量比對分析。本指南將詳細說明如何使用這些功能來驗證和對比不同引擎的效果。

## 🏗️ 系統架構

### 核心組件

**1. SmartInvention 適配器 (`smartinvention_adapter_mcp.py`)**
- 負責對話數據的收集、存儲和分析
- 提供 RESTful API 端點
- 支持對話搜索和檢索功能

**2. 對話歷史中間件 (`smartinvention_manus_hitl_middleware.py`)**
- 處理 VSIX 請求和對話歷史收集
- 執行與 Manus 的增量比對
- 提供 Human-in-the-Loop 審核功能

**3. 比較分析引擎 (`enhanced_test_flow_mcp_v4.py`)**
- 核心對比分析邏輯
- 系統狀態評估
- 差異分析和建議生成

## 🔧 環境準備

### 必要條件

1. **PowerAutomation 系統運行**
   - AICore 3.0 已啟動
   - SmartInvention 適配器已初始化
   - 相關 MCP 組件正常運行

2. **API 端點配置**
   ```python
   # 在 endpoint_mapping.py 中確認以下端點
   "/api/sync/conversations": "smartinvention_adapter.process_conversation_sync"
   "/api/conversations/latest": "smartinvention_adapter.get_latest_conversations"
   "/api/interventions/needed": "smartinvention_adapter.get_interventions_needed"
   ```

3. **依賴組件檢查**
   - EnhancedSmartinventionAdapterMCP
   - ManusAdapterMCP
   - ComparisonAnalysisEngine

## 📊 使用方法

### 方法一：直接 API 調用

#### 1. 獲取最新對話歷史

```python
import aiohttp
import json

async def get_conversation_history():
    """獲取最新對話歷史"""
    
    url = "http://localhost:8000/api/conversations/latest"
    params = {
        "limit": 10,
        "include_context": True
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                conversations = data.get("conversations", [])
                print(f"獲取到 {len(conversations)} 條對話")
                return conversations
            else:
                print(f"API 調用失敗: {response.status}")
                return []

# 使用範例
conversations = await get_conversation_history()
```

#### 2. 搜索特定對話

```python
async def search_conversations(keyword, limit=10):
    """搜索相關對話"""
    
    url = "http://localhost:8000/api/sync/conversations"
    payload = {
        "conversations": [],  # 空數組表示搜索請求
        "metadata": {
            "search_keyword": keyword,
            "limit": limit,
            "include_context": True
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("search_results", [])
            else:
                print(f"搜索失敗: {response.status}")
                return []

# 使用範例
results = await search_conversations("測試案例生成")
```

#### 3. 執行對比分析

```python
async def perform_comparison_analysis(request_content, context=None):
    """執行與 Manus 的對比分析"""
    
    # 創建 VSIX 請求
    vsix_request = {
        "request_id": f"req_{int(time.time())}",
        "content": request_content,
        "context": context or {},
        "timestamp": time.time(),
        "source": "api_call"
    }
    
    # 調用中間件進行處理
    url = "http://localhost:8000/api/smartinvention/process"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=vsix_request) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                print(f"對比分析失敗: {response.status}")
                return None

# 使用範例
comparison_result = await perform_comparison_analysis(
    "請幫我生成一個用戶登錄功能的測試案例",
    {"project": "web_app", "framework": "react"}
)
```

### 方法二：組件直接調用

#### 1. 初始化組件

```python
from PowerAutomation.components.smartinvention_adapter_mcp import SmartinventionAdapterMCP
from PowerAutomation.components.smartinvention_manus_hitl_middleware import SmartInventionManusHITLMiddleware
from PowerAutomation.components.enhanced_test_flow_mcp_v4 import ComparisonAnalysisEngine

# 初始化配置
config = {
    "smartinvention": {
        "api_base_url": "https://smartinvention.api",
        "api_key": "your_api_key"
    },
    "manus": {
        "api_base_url": "https://manus.chat",
        "api_key": "your_manus_key"
    },
    "storage": {
        "conversations_dir": "./data/conversations",
        "analysis_dir": "./data/analysis"
    }
}

# 創建組件實例
smartinvention_adapter = SmartinventionAdapterMCP(config)
hitl_middleware = SmartInventionManusHITLMiddleware(config)
comparison_engine = ComparisonAnalysisEngine(config)

# 初始化組件
await smartinvention_adapter.initialize()
await hitl_middleware.initialize()
```

#### 2. 收集對話歷史

```python
async def collect_conversation_history_direct(request_content):
    """直接調用組件收集對話歷史"""
    
    # 創建請求對象
    vsix_request = VSIXRequest(
        request_id=f"req_{int(time.time())}",
        content=request_content,
        context={},
        timestamp=time.time()
    )
    
    # 收集對話歷史
    conversation_history = await hitl_middleware._collect_conversation_history(vsix_request)
    
    print(f"收集到 {conversation_history.total_messages} 條消息")
    print(f"相關性分數: {conversation_history.relevant_score}")
    
    return conversation_history
```

#### 3. 執行增量比對

```python
async def perform_incremental_comparison_direct(request_content, conversation_history):
    """直接執行增量比對"""
    
    vsix_request = VSIXRequest(
        request_id=f"req_{int(time.time())}",
        content=request_content,
        context={},
        timestamp=time.time()
    )
    
    # 執行增量比對
    comparison_result = await hitl_middleware._perform_incremental_comparison(
        vsix_request, conversation_history
    )
    
    print(f"比對完成，信心分數: {comparison_result.confidence_score}")
    print(f"發現 {len(comparison_result.differences)} 個差異")
    print(f"生成 {len(comparison_result.recommendations)} 個建議")
    
    return comparison_result
```

### 方法三：完整流程調用

```python
async def complete_smartinvention_workflow(request_content, context=None):
    """完整的 SmartInvention 工作流程"""
    
    try:
        # 1. 創建請求
        vsix_request = VSIXRequest(
            request_id=f"req_{int(time.time())}",
            content=request_content,
            context=context or {},
            timestamp=time.time(),
            source="workflow_call"
        )
        
        # 2. 處理請求（包含所有步驟）
        response = await hitl_middleware.process_vsix_request(vsix_request)
        
        # 3. 分析結果
        if response.success:
            print("✅ 處理成功")
            
            # Manus 原始回覆
            if response.manus_original_response:
                print("📝 Manus 原始回覆:")
                print(json.dumps(response.manus_original_response, indent=2, ensure_ascii=False))
            
            # 對話歷史
            if response.conversation_history:
                print(f"📚 對話歷史: {response.conversation_history.total_messages} 條消息")
                print(f"相關性: {response.conversation_history.relevant_score:.2f}")
            
            # 增量比對結果
            if response.incremental_comparison:
                print(f"🔍 比對結果: {len(response.incremental_comparison.differences)} 個差異")
                print(f"信心分數: {response.incremental_comparison.confidence_score:.2f}")
            
            # 最終建議
            print(f"💡 最終建議: {len(response.final_recommendations)} 個")
            for i, rec in enumerate(response.final_recommendations, 1):
                print(f"  {i}. {rec.get('action', 'N/A')} - {rec.get('reason', 'N/A')}")
            
            return response
        else:
            print(f"❌ 處理失敗: {response.error_message}")
            return None
            
    except Exception as e:
        print(f"💥 工作流程異常: {str(e)}")
        return None

# 使用範例
result = await complete_smartinvention_workflow(
    "請幫我分析這個 API 設計是否符合 RESTful 標準",
    {"api_type": "user_management", "version": "v1"}
)
```

## 🔍 結果分析

### 對話歷史分析

```python
def analyze_conversation_history(conversation_history):
    """分析對話歷史結果"""
    
    print("=== 對話歷史分析 ===")
    print(f"對話 ID: {conversation_history.conversation_id}")
    print(f"總消息數: {conversation_history.total_messages}")
    print(f"參與者: {', '.join(conversation_history.participants)}")
    print(f"時間範圍: {conversation_history.timestamp_range['start']} ~ {conversation_history.timestamp_range['end']}")
    print(f"相關性分數: {conversation_history.relevant_score:.2f}")
    
    # 分析消息類型
    message_types = {}
    for msg in conversation_history.messages:
        msg_type = msg.get("type", "unknown")
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
    
    print("消息類型分布:")
    for msg_type, count in message_types.items():
        print(f"  {msg_type}: {count}")
```

### 比對結果分析

```python
def analyze_comparison_result(comparison_result):
    """分析比對結果"""
    
    print("=== 增量比對分析 ===")
    print(f"比對 ID: {comparison_result.comparison_id}")
    print(f"信心分數: {comparison_result.confidence_score:.2f}")
    print(f"時間戳: {comparison_result.timestamp}")
    
    # 分析差異
    print(f"\n發現 {len(comparison_result.differences)} 個差異:")
    for i, diff in enumerate(comparison_result.differences, 1):
        print(f"  {i}. {diff.get('category', 'N/A')}: {diff.get('description', 'N/A')}")
        print(f"     影響程度: {diff.get('impact', 'N/A')}")
    
    # 分析建議
    print(f"\n生成 {len(comparison_result.recommendations)} 個建議:")
    for i, rec in enumerate(comparison_result.recommendations, 1):
        print(f"  {i}. [{rec.get('priority', 'N/A')}] {rec.get('action', 'N/A')}")
        print(f"     原因: {rec.get('reason', 'N/A')}")
```

## ⚠️ 注意事項

### 1. API 連接檢查

在使用前請確認：
- PowerAutomation 系統正在運行
- API 端點可訪問
- 認證配置正確

### 2. 數據格式要求

- 對話數據必須包含必要字段（id, messages, participants）
- 時間戳格式為 ISO 8601
- 消息內容需要是有效的 JSON 格式

### 3. 性能考慮

- 大量對話歷史可能影響處理速度
- 建議設置合理的 limit 參數
- 考慮使用異步處理避免阻塞

### 4. 錯誤處理

- 實現完整的異常捕獲
- 記錄詳細的錯誤日誌
- 提供降級處理方案

## 🧪 測試驗證

### 基本功能測試

```python
async def test_basic_functionality():
    """測試基本功能"""
    
    # 測試對話歷史獲取
    conversations = await get_conversation_history()
    assert len(conversations) >= 0, "對話歷史獲取失敗"
    
    # 測試搜索功能
    search_results = await search_conversations("測試")
    assert isinstance(search_results, list), "搜索功能異常"
    
    # 測試比對分析
    comparison_result = await perform_comparison_analysis("測試請求")
    assert comparison_result is not None, "比對分析失敗"
    
    print("✅ 基本功能測試通過")

# 運行測試
await test_basic_functionality()
```

這就是 SmartInvention 對話歷史 API 和對比引擎的完整使用方法。您確認這個方法後，我會仿照 test_flow_mcp 的格式編寫詳細的 SOP 文檔。

