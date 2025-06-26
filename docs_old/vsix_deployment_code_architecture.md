# VSIX部署系統代碼架構和實現細節

## 🏗️ **代碼架構總覽**

### **模塊依賴關係**
```
┌─────────────────────────────────────────────────────────────┐
│                    VSIX部署系統架構                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────┐ │
│  │  AICore端       │    │  Local MCP端    │    │ VSCode端 │ │
│  │                 │    │                 │    │          │ │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌──────┐ │ │
│  │ │ Deployer    │ │───▶│ │ Receiver    │ │───▶│ │ CLI  │ │ │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └──────┘ │ │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌──────┐ │ │
│  │ │ Builder     │ │    │ │ Installer   │ │    │ │ Ext  │ │ │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └──────┘ │ │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │          │ │
│  │ │ Validator   │ │    │ │ Registry    │ │    │          │ │
│  │ └─────────────┘ │    │ └─────────────┘ │    │          │ │
│  └─────────────────┘    └─────────────────┘    └──────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              E2E驗證系統                                │ │
│  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │ │
│  │ │ Env     │ │ Build   │ │ Deploy  │ │ Verify  │        │ │
│  │ │ Check   │ │ Test    │ │ Test    │ │ Test    │        │ │
│  │ └─────────┘ └─────────┘ └─────────┘ └─────────┘        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📁 **文件結構和職責**

### **aicore_vsix_deployer.py** (AICore端部署組件)
```
aicore_vsix_deployer.py
├── VSIXDeploymentConfig        # 配置數據類
├── VSIXPackage                 # VSIX包信息數據類
├── DeploymentResult           # 部署結果數據類
└── AICore_VSIX_Deployer       # 主要部署器類
    ├── __aenter__/__aexit__   # 異步上下文管理
    ├── deploy_vsix_to_local_mcp()  # 主要部署方法
    ├── _build_vsix_package()      # VSIX構建
    ├── _validate_vsix_package()   # VSIX驗證
    ├── _prepare_deployment_payload()  # 部署載荷準備
    ├── _deploy_to_local_mcp()     # 部署到MCP
    ├── _verify_deployment()       # 部署驗證
    ├── _run_command()             # 命令執行
    ├── _calculate_file_checksum() # 校驗和計算
    ├── _extract_vsix_metadata()   # 元數據提取
    └── _generate_deployment_signature()  # 簽名生成
```

### **local_mcp_vsix_receiver.py** (Local MCP端接收組件)
```
local_mcp_vsix_receiver.py
├── LocalMCPConfig             # MCP配置數據類
├── ExtensionInfo              # 擴展信息數據類
├── DeploymentRequest          # 部署請求數據類
├── InstallationResult         # 安裝結果數據類
└── LocalMCP_VSIX_Receiver     # 主要接收器類
    ├── __init__()             # 初始化和路由設置
    ├── _setup_routes()        # API路由設置
    │   ├── POST /api/v1/extensions/deploy     # 部署端點
    │   ├── POST /api/v1/extensions/verify     # 驗證端點
    │   ├── GET  /api/v1/extensions/list       # 列表端點
    │   ├── DELETE /api/v1/extensions/{name}   # 卸載端點
    │   └── GET  /api/v1/health               # 健康檢查
    ├── _process_deployment_async()  # 異步部署處理
    ├── _save_vsix_file()           # VSIX文件保存
    ├── _validate_vsix_file()       # VSIX文件驗證
    ├── _install_extension()        # 擴展安裝
    ├── _verify_extension_installation()  # 安裝驗證
    ├── _check_extension_in_vscode()      # VSCode檢查
    └── _load_installed_extensions()      # 擴展註冊表管理
