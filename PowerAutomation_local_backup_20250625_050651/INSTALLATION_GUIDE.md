# PowerAutomation Local MCP Adapter - 安裝和使用指南

**版本**: 1.0.0  
**作者**: Manus AI  
**日期**: 2025-06-23

## 📋 目錄

1. [系統要求](#系統要求)
2. [安裝步驟](#安裝步驟)
3. [配置設置](#配置設置)
4. [基本使用](#基本使用)
5. [高級功能](#高級功能)
6. [故障排除](#故障排除)
7. [最佳實踐](#最佳實踐)

## 🖥️ 系統要求

### 最低要求

- **操作系統**: 
  - Linux: Ubuntu 18.04+ / CentOS 7+ / Debian 9+
  - macOS: 10.14 Mojave 或更高版本
  - Windows: Windows 10 版本 1903 或更高版本

- **硬件要求**:
  - CPU: 雙核 2.0GHz 或更高
  - 內存: 最少 2GB RAM
  - 磁盤空間: 最少 1GB 可用空間
  - 網絡: 穩定的互聯網連接

- **軟件依賴**:
  - Python 3.8 或更高版本
  - pip 包管理器
  - Git 版本控制系統

### 推薦配置

- **硬件配置**:
  - CPU: 四核 3.0GHz 或更高
  - 內存: 8GB RAM 或更多
  - 磁盤空間: 5GB 可用空間
  - SSD 存儲設備

- **軟件版本**:
  - Python 3.10 或更高版本
  - Node.js 18.0+ (用於 VSCode 擴展開發)
  - VSCode 1.70+ (用於 IDE 集成)

## 🚀 安裝步驟

### 步驟 1: 環境準備

#### Linux/macOS

```bash
# 更新系統包管理器
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# 或
brew update && brew upgrade             # macOS

# 安裝 Python 3.8+
sudo apt install python3 python3-pip python3-venv git  # Ubuntu/Debian
# 或
brew install python3 git                                # macOS

# 驗證 Python 版本
python3 --version
pip3 --version
```

#### Windows

```powershell
# 使用 Chocolatey 安裝 (推薦)
choco install python3 git

# 或從官網下載安裝
# Python: https://www.python.org/downloads/
# Git: https://git-scm.com/download/win

# 驗證安裝
python --version
pip --version
```

### 步驟 2: 獲取項目代碼

```bash
# 克隆項目倉庫
git clone https://github.com/your-org/PowerAutomationlocal_Adapter.git

# 進入項目目錄
cd PowerAutomationlocal_Adapter

# 檢查項目結構
ls -la
```

### 步驟 3: 創建虛擬環境

```bash
# 創建 Python 虛擬環境
python3 -m venv powerautomation_env

# 激活虛擬環境
source powerautomation_env/bin/activate  # Linux/macOS
# 或
powerautomation_env\Scripts\activate     # Windows

# 驗證虛擬環境
which python  # 應該指向虛擬環境中的 Python
```

### 步驟 4: 安裝 Python 依賴

```bash
# 升級 pip
pip install --upgrade pip

# 安裝核心依賴
pip install toml aiohttp flask flask-cors websockets psutil

# 安裝自動化測試依賴
pip install playwright

# 安裝 Playwright 瀏覽器
playwright install chromium

# 驗證安裝
python -c "import playwright; print('Playwright installed successfully')"
```

### 步驟 5: 驗證安裝

```bash
# 運行基本功能測試
python3 basic_test.py

# 預期輸出應該顯示所有測試通過
# 🎉 基本功能測試通過！
```

## ⚙️ 配置設置

### 基本配置

編輯 `config.toml` 文件進行基本配置：

```toml
# PowerAutomation Local MCP 配置文件

[server]
# 服務器基本設置
host = "0.0.0.0"          # 綁定地址，0.0.0.0 表示所有接口
port = 5000               # 服務端口
debug = false             # 調試模式
cors_enabled = true       # 跨域請求支持
max_connections = 100     # 最大連接數
request_timeout = 30      # 請求超時時間(秒)

[manus]
# Manus 平台集成設置
app_url = "https://manus.im/app/uuX3KzwzsthCSgqmbQbgOz"
login_email = "your-email@example.com"     # 替換為您的郵箱
login_password = "your-password"           # 替換為您的密碼
auto_login = true                          # 自動登錄
session_timeout = 3600                     # 會話超時時間(秒)
retry_attempts = 3                         # 重試次數
retry_delay = 5                           # 重試延遲(秒)

[automation]
# 自動化測試設置
browser = "chromium"                       # 瀏覽器類型
headless = false                          # 無頭模式
screenshot_enabled = true                 # 截圖功能
video_recording = true                    # 視頻錄製
test_timeout = 300                        # 測試超時時間(秒)
parallel_tests = 1                        # 並行測試數量
```

### 高級配置

```toml
[storage]
# 數據存儲設置
base_path = "/home/ubuntu/powerautomation_data"  # 數據存儲根目錄
index_enabled = true                             # 搜索索引
backup_enabled = true                            # 自動備份
cleanup_days = 30                               # 清理週期(天)
max_file_size = "100MB"                         # 最大文件大小
compression_enabled = true                      # 壓縮存儲
allowed_extensions = [".pdf", ".png", ".jpg", ".txt", ".md", ".json"]

# 存儲路徑配置
[storage.paths]
screenshots = "screenshots"
videos = "videos"
reports = "reports"
logs = "logs"
temp = "temp"
backups = "backups"

[extension]
# VSCode 擴展設置
auto_start = true                               # 自動啟動
sidebar_enabled = true                          # 側邊欄顯示
notifications_enabled = true                    # 通知功能
theme = "dark"                                 # 主題設置
auto_refresh = true                            # 自動刷新
refresh_interval = 30                          # 刷新間隔(秒)
max_history_items = 100                        # 最大歷史記錄數

# 擴展命令配置
[extension.commands]
login = "powerautomation.login"
send_message = "powerautomation.sendMessage"
get_conversations = "powerautomation.getConversations"
get_tasks = "powerautomation.getTasks"
run_test = "powerautomation.runTest"
view_status = "powerautomation.viewStatus"

[logging]
# 日誌設置
level = "INFO"                                 # 日誌級別
console_enabled = true                         # 控制台輸出
file_enabled = true                           # 文件輸出
max_file_size = "10MB"                        # 最大文件大小
backup_count = 5                              # 備份文件數量
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 環境變量配置

為了安全起見，建議使用環境變量存儲敏感信息：

```bash
# 創建 .env 文件
cat > .env << EOF
POWERAUTOMATION_CONFIG_PATH=./config.toml
POWERAUTOMATION_LOG_LEVEL=INFO
POWERAUTOMATION_DATA_PATH=./data
MANUS_EMAIL=your-email@example.com
MANUS_PASSWORD=your-secure-password
MANUS_APP_URL=https://manus.im/app/uuX3KzwzsthCSgqmbQbgOz
EOF

# 設置文件權限
chmod 600 .env

# 加載環境變量
source .env
```

然後在 `config.toml` 中使用環境變量：

```toml
[manus]
app_url = "${MANUS_APP_URL}"
login_email = "${MANUS_EMAIL}"
login_password = "${MANUS_PASSWORD}"
```

## 🎯 基本使用

### 啟動方式

#### 1. 命令行模式

```bash
# 直接啟動 MCP 適配器
python3 powerautomation_local_mcp.py

# 使用 CLI 工具啟動
python3 cli.py --mode server

# 交互模式啟動
python3 cli.py --interactive
```

#### 2. 後台服務模式

```bash
# 使用 nohup 後台運行
nohup python3 powerautomation_local_mcp.py > powerautomation.log 2>&1 &

# 使用 systemd 服務 (Linux)
sudo systemctl start powerautomation
sudo systemctl enable powerautomation

# 檢查服務狀態
sudo systemctl status powerautomation
```

#### 3. 開發模式

```bash
# 啟用調試模式
export POWERAUTOMATION_DEBUG=true
python3 powerautomation_local_mcp.py

# 或修改配置文件
# config.toml: debug = true
```

### 基本操作

#### 1. 檢查系統狀態

```bash
# 使用 CLI 工具檢查狀態
python3 cli.py --status

# 使用 curl 檢查 API
curl http://localhost:5000/api/status
```

#### 2. 運行測試案例

```bash
# 運行單個測試案例
python3 cli.py --test TC001

# 運行所有測試案例
python3 cli.py --test-all

# 運行特定類型的測試
python3 cli.py --test-category automation
```

#### 3. Manus 平台操作

```bash
# 登錄 Manus
curl -X POST http://localhost:5000/api/server/manus_login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "password": "your-password"}'

# 發送消息
curl -X POST http://localhost:5000/api/server/send_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from PowerAutomation!"}'

# 獲取對話歷史
curl http://localhost:5000/api/server/get_conversations

# 獲取任務列表
curl http://localhost:5000/api/server/get_tasks
```

### VSCode 擴展使用

#### 1. 安裝擴展

```bash
# 進入擴展目錄
cd vscode-extension

# 安裝依賴
npm install

# 編譯 TypeScript
npm run compile

# 打包擴展
npm run package

# 安裝到 VSCode
code --install-extension powerautomation-local-1.0.0.vsix
```

#### 2. 使用擴展

1. **打開命令面板**: `Ctrl+Shift+P` (Windows/Linux) 或 `Cmd+Shift+P` (macOS)
2. **搜索 PowerAutomation 命令**:
   - `PowerAutomation: Login to Manus`
   - `PowerAutomation: Send Message`
   - `PowerAutomation: Get Conversations`
   - `PowerAutomation: Get Tasks`
   - `PowerAutomation: Run Test`
   - `PowerAutomation: View Status`

3. **使用側邊欄**: 在 VSCode 左側面板中查看 PowerAutomation 狀態和活動

#### 3. 擴展配置

在 VSCode 設置中配置 PowerAutomation：

```json
{
  "powerautomation.serverUrl": "http://localhost:5000",
  "powerautomation.autoStart": true,
  "powerautomation.notifications": true,
  "powerautomation.theme": "dark"
}
```

## 🔧 高級功能

### 自定義測試案例

#### 1. 創建新測試案例

```python
# 在 server/automation/automation_engine.py 中添加新方法
async def _run_tc007_custom_test(self, page: Page) -> Dict[str, Any]:
    """運行自定義測試案例"""
    try:
        self.logger.info("執行TC007 - 自定義測試")
        
        screenshots = []
        details = {}
        
        # 您的自定義測試邏輯
        # ...
        
        return {
            "success": True,
            "message": "自定義測試成功",
            "details": details,
            "screenshots": screenshots
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"TC007測試執行失敗: {e}",
            "details": details,
            "screenshots": screenshots
        }
```

#### 2. 註冊新測試案例

```python
# 在 run_test 方法中添加新案例
elif test_case.upper() == "TC007":
    result = await self._run_tc007_custom_test(page)
```

### 數據存儲和搜索

#### 1. 存儲文件

```python
import requests

# 存儲文件到系統
response = requests.post('http://localhost:5000/api/server/store_file', json={
    "file_path": "/path/to/your/file.pdf",
    "category": "reports",
    "metadata": {
        "title": "Monthly Report",
        "tags": ["report", "monthly", "analysis"],
        "author": "John Doe"
    }
})
```

#### 2. 搜索文件

```python
# 搜索文件
response = requests.post('http://localhost:5000/api/server/storage_search', json={
    "query": "monthly report",
    "category": "reports",
    "limit": 10
})

results = response.json()
for file_info in results['data']['results']:
    print(f"文件: {file_info['file_name']}")
    print(f"路徑: {file_info['file_path']}")
    print(f"大小: {file_info['size_formatted']}")
```

### 自動化工作流程

#### 1. 創建工作流程腳本

```python
#!/usr/bin/env python3
"""
自動化工作流程示例
"""

import asyncio
import aiohttp
import json

async def automated_workflow():
    """執行自動化工作流程"""
    
    base_url = "http://localhost:5000/api"
    
    async with aiohttp.ClientSession() as session:
        # 步驟 1: 登錄 Manus
        async with session.post(f"{base_url}/server/manus_login") as resp:
            login_result = await resp.json()
            if not login_result.get('success'):
                print("登錄失敗")
                return
        
        # 步驟 2: 發送消息
        message_data = {"message": "開始自動化測試流程"}
        async with session.post(f"{base_url}/server/send_message", 
                               json=message_data) as resp:
            await resp.json()
        
        # 步驟 3: 運行測試案例
        for test_case in ["TC001", "TC002", "TC003"]:
            test_data = {"test_case": test_case}
            async with session.post(f"{base_url}/server/run_test", 
                                   json=test_data) as resp:
                result = await resp.json()
                print(f"測試 {test_case}: {'成功' if result.get('success') else '失敗'}")
        
        # 步驟 4: 獲取結果
        async with session.get(f"{base_url}/server/get_test_results") as resp:
            results = await resp.json()
            print(f"總共執行了 {len(results['data'])} 個測試")

if __name__ == "__main__":
    asyncio.run(automated_workflow())
```

#### 2. 定時任務

```python
import schedule
import time

def run_daily_tests():
    """每日測試任務"""
    print("開始執行每日測試...")
    # 調用您的測試邏輯
    asyncio.run(automated_workflow())

# 設置定時任務
schedule.every().day.at("09:00").do(run_daily_tests)
schedule.every().monday.at("08:00").do(run_weekly_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 監控和警報

#### 1. 系統監控

```python
import psutil
import time

def monitor_system():
    """監控系統資源"""
    while True:
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 內存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 磁盤使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        print(f"CPU: {cpu_percent}%, 內存: {memory_percent}%, 磁盤: {disk_percent:.1f}%")
        
        # 警報條件
        if cpu_percent > 80 or memory_percent > 80 or disk_percent > 90:
            send_alert(f"系統資源警報: CPU={cpu_percent}%, 內存={memory_percent}%, 磁盤={disk_percent:.1f}%")
        
        time.sleep(60)

def send_alert(message):
    """發送警報"""
    # 實現您的警報邏輯（郵件、Slack、微信等）
    print(f"🚨 警報: {message}")
```

## 🔍 故障排除

### 常見問題和解決方案

#### 1. 安裝問題

**問題**: `pip install` 失敗

```bash
# 解決方案 1: 升級 pip
python3 -m pip install --upgrade pip

# 解決方案 2: 使用國內鏡像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ package_name

# 解決方案 3: 清理緩存
pip cache purge
```

**問題**: Playwright 瀏覽器安裝失敗

```bash
# 解決方案 1: 手動安裝
playwright install --with-deps chromium

# 解決方案 2: 使用系統包管理器
sudo apt install chromium-browser  # Ubuntu
brew install chromium              # macOS

# 解決方案 3: 設置環境變量
export PLAYWRIGHT_BROWSERS_PATH=/path/to/browsers
```

#### 2. 配置問題

**問題**: 配置文件語法錯誤

```bash
# 驗證 TOML 語法
python3 -c "import toml; toml.load('config.toml')"

# 常見錯誤修復
# 1. 字符串必須使用引號
app_url = "https://example.com"  # 正確
app_url = https://example.com    # 錯誤

# 2. 布爾值不使用引號
debug = true   # 正確
debug = "true" # 錯誤

# 3. 數組格式
allowed_extensions = [".pdf", ".png"]  # 正確
allowed_extensions = .pdf, .png        # 錯誤
```

#### 3. 運行時問題

**問題**: 端口被佔用

```bash
# 查找佔用端口的進程
lsof -i :5000
netstat -tulpn | grep :5000

# 終止進程
kill -9 <PID>

# 或修改配置使用其他端口
```

**問題**: 權限錯誤

```bash
# 檢查文件權限
ls -la config.toml

# 修復權限
chmod 644 config.toml
chmod 755 powerautomation_local_mcp.py

# 檢查目錄權限
chmod 755 /path/to/data/directory
```

#### 4. 網絡問題

**問題**: 無法連接到 Manus

```bash
# 測試網絡連接
curl -I https://manus.im

# 檢查 DNS 解析
nslookup manus.im

# 測試代理設置
export https_proxy=http://proxy.example.com:8080
```

**問題**: API 請求超時

```toml
# 增加超時時間
[server]
request_timeout = 60

[manus]
session_timeout = 7200
```

### 調試技巧

#### 1. 啟用詳細日誌

```toml
[logging]
level = "DEBUG"
console_enabled = true
file_enabled = true
```

#### 2. 使用調試模式

```bash
# 設置調試環境變量
export POWERAUTOMATION_DEBUG=true
export POWERAUTOMATION_LOG_LEVEL=DEBUG

# 運行程序
python3 powerautomation_local_mcp.py
```

#### 3. 檢查系統狀態

```bash
# 檢查進程
ps aux | grep powerautomation

# 檢查端口
netstat -tulpn | grep 5000

# 檢查日誌
tail -f logs/powerautomation.log
```

#### 4. 測試 API 端點

```bash
# 測試基本連接
curl http://localhost:5000/api/status

# 測試具體功能
curl -X POST http://localhost:5000/api/server/manus_login \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## 💡 最佳實踐

### 安全最佳實踐

#### 1. 憑證管理

```bash
# 使用環境變量存儲敏感信息
export MANUS_EMAIL="your-email@example.com"
export MANUS_PASSWORD="your-secure-password"

# 使用加密的配置文件
gpg --symmetric config.toml
gpg --decrypt config.toml.gpg > config.toml
```

#### 2. 網絡安全

```toml
[server]
# 僅綁定本地地址（生產環境）
host = "127.0.0.1"

# 使用 HTTPS（生產環境）
ssl_enabled = true
ssl_cert = "/path/to/cert.pem"
ssl_key = "/path/to/key.pem"
```

#### 3. 訪問控制

```python
# 實施 API 密鑰認證
API_KEYS = ["your-secret-api-key"]

def require_api_key(f):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key not in API_KEYS:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

### 性能最佳實踐

#### 1. 資源優化

```toml
[automation]
# 使用無頭模式提高性能
headless = true

# 限制並行測試數量
parallel_tests = 2

[storage]
# 啟用壓縮節省空間
compression_enabled = true

# 定期清理舊文件
cleanup_days = 7
```

#### 2. 緩存策略

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_cached_data(key):
    """緩存數據獲取"""
    # 實際的數據獲取邏輯
    return expensive_operation(key)

# 時間基礎的緩存
cache_timeout = 300  # 5分鐘
cache_data = {}

def get_data_with_timeout(key):
    now = time.time()
    if key in cache_data:
        data, timestamp = cache_data[key]
        if now - timestamp < cache_timeout:
            return data
    
    # 獲取新數據
    data = fetch_new_data(key)
    cache_data[key] = (data, now)
    return data
```

### 維護最佳實踐

#### 1. 定期備份

```bash
#!/bin/bash
# backup.sh - 自動備份腳本

BACKUP_DIR="/backup/powerautomation"
DATE=$(date +%Y%m%d_%H%M%S)

# 創建備份目錄
mkdir -p "$BACKUP_DIR"

# 備份配置文件
cp config.toml "$BACKUP_DIR/config_$DATE.toml"

# 備份數據目錄
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" data/

# 備份日誌
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/

# 清理舊備份（保留30天）
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.toml" -mtime +30 -delete

echo "備份完成: $DATE"
```

#### 2. 監控腳本

```bash
#!/bin/bash
# monitor.sh - 監控腳本

SERVICE_URL="http://localhost:5000/api/status"
LOG_FILE="/var/log/powerautomation_monitor.log"

# 檢查服務狀態
if curl -f -s "$SERVICE_URL" > /dev/null; then
    echo "$(date): 服務正常運行" >> "$LOG_FILE"
else
    echo "$(date): 服務異常，嘗試重啟" >> "$LOG_FILE"
    systemctl restart powerautomation
    
    # 發送警報
    echo "PowerAutomation 服務異常，已嘗試重啟" | mail -s "服務警報" admin@example.com
fi
```

#### 3. 日誌輪轉

```bash
# /etc/logrotate.d/powerautomation
/path/to/powerautomation/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload powerautomation
    endscript
}
```

### 開發最佳實踐

#### 1. 代碼結構

```python
# 使用類型提示
from typing import Dict, List, Optional, Union

async def process_data(
    data: Dict[str, Any], 
    options: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    處理數據的函數
    
    Args:
        data: 輸入數據
        options: 可選配置
        
    Returns:
        處理後的數據列表
        
    Raises:
        ValueError: 當數據格式不正確時
    """
    if not isinstance(data, dict):
        raise ValueError("數據必須是字典格式")
    
    # 處理邏輯
    result = []
    # ...
    
    return result
```

#### 2. 錯誤處理

```python
import logging
from functools import wraps

def handle_exceptions(default_return=None):
    """異常處理裝飾器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logging.error(f"函數 {func.__name__} 執行失敗: {e}")
                return default_return
        return wrapper
    return decorator

@handle_exceptions(default_return=[])
async def risky_operation():
    """可能失敗的操作"""
    # 可能拋出異常的代碼
    pass
```

#### 3. 測試覆蓋

```python
import unittest
from unittest.mock import patch, MagicMock

class TestPowerAutomation(unittest.TestCase):
    
    def setUp(self):
        """測試初始化"""
        self.mcp_adapter = PowerAutomationLocalMCP("test_config.toml")
    
    @patch('requests.post')
    def test_api_call(self, mock_post):
        """測試 API 調用"""
        # 模擬響應
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # 執行測試
        result = self.mcp_adapter.call_api("/test")
        
        # 驗證結果
        self.assertTrue(result["success"])
        mock_post.assert_called_once()
    
    def tearDown(self):
        """測試清理"""
        # 清理測試數據
        pass
```

---

通過遵循這些安裝和使用指南，您應該能夠成功部署和使用 PowerAutomation Local MCP Adapter。如果遇到任何問題，請參考故障排除部分或聯繫技術支持。

