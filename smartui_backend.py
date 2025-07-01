#!/usr/bin/env python3
"""
SmartUI 后端API服务
提供真实的文件系统操作功能
"""

import os
import json
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/api/browse-folder', methods=['POST'])
def browse_folder():
    """浏览文件夹内容"""
    try:
        data = request.get_json()
        path = data.get('path', '/home/ec2-user')
        
        # 安全检查：确保路径在允许的范围内
        allowed_paths = ['/home/ec2-user', '/home/ubuntu']
        if not any(path.startswith(allowed) for allowed in allowed_paths):
            return jsonify({'error': '路径不被允许'}), 403
        
        # 检查路径是否存在
        if not os.path.exists(path):
            return jsonify({'error': '路径不存在'}), 404
        
        items = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                item_type = 'folder' if os.path.isdir(item_path) else 'file'
                
                items.append({
                    'name': item,
                    'type': item_type,
                    'path': item_path
                })
        except PermissionError:
            return jsonify({'error': '没有权限访问此目录'}), 403
        
        # 按类型和名称排序（文件夹在前）
        items.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))
        
        return jsonify({'items': items})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-file', methods=['POST'])
def save_file():
    """保存文件"""
    try:
        data = request.get_json()
        file_path = data.get('path')
        content = data.get('content', '')
        
        # 安全检查
        allowed_paths = ['/home/ec2-user', '/home/ubuntu']
        if not any(file_path.startswith(allowed) for allowed in allowed_paths):
            return jsonify({'error': '路径不被允许'}), 403
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({'success': True, 'message': '文件保存成功'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/read-file', methods=['POST'])
def read_file():
    """读取文件内容"""
    try:
        data = request.get_json()
        file_path = data.get('path')
        
        # 安全检查
        allowed_paths = ['/home/ec2-user', '/home/ubuntu']
        if not any(file_path.startswith(allowed) for allowed in allowed_paths):
            return jsonify({'error': '路径不被允许'}), 403
        
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        if os.path.isdir(file_path):
            return jsonify({'error': '这是一个目录，不是文件'}), 400
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({'content': content})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clone-repo', methods=['POST'])
def clone_repo():
    """克隆Git仓库"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        local_dir = data.get('local_dir')
        
        if not repo_url or not local_dir:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 构建完整路径
        full_path = f'/home/ec2-user/{local_dir}'
        
        # 执行git clone
        result = subprocess.run(
            ['git', 'clone', repo_url, full_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True, 
                'message': '仓库克隆成功',
                'path': full_path
            })
        else:
            return jsonify({
                'error': f'克隆失败: {result.stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-project-info', methods=['POST'])
def get_project_info():
    """获取项目信息"""
    try:
        data = request.get_json()
        project_path = data.get('path')
        
        if not project_path or not os.path.exists(project_path):
            return jsonify({'error': '项目路径不存在'}), 404
        
        project_info = {
            'name': os.path.basename(project_path),
            'path': project_path,
            'type': 'unknown'
        }
        
        # 检查项目类型
        if os.path.exists(os.path.join(project_path, 'package.json')):
            project_info['type'] = 'node'
            try:
                with open(os.path.join(project_path, 'package.json'), 'r') as f:
                    package_data = json.load(f)
                    project_info['description'] = package_data.get('description', '')
                    project_info['version'] = package_data.get('version', '')
            except:
                pass
        elif os.path.exists(os.path.join(project_path, 'requirements.txt')):
            project_info['type'] = 'python'
        elif os.path.exists(os.path.join(project_path, '.git')):
            project_info['type'] = 'git'
            # 获取Git信息
            try:
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      cwd=project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    project_info['git_url'] = result.stdout.strip()
            except:
                pass
        
        # 获取文件统计
        file_count = 0
        folder_count = 0
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path):
                folder_count += 1
            else:
                file_count += 1
        
        project_info['file_count'] = file_count
        project_info['folder_count'] = folder_count
        
        return jsonify(project_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-file-tree', methods=['POST'])
def get_file_tree():
    """获取完整的文件树结构"""
    try:
        data = request.get_json()
        root_path = data.get('path')
        max_depth = data.get('max_depth', 3)  # 限制深度避免过大
        
        if not root_path or not os.path.exists(root_path):
            return jsonify({'error': '路径不存在'}), 404
        
        def build_tree(path, current_depth=0):
            if current_depth >= max_depth:
                return None
            
            items = []
            try:
                for item in os.listdir(path):
                    # 跳过隐藏文件和常见的忽略目录
                    if item.startswith('.') and item not in ['.git', '.gitignore']:
                        continue
                    if item in ['node_modules', '__pycache__', '.vscode']:
                        continue
                    
                    item_path = os.path.join(path, item)
                    item_info = {
                        'name': item,
                        'path': item_path,
                        'type': 'folder' if os.path.isdir(item_path) else 'file'
                    }
                    
                    if item_info['type'] == 'folder':
                        children = build_tree(item_path, current_depth + 1)
                        if children is not None:
                            item_info['children'] = children
                    
                    items.append(item_info)
            except PermissionError:
                pass
            
            # 排序：文件夹在前，然后按名称排序
            items.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))
            return items
        
        tree = build_tree(root_path)
        return jsonify({'tree': tree})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-command', methods=['POST'])
def execute_command():
    """执行命令"""
    try:
        data = request.get_json()
        command = data.get('command')
        working_dir = data.get('working_dir', '/home/ec2-user')
        
        if not command:
            return jsonify({'error': '缺少命令'}), 400
        
        # 安全检查：只允许特定的命令
        allowed_commands = ['ls', 'pwd', 'cat', 'echo', 'mkdir', 'touch', 'cp', 'mv', 'rm', 'git']
        cmd_parts = command.split()
        if cmd_parts and cmd_parts[0] not in allowed_commands:
            return jsonify({'error': '命令不被允许'}), 403
        
        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': '命令执行超时'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("启动SmartUI后端API服务...")
    app.run(host='0.0.0.0', port=5002, debug=True)