```

### **e2e_vsix_verifier.py** (端到端驗證組件)
```
e2e_vsix_verifier.py
├── VerificationConfig         # 驗證配置數據類
├── VerificationStep           # 驗證步驟數據類
├── E2EVerificationResult      # 驗證結果數據類
└── E2E_VSIX_Verifier         # 主要驗證器類
    ├── run_full_verification()    # 主要驗證流程
    ├── _run_verification_step()   # 步驟執行框架
    ├── _verify_environment()      # 步驟1: 環境檢查
    ├── _verify_aicore_build()     # 步驟2: 構建驗證
    ├── _verify_deployment()       # 步驟3: 部署驗證
    ├── _verify_installation()     # 步驟4: 安裝驗證
    ├── _verify_vscode_functionality()  # 步驟5: 功能驗證
    ├── _verify_performance()      # 步驟6: 性能驗證
    └── _generate_recommendations() # 建議生成
```

## 🔧 **核心實現細節**

### **1. 異步處理架構**

#### **異步上下文管理器模式**
```python
class AICore_VSIX_Deployer:
    async def __aenter__(self):
        """
        初始化異步資源：
        • 創建aiohttp.ClientSession
        • 設置超時配置
        • 準備HTTP連接池
        """
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.deployment_timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        清理異步資源：
        • 關閉HTTP會話
        • 釋放連接池
        • 清理臨時文件
        """
        if self.session:
            await self.session.close()
```

#### **並發處理機制**
```python
# Local MCP端使用FastAPI的BackgroundTasks進行異步處理
@app.post("/api/v1/extensions/deploy")
async def deploy_extension(request: dict, background_tasks: BackgroundTasks):
    # 立即返回接受響應
    background_tasks.add_task(self._process_deployment_async, deployment_request)
    return {"status": "accepted", "deployment_id": deployment_request.deployment_id}

# 後台異步處理實際安裝
async def _process_deployment_async(self, request: DeploymentRequest):
    # 長時間運行的安裝過程
    # 不阻塞API響應
```

### **2. 錯誤處理和重試機制**

#### **分層錯誤處理**
```python
async def deploy_vsix_to_local_mcp(self) -> DeploymentResult:
    try:
        # 步驟1: 構建VSIX包
        vsix_package = await self._build_vsix_package(extension_source_path)
        
        # 步驟2: 驗證VSIX包
        validation_result = await self._validate_vsix_package(vsix_package)
        if not validation_result["valid"]:
            raise Exception(f"VSIX包驗證失敗: {validation_result['errors']}")
        
        # ... 其他步驟
        
    except Exception as e:
        logger.error(f"VSIX部署失敗: {e}")
        return DeploymentResult(
            success=False,
            error_message=str(e),
            # ... 其他錯誤信息
        )
```

#### **重試機制實現**
```python
async def _wait_for_build_completion(self, build_id: str) -> Dict[str, Any]:
    """帶重試的狀態檢查"""
    for attempt in range(self.config.retry_attempts):
        try:
            async with self.session.get(status_url, headers=headers) as response:
                if response.status == 200:
                    status_data = await response.json()
                    if status_data["status"] == "completed":
                        return status_data
                    elif status_data["status"] == "failed":
                        raise Exception(f"構建失敗: {status_data.get('error')}")
                
                # 等待後重試
                await asyncio.sleep(self.config.retry_delay)
        except Exception as e:
            if attempt == self.config.retry_attempts - 1:
                raise e
            await asyncio.sleep(self.config.retry_delay)
    
    raise Exception("構建超時")
```

### **3. 安全機制實現**

#### **API認證**
```python
# FastAPI安全依賴
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != self.config.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

# 使用認證的端點
@app.post("/api/v1/extensions/deploy")
async def deploy_extension(
    request: dict,
    api_key: str = Depends(verify_api_key)
):
    # 已認證的請求處理
```

#### **文件完整性驗證**
```python
async def _validate_vsix_file(self, file_path: str, request: DeploymentRequest) -> Dict[str, Any]:
    """多層次文件驗證"""
    errors = []
    
    # 1. 文件存在性檢查
    if not Path(file_path).exists():
        errors.append("VSIX文件不存在")
    
    # 2. 校驗和驗證
    actual_checksum = await self._calculate_file_checksum(file_path)
    expected_checksum = request.vsix_package.get("checksum")
    if actual_checksum != expected_checksum:
        errors.append(f"校驗和不匹配: {actual_checksum} != {expected_checksum}")
    
    # 3. ZIP格式驗證
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            zip_contents = zip_file.namelist()
            if not any('package.json' in content for content in zip_contents):
                errors.append("VSIX文件中缺少package.json")
    except zipfile.BadZipFile:
        errors.append("VSIX文件格式無效")
    
    return {"valid": len(errors) == 0, "errors": errors}
```

#### **部署簽名機制**
```python
async def _generate_deployment_signature(self, vsix_package: VSIXPackage) -> str:
    """生成部署簽名"""
    signature_data = f"{vsix_package.name}:{vsix_package.version}:{vsix_package.checksum}:{self.deployment_id}"
    return hashlib.sha256(signature_data.encode()).hexdigest()

async def _verify_deployment_signature(self, request: DeploymentRequest) -> bool:
    """驗證部署簽名"""
    expected_signature = request.security.get("signature", "")
    calculated_signature = self._calculate_signature(request)
    return expected_signature == calculated_signature
```

### **4. VSCode CLI集成**

#### **命令執行框架**
```python
async def _run_command(self, cmd: List[str], cwd: Path = None) -> str:
    """安全的命令執行"""
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"命令執行失敗: {' '.join(cmd)}\n{stderr.decode()}")
    
    return stdout.decode()
```

#### **VSCode擴展安裝**
```python
async def _install_extension(self, vsix_file_path: str, request: DeploymentRequest) -> InstallationResult:
    """VSCode擴展安裝實現"""
    installation_log = []
    
    try:
        # 構建安裝命令
        cmd = [self.config.vscode_command, "--install-extension", vsix_file_path]
        
        # 執行安裝
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # 記錄詳細日誌
        installation_log.extend([
            f"命令: {' '.join(cmd)}",
            f"返回碼: {process.returncode}",
            f"stdout: {stdout.decode()}",
            f"stderr: {stderr.decode()}"
        ])
        
        if process.returncode == 0:
            # 安裝成功，創建擴展信息
            extension_info = ExtensionInfo(
                name=request.vsix_package["name"],
                version=request.vsix_package["version"],
                install_path=self._get_extension_install_path(request.vsix_package["name"]),
                checksum=request.vsix_package["checksum"],
                install_timestamp=datetime.now(),
                source_deployment_id=request.deployment_id,
                status="installed",
                metadata=request.vsix_package.get("metadata", {})
            )
            
            return InstallationResult(
                success=True,
                extension_info=extension_info,
                installation_log=installation_log
            )
        else:
            return InstallationResult(
                success=False,
                extension_info=None,
                installation_log=installation_log,
                error_message=f"VSCode安裝命令失敗: {stderr.decode()}"
            )
            
    except Exception as e:
        installation_log.append(f"安裝異常: {str(e)}")
        return InstallationResult(
            success=False,
            extension_info=None,
            installation_log=installation_log,
            error_message=str(e)
        )
```

### **5. 狀態管理和持久化**

#### **擴展註冊表管理**
```python
class LocalMCP_VSIX_Receiver:
    def __init__(self, config: LocalMCPConfig):
        self.installed_extensions: Dict[str, ExtensionInfo] = {}
        self._load_installed_extensions()
    
    def _load_installed_extensions(self):
        """從文件加載擴展註冊表"""
        registry_file = Path(self.config.extensions_dir) / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, ext_data in data.items():
                        # 重建ExtensionInfo對象
                        ext_data['install_timestamp'] = datetime.fromisoformat(ext_data['install_timestamp'])
                        self.installed_extensions[name] = ExtensionInfo(**ext_data)
            except Exception as e:
                logger.warning(f"加載擴展註冊表失敗: {e}")
    
    async def _save_extension_registry(self):
        """保存擴展註冊表到文件"""
        registry_file = Path(self.config.extensions_dir) / "registry.json"
        try:
            data = {}
            for name, ext in self.installed_extensions.items():
                ext_dict = asdict(ext)
                # 序列化datetime對象
                ext_dict['install_timestamp'] = ext.install_timestamp.isoformat()
                data[name] = ext_dict
            
            async with aiofiles.open(registry_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"保存擴展註冊表失敗: {e}")
```

### **6. 性能監控和指標收集**

#### **性能測量框架**
```python
class E2E_VSIX_Verifier:
    async def _measure_extension_startup_time(self, extension_name: str) -> Dict[str, Any]:
        """測量擴展啟動時間"""
        start_time = time.time()
        
        # 啟動VSCode並激活擴展
        cmd = [
            "code", 
            "--new-window",
            "--wait",
            f"--enable-extension={extension_name}",
            "/tmp/test-workspace"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 等待進程啟動
            await asyncio.sleep(2)  # 給VSCode時間啟動
            
            # 測量實際啟動時間
            startup_time = (time.time() - start_time) * 1000  # 轉換為毫秒
            
            # 終止進程
            process.terminate()
            await process.wait()
            
            # 評估性能等級
            if startup_time < 100:
                benchmark = "excellent"
            elif startup_time < 300:
                benchmark = "good"
            elif startup_time < 1000:
                benchmark = "average"
            else:
                benchmark = "poor"
            
            return {
                "startup_time_ms": startup_time,
                "benchmark": benchmark,
                "measurement_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "startup_time_ms": -1,
                "benchmark": "error",
                "error": str(e)
            }
```

#### **內存使用監控**
```python
async def _measure_memory_usage(self) -> Dict[str, Any]:
    """測量內存使用"""
    try:
        # 使用psutil監控VSCode進程
        import psutil
        
        vscode_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            if 'code' in proc.info['name'].lower():
                vscode_processes.append(proc)
        
        if vscode_processes:
            total_memory = sum(proc.info['memory_info'].rss for proc in vscode_processes)
            memory_mb = total_memory / (1024 * 1024)  # 轉換為MB
            
            # 評估內存使用等級
            if memory_mb < 50:
                benchmark = "excellent"
            elif memory_mb < 150:
                benchmark = "good"
            elif memory_mb < 300:
                benchmark = "average"
            else:
                benchmark = "poor"
            
            return {
                "memory_usage_mb": memory_mb,
                "process_count": len(vscode_processes),
                "benchmark": benchmark
            }
        else:
            return {
                "memory_usage_mb": 0,
                "process_count": 0,
                "benchmark": "no_process"
            }
            
    except ImportError:
        return {
            "memory_usage_mb": -1,
            "benchmark": "psutil_not_available"
        }
    except Exception as e:
        return {
            "memory_usage_mb": -1,
            "benchmark": "error",
            "error": str(e)
        }
```

## 🔄 **數據流轉和狀態機**

### **部署狀態機**
```
[準備] → [構建] → [驗證] → [部署] → [安裝] → [完成]
   ↓        ↓        ↓        ↓        ↓        ↓
[錯誤] ← [錯誤] ← [錯誤] ← [錯誤] ← [錯誤] ← [錯誤]
   ↓
[回滾] → [清理] → [失敗]
```

### **數據轉換流程**
```
源代碼 → npm build → VSIX文件 → base64編碼 → HTTP傳輸 → 
base64解碼 → VSIX文件 → VSCode安裝 → 擴展激活
```

## 📊 **關鍵配置參數**

### **性能調優參數**
```python
# 超時配置
deployment_timeout: int = 300      # 部署總超時時間
retry_attempts: int = 3            # 重試次數
retry_delay: int = 30              # 重試間隔

# 文件大小限制
max_extension_size: int = 50 * 1024 * 1024  # 50MB

# 並發控制
max_concurrent_deployments: int = 5  # 最大並發部署數
```

### **安全配置參數**
```python
# 認證配置
enable_signature_verification: bool = True
api_key_length: int = 32

# 文件驗證
checksum_algorithm: str = "sha256"
required_files: List[str] = ["package.json", "extension.vsixmanifest"]
```

這個代碼架構提供了完整的VSIX部署解決方案，具有良好的可擴展性、安全性和性能。每個組件都有明確的職責分工，通過異步處理和錯誤處理機制確保系統的穩定性和可靠性。

