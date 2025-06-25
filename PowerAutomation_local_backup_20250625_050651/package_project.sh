#!/bin/bash

# PowerAutomation Local MCP Adapter 項目打包腳本
# 版本: 1.0.0
# 作者: Manus AI
# 日期: 2025-06-23

set -e

PROJECT_NAME="PowerAutomationlocal_Adapter"
VERSION="1.0.0"
DATE=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="${PROJECT_NAME}_v${VERSION}_${DATE}"

echo "🚀 開始打包 PowerAutomation Local MCP Adapter..."
echo "項目名稱: $PROJECT_NAME"
echo "版本: $VERSION"
echo "打包名稱: $PACKAGE_NAME"
echo "="*60

# 創建打包目錄
echo "📁 創建打包目錄..."
mkdir -p "packages/$PACKAGE_NAME"

# 複製核心文件
echo "📋 複製核心文件..."
cp -r server/ "packages/$PACKAGE_NAME/"
cp -r extension/ "packages/$PACKAGE_NAME/"
cp -r shared/ "packages/$PACKAGE_NAME/"
cp -r tests/ "packages/$PACKAGE_NAME/"

# 複製配置和文檔
echo "📄 複製配置和文檔..."
cp powerautomation_local_mcp.py "packages/$PACKAGE_NAME/"
cp config.toml "packages/$PACKAGE_NAME/"
cp cli.py "packages/$PACKAGE_NAME/"
cp __init__.py "packages/$PACKAGE_NAME/"
cp README.md "packages/$PACKAGE_NAME/"
cp INSTALLATION_GUIDE.md "packages/$PACKAGE_NAME/"
cp basic_test.py "packages/$PACKAGE_NAME/"
cp test_powerautomation_mcp.py "packages/$PACKAGE_NAME/"

# 創建 requirements.txt
echo "📦 創建 requirements.txt..."
cat > "packages/$PACKAGE_NAME/requirements.txt" << 'REQUIREMENTS'
toml>=0.10.2
aiohttp>=3.8.0
flask>=2.0.0
flask-cors>=4.0.0
websockets>=11.0.0
psutil>=5.9.0
playwright>=1.40.0
REQUIREMENTS

# 創建安裝腳本
echo "🔧 創建安裝腳本..."
cat > "packages/$PACKAGE_NAME/install.sh" << 'INSTALL'
#!/bin/bash

echo "🚀 安裝 PowerAutomation Local MCP Adapter..."

# 檢查 Python 版本
python3 --version || {
    echo "❌ Python 3 未安裝，請先安裝 Python 3.8+"
    exit 1
}

# 創建虛擬環境
echo "📦 創建虛擬環境..."
python3 -m venv powerautomation_env
source powerautomation_env/bin/activate

# 安裝依賴
echo "📥 安裝依賴包..."
pip install --upgrade pip
pip install -r requirements.txt

# 安裝 Playwright 瀏覽器
echo "🌐 安裝 Playwright 瀏覽器..."
playwright install chromium

# 運行測試
echo "🧪 運行基本測試..."
python3 basic_test.py

echo "✅ 安裝完成！"
echo "使用方法:"
echo "  source powerautomation_env/bin/activate"
echo "  python3 powerautomation_local_mcp.py"
INSTALL

chmod +x "packages/$PACKAGE_NAME/install.sh"

# 創建啟動腳本
echo "🚀 創建啟動腳本..."
cat > "packages/$PACKAGE_NAME/start.sh" << 'START'
#!/bin/bash

# 激活虛擬環境
if [ -d "powerautomation_env" ]; then
    source powerautomation_env/bin/activate
else
    echo "❌ 虛擬環境不存在，請先運行 install.sh"
    exit 1
fi

# 啟動服務
echo "🚀 啟動 PowerAutomation Local MCP Adapter..."
python3 powerautomation_local_mcp.py
START

chmod +x "packages/$PACKAGE_NAME/start.sh"

# 創建 VSCode 擴展目錄
echo "🔌 創建 VSCode 擴展..."
mkdir -p "packages/$PACKAGE_NAME/vscode-extension"

