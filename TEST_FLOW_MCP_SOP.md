# PowerAutomation test_flow_mcp 使用 SOP 文檔

## 📋 文檔概述

本文檔為其他團隊提供使用 `test_flow_mcp` 系統來讀取測試案例並生成測試結果的標準操作程序 (SOP)。

**版本**: 1.0  
**更新日期**: 2025-06-25  
**適用對象**: 開發團隊、測試團隊、QA 團隊  

---

## 🎯 test_flow_mcp 系統概述

### 系統架構
`test_flow_mcp` 是 PowerAutomation 系統的核心測試引擎，採用四階段處理流程：

1. **需求同步引擎** (Requirement Sync Engine)
2. **比較分析引擎** (Comparison Analysis Engine)
3. **評估報告生成器** (Evaluation Report Generator)
4. **Code Fix Adapter**

### 支援的測試類型
- **API 測試**: REST API 端點測試
- **集成測試**: 系統間集成驗證
- **功能測試**: 業務邏輯驗證
- **性能測試**: 響應時間和負載測試

---

## 🚀 快速開始指南

### 前置條件

#### 1. 環境要求
```bash
# Python 環境
Python >= 3.8
requests >= 2.25.0
json >= 2.0.9

# 網絡要求
PowerAutomation 服務器可訪問 (預設: http://127.0.0.1:8080)
```

#### 2. API Key 配置
```bash
# 獲取 API Key (聯繫系統管理員)
開發者 Key: dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso
使用者 Key: user_RcmKEIPfGCQrA6sSohzn5NDXYMsS5mkyP9jPhM3llTw
管理員 Key: admin_pth4jG-nVjvGaTZA2URN7SyHu-o7wBaeLOYbMrLMKkc
```

#### 3. 測試框架安裝
```bash
# 克隆項目
git clone https://github.com/alexchuang650730/aicore0624.git
cd aicore0624

# 安裝依賴
pip install -r requirements.txt
```

---

## 📖 測試案例讀取指南

### 1. 測試案例模板結構

測試案例位於 `tests/templates/` 目錄，採用 Markdown 格式：

```markdown
# 測試用例標題

**測試類型**: API型測試
**業務模塊**: PowerAutomation Core
**測試ID**: PA_XXX_001

**測試描述**: 詳細描述測試目的

**環境前置條件**:
```yaml
硬件環境:
  - 設備類型: 任何支持 Python 的計算機
  - 內存: >=4GB

軟件環境:
  - Python版本: >=3.8
  - 測試庫: requests
```

**測試步驟與檢查點**:
1. **步驟1**: 具體操作描述
   - **API調用**: POST /api/endpoint
   - **驗證**: 檢查響應狀態碼
```

### 2. 讀取測試案例的方法

#### 方法 A: 使用測試生成器
```bash
# 進入測試生成器目錄
cd tests/generators

# 運行測試生成器
python3 api_test_generator.py

# 輸出: 在 generated_api_tests/ 目錄生成可執行的 Python 測試文件
```

#### 方法 B: 直接讀取模板文件
```python
import os
import re

def read_test_template(template_path):
    """讀取測試案例模板"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析測試案例結構
    test_cases = parse_test_cases(content)
    return test_cases

def parse_test_cases(content):
    """解析測試案例內容"""
    # 實現解析邏輯
    pass
```

---

## ⚙️ test_flow_mcp 執行流程

### 1. 基本 API 調用

```python
import requests
import json

# 配置
SERVER_URL = "http://127.0.0.1:8080"
API_KEY = "dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso"  # 使用您的 API Key

# 構建請求
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

request_data = {
    "request": "請分析當前系統的測試覆蓋率並提供改進建議",
    "context": {
        "source": "vscode_vsix",
        "user_role": "developer",
        "workflow_type": "test_flow_analysis",
        "target_component": "test_flow_mcp",
        "analysis_type": "coverage_analysis"
    }
}

# 發送請求
response = requests.post(
    f"{SERVER_URL}/api/process",
    headers=headers,
    json=request_data,
    timeout=30
)

# 處理響應
if response.status_code == 200:
    result = response.json()
    print("測試分析完成:", result)
else:
    print(f"請求失敗: {response.status_code}")
```

### 2. 四階段處理流程詳解

#### 階段 1: 需求同步引擎
```python
# 輸入: 測試需求描述
# 輸出: 標準化的測試需求
{
    "requirement_sync": {
        "original_request": "用戶原始請求",
        "standardized_requirement": "標準化需求",
        "test_scope": ["scope1", "scope2"],
        "priority_level": "high"
    }
}
```

