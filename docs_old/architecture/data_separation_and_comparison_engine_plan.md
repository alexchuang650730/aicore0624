# 數據庫分離與對比引擎調整方案

## 📋 概述

本方案旨在將 Manus 系統的核心數據與來自 VSCode 插件的數據分離存儲到不同的數據庫中，並調整現有的對比引擎以支持多數據源的透明訪問。

## 🎯 目標

1. **數據獨立性**：將 Manus 數據和插件數據分離，提高系統的可維護性
2. **性能優化**：針對不同數據類型選擇最優的存儲和索引策略
3. **可擴展性**：為未來引入更多數據源奠定基礎
4. **向後兼容**：確保現有功能不受影響

## 🏗️ 架構設計

### 數據庫分離策略

#### Manus 核心數據庫 (ManusDB)
- **內容**：對話歷史、分析報告、模型訓練數據、系統配置
- **技術棧**：保持現有數據庫技術（PostgreSQL/SQLite）
- **訪問層**：通過現有的 `manus_data_access` 模塊

#### 插件數據庫 (PluginDB)
- **內容**：代碼同步數據、插件用戶行為、項目結構信息
- **技術棧**：與 ManusDB 保持一致（初期）
- **訪問層**：新建 `plugin_data_access` 模塊

### 數據源抽象層

```
對比引擎 (ComparisonAnalysisEngine)
           ↓
    數據提供者 (DataProvider)
           ↓
    ┌─────────────────┬─────────────────┐
    ↓                 ↓                 ↓
ManusDataAccess  PluginDataAccess  [未來數據源]
    ↓                 ↓
  ManusDB          PluginDB
```

## 📊 數據模型設計

### UserRequest 擴展

```python
@dataclass
class UserRequest:
    id: str
    content: str
    context: Dict[str, Any]  # 包含 code_sync_data
    priority: str = "normal"
    metadata: Dict[str, Any]
    timestamp: float
```

### code_sync_data 結構

```python
{
    "code_sync_data": {
        "project_root": "/path/to/project",
        "files": [
            {
                "path": "src/main.py",
                "content": "print('Hello, World!')",
                "checksum": "md5_hash_of_content",
                "last_modified": 1678886400,
                "status": "modified"  # added, modified, deleted, unchanged
            }
        ],
        "project_metadata": {
            "name": "MyProject",
            "version": "1.0.0",
            "language": "Python",
            "git_info": {
                "branch": "main",
                "commit_hash": "abcdef123456",
                "remote_url": "https://github.com/user/repo.git"
            }
        },
        "sync_type": "full"  # full, incremental
    }
}
```

### PluginDB Schema

#### 表：code_projects
```sql
CREATE TABLE code_projects (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    language VARCHAR(50),
    git_branch VARCHAR(255),
    git_commit_hash VARCHAR(255),
    git_remote_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 表：code_files
```sql
CREATE TABLE code_files (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) REFERENCES code_projects(id),
    file_path TEXT NOT NULL,
    content_hash VARCHAR(255) NOT NULL,
    file_size INTEGER,
    last_modified TIMESTAMP,
    status VARCHAR(20) DEFAULT 'unchanged',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 表：code_file_contents
```sql
CREATE TABLE code_file_contents (
    content_hash VARCHAR(255) PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 表：sync_sessions
```sql
CREATE TABLE sync_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    project_id VARCHAR(255) REFERENCES code_projects(id),
    sync_type VARCHAR(20) NOT NULL,
    files_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

## 🔧 實施步驟

### 階段 1：創建插件數據訪問層

1. **創建 PluginDB Schema**
   ```bash
   # 創建數據庫遷移腳本
   /home/ubuntu/aicore0624/PowerAutomation/components/mcp/shared/migrations/
   ```

2. **實現 plugin_data_access.py**
   ```python
   # /home/ubuntu/aicore0624/PowerAutomation/components/mcp/shared/plugin_data_access.py
   class PluginDataAccess:
       async def save_code_sync_data(self, user_id: str, code_sync_data: Dict)
       async def get_user_code_snapshot(self, user_id: str, timestamp: float = None)
       async def search_code_files(self, user_id: str, query: str)
       async def get_project_history(self, user_id: str, project_id: str)
   ```

