#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import sys
import logging
sys.path.append('/home/ubuntu')

from github_connector_fixed import GitHubConnector

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局GitHub连接器
github_connector = None

async def init_github():
    global github_connector
    config = {}
    github_connector = GitHubConnector(config)
    await github_connector.initialize()
    logger.info("✅ GitHub连接器初始化成功")

@app.route('/api/github/files', methods=['GET'])
def get_github_files():
    """获取GitHub仓库文件列表"""
    try:
        if not github_connector:
            return jsonify({'error': 'GitHub连接器未初始化'}), 500
        
        # 获取文件列表
        files = asyncio.run(github_connector.get_repository_files())
        
        # 组织文件树结构
        organized_files = organize_files_tree(files)
        
        return jsonify({
            'success': True,
            'files': organized_files,
            'total_count': len(files),
            'repository': 'alexchuang650730/aicore0624',
            'timestamp': '2025-06-29T06:50:00.000000'
        })
        
    except Exception as e:
        logger.error(f"❌ 获取文件列表失败: {e}")
        return jsonify({'error': str(e)}), 500

def organize_files_tree(files):
    """组织文件为树形结构"""
    try:
        # 按路径深度和类型排序
        sorted_files = sorted(files, key=lambda x: (x.get('depth', 0), x.get('type') == 'file', x.get('name', '')))
        
        organized = []
        for file in sorted_files:
            file_info = {
                'name': file.get('name', ''),
                'path': file.get('path', ''),
                'type': file.get('type', ''),
                'size': file.get('size', 0),
                'depth': file.get('depth', 0),
                'icon': '📁' if file.get('type') == 'dir' else get_file_icon(file.get('name', ''))
            }
            organized.append(file_info)
        
        return organized
        
    except Exception as e:
        logger.error(f"❌ 组织文件树失败: {e}")
        return files

def get_file_icon(filename):
    """根据文件名获取图标"""
    if not filename:
        return '📄'
    
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    icon_map = {
        'py': '🐍',
        'js': '📜',
        'jsx': '⚛️',
        'ts': '📘',
        'tsx': '⚛️',
        'html': '🌐',
        'css': '🎨',
        'scss': '🎨',
        'json': '📋',
        'md': '📝',
        'txt': '📄',
        'yml': '⚙️',
        'yaml': '⚙️',
        'xml': '📋',
        'sql': '🗃️',
        'sh': '💻',
        'bat': '💻',
        'dockerfile': '🐳',
        'gitignore': '🚫',
        'env': '🔧',
        'config': '⚙️'
    }
    
    return icon_map.get(ext, '📄')

@app.route('/api/github/file/<path:file_path>', methods=['GET'])
def get_github_file_content(file_path):
    """获取GitHub文件内容"""
    try:
        if not github_connector:
            return jsonify({'error': 'GitHub连接器未初始化'}), 500
        
        # 获取文件内容
        content = asyncio.run(github_connector.get_file_content(file_path))
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'content': content,
            'size': len(content),
            'timestamp': '2025-06-29T06:50:00.000000'
        })
        
    except Exception as e:
        logger.error(f"❌ 获取文件内容失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/github/info', methods=['GET'])
def get_github_info():
    """获取GitHub仓库信息"""
    try:
        if not github_connector:
            return jsonify({'error': 'GitHub连接器未初始化'}), 500
        
        # 获取仓库信息
        info = asyncio.run(github_connector.get_repository_info())
        
        return jsonify({
            'success': True,
            'repository_info': info,
            'timestamp': '2025-06-29T06:50:00.000000'
        })
        
    except Exception as e:
        logger.error(f"❌ 获取仓库信息失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/github/status', methods=['GET'])
def get_github_status():
    """获取GitHub连接器状态"""
    return jsonify({
        'success': True,
        'initialized': github_connector is not None,
        'repository': 'alexchuang650730/aicore0624',
        'timestamp': '2025-06-29T06:50:00.000000'
    })

if __name__ == '__main__':
    # 初始化GitHub连接器
    asyncio.run(init_github())
    
    # 启动Flask应用
    logger.info("🚀 启动GitHub API代理服务 (端口: 8083)")
    app.run(host="0.0.0.0", port=8083, debug=False)

