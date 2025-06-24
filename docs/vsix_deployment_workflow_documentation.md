# AICore到Local MCP的VSIX部署和驗證工作流

## 📋 **工作流概述**

本工作流實現了從AICore端構建、部署VSIX擴展到Local MCP端側，並進行完整驗證的端到端解決方案。

### **核心目標**
- 解決VSIX文件安裝失敗問題（如"暫不支持安裝插件的 3.0.0 版本"）
- 實現AICore與Local MCP的無縫集成
- 提供完整的部署驗證和監控機制
- 確保VSCode擴展的正確安裝和功能驗證

### **架構設計**
```
┌─────────────────┐    HTTP API    ┌─────────────────┐    VSCode CLI    ┌─────────────────┐
│   AICore端      │ ──────────────► │  Local MCP端    │ ──────────────► │   VSCode端      │
│                 │                 │                 │                 │                 │
│ • VSIX構建      │                 │ • 接收部署      │                 │ • 擴展安裝      │
│ • 打包壓縮      │                 │ • 驗證文件      │                 │ • 功能驗證      │
│ • 部署請求      │                 │ • 調用安裝      │                 │ • 性能測試      │
│ • 狀態監控      │                 │ • 狀態回報      │                 │                 │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
```

## 🔧 **核心組件介紹**

### **1. AICore端部署組件** (`aicore_vsix_deployer.py`)

#### **主要功能**
- **VSIX構建**: 從源代碼構建VSCode擴展
- **包驗證**: 檢查VSIX文件完整性和兼容性
- **安全部署**: 帶簽名驗證的安全部署機制
- **狀態監控**: 實時監控部署進度和結果

#### **關鍵類和方法**

##### **VSIXDeploymentConfig**
```python
@dataclass
class VSIXDeploymentConfig:
    # AICore配置
    aicore_workspace: str           # AICore工作空間路徑
    build_output_dir: str          # 構建輸出目錄
    
    # Local MCP端點配置
    local_mcp_endpoint: str        # Local MCP API端點
    local_mcp_api_key: str         # API密鑰
    deployment_timeout: int = 300  # 部署超時時間
    
    # VSIX配置
    extension_name: str            # 擴展名稱
    extension_version: str         # 擴展版本
    vscode_engine_version: str     # VSCode引擎版本要求
```

##### **AICore_VSIX_Deployer**
```python
class AICore_VSIX_Deployer:
    async def deploy_vsix_to_local_mcp(self, extension_source_path: str) -> DeploymentResult:
        """
        主要部署流程：
        1. 構建VSIX包 (_build_vsix_package)
        2. 驗證VSIX包 (_validate_vsix_package)
        3. 準備部署載荷 (_prepare_deployment_payload)
        4. 部署到Local MCP (_deploy_to_local_mcp)
        5. 驗證部署結果 (_verify_deployment)
        """
```

#### **核心流程**

##### **步驟1: VSIX構建**
```python
async def _build_vsix_package(self, source_path: str) -> VSIXPackage:
    # 1. 創建臨時構建目錄
    # 2. 複製源代碼
    # 3. 安裝npm依賴: npm install
    # 4. 編譯TypeScript: npm run compile
    # 5. 使用vsce打包: npx vsce package
    # 6. 計算校驗和
    # 7. 提取元數據
```

##### **步驟2: 包驗證**
```python
async def _validate_vsix_package(self, vsix_package: VSIXPackage) -> Dict[str, Any]:
    # 檢查項目：
    # • 文件存在性和大小
    # • ZIP格式完整性
    # • 必要文件存在（extension.vsixmanifest, package.json）
    # • 版本兼容性（檢測問題版本3.0.0）
```

##### **步驟3: 安全部署**
```python
async def _prepare_deployment_payload(self, vsix_package: VSIXPackage) -> Dict[str, Any]:
    # 部署載荷包含：
    # • VSIX文件內容（base64編碼）
    # • 元數據和校驗和
    # • 部署配置（自動安裝、驗證、備份、回滾）
    # • 安全簽名
```