#### 階段 2: 比較分析引擎
```python
# 輸入: 標準化需求 + 現有測試案例
# 輸出: 差異分析報告
{
    "comparison_analysis": {
        "coverage_gaps": ["gap1", "gap2"],
        "redundant_tests": ["test1", "test2"],
        "improvement_areas": ["area1", "area2"],
        "manus_standard_comparison": "completed"
    }
}
```

#### 階段 3: 評估報告生成器
```python
# 輸入: 分析結果
# 輸出: 詳細評估報告
{
    "evaluation_report": {
        "executive_summary": "執行摘要",
        "detailed_findings": ["發現1", "發現2"],
        "priority_recommendations": ["建議1", "建議2"],
        "risk_assessment": "風險評估"
    }
}
```

#### 階段 4: Code Fix Adapter
```python
# 輸入: 評估報告
# 輸出: 具體修復建議
{
    "code_fixes": [
        {
            "file_path": "/path/to/file.py",
            "fix_type": "error_handling",
            "issue": "問題描述",
            "suggested_code": "建議代碼"
        }
    ]
}
```

---

## 📊 結果生成與解讀

### 1. 標準輸出格式

```json
{
    "timestamp": "2025-06-25T04:14:42Z",
    "user_role": "developer",
    "test_flow_analysis": {
        "requirement_sync": { ... },
        "comparison_analysis": { ... },
        "evaluation_report": { ... }
    },
    "recommendations": [ ... ],
    "code_fixes": [ ... ],
    "execution_time": "5.23s",
    "status": "completed"
}
```

### 2. 結果解讀指南

#### 成功指標
- `status`: "completed"
- `user_role`: 正確識別使用者角色
- `execution_time`: < 30 秒
- `test_flow_analysis`: 包含四個階段的完整結果

#### 關鍵指標分析
```python
def analyze_test_results(result):
    """分析測試結果"""
    
    # 檢查完整性
    required_fields = [
        'test_flow_analysis',
        'recommendations', 
        'code_fixes'
    ]
    
    for field in required_fields:
        if field not in result:
            print(f"警告: 缺少必要字段 {field}")
    
    # 分析建議數量
    recommendations = result.get('recommendations', [])
    print(f"生成建議數量: {len(recommendations)}")
    
    # 分析修復建議
    code_fixes = result.get('code_fixes', [])
    print(f"代碼修復建議: {len(code_fixes)}")
    
    return {
        "completeness_score": calculate_completeness(result),
        "recommendation_count": len(recommendations),
        "fix_count": len(code_fixes)
    }
```

---

## 🔧 實際操作範例

### 範例 1: 開發者測試流程

```python
#!/usr/bin/env python3
"""
開發者使用 test_flow_mcp 的完整範例
"""

import requests
import json
from datetime import datetime

class TestFlowMCPClient:
    def __init__(self, server_url, api_key):
        self.server_url = server_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def run_test_analysis(self, test_request, context):
        """執行測試分析"""
        
        request_data = {
            "request": test_request,
            "context": context
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/process",
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": "Exception",
                "message": str(e)
            }
    
    def save_results(self, results, filename):
        """保存測試結果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

# 使用範例
if __name__ == "__main__":
    # 初始化客戶端
    client = TestFlowMCPClient(
        server_url="http://127.0.0.1:8080",
        api_key="dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso"
    )
    
    # 執行測試分析
    result = client.run_test_analysis(
        test_request="請分析當前系統的測試覆蓋率並提供改進建議",
        context={
            "source": "vscode_vsix",
            "user_role": "developer",
            "workflow_type": "test_flow_analysis",
            "target_component": "test_flow_mcp",
            "analysis_type": "coverage_analysis"
        }
    )
    
    # 處理結果
    if result["success"]:
        print("✅ 測試分析成功完成")
        
        # 保存結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_flow_results_{timestamp}.json"
        client.save_results(result, filename)
        
        print(f"📁 結果已保存到: {filename}")
        
        # 顯示關鍵信息
        data = result["data"]
        print(f"👤 使用者角色: {data.get('user_role', 'unknown')}")
        print(f"⏱️ 執行時間: {data.get('execution_time', 'unknown')}")
        print(f"📋 建議數量: {len(data.get('recommendations', []))}")
        print(f"🔧 修復建議: {len(data.get('code_fixes', []))}")
        
    else:
        print("❌ 測試分析失敗")
        print(f"錯誤: {result['error']}")
        print(f"訊息: {result['message']}")
```

### 範例 2: 批量測試執行

