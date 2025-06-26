# MCP 目錄化重構方案

## 📋 現狀問題分析

### 當前文件散落情況
- **總計**: 22 個 MCP 文件散落在 `PowerAutomation/components/` 目錄
- **總大小**: 716K
- **版本混亂**: 多個版本文件混雜（v4, v5, v51, v52, v6）
- **缺乏層次**: 大型 MCP 的子組件沒有清晰組織

### 主要問題
1. **文件散落**: 所有 MCP 文件平鋪在同一目錄
2. **版本管理混亂**: 同一 MCP 的多個版本並存
3. **依賴關係不清**: 主 MCP 和子 MCP 關係模糊
4. **維護困難**: 難以快速定位和管理相關文件

## 🏗️ 重構方案設計

### 新的目錄結構

```
PowerAutomation/
├── components/
│   ├── mcp/                           # MCP 組件根目錄
│   │   ├── core/                      # 核心 MCP
│   │   │   ├── general_processor/     # 通用處理器 MCP
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py           # 主要實現
│   │   │   │   ├── config.py         # 配置管理
│   │   │   │   └── utils.py          # 工具函數
│   │   │   ├── local_adapter/         # 本地適配器 MCP
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py
│   │   │   │   ├── original.py       # 原始版本
│   │   │   │   └── enhanced.py       # 增強版本
│   │   │   └── mcp_coordinator/       # MCP 協調器
│   │   │       ├── __init__.py
│   │   │       ├── pattern.py
│   │   │       └── manager.py
│   │   ├── workflow/                  # 工作流 MCP
│   │   │   ├── recorder/              # 錄製器 MCP
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py
│   │   │   │   └── storage.py
│   │   │   └── test_flow/             # 測試流程 MCP
│   │   │       ├── __init__.py
│   │   │       ├── v4/               # 版本 4
│   │   │       │   ├── main.py
│   │   │       │   ├── comparison_engine.py
│   │   │       │   └── evaluation.py
│   │   │       ├── v5/               # 版本 5
│   │   │       │   ├── main.py
│   │   │       │   ├── v51/          # 子版本 5.1
│   │   │       │   │   └── main.py
│   │   │       │   └── v52/          # 子版本 5.2
│   │   │       │       └── main.py
│   │   │       ├── v6/               # 版本 6
│   │   │       │   └── internal/
│   │   │       │       └── main.py
│   │   │       └── current -> v5/    # 符號鏈接指向當前版本
│   │   ├── adapters/                  # 適配器 MCP
│   │   │   ├── smartinvention/        # SmartInvention 適配器
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py           # 主適配器
│   │   │   │   ├── enhanced.py       # 增強版本
│   │   │   │   ├── v2.py             # 版本 2
│   │   │   │   ├── hitl_middleware.py # HITL 中間件
│   │   │   │   └── processors/       # 子處理器
│   │   │   │       ├── conversation.py
│   │   │   │       ├── analysis.py
│   │   │   │       └── storage.py
│   │   │   ├── manus/                 # Manus 適配器
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py
│   │   │   │   └── parser.py
│   │   │   └── human_loop/            # Human Loop 適配器
│   │   │       ├── __init__.py
│   │   │       └── main.py
│   │   ├── tools/                     # 工具 MCP
│   │   │   ├── code_generation/       # 代碼生成 MCP
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py
│   │   │   │   └── templates/
│   │   │   ├── cloud_search/          # 雲搜索 MCP
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py           # 基礎版本
│   │   │   │   └── dynamic.py        # 動態版本
│   │   │   └── dynamic_generator/     # 動態生成器 MCP
│   │   │       ├── __init__.py
│   │   │       └── main.py
│   │   ├── deployment/                # 部署 MCP
│   │   │   ├── vsix_deployer/         # VSIX 部署器
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py
│   │   │   │   └── installer/
│   │   │   │       └── vscode.py
│   │   │   └── vscode_installer/      # VSCode 安裝器
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       └── enhanced.py
│   │   └── shared/                    # 共享組件
│   │       ├── __init__.py
│   │       ├── base_mcp.py           # MCP 基類
│   │       ├── config_manager.py     # 配置管理
│   │       ├── logger.py             # 日誌管理
│   │       └── utils.py              # 通用工具
│   └── [其他非 MCP 組件...]
```

## 📦 分組邏輯

### 1. **core/** - 核心 MCP
- `general_processor/` - 通用處理器
- `local_adapter/` - 本地適配器
- `mcp_coordinator/` - MCP 協調器

### 2. **workflow/** - 工作流 MCP
- `recorder/` - 工作流錄製器
- `test_flow/` - 測試流程（包含多版本）

### 3. **adapters/** - 適配器 MCP
- `smartinvention/` - SmartInvention 適配器（含子組件）
- `manus/` - Manus 適配器
- `human_loop/` - Human Loop 適配器

### 4. **tools/** - 工具 MCP
- `code_generation/` - 代碼生成
- `cloud_search/` - 雲搜索
- `dynamic_generator/` - 動態生成器

### 5. **deployment/** - 部署 MCP
- `vsix_deployer/` - VSIX 部署器
- `vscode_installer/` - VSCode 安裝器

### 6. **shared/** - 共享組件
- 基類、工具、配置等共用代碼

## 🔄 版本管理策略