### **2. Local MCP端接收組件** (`local_mcp_vsix_receiver.py`)

#### **主要功能**
- **API服務**: 提供RESTful API接收部署請求
- **文件處理**: 解碼、驗證和保存VSIX文件
- **VSCode集成**: 調用VSCode CLI進行實際安裝
- **狀態管理**: 維護擴展安裝狀態和註冊表

#### **關鍵API端點**

##### **POST /api/v1/extensions/deploy**
```python
async def deploy_extension(request: dict, background_tasks: BackgroundTasks):
    """
    接收並部署VSIX擴展
    
    請求格式：
    {
        "deployment_id": "deploy_xxx",
        "vsix_package": {
            "name": "extension-name",
            "version": "1.0.0",
            "content": "base64-encoded-vsix",
            "checksum": "sha256-hash"
        },
        "deployment_config": {
            "auto_install": true,
            "verify_after_install": true,
            "backup_existing": true,
            "rollback_on_failure": true
        }
    }
    
    響應：
    {
        "status": "accepted",
        "deployment_id": "deploy_xxx",
        "message": "部署請求已接受，正在後台處理"
    }
    """
```

##### **POST /api/v1/extensions/verify**
```python
async def verify_extension(request: dict):
    """
    驗證擴展安裝狀態
    
    請求格式：
    {
        "deployment_id": "deploy_xxx",
        "extension_name": "extension-name",
        "expected_checksum": "sha256-hash"
    }
    
    響應：
    {
        "verified": true,
        "extension_info": {...},
        "vscode_installed": true
    }
    """
```

##### **GET /api/v1/extensions/list**
```python
async def list_extensions():
    """
    列出已安裝的擴展
    
    響應：
    {
        "extensions": [
            {
                "name": "extension-name",
                "version": "1.0.0",
                "install_path": "/path/to/extension",
                "status": "installed",
                "install_timestamp": "2025-01-01T00:00:00"
            }
        ],
        "total_count": 1
    }
    """
```

#### **核心處理流程**

##### **異步部署處理**
```python
async def _process_deployment_async(self, request: DeploymentRequest):
    """
    後台異步處理部署：
    1. 解碼和保存VSIX文件
    2. 驗證VSIX文件完整性
    3. 備份現有擴展（如果存在）
    4. 調用VSCode CLI安裝擴展
    5. 更新擴展註冊表
    6. 失敗時執行回滾
    """
```

##### **VSCode CLI集成**
```python
async def _install_extension(self, vsix_file_path: str, request: DeploymentRequest) -> InstallationResult:
    """
    使用VSCode命令行安裝擴展：
    
    命令: code --install-extension /path/to/extension.vsix
    
    處理：
    • 執行安裝命令
    • 捕獲stdout/stderr
    • 檢查返回碼
    • 生成安裝日誌
    • 創建擴展信息記錄
    """
```

### **3. 端到端驗證組件** (`e2e_vsix_verifier.py`)

#### **主要功能**
- **完整驗證**: 6步驟端到端驗證流程
- **性能測試**: 啟動時間、內存使用、響應時間測試
- **功能測試**: VSCode擴展功能驗證
- **穩定性測試**: 重複操作和錯誤恢復測試

#### **6步驟驗證流程**

##### **步驟1: 環境準備和檢查**
```python
async def _verify_environment(self) -> Dict[str, Any]:
    """
    檢查項目：
    • AICore端點健康狀態
    • Local MCP端點健康狀態  
    • 測試環境準備情況
    • 必需工具可用性（node, npm, code）
    """
```

##### **步驟2: AICore端VSIX構建**
```python
async def _verify_aicore_build(self) -> Dict[str, Any]:
    """
    構建驗證：
    • 發送構建請求到AICore
    • 等待構建完成
    • 驗證構建結果
    • 獲取VSIX信息
    """
```

