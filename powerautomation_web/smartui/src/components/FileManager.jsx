import React, { useState, useEffect } from 'react'
import { usePermissions, PermissionGuard } from '../hooks/usePermissions'

// 文件类型图标映射
const FILE_ICONS = {
  // 代码文件
  '.js': '📄', '.jsx': '⚛️', '.ts': '📘', '.tsx': '⚛️',
  '.py': '🐍', '.java': '☕', '.cpp': '⚙️', '.c': '⚙️',
  '.html': '🌐', '.css': '🎨', '.scss': '🎨', '.sass': '🎨',
  '.json': '📋', '.xml': '📋', '.yaml': '📋', '.yml': '📋',
  
  // 文档文件
  '.md': '📝', '.txt': '📄', '.pdf': '📕', '.doc': '📘', '.docx': '📘',
  
  // 图片文件
  '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
  
  // 其他
  '.zip': '📦', '.tar': '📦', '.gz': '📦',
  'folder': '📁',
  'default': '📄'
}

// 获取文件图标
const getFileIcon = (fileName, isDirectory = false) => {
  if (isDirectory) return FILE_ICONS.folder
  const ext = fileName.toLowerCase().match(/\.[^.]+$/)
  return ext ? FILE_ICONS[ext[0]] || FILE_ICONS.default : FILE_ICONS.default
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 文件项组件
const FileItem = ({ file, onSelect, onDelete, onRename, isSelected }) => {
  const { hasPermission } = usePermissions()
  const [isRenaming, setIsRenaming] = useState(false)
  const [newName, setNewName] = useState(file.name)

  const handleRename = () => {
    if (newName.trim() && newName !== file.name) {
      onRename(file, newName.trim())
    }
    setIsRenaming(false)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleRename()
    } else if (e.key === 'Escape') {
      setNewName(file.name)
      setIsRenaming(false)
    }
  }

  return (
    <div 
      className={`flex items-center p-2 rounded-lg hover:bg-purple-500/10 cursor-pointer transition-colors ${
        isSelected ? 'bg-purple-500/20 border border-purple-500/30' : ''
      }`}
      onClick={() => onSelect(file)}
    >
      <div className="text-lg mr-3">
        {getFileIcon(file.name, file.isDirectory)}
      </div>
      
      <div className="flex-1 min-w-0">
        {isRenaming ? (
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onBlur={handleRename}
            onKeyPress={handleKeyPress}
            className="w-full px-2 py-1 bg-gray-800 border border-purple-500/30 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
            autoFocus
          />
        ) : (
          <div className="text-white text-sm font-medium truncate">
            {file.name}
          </div>
        )}
        
        <div className="flex items-center text-xs text-gray-400 mt-1">
          <span>{file.modifiedAt}</span>
          {!file.isDirectory && (
            <>
              <span className="mx-2">•</span>
              <span>{formatFileSize(file.size)}</span>
            </>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-1 ml-2">
        {/* 重命名按钮 */}
        <PermissionGuard permission="file_manage_limited" showMessage={false}>
          <button
            onClick={(e) => {
              e.stopPropagation()
              setIsRenaming(true)
            }}
            className="p-1 text-gray-400 hover:text-purple-400 transition-colors"
            title="重命名"
          >
            ✏️
          </button>
        </PermissionGuard>

        {/* 删除按钮 */}
        <PermissionGuard permission="file_delete" showMessage={false}>
          <button
            onClick={(e) => {
              e.stopPropagation()
              if (confirm(`確定要刪除 "${file.name}" 嗎？`)) {
                onDelete(file)
              }
            }}
            className="p-1 text-gray-400 hover:text-red-400 transition-colors"
            title="刪除"
          >
            🗑️
          </button>
        </PermissionGuard>
      </div>
    </div>
  )
}

// 文件上传组件
const FileUpload = ({ onUpload, currentPath }) => {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    files.forEach(file => onUpload(file, currentPath))
  }

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)
    files.forEach(file => onUpload(file, currentPath))
    e.target.value = '' // 清空input
  }

  return (
    <PermissionGuard permission="file_upload">
      <div
        className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
          isDragging 
            ? 'border-purple-400 bg-purple-500/10' 
            : 'border-gray-600 hover:border-purple-500/50'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="text-4xl mb-2">📁</div>
        <div className="text-white text-sm mb-2">
          拖拽文件到這裡上傳
        </div>
        <div className="text-gray-400 text-xs mb-3">
          或者點擊選擇文件
        </div>
        <input
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-block px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg cursor-pointer transition-colors"
        >
          選擇文件
        </label>
      </div>
    </PermissionGuard>
  )
}

