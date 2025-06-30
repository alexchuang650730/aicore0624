import { useState, useEffect, useRef } from 'react'
import * as monaco from 'monaco-editor'

/**
 * Monaco Editor 版本的代码编辑器组件
 * 支持基础编辑功能和语法高亮
 */
const MonacoCodeEditor = ({ selectedFile, hasPermission, lspServerUrl }) => {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [isModified, setIsModified] = useState(false)
  const [language, setLanguage] = useState('python')
  
  const editorRef = useRef(null)
  const monacoEditorRef = useRef(null)

  // 语言映射
  const getLanguageFromExtension = (filename) => {
    if (!filename) return 'python'
    const ext = filename.split('.').pop()?.toLowerCase()
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
      'yaml': 'yaml',
      'xml': 'xml',
      'sql': 'sql',
      'sh': 'shell',
      'bash': 'shell',
      'dockerfile': 'dockerfile',
      'go': 'go',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'cs': 'csharp',
      'php': 'php',
      'rb': 'ruby',
      'rs': 'rust',
      'swift': 'swift',
    }
    return langMap[ext] || 'text'
  }

  // 初始化Monaco Editor
  useEffect(() => {
    if (editorRef.current && !monacoEditorRef.current) {
      // 设置Monaco Editor主题
      monaco.editor.defineTheme('dark-theme', {
        base: 'vs-dark',
        inherit: true,
        rules: [],
        colors: {
          'editor.background': '#1a1a1a',
          'editor.foreground': '#ffffff',
          'editorLineNumber.foreground': '#666666',
          'editor.selectionBackground': '#264f78',
          'editor.inactiveSelectionBackground': '#3a3d41'
        }
      })

      // 创建编辑器实例
      monacoEditorRef.current = monaco.editor.create(editorRef.current, {
        value: content,
        language: language,
        theme: 'dark-theme',
        automaticLayout: true,
        fontSize: 14,
        lineNumbers: 'on',
        roundedSelection: false,
        scrollBeyondLastLine: false,
        readOnly: !hasPermission('code_edit'),
        minimap: {
          enabled: true
        },
        wordWrap: 'on',
        folding: true,
        lineDecorationsWidth: 10,
        lineNumbersMinChars: 3,
        glyphMargin: false,
        contextmenu: true,
        mouseWheelZoom: true,
        cursorStyle: 'line',
        renderWhitespace: 'selection',
        renderControlCharacters: false,
        fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
        tabSize: 4,
        insertSpaces: true,
        detectIndentation: true,
        trimAutoWhitespace: true,
        formatOnPaste: true,
        formatOnType: true
      })

      // 监听内容变化
      monacoEditorRef.current.onDidChangeModelContent(() => {
        const newContent = monacoEditorRef.current.getValue()
        setContent(newContent)
        setIsModified(true)
      })

      // 添加快捷键
      monacoEditorRef.current.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        handleSave()
      })
    }

    return () => {
      if (monacoEditorRef.current) {
        monacoEditorRef.current.dispose()
        monacoEditorRef.current = null
      }
    }
  }, [])

  // 更新语言
  useEffect(() => {
    if (selectedFile) {
      const newLanguage = getLanguageFromExtension(selectedFile.name)
      setLanguage(newLanguage)
      
      if (monacoEditorRef.current) {
        const model = monacoEditorRef.current.getModel()
        if (model) {
          monaco.editor.setModelLanguage(model, newLanguage)
        }
      }
    }
  }, [selectedFile])

  // 更新内容
  useEffect(() => {
    if (monacoEditorRef.current && selectedFile) {
      setLoading(true)
      // 模拟加载文件内容
      const sampleContent = selectedFile.name?.endsWith('.py') ? 
        `# Python示例代码
def hello_world():
    """
    这是一个示例Python函数
    """
    print("Hello, World!")
    return "Hello from Monaco Editor!"

# 测试LSP功能
class ExampleClass:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"

if __name__ == "__main__":
    hello_world()
    example = ExampleClass("Monaco")
    print(example.greet())
` : 
        `// JavaScript示例代码
function helloWorld() {
    console.log("Hello, World!");
    return "Hello from Monaco Editor!";
}

// 测试代码
const example = {
    name: "Monaco",
    greet() {
        return \`Hello, \${this.name}!\`;
    }
};

helloWorld();
console.log(example.greet());
`
      
      monacoEditorRef.current.setValue(sampleContent)
      setContent(sampleContent)
      setIsModified(false)
      setLoading(false)
    }
  }, [selectedFile])

  const handleSave = () => {
    if (monacoEditorRef.current && hasPermission('code_edit')) {
      const currentContent = monacoEditorRef.current.getValue()
      console.log('保存文件:', selectedFile?.name, currentContent)
      setIsModified(false)
      // 这里可以添加实际的保存逻辑
    }
  }

  const handleFormat = () => {
    if (monacoEditorRef.current) {
      monacoEditorRef.current.getAction('editor.action.formatDocument').run()
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* 工具栏 */}
      <div className="flex items-center justify-between p-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-300">
            {selectedFile ? (
              <span className="flex items-center">
                <span className="text-blue-400">📄</span>
                <span className="ml-2">{selectedFile.name}</span>
                {isModified && <span className="ml-2 text-yellow-400">●</span>}
              </span>
            ) : (
              <span className="text-gray-500">请选择文件</span>
            )}
          </div>
          <div className="text-xs text-gray-500">
            语言: {language}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {lspServerUrl && (
            <div className="text-xs text-green-400 flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
              LSP Ready
            </div>
          )}
          
          {hasPermission('code_edit') && (
            <>
              <button
                onClick={handleFormat}
                className="px-3 py-1 text-xs bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors"
                title="格式化代码 (Shift+Alt+F)"
              >
                格式化
              </button>
              <button
                onClick={handleSave}
                className="px-3 py-1 text-xs bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                title="保存 (Ctrl+S)"
                disabled={!isModified}
              >
                保存
              </button>
            </>
          )}
        </div>
      </div>

      {/* 编辑器容器 */}
      <div className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 bg-gray-900/50 flex items-center justify-center z-10">
            <div className="text-white">加载中...</div>
          </div>
        )}
        <div 
          ref={editorRef} 
          className="w-full h-full"
          style={{ minHeight: '400px' }}
        />
      </div>

      {/* 状态栏 */}
      <div className="flex items-center justify-between px-3 py-1 bg-gray-800 border-t border-gray-700 text-xs text-gray-400">
        <div className="flex items-center space-x-4">
          <span>Monaco Editor</span>
          {selectedFile && (
            <span>行: 1, 列: 1</span>
          )}
        </div>
        <div className="flex items-center space-x-4">
          <span>UTF-8</span>
          <span>{language.toUpperCase()}</span>
          {lspServerUrl && (
            <span className="text-green-400">LSP: {lspServerUrl}</span>
          )}
        </div>
      </div>
    </div>
  )
}

export default MonacoCodeEditor