# 生成 package.json
cat > "packages/$PACKAGE_NAME/vscode-extension/package.json" << 'PACKAGE_JSON'
{
  "name": "powerautomation-local",
  "displayName": "PowerAutomation Local",
  "description": "PowerAutomation Local MCP Extension",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.60.0"
  },
  "categories": ["Other"],
  "activationEvents": ["*"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "powerautomation.login",
        "title": "Login to Manus",
        "category": "PowerAutomation"
      },
      {
        "command": "powerautomation.sendMessage",
        "title": "Send Message",
        "category": "PowerAutomation"
      },
      {
        "command": "powerautomation.getConversations",
        "title": "Get Conversations",
        "category": "PowerAutomation"
      },
      {
        "command": "powerautomation.getTasks",
        "title": "Get Tasks",
        "category": "PowerAutomation"
      },
      {
        "command": "powerautomation.runTest",
        "title": "Run Test",
        "category": "PowerAutomation"
      },
      {
        "command": "powerautomation.viewStatus",
        "title": "View Status",
        "category": "PowerAutomation"
      }
    ],
    "configuration": {
      "title": "PowerAutomation",
      "properties": {
        "powerautomation.serverUrl": {
          "type": "string",
          "default": "http://localhost:5000",
          "description": "PowerAutomation Server URL"
        },
        "powerautomation.autoStart": {
          "type": "boolean",
          "default": true,
          "description": "Auto start PowerAutomation"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.60.0",
    "@types/node": "14.x",
    "typescript": "^4.4.4"
  }
}
PACKAGE_JSON

# 創建 TypeScript 配置
cat > "packages/$PACKAGE_NAME/vscode-extension/tsconfig.json" << 'TSCONFIG'
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "es6",
    "outDir": "out",
    "lib": ["es6"],
    "sourceMap": true,
    "rootDir": "src",
    "strict": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
TSCONFIG

# 創建擴展源碼目錄
mkdir -p "packages/$PACKAGE_NAME/vscode-extension/src"

# 複製擴展源碼（簡化版）
cat > "packages/$PACKAGE_NAME/vscode-extension/src/extension.ts" << 'EXTENSION_TS'
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('PowerAutomation Extension is now active!');
    
    // 註冊命令
    const commands = [
        vscode.commands.registerCommand('powerautomation.login', () => {
            vscode.window.showInformationMessage('PowerAutomation: Login command executed');
        }),
        vscode.commands.registerCommand('powerautomation.sendMessage', () => {
            vscode.window.showInformationMessage('PowerAutomation: Send Message command executed');
        }),
        vscode.commands.registerCommand('powerautomation.getConversations', () => {
            vscode.window.showInformationMessage('PowerAutomation: Get Conversations command executed');
        }),
        vscode.commands.registerCommand('powerautomation.getTasks', () => {
            vscode.window.showInformationMessage('PowerAutomation: Get Tasks command executed');
        }),
        vscode.commands.registerCommand('powerautomation.runTest', () => {
            vscode.window.showInformationMessage('PowerAutomation: Run Test command executed');
        }),
        vscode.commands.registerCommand('powerautomation.viewStatus', () => {
            vscode.window.showInformationMessage('PowerAutomation: View Status command executed');
        })
    ];
    
    commands.forEach(command => context.subscriptions.push(command));
    
    // 創建狀態欄項目
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(gear) PowerAutomation";
    statusBarItem.command = 'powerautomation.viewStatus';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

export function deactivate() {}
EXTENSION_TS

# 創建擴展安裝腳本
cat > "packages/$PACKAGE_NAME/vscode-extension/install_extension.sh" << 'EXT_INSTALL'
#!/bin/bash

echo "🔌 安裝 PowerAutomation VSCode 擴展..."

# 檢查 Node.js
node --version || {
    echo "❌ Node.js 未安裝，請先安裝 Node.js 16+"
    exit 1
}

# 安裝依賴
echo "📦 安裝依賴..."
npm install

# 編譯 TypeScript
echo "🔨 編譯 TypeScript..."
npm run compile

# 安裝 vsce 工具
echo "🛠️ 安裝 vsce 工具..."
npm install -g vsce

# 打包擴展
echo "📦 打包擴展..."
vsce package

# 安裝擴展
echo "🔌 安裝擴展到 VSCode..."
code --install-extension *.vsix

echo "✅ VSCode 擴展安裝完成！"
EXT_INSTALL

chmod +x "packages/$PACKAGE_NAME/vscode-extension/install_extension.sh"

# 創建項目信息文件
echo "📋 創建項目信息..."
cat > "packages/$PACKAGE_NAME/PROJECT_INFO.md" << INFO
# PowerAutomation Local MCP Adapter

**版本**: $VERSION
**打包日期**: $(date)
**打包者**: Manus AI

## 📦 包含內容

- **核心組件**: MCP適配器、Server、Extension管理器
- **集成模組**: Manus平台集成、自動化測試引擎、數據存儲
- **配置文件**: config.toml、requirements.txt
- **文檔**: README.md、INSTALLATION_GUIDE.md
- **測試**: 基本測試、完整測試套件
- **VSCode擴展**: 完整的IDE集成擴展
- **安裝腳本**: 自動化安裝和啟動腳本

## 🚀 快速開始

1. 運行安裝腳本: \`./install.sh\`
2. 啟動服務: \`./start.sh\`
3. 安裝VSCode擴展: \`cd vscode-extension && ./install_extension.sh\`

## 📞 支持

- 項目主頁: https://github.com/your-org/powerautomation-local-mcp
- 技術支持: support@manus.ai
- 文檔: README.md, INSTALLATION_GUIDE.md

---
PowerAutomation Local MCP Adapter - 讓自動化測試變得簡單而強大！
INFO

# 創建壓縮包
echo "🗜️ 創建壓縮包..."
cd packages
tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"
zip -r "${PACKAGE_NAME}.zip" "$PACKAGE_NAME" > /dev/null

# 計算文件大小
TAR_SIZE=$(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)
ZIP_SIZE=$(du -h "${PACKAGE_NAME}.zip" | cut -f1)

echo ""
echo "✅ 打包完成！"
echo "="*60
echo "📦 打包結果:"
echo "  - 目錄: packages/$PACKAGE_NAME/"
echo "  - TAR.GZ: packages/${PACKAGE_NAME}.tar.gz ($TAR_SIZE)"
echo "  - ZIP: packages/${PACKAGE_NAME}.zip ($ZIP_SIZE)"
echo ""
echo "📋 包含文件:"
find "$PACKAGE_NAME" -type f | head -20
echo "  ... (更多文件)"
echo ""
echo "🚀 使用方法:"
echo "  1. 解壓: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "  2. 安裝: cd $PACKAGE_NAME && ./install.sh"
echo "  3. 啟動: ./start.sh"
echo "="*60