// 主文件管理器组件
const FileManager = () => {
  const { hasPermission } = usePermissions()
  const [files, setFiles] = useState([])
  const [currentPath, setCurrentPath] = useState('/')
  const [selectedFile, setSelectedFile] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('name') // name, size, date
  const [sortOrder, setSortOrder] = useState('asc') // asc, desc
  const [viewMode, setViewMode] = useState('list') // list, grid

  // 模拟文件数据
  useEffect(() => {
    // 这里应该从API获取文件列表
    const mockFiles = [
      {
        id: 1,
        name: 'PowerAutomation',
        isDirectory: true,
        size: 0,
        modifiedAt: '2025-06-28 10:30',
        path: '/PowerAutomation'
      },
      {
        id: 2,
        name: 'README.md',
        isDirectory: false,
        size: 15420,
        modifiedAt: '2025-06-28 09:15',
        path: '/README.md'
      },
      {
        id: 3,
        name: 'package.json',
        isDirectory: false,
        size: 2580,
        modifiedAt: '2025-06-27 16:45',
        path: '/package.json'
      },
      {
        id: 4,
        name: 'src',
        isDirectory: true,
        size: 0,
        modifiedAt: '2025-06-28 11:20',
        path: '/src'
      },
      {
        id: 5,
        name: 'output_files',
        isDirectory: true,
        size: 0,
        modifiedAt: '2025-06-28 12:00',
        path: '/output_files'
      }
    ]
    setFiles(mockFiles)
  }, [currentPath])

  // 过滤和排序文件
  const filteredAndSortedFiles = files
    .filter(file => 
      file.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let comparison = 0
      
      // 目录优先
      if (a.isDirectory && !b.isDirectory) return -1
      if (!a.isDirectory && b.isDirectory) return 1
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'size':
          comparison = a.size - b.size
          break
        case 'date':
          comparison = new Date(a.modifiedAt) - new Date(b.modifiedAt)
          break
        default:
          comparison = 0
      }
      
      return sortOrder === 'asc' ? comparison : -comparison
    })

  // 文件操作
  const handleFileSelect = (file) => {
    setSelectedFile(file)
    if (file.isDirectory) {
      // 进入目录
      setCurrentPath(file.path)
    }
  }

  const handleFileUpload = (file, path) => {
    console.log('上传文件:', file.name, '到路径:', path)
    // 这里应该调用API上传文件
  }

  const handleFileDelete = (file) => {
    console.log('删除文件:', file.name)
    // 这里应该调用API删除文件
    setFiles(files.filter(f => f.id !== file.id))
  }

  const handleFileRename = (file, newName) => {
    console.log('重命名文件:', file.name, '为:', newName)
    // 这里应该调用API重命名文件
    setFiles(files.map(f => 
      f.id === file.id ? { ...f, name: newName } : f
    ))
  }

  const handleCreateFolder = () => {
    const folderName = prompt('請輸入資料夾名稱:')
    if (folderName && folderName.trim()) {
      const newFolder = {
        id: Date.now(),
        name: folderName.trim(),
        isDirectory: true,
        size: 0,
        modifiedAt: new Date().toLocaleString('zh-TW'),
        path: `${currentPath}/${folderName.trim()}`
      }
      setFiles([...files, newFolder])
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-900/50 border border-purple-500/20 rounded-lg">
      {/* 文件管理器头部 */}
      <div className="flex items-center justify-between p-4 border-b border-purple-500/20">
        <div className="flex items-center space-x-4">
          <h2 className="text-white font-semibold">📁 文件管理器</h2>
          <div className="text-sm text-gray-400">
            {currentPath}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* 搜索框 */}
          <input
            type="text"
            placeholder="搜索文件..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-1 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
          
          {/* 排序选择 */}
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [by, order] = e.target.value.split('-')
              setSortBy(by)
              setSortOrder(order)
            }}
            className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
          >
            <option value="name-asc">名稱 ↑</option>
            <option value="name-desc">名稱 ↓</option>
            <option value="size-asc">大小 ↑</option>
            <option value="size-desc">大小 ↓</option>
            <option value="date-asc">日期 ↑</option>
            <option value="date-desc">日期 ↓</option>
          </select>

          {/* 新建文件夹按钮 */}
          <PermissionGuard permission="file_create" showMessage={false}>
            <button
              onClick={handleCreateFolder}
              className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition-colors"
              title="新建資料夾"
            >
              📁+
            </button>
          </PermissionGuard>
        </div>
      </div>

      {/* 文件上传区域 */}
      <div className="p-4 border-b border-purple-500/20">
        <FileUpload onUpload={handleFileUpload} currentPath={currentPath} />
      </div>

      {/* 文件列表 */}
      <div className="flex-1 overflow-auto p-4">
        {filteredAndSortedFiles.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            <div className="text-4xl mb-4">📂</div>
            <div>沒有找到文件</div>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredAndSortedFiles.map(file => (
              <FileItem
                key={file.id}
                file={file}
                onSelect={handleFileSelect}
                onDelete={handleFileDelete}
                onRename={handleFileRename}
                isSelected={selectedFile?.id === file.id}
              />
            ))}
          </div>
        )}
      </div>

      {/* 状态栏 */}
      <div className="flex items-center justify-between p-3 border-t border-purple-500/20 text-xs text-gray-400">
        <div>
          共 {filteredAndSortedFiles.length} 個項目
        </div>
        <div className="flex items-center space-x-4">
          {selectedFile && (
            <div>
              已選擇: {selectedFile.name}
            </div>
          )}
          <PermissionGuard permission="file_download" showMessage={false}>
            {selectedFile && !selectedFile.isDirectory && (
              <button
                onClick={() => console.log('下載文件:', selectedFile.name)}
                className="text-purple-400 hover:text-purple-300 transition-colors"
              >
                下載
              </button>
            )}
          </PermissionGuard>
        </div>
      </div>
    </div>
  )
}

export default FileManager