```python
#!/usr/bin/env python3
"""
批量執行測試案例的範例
"""

import os
import glob
from test_flow_client import TestFlowMCPClient

def run_batch_tests(test_directory, client):
    """批量執行測試"""
    
    # 查找所有測試文件
    test_files = glob.glob(f"{test_directory}/**/*.py", recursive=True)
    
    results = []
    
    for test_file in test_files:
        print(f"🔄 執行測試: {test_file}")
        
        # 讀取測試案例
        test_case = read_test_case(test_file)
        
        # 執行測試
        result = client.run_test_analysis(
            test_request=test_case["request"],
            context=test_case["context"]
        )
        
        # 記錄結果
        results.append({
            "test_file": test_file,
            "result": result
        })
        
        if result["success"]:
            print(f"✅ {test_file} - 成功")
        else:
            print(f"❌ {test_file} - 失敗: {result['error']}")
    
    return results

def generate_batch_report(results):
    """生成批量測試報告"""
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["result"]["success"])
    failed_tests = total_tests - successful_tests
    
    report = {
        "summary": {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%"
        },
        "details": results
    }
    
    return report
```

---

## 🛠️ 故障排除指南

### 常見問題與解決方案

#### 1. 連接問題
```
問題: 無法連接到 PowerAutomation 服務器
解決方案:
1. 檢查服務器是否運行: curl http://127.0.0.1:8080/api/status
2. 檢查網絡連接
3. 確認服務器地址和端口正確
```

#### 2. 認證問題
```
問題: HTTP 401 Unauthorized
解決方案:
1. 檢查 API Key 是否正確
2. 確認 API Key 沒有過期
3. 檢查請求頭格式: "X-API-Key": "your_api_key"
```

#### 3. 超時問題
```
問題: 請求超時
解決方案:
1. 增加超時時間: timeout=60
2. 檢查服務器負載
3. 簡化測試請求內容
```

#### 4. 結果不完整
```
問題: 返回結果缺少某些字段
解決方案:
1. 檢查請求格式是否正確
2. 確認 context 參數完整
3. 查看服務器日誌
```

### 調試技巧

#### 1. 啟用詳細日誌
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 在請求前後添加日誌
logger.debug(f"發送請求: {request_data}")
response = requests.post(...)
logger.debug(f"收到響應: {response.status_code}")
```

#### 2. 驗證請求格式
```python
def validate_request(request_data):
    """驗證請求格式"""
    required_fields = ["request", "context"]
    
    for field in required_fields:
        if field not in request_data:
            raise ValueError(f"缺少必要字段: {field}")
    
    context = request_data["context"]
    required_context_fields = ["source", "user_role"]
    
    for field in required_context_fields:
        if field not in context:
            raise ValueError(f"context 缺少必要字段: {field}")
```

---

## 📚 最佳實踐

### 1. 測試案例設計
- **明確性**: 測試目標要明確具體
- **可重複性**: 測試結果應該可重複
- **獨立性**: 測試案例之間不應相互依賴
- **完整性**: 包含前置條件、執行步驟、預期結果

### 2. 結果處理
- **及時保存**: 立即保存測試結果到文件
- **結構化存儲**: 使用 JSON 格式便於後續分析
- **版本控制**: 為結果文件添加時間戳
- **備份策略**: 定期備份重要測試結果

### 3. 性能優化
- **批量處理**: 合併相似的測試請求
- **並發控制**: 避免同時發送過多請求
- **緩存機制**: 對重複請求使用緩存
- **資源監控**: 監控系統資源使用情況

### 4. 安全考慮
- **API Key 管理**: 不要在代碼中硬編碼 API Key
- **權限控制**: 使用最小權限原則
- **數據保護**: 敏感測試數據要加密存儲
- **訪問日誌**: 記錄所有 API 訪問

---

## 📞 支援與聯繫

### 技術支援
- **文檔問題**: 查看 GitHub Issues
- **系統問題**: 聯繫系統管理員
- **API 問題**: 參考 API 文檔

### 更新通知
- **版本更新**: 關注 GitHub Releases
- **功能變更**: 訂閱項目通知
- **安全更新**: 及時更新到最新版本

### 貢獻指南
- **問題報告**: 使用 GitHub Issues
- **功能建議**: 提交 Feature Request
- **代碼貢獻**: 遵循 Pull Request 流程

---

## 📝 版本歷史

| 版本 | 日期 | 更新內容 |
|------|------|----------|
| 1.0 | 2025-06-25 | 初始版本，包含基本使用指南 |

---

## 📄 附錄

### A. API 參考
詳細的 API 端點和參數說明請參考 `PowerAutomation/docs/api_reference.md`

### B. 測試案例模板
完整的測試案例模板請參考 `tests/templates/powerautomation_api_test_template.md`

### C. 範例代碼
更多範例代碼請參考 `tests/generators/generated_api_tests/` 目錄

---

**文檔結束**

> 💡 **提示**: 本文檔會隨著系統更新而持續更新，請定期查看最新版本。

