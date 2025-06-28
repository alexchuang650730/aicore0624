import { useState, useEffect } from 'react'

const GitHubFileExplorer = ({ onFileSelect, onRepositoryChange }) => {
  const [fileStructure, setFileStructure] = useState([])
  const [expandedFolders, setExpandedFolders] = useState(new Set(['root']))
  const [loading, setLoading] = useState(true)
  const [selectedRepo, setSelectedRepo] = useState('alexchuang650730/aicore0624')
  const [showRepoSelector, setShowRepoSelector] = useState(false)

  // 可選擇的倉庫列表
  const availableRepos = [
    {
      name: 'alexchuang650730/aicore0624',
      displayName: 'aicore0624',
      description: 'PowerAutomation - AICore 3.0 智能自動化平台',
      branch: 'main'
    },
    {
      name: 'alexchuang650730/aicore0624',
      displayName: 'aicore0624 (smartui)',
      description: 'SmartUI Fusion v1.0.0 分支',
      branch: 'smartui'
    },
    {
      name: 'microsoft/vscode',
      displayName: 'vscode',
      description: 'Visual Studio Code',
      branch: 'main'
    },
    {
      name: 'facebook/react',
      displayName: 'react',
      description: 'React JavaScript Library',
      branch: 'main'
    }
  ]

  // 根據不同倉庫的文件結構
  const getFileStructureForRepo = (repoName, branch) => {
    if (repoName === 'alexchuang650730/aicore0624') {
      if (branch === 'smartui') {
        return [
          {
            name: 'SmartUI',
            type: 'folder',
            path: 'SmartUI',
            children: [
              { name: 'components', type: 'folder', path: 'SmartUI/components' },
              { name: 'fusion', type: 'folder', path: 'SmartUI/fusion' },
              { name: 'ui-engine', type: 'folder', path: 'SmartUI/ui-engine' },
              { name: 'README.md', type: 'file', path: 'SmartUI/README.md' }
            ]
          },
          {
            name: 'Claude-Integration',
            type: 'folder',
            path: 'Claude-Integration',
            children: [
              { name: 'sdk', type: 'folder', path: 'Claude-Integration/sdk' },
              { name: 'adapters', type: 'folder', path: 'Claude-Integration/adapters' },
              { name: 'config.json', type: 'file', path: 'Claude-Integration/config.json' }
            ]
          },
          { name: 'package.json', type: 'file', path: 'package.json' },
          { name: 'README.md', type: 'file', path: 'README.md' }
        ]
      } else {
        return [
          {
            name: 'PowerAutomation',
            type: 'folder',
            path: 'PowerAutomation',
            children: [
              { name: 'components', type: 'folder', path: 'PowerAutomation/components' },
              { name: 'servers', type: 'folder', path: 'PowerAutomation/servers' },
              { name: 'tools', type: 'folder', path: 'PowerAutomation/tools' },
              { name: 'workflows', type: 'folder', path: 'PowerAutomation/workflows' },
              { name: '__init__.py', type: 'file', path: 'PowerAutomation/__init__.py' },
              { name: 'main.py', type: 'file', path: 'PowerAutomation/main.py' }
            ]
          },
          {
            name: 'development',
            type: 'folder',
            path: 'development',
            children: [
              { name: 'src', type: 'folder', path: 'development/src' },
              { name: 'tests', type: 'folder', path: 'development/tests' },
              { name: 'docs', type: 'folder', path: 'development/docs' },
              { name: 'package.json', type: 'file', path: 'development/package.json' }
            ]
          },
          {
            name: 'docs',
            type: 'folder',
            path: 'docs',
            children: [
              { name: 'api', type: 'folder', path: 'docs/api' },
              { name: 'user-guide', type: 'folder', path: 'docs/user-guide' },
              { name: 'README.md', type: 'file', path: 'docs/README.md' },
              { name: 'CHANGELOG.md', type: 'file', path: 'docs/CHANGELOG.md' }
            ]
          },
          { name: '.gitignore', type: 'file', path: '.gitignore' },
          { name: 'README.md', type: 'file', path: 'README.md' },
          { name: 'requirements.txt', type: 'file', path: 'requirements.txt' }
        ]
      }
    } else if (repoName === 'microsoft/vscode') {
      return [
        {
          name: 'src',
          type: 'folder',
          path: 'src',
          children: [
            { name: 'vs', type: 'folder', path: 'src/vs' },
            { name: 'bootstrap.js', type: 'file', path: 'src/bootstrap.js' }
          ]
        },
        {
          name: 'extensions',
          type: 'folder',
          path: 'extensions',
          children: [
            { name: 'typescript', type: 'folder', path: 'extensions/typescript' },
            { name: 'python', type: 'folder', path: 'extensions/python' }
          ]
        },
        { name: 'package.json', type: 'file', path: 'package.json' },
        { name: 'README.md', type: 'file', path: 'README.md' }
      ]
    } else if (repoName === 'facebook/react') {
      return [
        {
          name: 'packages',
          type: 'folder',
          path: 'packages',
          children: [
            { name: 'react', type: 'folder', path: 'packages/react' },
            { name: 'react-dom', type: 'folder', path: 'packages/react-dom' }
          ]
        },
        {
          name: 'scripts',
          type: 'folder',
          path: 'scripts',
          children: [
            { name: 'build.js', type: 'file', path: 'scripts/build.js' },
            { name: 'test.js', type: 'file', path: 'scripts/test.js' }
          ]
        },
        { name: 'package.json', type: 'file', path: 'package.json' },
        { name: 'README.md', type: 'file', path: 'README.md' }
      ]
    }
    return []
  }

  useEffect(() => {
    const loadFileStructure = async () => {
      setLoading(true)
      await new Promise(resolve => setTimeout(resolve, 800))
      
      const currentRepo = availableRepos.find(repo => repo.name === selectedRepo)
      const structure = getFileStructureForRepo(selectedRepo, currentRepo?.branch || 'main')
      setFileStructure(structure)
      setLoading(false)
    }

    loadFileStructure()
  }, [selectedRepo])

  const handleRepoChange = (repoName) => {
    setSelectedRepo(repoName)
    setShowRepoSelector(false)
    setExpandedFolders(new Set(['root']))
    onRepositoryChange && onRepositoryChange(repoName)
  }

  const toggleFolder = (path) => {
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedFolders(newExpanded)
  }

  const handleFileClick = (file) => {
    if (file.type === 'file') {
      onFileSelect && onFileSelect(file, selectedRepo)
    } else {
      toggleFolder(file.path)
    }
  }

  const renderFileTree = (files, level = 0) => {
    return files.map((file, index) => (
      <div key={`${file.path}-${index}`}>
        <div
          className={`flex items-center py-1 hover:bg-slate-700 rounded px-2 cursor-pointer transition-colors ${
            level > 0 ? `ml-${level * 4}` : ''
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => handleFileClick(file)}
        >
          <span className="mr-2 text-sm">
            {file.type === 'folder' ? (
              expandedFolders.has(file.path) ? '📂' : '📁'
            ) : (
              getFileIcon(file.name)
            )}
          </span>
          <span className="text-sm text-slate-300 hover:text-white truncate">
            {file.name}
          </span>
          {file.type === 'folder' && (
            <span className="ml-auto text-xs text-slate-500 flex-shrink-0">
              {file.children?.length || 0}
            </span>
          )}
        </div>
        
        {file.type === 'folder' && 
         expandedFolders.has(file.path) && 
         file.children && 
         renderFileTree(file.children, level + 1)}
      </div>
    ))
  }

  const getFileIcon = (fileName) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    const iconMap = {
      'py': '🐍',
      'js': '📜',
      'jsx': '⚛️',
      'ts': '📘',
      'tsx': '⚛️',
      'json': '📋',
      'md': '📝',
      'txt': '📄',
      'yml': '⚙️',
      'yaml': '⚙️',
      'env': '🔐',
      'sh': '🔧',
      'html': '🌐',
      'css': '🎨',
      'scss': '🎨',
      'png': '🖼️',
      'jpg': '🖼️',
      'jpeg': '🖼️',
      'gif': '🖼️',
      'svg': '🎨'
    }
    return iconMap[extension] || '📄'
  }

  const getCurrentRepo = () => {
    return availableRepos.find(repo => repo.name === selectedRepo)
  }

  if (loading) {
    return (
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-4 flex items-center">
          📁 項目瀏覽器
        </h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin text-purple-400 text-2xl">⚡</div>
          <span className="ml-2 text-slate-300">載入倉庫中...</span>
        </div>
      </div>
    )
  }

  const currentRepo = getCurrentRepo()

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold flex items-center">
          📁 項目瀏覽器
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded">
            GitHub 已連接
          </span>
        </div>
      </div>
      
      {/* 倉庫選擇器 */}
      <div className="mb-4">
        <div className="relative">
          <button
            onClick={() => setShowRepoSelector(!showRepoSelector)}
            className="w-full p-3 bg-slate-700/50 rounded-lg border border-slate-600 text-left hover:bg-slate-600/50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-blue-400">🔗</span>
                  <span className="text-sm text-white font-medium truncate">
                    {currentRepo?.displayName || '選擇倉庫'}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-1 truncate">
                  {currentRepo?.description}
                </div>
              </div>
              <span className="text-slate-400 ml-2 flex-shrink-0">
                {showRepoSelector ? '▲' : '▼'}
              </span>
            </div>
          </button>
          
          {showRepoSelector && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-slate-700 border border-slate-600 rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
              {availableRepos.map((repo, index) => (
                <button
                  key={index}
                  onClick={() => handleRepoChange(repo.name)}
                  className={`w-full p-3 text-left hover:bg-slate-600 transition-colors border-b border-slate-600 last:border-b-0 ${
                    selectedRepo === repo.name ? 'bg-slate-600' : ''
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-blue-400">📦</span>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm text-white font-medium truncate">
                        {repo.displayName}
                      </div>
                      <div className="text-xs text-slate-400 truncate">
                        {repo.description}
                      </div>
                      <div className="text-xs text-slate-500">
                        分支: {repo.branch}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        
        {/* 倉庫信息 */}
        <div className="mt-3 flex items-center space-x-4 text-xs text-slate-400">
          <span>📊 {currentRepo?.branch} 分支</span>
          <span>📁 {fileStructure.length} 項目</span>
          <span>🔄 即時同步</span>
        </div>
      </div>

      {/* 文件樹 */}
      <div className="space-y-1 text-sm text-slate-300 max-h-96 overflow-y-auto">
        {renderFileTree(fileStructure)}
      </div>
      
      {/* 快速操作 */}
      <div className="mt-4 pt-4 border-t border-slate-600">
        <h4 className="text-white text-sm font-medium mb-2">快速操作</h4>
        <div className="space-y-2">
          <button 
            className="w-full text-left text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded px-2 py-1 flex items-center space-x-2"
            onClick={() => window.open(`https://github.com/${selectedRepo}`, '_blank')}
          >
            <span>🔗</span>
            <span>在 GitHub 中打開</span>
          </button>
          <button 
            className="w-full text-left text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded px-2 py-1 flex items-center space-x-2"
            onClick={() => {
              setExpandedFolders(new Set())
              setTimeout(() => setExpandedFolders(new Set(['root'])), 100)
            }}
          >
            <span>🔄</span>
            <span>刷新文件樹</span>
          </button>
          <button 
            className="w-full text-left text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded px-2 py-1 flex items-center space-x-2"
            onClick={() => {
              const allPaths = new Set()
              const addAllPaths = (files) => {
                files.forEach(file => {
                  if (file.type === 'folder') {
                    allPaths.add(file.path)
                    if (file.children) {
                      addAllPaths(file.children)
                    }
                  }
                })
              }
              addAllPaths(fileStructure)
              setExpandedFolders(allPaths)
            }}
          >
            <span>📂</span>
            <span>展開所有文件夾</span>
          </button>
          <button 
            className="w-full text-left text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded px-2 py-1 flex items-center space-x-2"
            onClick={() => setExpandedFolders(new Set())}
          >
            <span>📁</span>
            <span>收起所有文件夾</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default GitHubFileExplorer

