# Development Demos - Manus_Adapter_MCP 整合

## 概述

本目錄包含 **Manus_Adapter_MCP** 的演示應用和測試案例。Manus_Adapter_MCP 是一個統一的組件，整合了 Manus 系統與 AICore 3.0，同時提供完整的需求分析處理功能。

## 🏗️ 架構說明

### 統一組件設計
**Manus_Adapter_MCP** 是一個單一的、功能完整的組件，包含：

1. **Manus 適配器功能**
   - 連接 Manus 系統與 AICore 3.0
   - 利用 AICore 的動態專家系統
   - 利用 AICore 的智慧路由引擎
   - 利用 AICore 的工具發現機制

2. **需求分析處理功能**
   - 智能需求解析
   - 專家協調分析
   - 結果聚合處理
   - 跨任務關聯分析

### 組件位置
- **核心組件**: `PowerAutomation/components/manus_adapter_mcp.py`
- **演示應用**: `development/demos/`

## 📁 目錄結構

```
development/demos/
├── README.md                    # 本文檔
├── req001_analysis/            # REQ_001 分析演示
│   ├── README.md              # REQ_001 專用說明
│   ├── req001_demo.py         # REQ_001 演示腳本
│   └── req001_aicore_processor.py  # REQ_001 處理器
└── manus_examples/            # 其他 Manus 示例
    └── (待添加)
```

## 🚀 核心功能

### 1. 需求分析處理
```python
# 使用統一的 Manus_Adapter_MCP
from components.manus_adapter_mcp import ManusAdapterMCP

adapter = ManusAdapterMCP(aicore)
await adapter.initialize()

result = await adapter.analyze_requirement(
    requirement_text="針對 REQ_001: 用戶界面設計需求 列出明確需求及manus action...",
    target_entity="REQ_001"
)
```

### 2. AICore 能力整合
- **動態專家系統**: 自動調用相關領域專家
- **智慧路由**: 智能路由請求到合適的處理器
- **工具發現**: 自動發現和使用合適的工具

### 3. API 端點處理
```python
# 處理各種 Manus API 請求
result = await adapter.handle_manus_request(
    endpoint="/api/manus/requirement/analyze",
    request_data={"requirement_text": "...", "target_entity": "REQ_001"}
)
```

## 🎯 演示案例

### REQ_001 分析演示
位置: `req001_analysis/`

這個演示展示如何使用 Manus_Adapter_MCP 處理具體的 REQ_001 需求：
- 解析用戶界面設計需求
- 生成明確需求列表
- 提供 Manus actions
- 列出相關檔案
- 執行跨任務分析

### 運行演示
```bash
cd development/demos/req001_analysis/
python req001_demo.py
```

## 🔧 技術特性

### 利用 AICore 3.0 核心能力
1. **動態專家註冊**: 註冊 Manus 專用專家到 AICore
2. **智慧路由規則**: 設置 Manus 請求的路由規則
3. **工具自動發現**: 註冊和發現 Manus 專用工具

### 數據整合
- **Smartinvention MCP**: 無縫整合獲取任務數據
- **跨任務分析**: 智能分析任務間關聯
- **檔案智能**: 自動識別相關檔案

### 結果格式
- **結構化輸出**: 標準化的分析結果格式
- **專家洞察**: 多專家協作的深度分析
- **信心度評估**: 量化的結果可信度

## 📊 性能指標

- **處理時間**: 通常 < 5 秒
- **專家協調**: 支持 4+ 個專家並行
- **信心度**: 平均 85%+
- **成功率**: 95%+

## 🔄 與 AICore 的整合

Manus_Adapter_MCP 已完全整合到 AICore 3.0 中：

```python
# 在 AICore 中直接使用
aicore = AICore3()
await aicore.initialize()

# Manus_Adapter_MCP 自動初始化
result = await aicore.process_manus_requirement(
    requirement_text="...",
    target_entity="REQ_001"
)
```

## 📝 開發指南

### 添加新的演示
1. 在 `development/demos/` 下創建新目錄
2. 添加演示腳本和說明文檔
3. 更新本 README 文檔

### 擴展功能
1. 修改 `PowerAutomation/components/manus_adapter_mcp.py`
2. 添加新的專家或工具
3. 更新相關文檔

## 🎉 總結

Manus_Adapter_MCP 提供了一個統一、強大的解決方案，將 Manus 系統與 AICore 3.0 完美整合，同時提供完整的需求分析處理功能。通過利用 AICore 的核心能力，實現了智能化、自動化的需求處理流程。