### 階段 2：創建數據提供者抽象層

1. **實現 data_provider.py**
   ```python
   # /home/ubuntu/aicore0624/PowerAutomation/components/mcp/shared/data_provider.py
   class DataProvider:
       def __init__(self, manus_access, plugin_access)
       async def get_user_full_context(self, user_id: str, timestamp: float = None)
       async def get_comparison_data(self, user_id: str, request_id: str)
       async def save_user_request_data(self, user_request: UserRequest)
   ```

### 階段 3：調整對比引擎

1. **修改 ComparisonAnalysisEngine**
   - 替換直接的 `manus_data_access` 調用
   - 使用新的 `DataProvider` 獲取統一數據
   - 更新比較邏輯以處理代碼上下文

2. **更新相關組件**
   - `enhanced_aicore3.py`
   - `smartinvention_adapter_mcp.py`
   - `smartinvention_manus_hitl_middleware.py`

### 階段 4：API 端點調整

1. **修改 UserRequest 處理邏輯**
   ```python
   # 在接收 UserRequest 時
   if 'code_sync_data' in user_request.context:
       await plugin_data_access.save_code_sync_data(
           user_request.metadata.get('user_id'),
           user_request.context['code_sync_data']
       )
   ```

2. **新增插件專用 API 端點**
   - `/api/plugin/sync/code` - 代碼同步
   - `/api/plugin/context/get` - 獲取用戶上下文
   - `/api/plugin/projects/list` - 項目列表

## 🧪 測試策略

### 單元測試
- `plugin_data_access` 模塊的所有方法
- `data_provider` 的數據聚合邏輯
- 對比引擎的新功能

### 集成測試
- 完整的 UserRequest 處理流程
- 多數據源的對比分析
- API 端點的正確性

### 性能測試
- 大量代碼文件的同步性能
- 對比引擎在多數據源下的響應時間
- 併發請求的處理能力

## 📈 預期效果

### 性能提升
- **代碼搜索響應時間**: < 1.5 秒
- **對比分析準確率**: > 80%
- **併發用戶支持**: 50 用戶
- **未來擴容能力**: 1000+ 用戶

### 功能增強
- 支持增量代碼同步
- 更豐富的上下文信息
- 更精確的對比分析
- 更好的用戶體驗

## 🔄 遷移計劃

### 向後兼容性
- 保持現有 API 接口不變
- 漸進式遷移數據訪問邏輯
- 提供回滾機制

### 數據遷移
- 現有數據保持在 ManusDB
- 新數據自動路由到對應數據庫
- 提供數據同步工具

## 📋 檢查清單

### 開發階段
- [ ] 創建 PluginDB Schema
- [ ] 實現 plugin_data_access.py
- [ ] 實現 data_provider.py
- [ ] 調整對比引擎
- [ ] 更新 API 端點
- [ ] 編寫測試用例

### 測試階段
- [ ] 單元測試通過
- [ ] 集成測試通過
- [ ] 性能測試達標
- [ ] 安全性測試通過

### 部署階段
- [ ] 數據庫遷移腳本
- [ ] 配置文件更新
- [ ] 監控和日誌設置
- [ ] 文檔更新

## 🚀 部署注意事項

1. **數據庫配置**
   - 確保 PluginDB 連接配置正確
   - 設置適當的連接池大小
   - 配置備份策略

2. **性能監控**
   - 監控數據庫查詢性能
   - 跟踪 API 響應時間
   - 監控內存和 CPU 使用率

3. **安全考慮**
   - 代碼內容的加密存儲
   - 用戶數據的訪問控制
   - API 的認證和授權

## 📚 相關文檔

- [SmartInvention 使用指南](../components/smartinvention/Usage_Guide.md)
- [TEST_FLOW_MCP SOP](../TEST_FLOW_MCP_SOP.md)
- [MCP 目錄重構計劃](../MCP_Directory_Refactor_Plan.md)
- [ContextManager 驗證測試計劃](../upload/ContextManager驗證測試計劃.md)

---

**文檔版本**: v1.0  
**創建日期**: 2025-06-26  
**最後更新**: 2025-06-26  
**負責人**: AI Core Team