##### **步驟3: 部署到Local MCP**
```python
async def _verify_deployment(self, build_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    部署驗證：
    • 發送部署請求
    • 監控部署進度
    • 驗證部署結果
    • 獲取Local MCP響應
    """
```

##### **步驟4: Local MCP端安裝驗證**
```python
async def _verify_installation(self, deployment_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    安裝驗證：
    • 查詢Local MCP安裝狀態
    • 驗證校驗和匹配
    • 檢查擴展是否在已安裝列表中
    • 確認安裝記錄完整性
    """
```

##### **步驟5: VSCode功能測試**
```python
async def _verify_vscode_functionality(self, deployment_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    功能測試：
    • VSCode擴展列表檢查: code --list-extensions
    • 擴展命令測試（如果有contributes.commands）
    • 擴展激活測試
    • 功能完整性驗證
    """
```

##### **步驟6: 性能和穩定性測試**
```python
async def _verify_performance(self, deployment_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    性能測試：
    • 擴展啟動時間測量
    • 內存使用監控
    • 響應時間測試
    • 穩定性測試（重複操作）
    • 性能分數計算
    """
```

## 🔄 **完整工作流程**

### **階段1: 準備階段**
```
1. 配置AICore和Local MCP端點
2. 準備測試擴展源代碼
3. 檢查環境依賴（node, npm, vscode）
4. 驗證API連接和認證
```

### **階段2: 構建階段**
```
AICore端：
1. 讀取擴展源代碼
2. 安裝npm依賴
3. 編譯TypeScript
4. 使用vsce打包VSIX
5. 計算文件校驗和
6. 提取擴展元數據
```

### **階段3: 部署階段**
```
AICore → Local MCP：
1. 準備部署載荷（base64編碼VSIX）
2. 生成安全簽名
3. 發送HTTP POST請求到Local MCP
4. 接收部署確認響應
```

### **階段4: 安裝階段**
```
Local MCP端：
1. 驗證API認證
2. 解碼VSIX文件
3. 驗證文件完整性
4. 備份現有擴展
5. 調用VSCode CLI安裝
6. 更新擴展註冊表
```

### **階段5: 驗證階段**
```
端到端驗證：
1. 查詢安裝狀態
2. 驗證校驗和匹配
3. 檢查VSCode擴展列表
4. 測試擴展功能
5. 性能和穩定性測試
```

### **階段6: 監控階段**
```
持續監控：
1. 健康狀態檢查
2. 性能指標收集
3. 錯誤日誌監控
4. 自動故障恢復
```

## 📊 **數據流和API交互**

### **部署請求數據流**
```json
{
  "deployment_id": "deploy_1640995200",
  "deployment_type": "vsix_extension",
  "timestamp": "2025-01-01T00:00:00Z",
  "vsix_package": {
    "name": "powerautomation-local",
    "version": "1.0.0",
    "checksum": "sha256:abc123...",
    "size": 4096,
    "content": "UEsDBBQAAAAIAA...",  // base64編碼的VSIX文件
    "metadata": {
      "engines": {"vscode": "^1.60.0"},
      "categories": ["Other"],
      "contributes": {...}
    }
  },
  "deployment_config": {
    "auto_install": true,
    "verify_after_install": true,
    "backup_existing": true,
    "rollback_on_failure": true
  },
  "security": {
    "signature": "sha256:def456...",
    "api_key": "powerautomation-local-key"
  }
}
```

### **驗證響應數據流**
```json
{
  "verified": true,
  "extension_info": {
    "name": "powerautomation-local",
    "version": "1.0.0",
    "install_path": "~/.vscode/extensions/powerautomation-local",
    "checksum": "sha256:abc123...",
    "install_timestamp": "2025-01-01T00:05:00Z",
    "source_deployment_id": "deploy_1640995200",
    "status": "installed"
  },
  "vscode_installed": true,
  "extension_in_list": true,
  "timestamp": "2025-01-01T00:05:30Z"
}
```

## 🔒 **安全機制**