### 版本目錄結構
```
test_flow/
├── __init__.py           # 導入當前版本
├── v4/                   # 版本 4（穩定版）
├── v5/                   # 版本 5（當前版）
│   ├── v51/             # 子版本 5.1
│   └── v52/             # 子版本 5.2
├── v6/                   # 版本 6（開發版）
└── current -> v5/        # 符號鏈接指向當前版本
```

### 版本導入機制
```python
# test_flow/__init__.py
from .current.main import EnhancedTestFlowMCP as TestFlowMCP
from .v4.main import EnhancedTestFlowMCPv4
from .v5.main import EnhancedTestFlowMCPv5

__all__ = ['TestFlowMCP', 'EnhancedTestFlowMCPv4', 'EnhancedTestFlowMCPv5']
```

## 🛠️ 重構實施步驟

### 階段一：創建目錄結構
1. 創建新的 MCP 目錄結構
2. 設置基礎的 `__init__.py` 文件
3. 創建共享組件基類

### 階段二：遷移核心 MCP
1. 遷移 `general_processor_mcp.py`
2. 遷移 `local_mcp_adapter.py` 及其變體
3. 遷移 `mcp_coordinator_pattern.py`

### 階段三：遷移工作流 MCP
1. 遷移 `recorder_workflow_mcp.py`
2. 遷移所有 `test_flow` 版本並建立版本結構

### 階段四：遷移適配器 MCP
1. 遷移 SmartInvention 相關 MCP
2. 遷移 Manus 和 Human Loop 適配器
3. 建立子組件結構

### 階段五：遷移工具和部署 MCP
1. 遷移代碼生成和搜索工具
2. 遷移部署相關 MCP
3. 建立模板和配置結構

### 階段六：更新導入和引用
1. 更新所有導入語句
2. 修改配置文件中的路徑
3. 更新文檔和 README

## 📋 文件映射表

### 當前文件 → 新位置

| 當前文件 | 新位置 |
|---------|--------|
| `general_processor_mcp.py` | `mcp/core/general_processor/main.py` |
| `local_mcp_adapter.py` | `mcp/core/local_adapter/main.py` |
| `local_mcp_adapter_original.py` | `mcp/core/local_adapter/original.py` |
| `mcp_coordinator_pattern.py` | `mcp/core/mcp_coordinator/pattern.py` |
| `recorder_workflow_mcp.py` | `mcp/workflow/recorder/main.py` |
| `enhanced_test_flow_mcp_v4.py` | `mcp/workflow/test_flow/v4/main.py` |
| `enhanced_test_flow_mcp_v5.py` | `mcp/workflow/test_flow/v5/main.py` |
| `enhanced_test_flow_mcp_v51.py` | `mcp/workflow/test_flow/v5/v51/main.py` |
| `enhanced_test_flow_mcp_v52.py` | `mcp/workflow/test_flow/v5/v52/main.py` |
| `enhanced_test_flow_mcp_v6_internal.py` | `mcp/workflow/test_flow/v6/internal/main.py` |
| `smartinvention_adapter_mcp.py` | `mcp/adapters/smartinvention/main.py` |
| `smartinvention_adapter_mcp_enhanced.py` | `mcp/adapters/smartinvention/enhanced.py` |
| `enhanced_smartinvention_mcp.py` | `mcp/adapters/smartinvention/enhanced_v1.py` |
| `enhanced_smartinvention_mcp_v2.py` | `mcp/adapters/smartinvention/enhanced_v2.py` |
| `smartinvention_manus_hitl_middleware.py` | `mcp/adapters/smartinvention/hitl_middleware.py` |
| `manus_adapter_mcp.py` | `mcp/adapters/manus/main.py` |
| `human_loop_mcp_adapter.py` | `mcp/adapters/human_loop/main.py` |
| `code_generation_mcp.py` | `mcp/tools/code_generation/main.py` |
| `cloud_search_mcp.py` | `mcp/tools/cloud_search/main.py` |
| `dynamic_cloud_search_mcp.py` | `mcp/tools/cloud_search/dynamic.py` |
| `dynamic_mcp_generator.py` | `mcp/tools/dynamic_generator/main.py` |
| `vsix_deployer_mcp.py` | `mcp/deployment/vsix_deployer/main.py` |
| `enhanced_vscode_installer_mcp.py` | `mcp/deployment/vscode_installer/enhanced.py` |

## ✅ 重構優勢

### 1. **清晰的組織結構**
- 按功能分組，易於理解和維護
- 主 MCP 和子 MCP 關係清晰
- 版本管理有序

### 2. **更好的可維護性**
- 相關文件集中管理
- 減少文件查找時間
- 便於團隊協作

### 3. **版本控制優化**
- 多版本並存且有序
- 符號鏈接指向當前版本
- 便於版本切換和測試

### 4. **擴展性增強**
- 新 MCP 有明確的放置位置
- 子組件可以靈活添加
- 共享組件避免重複代碼

### 5. **導入管理簡化**
- 統一的導入接口
- 版本選擇更靈活
- 向後兼容性保證

## 🚀 實施建議

1. **分階段執行**: 避免一次性大規模變更
2. **保持向後兼容**: 在過渡期保留舊的導入方式
3. **完善測試**: 確保重構後功能正常
4. **更新文檔**: 同步更新所有相關文檔
5. **團隊溝通**: 確保所有開發者了解新結構

這個重構方案將大大改善 MCP 組件的組織結構，解決文件散落問題，並為未來的擴展奠定良好基礎。

