import { useState, useEffect } from 'react'

const CodeEditor = ({ file, repository, onClose }) => {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [isModified, setIsModified] = useState(false)
  const [language, setLanguage] = useState('text')

  // 模擬文件內容
  const getFileContent = (file, repo) => {
    const extension = file.name.split('.').pop()?.toLowerCase()
    
    if (extension === 'py') {
      return `# ${file.name}
# 來自倉庫: ${repo}
# 路徑: ${file.path}

"""
${file.name} - Python 模組
這是一個示例 Python 文件，展示 Claude Code SDK 的代碼編輯功能
"""

import os
import sys
from typing import Dict, List, Optional

class ${file.name.replace('.py', '').replace('_', '').replace('-', '')}:
    """
    ${file.name} 的主要類別
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 ${file.name.replace('.py', '')} 實例
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        初始化組件
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 初始化邏輯
            self.initialized = True
            return True
        except Exception as e:
            print(f"初始化失敗: {e}")
            return False
    
    def process(self, data: List[Dict]) -> List[Dict]:
        """
        處理數據
        
        Args:
            data: 輸入數據列表
            
        Returns:
            List[Dict]: 處理後的數據
        """
        if not self.initialized:
            raise RuntimeError("組件尚未初始化")
        
        result = []
        for item in data:
            # 處理邏輯
            processed_item = self._process_item(item)
            result.append(processed_item)
        
        return result
    
    def _process_item(self, item: Dict) -> Dict:
        """
        處理單個項目
        
        Args:
            item: 單個數據項目
            
        Returns:
            Dict: 處理後的項目
        """
        # 實現具體的處理邏輯
        return {
            **item,
            'processed': True,
            'timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """
        獲取當前時間戳
        
        Returns:
            str: ISO 格式的時間戳
        """
        from datetime import datetime
        return datetime.now().isoformat()

# 使用示例
if __name__ == "__main__":
    # 創建實例
    processor = ${file.name.replace('.py', '').replace('_', '').replace('-', '')}()
    
    # 初始化
    if processor.initialize():
        print("組件初始化成功")
        
        # 處理示例數據
        sample_data = [
            {"id": 1, "name": "示例1"},
            {"id": 2, "name": "示例2"}
        ]
        
        result = processor.process(sample_data)
        print(f"處理結果: {result}")
    else:
        print("組件初始化失敗")
`
    } else if (extension === 'js' || extension === 'jsx') {
      return `// ${file.name}
// 來自倉庫: ${repo}
// 路徑: ${file.path}

import React, { useState, useEffect } from 'react'

/**
 * ${file.name} - React 組件
 * 這是一個示例 React 組件，展示 Claude Code SDK 的代碼編輯功能
 */
const ${file.name.replace('.jsx', '').replace('.js', '').replace('-', '').replace('_', '')} = ({ 
  data = [], 
  onUpdate = () => {},
  className = '' 
}) => {
  const [items, setItems] = useState(data)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    // 組件掛載時的初始化邏輯
    console.log('${file.name} 組件已掛載')
    
    // 如果有初始數據，設置到狀態中
    if (data.length > 0) {
      setItems(data)
    }
    
    return () => {
      // 清理邏輯
      console.log('${file.name} 組件即將卸載')
    }
  }, [data])

  const handleItemClick = (item, index) => {
    console.log('點擊項目:', item, '索引:', index)
    
    // 觸發父組件的更新回調
    onUpdate(item, index)
  }

  const handleAddItem = () => {
    const newItem = {
      id: Date.now(),
      name: \`新項目 \${items.length + 1}\`,
      created: new Date().toISOString()
    }
    
    setItems(prev => [...prev, newItem])
    onUpdate(newItem, items.length)
  }

  const handleRemoveItem = (index) => {
    const updatedItems = items.filter((_, i) => i !== index)
    setItems(updatedItems)
    onUpdate(null, index, 'remove')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin text-blue-500 text-2xl">⚡</div>
        <span className="ml-2">載入中...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <strong>錯誤:</strong> {error}
      </div>
    )
  }

  return (
    <div className={\`\${className} p-4\`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">
          ${file.name.replace('.jsx', '').replace('.js', '')} 組件
        </h2>
        <button
          onClick={handleAddItem}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        >
          添加項目
        </button>
      </div>
      
      <div className="space-y-2">
        {items.map((item, index) => (
          <div
            key={item.id || index}
            className="flex items-center justify-between p-3 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
          >
            <div
              className="flex-1 cursor-pointer"
              onClick={() => handleItemClick(item, index)}
            >
              <div className="font-medium">{item.name}</div>
              {item.created && (
                <div className="text-sm text-gray-500">
                  創建時間: {new Date(item.created).toLocaleString('zh-TW')}
                </div>
              )}
            </div>
            <button
              onClick={() => handleRemoveItem(index)}
              className="text-red-500 hover:text-red-700 ml-2"
            >
              刪除
            </button>
          </div>
        ))}
      </div>
      
      {items.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          暫無項目，點擊上方按鈕添加
        </div>
      )}
    </div>
  )
}

export default ${file.name.replace('.jsx', '').replace('.js', '').replace('-', '').replace('_', '')}
`
    } else if (extension === 'md') {
      return `# ${file.name}

> 來自倉庫: ${repo}  
> 路徑: ${file.path}

## 概述

這是 ${file.name} 文件，展示 Claude Code SDK 的 Markdown 編輯功能。

## 功能特色

### ✨ 主要功能

- **功能 1**: 描述第一個主要功能
- **功能 2**: 描述第二個主要功能  
- **功能 3**: 描述第三個主要功能

### 🔧 技術規格

| 項目 | 說明 |
|------|------|
| 語言 | Markdown |
| 編碼 | UTF-8 |
| 版本 | 1.0.0 |

## 安裝說明

\`\`\`bash
# 克隆倉庫
git clone ${repo}

# 進入目錄
cd ${file.path.split('/')[0]}

# 安裝依賴
npm install
\`\`\`

## 使用方法

### 基本用法

\`\`\`javascript
// 導入模組
import { Component } from './${file.path}'

// 創建實例
const instance = new Component({
  option1: 'value1',
  option2: 'value2'
})

// 使用功能
instance.execute()
\`\`\`

### 進階配置

\`\`\`json
{
  "config": {
    "mode": "production",
    "debug": false,
    "features": {
      "feature1": true,
      "feature2": false
    }
  }
}
\`\`\`

## API 文檔

### 方法列表

#### \`initialize(options)\`

初始化組件

**參數:**
- \`options\` (Object): 配置選項

**返回值:**
- \`Promise<boolean>\`: 初始化是否成功

#### \`process(data)\`

處理數據

**參數:**
- \`data\` (Array): 要處理的數據

**返回值:**
- \`Array\`: 處理後的數據

## 範例

### 完整範例

\`\`\`javascript
import { ${file.name.replace('.md', '')} } from './${file.path}'

async function example() {
  const processor = new ${file.name.replace('.md', '')}()
  
  // 初始化
  const initialized = await processor.initialize({
    mode: 'development',
    debug: true
  })
  
  if (initialized) {
    // 處理數據
    const result = await processor.process([
      { id: 1, name: '項目1' },
      { id: 2, name: '項目2' }
    ])
    
    console.log('處理結果:', result)
  }
}

example()
\`\`\`

## 注意事項

> ⚠️ **重要提醒**
> 
> 1. 請確保在使用前正確初始化組件
> 2. 建議在生產環境中關閉 debug 模式
> 3. 定期檢查更新和安全補丁

## 更新日誌

### v1.0.0 (2024-06-27)
- 🎉 初始版本發布
- ✨ 添加基本功能
- 📝 完善文檔

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 本倉庫
2. 創建功能分支
3. 提交變更
4. 發起 Pull Request

## 授權

MIT License - 詳見 [LICENSE](./LICENSE) 文件

---

**最後更新**: ${new Date().toLocaleDateString('zh-TW')}  
**維護者**: Claude Code SDK Team
`
    } else if (extension === 'json') {
      return `{
  "name": "${file.name}",
  "repository": "${repo}",
  "path": "${file.path}",
  "version": "1.0.0",
  "description": "這是一個示例 JSON 配置文件，展示 Claude Code SDK 的 JSON 編輯功能",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "build": "webpack --mode production",
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  },
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5",
    "dotenv": "^16.0.0",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "nodemon": "^2.0.20",
    "jest": "^29.0.0",
    "eslint": "^8.0.0",
    "prettier": "^2.7.0",
    "webpack": "^5.74.0"
  },
  "config": {
    "port": 3000,
    "host": "localhost",
    "database": {
      "type": "mongodb",
      "url": "mongodb://localhost:27017/myapp",
      "options": {
        "useNewUrlParser": true,
        "useUnifiedTopology": true
      }
    },
    "features": {
      "authentication": true,
      "logging": true,
      "caching": false,
      "analytics": true
    },
    "api": {
      "version": "v1",
      "prefix": "/api",
      "rateLimit": {
        "windowMs": 900000,
        "max": 100
      }
    }
  },
  "keywords": [
    "nodejs",
    "express",
    "api",
    "claude-code-sdk",
    "smartui"
  ],
  "author": {
    "name": "Claude Code SDK Team",
    "email": "team@claudecode.dev",
    "url": "https://claudecode.dev"
  },
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/${repo}.git"
  },
  "bugs": {
    "url": "https://github.com/${repo}/issues"
  },
  "homepage": "https://github.com/${repo}#readme",
  "engines": {
    "node": ">=16.0.0",
    "npm": ">=8.0.0"
  }
}`
    } else {
      return `# ${file.name}
# 來自倉庫: ${repo}
# 路徑: ${file.path}

這是一個示例文件，展示 Claude Code SDK 的代碼編輯功能。

文件類型: ${extension?.toUpperCase() || '未知'}
創建時間: ${new Date().toLocaleString('zh-TW')}

您可以在此編輯文件內容，所有變更都會被 Claude Code SDK 追蹤和分析。

功能特色:
- 語法高亮
- 自動完成
- 錯誤檢測
- 智能重構建議
- 實時協作

使用 Ctrl+S 保存文件
使用 Ctrl+Z 撤銷操作
使用 Ctrl+Y 重做操作
`
    }
  }

  useEffect(() => {
    const loadContent = async () => {
      setLoading(true)
      
      // 模擬從 GitHub API 獲取文件內容
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const fileContent = getFileContent(file, repository)
      setContent(fileContent)
      
      // 設置語言模式
      const ext = file.name.split('.').pop()?.toLowerCase()
      const langMap = {
        'py': 'python',
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'json': 'json',
        'md': 'markdown',
        'html': 'html',
        'css': 'css',
        'scss': 'scss',
        'yml': 'yaml',
        'yaml': 'yaml'
      }
      setLanguage(langMap[ext] || 'text')
      
      setLoading(false)
    }

    if (file) {
      loadContent()
    }
  }, [file, repository])

  const handleContentChange = (e) => {
    setContent(e.target.value)
    setIsModified(true)
  }

  const handleSave = () => {
    // 模擬保存文件
    console.log('保存文件:', file.path, content)
    setIsModified(false)
    
    // 顯示保存成功提示
    alert(`文件 ${file.name} 已保存`)
  }

  const handleKeyDown = (e) => {
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault()
      handleSave()
    }
  }

  if (loading) {
    return (
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 h-full">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin text-purple-400 text-2xl">⚡</div>
          <span className="ml-2 text-slate-300">載入文件內容中...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 h-full flex flex-col">
      {/* 編輯器標題欄 */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-600">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">📝</span>
          <div>
            <h2 className="text-white text-lg font-semibold">{file.name}</h2>
            <p className="text-slate-400 text-sm">{file.path}</p>
          </div>
          {isModified && (
            <span className="bg-orange-500 text-white px-2 py-1 rounded text-xs">
              未保存
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 bg-slate-700 px-2 py-1 rounded">
            {language.toUpperCase()}
          </span>
          <button
            onClick={handleSave}
            disabled={!isModified}
            className="bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-3 py-1 rounded text-sm"
          >
            💾 保存
          </button>
          <button
            onClick={onClose}
            className="bg-slate-600 hover:bg-slate-700 text-white px-3 py-1 rounded text-sm"
          >
            ✕ 關閉
          </button>
        </div>
      </div>

      {/* 編輯器工具欄 */}
      <div className="flex items-center space-x-4 mb-4 text-sm text-slate-400">
        <span>第 1 行, 第 1 列</span>
        <span>UTF-8</span>
        <span>LF</span>
        <span>{content.length} 字符</span>
        <span>{content.split('\n').length} 行</span>
      </div>

      {/* 代碼編輯區域 */}
      <div className="flex-1 relative">
        <textarea
          value={content}
          onChange={handleContentChange}
          onKeyDown={handleKeyDown}
          className="w-full h-full bg-slate-900 text-slate-100 font-mono text-sm p-4 rounded border border-slate-600 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="開始編輯您的代碼..."
          spellCheck={false}
        />
        
        {/* 行號 */}
        <div className="absolute left-0 top-0 bottom-0 w-12 bg-slate-800 border-r border-slate-600 p-4 text-slate-500 text-sm font-mono pointer-events-none">
          {content.split('\n').map((_, index) => (
            <div key={index} className="leading-5">
              {index + 1}
            </div>
          ))}
        </div>
      </div>

      {/* 狀態欄 */}
      <div className="mt-4 pt-4 border-t border-slate-600 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-4">
          <span>🔗 {repository}</span>
          <span>📁 {file.path}</span>
          <span>🕒 {new Date().toLocaleTimeString('zh-TW')}</span>
        </div>
        <div className="flex items-center space-x-2">
          <span>Ctrl+S 保存</span>
          <span>Ctrl+Z 撤銷</span>
        </div>
      </div>
    </div>
  )
}

export default CodeEditor