### **認證和授權**
- **API密鑰認證**: 所有API調用需要有效的Bearer token
- **部署簽名**: 使用SHA256簽名驗證部署請求完整性
- **來源驗證**: 檢查部署請求來源的合法性

### **文件完整性**
- **校驗和驗證**: SHA256校驗和確保文件傳輸完整性
- **格式驗證**: 檢查VSIX文件的ZIP格式和必要文件
- **大小限制**: 限制VSIX文件最大大小（默認50MB）

### **錯誤處理和回滾**
- **自動備份**: 安裝前自動備份現有擴展
- **失敗回滾**: 安裝失敗時自動恢復到之前狀態
- **詳細日誌**: 記錄所有操作步驟便於問題診斷

## 📈 **性能和監控**

### **性能指標**
- **構建時間**: VSIX構建耗時
- **部署時間**: 從AICore到Local MCP的傳輸時間
- **安裝時間**: VSCode擴展安裝耗時
- **啟動時間**: 擴展激活和啟動時間
- **內存使用**: 擴展運行時內存佔用

### **監控機制**
- **健康檢查**: 定期檢查各組件健康狀態
- **狀態追蹤**: 實時追蹤部署和安裝狀態
- **錯誤報告**: 自動收集和報告錯誤信息
- **性能分析**: 生成性能報告和改進建議

## 🚀 **使用示例**

### **基本使用**
```python
# 1. 配置
config = VSIXDeploymentConfig(
    aicore_workspace="/workspace/powerautomation",
    build_output_dir="/workspace/build/vsix",
    local_mcp_endpoint="http://localhost:8080",
    local_mcp_api_key="your-api-key",
    extension_name="powerautomation-local",
    extension_version="1.0.0",
    vscode_engine_version="^1.60.0"
)

# 2. 部署
async with AICore_VSIX_Deployer(config) as deployer:
    result = await deployer.deploy_vsix_to_local_mcp(
        extension_source_path="/workspace/powerautomation/vscode-extension"
    )

# 3. 驗證
verification_config = VerificationConfig(
    aicore_endpoint="http://localhost:5000",
    aicore_api_key="aicore-key",
    local_mcp_endpoint="http://localhost:8080",
    local_mcp_api_key="mcp-key"
)

async with E2E_VSIX_Verifier(verification_config) as verifier:
    verification_result = await verifier.run_full_verification()
```

### **Local MCP服務啟動**
```python
# 啟動Local MCP接收服務
config = LocalMCPConfig(
    host="0.0.0.0",
    port=8080,
    api_key="powerautomation-local-key",
    extensions_dir="/local/powerautomation/extensions"
)

receiver = LocalMCP_VSIX_Receiver(config)
receiver.run()  # 啟動FastAPI服務
```

## 🎯 **解決的核心問題**

### **VSIX版本兼容性問題**
- **問題**: "暫不支持安裝插件的 3.0.0 版本"
- **解決**: 自動檢測和修正package.json中的engines.vscode版本
- **驗證**: 確保使用^1.60.0等兼容版本範圍

### **部署自動化**
- **問題**: 手動部署VSIX文件繁瑣且容易出錯
- **解決**: 完全自動化的構建、部署、安裝流程
- **驗證**: 端到端驗證確保每個步驟正確執行

### **狀態可見性**
- **問題**: 無法了解部署和安裝的實時狀態
- **解決**: 詳細的狀態追蹤和實時監控
- **驗證**: 完整的日誌記錄和狀態報告

## 📋 **下一步執行計劃**

1. **Review代碼**: 檢查三個核心組件的實現
2. **環境準備**: 設置AICore和Local MCP測試環境
3. **集成測試**: 運行端到端驗證流程
4. **性能優化**: 根據測試結果優化性能
5. **生產部署**: 部署到實際環境並監控運行狀態

這個工作流提供了完整的解決方案，從AICore端的VSIX構建到Local MCP端的安裝驗證，確保VSCode擴展能夠正確部署和運行。

