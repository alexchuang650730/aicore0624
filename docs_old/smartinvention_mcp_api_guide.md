# Enhanced Smartinvention MCP API 使用指南

## 概述

Enhanced Smartinvention MCP 是一個增強版的智能發明MCP組件，提供完整的任務管理API功能，能夠：

- 獲取任務列表和詳細信息
- 查詢任務存儲位置
- 獲取對話歷史列表
- 獲取存儲檔案列表
- 搜尋任務、對話和檔案

## 系統架構

```
Enhanced Smartinvention MCP
├── TaskStorageManager     # EC2存儲管理器
├── TaskListAPI           # 任務列表API
├── ConversationAPI       # 對話歷史API
├── FileAPI              # 檔案管理API
└── EnhancedSmartinventionMCP  # 主要MCP類
```

## 數據模型

### TaskInfo (任務信息)
```python
{
    "task_id": "TASK_001",
    "task_name": "UI_UX_Design",
    "cluster_name": "UI_UX_Design", 
    "description": "UI/UX設計群組任務",
    "status": "deployed",
    "created_at": "2025-06-24T00:12:06",
    "storage_path": "/home/ec2-user/smartinvention_mcp/tasks/TASK_001",
    "conversations_count": 0,
    "files_count": 1,
    "metadata": {...}
}
```

### ConversationInfo (對話信息)
```python
{
    "conversation_id": "conv_001",
    "task_id": "TASK_001",
    "file_path": "/path/to/conversation.json",
    "timestamp": "2025-06-24T00:12:06",
    "participants": ["user", "assistant"],
    "message_count": 10,
    "topics": ["UI設計", "用戶體驗"],
    "summary": "關於UI設計的討論"
}
```

### FileInfo (檔案信息)
```python
{
    "file_id": "TASK_001_task_info",
    "task_id": "TASK_001",
    "file_path": "/path/to/file.json",
    "file_name": "task_info.json",
    "file_type": ".json",
    "file_size": 433,
    "created_at": "2025-06-24T00:12:08",
    "modified_at": "2025-06-24T00:12:08",
    "category": "metadata"
}
```

## API 方法

### 1. 初始化和健康檢查

#### initialize()
初始化MCP組件
```python
result = await mcp.initialize()
# 返回: {"success": True, "component": "EnhancedSmartinventionMCP", ...}
```

#### health_check()
檢查MCP健康狀態
```python
result = await mcp.health_check()
# 返回: {"success": True, "healthy": True, "ec2_status": "connected", ...}
```

### 2. 任務管理API

#### get_all_tasks()
獲取所有任務列表
```python
result = await mcp.get_all_tasks()
# 返回: {"success": True, "tasks": [...], "total_count": 9}
```

#### get_task_by_id(task_id)
根據ID獲取特定任務
```python
result = await mcp.get_task_by_id("TASK_001")
# 返回: {"success": True, "task": {...}}
```

#### search_tasks(keyword)
搜尋任務
```python
result = await mcp.search_tasks("UI設計")
# 返回: {"success": True, "tasks": [...], "search_keyword": "UI設計"}
```

### 3. 對話歷史API

#### get_task_conversations(task_id)
獲取任務的所有對話
```python
result = await mcp.get_task_conversations("TASK_001")
# 返回: {"success": True, "conversations": [...], "total_count": 5}
```

#### get_conversation_content(task_id, conversation_id)
獲取特定對話的內容
```python
result = await mcp.get_conversation_content("TASK_001", "conv_001")
# 返回: {"success": True, "content": {...}, "conversation_info": {...}}
```

#### search_conversations(task_id, keyword)
搜尋任務中的對話
```python
result = await mcp.search_conversations("TASK_001", "智能路由")
# 返回: {"success": True, "conversations": [...], "search_keyword": "智能路由"}
```

### 4. 檔案管理API

#### get_task_files(task_id)
獲取任務的所有檔案
```python
result = await mcp.get_task_files("TASK_001")
# 返回: {"success": True, "files": [...], "total_count": 10}
```

#### get_file_content(task_id, file_path)
獲取檔案內容
```python
result = await mcp.get_file_content("TASK_001", "/path/to/file.json")
# 返回: {"success": True, "content": {...}, "content_type": "json"}
```

#### search_files(task_id, keyword)
搜尋任務中的檔案
```python
result = await mcp.search_files("TASK_001", "metadata")
# 返回: {"success": True, "files": [...], "search_keyword": "metadata"}
```

## 使用示例

### 基本使用
```python
import asyncio
from enhanced_smartinvention_mcp import EnhancedSmartinventionMCP

async def main():
    # 初始化MCP
    mcp = EnhancedSmartinventionMCP()
    
    try:
        # 初始化
        await mcp.initialize()
        
        # 獲取所有任務
        tasks = await mcp.get_all_tasks()
        print(f"找到 {tasks['total_count']} 個任務")
        
        # 搜尋特定任務
        ui_tasks = await mcp.search_tasks("UI")
        print(f"找到 {ui_tasks['total_count']} 個UI相關任務")
        
        # 獲取第一個任務的詳細信息
        if tasks['tasks']:
            task_id = tasks['tasks'][0]['task_id']
            
            # 獲取對話
            conversations = await mcp.get_task_conversations(task_id)
            print(f"任務 {task_id} 有 {conversations['total_count']} 個對話")
            
            # 獲取檔案
            files = await mcp.get_task_files(task_id)
            print(f"任務 {task_id} 有 {files['total_count']} 個檔案")
    
    finally:
        # 清理資源
        await mcp.cleanup()

# 運行
asyncio.run(main())
```

### 搜尋示例
```python
async def search_example():
    mcp = EnhancedSmartinventionMCP()
    await mcp.initialize()
    
    try:
        # 搜尋包含"智能路由"的任務
        routing_tasks = await mcp.search_tasks("智能路由")
        
        for task in routing_tasks['tasks']:
            print(f"任務: {task['task_name']}")
            
            # 搜尋該任務中的相關對話
            conversations = await mcp.search_conversations(
                task['task_id'], "路由"
            )
            
            print(f"  - 找到 {conversations['total_count']} 個相關對話")
            
            # 搜尋該任務中的相關檔案
            files = await mcp.search_files(
                task['task_id'], "routing"
            )
            
            print(f"  - 找到 {files['total_count']} 個相關檔案")
    
    finally:
        await mcp.cleanup()
```

## 配置說明

### EC2連接配置
```python
ec2_config = {
    "host": "18.212.97.173",
    "username": "ec2-user", 
    "key_file": "/home/ubuntu/alexchuang.pem"
}
```

### 存儲路徑配置
- 基礎路徑: `/home/ec2-user/smartinvention_mcp/tasks`
- 任務路徑: `{base_path}/{task_id}/`
- 對話路徑: `{task_path}/conversations_analysis/raw_conversations/`
- 檔案路徑: `{task_path}/corrected_files/`, `{task_path}/reports/`, etc.

## 錯誤處理

所有API方法都返回統一的響應格式：
```python
{
    "success": True/False,
    "error": "錯誤信息" (如果失敗),
    "data": {...} (具體數據),
    "timestamp": "2025-06-24T04:22:44.746198"
}
```

## 性能考慮

1. **連接管理**: 自動管理EC2 SSH連接，支持重連
2. **緩存**: 可以添加本地緩存以提高性能
3. **並發**: 支持異步操作，可以並發處理多個請求
4. **資源清理**: 使用完畢後調用 `cleanup()` 方法

## 擴展功能

### 未來可以添加的功能：
1. **RAG搜尋**: 整合向量搜尋和語義搜尋
2. **實時同步**: 監控EC2上的檔案變化
3. **批量操作**: 支持批量獲取和處理
4. **權限控制**: 添加用戶權限和訪問控制
5. **API服務器**: 包裝成REST API服務

## 故障排除

### 常見問題：
1. **EC2連接失敗**: 檢查密鑰文件路徑和權限
2. **任務數據為空**: 確認EC2上的數據路徑正確
3. **搜尋無結果**: 檢查關鍵詞和數據格式
4. **權限錯誤**: 確認SSH用戶有足夠的讀取權限

