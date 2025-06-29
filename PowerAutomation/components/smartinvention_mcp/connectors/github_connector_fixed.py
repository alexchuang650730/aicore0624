#!/usr/bin/env python3
"""
GitHub连接器 - 修复版本
修复文件列表和内容获取功能
"""

import asyncio
import logging
import json
import requests
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List

class GitHubConnector:
    """GitHub连接器 - 修复版本"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        
        # GitHub配置
        self.repository_owner = "alexchuang650730"
        self.repository_name = "aicore0624"
        self.repository_full_name = f"{self.repository_owner}/{self.repository_name}"
        
        # GitHub API配置
        self.github_api_base = "https://api.github.com"
        self.github_token = None  # 可选的GitHub token
        
        # 缓存
        self.repository_info_cache = None
        self.files_cache = None
        self.cache_timestamp = None
        self.cache_duration = 300  # 5分钟缓存
        
    async def initialize(self):
        """初始化GitHub连接器"""
        try:
            self.logger.info(f"🔗 初始化 GitHub 连接器: {self.repository_full_name}")
            
            # 测试GitHub API连接
            await self._test_github_connection()
            
            self.initialized = True
            self.logger.info("✅ GitHub连接器初始化成功")
            
        except Exception as e:
            self.logger.error(f"❌ GitHub连接器初始化失败: {e}")
            self.initialized = True  # 即使失败也标记为初始化
            
    async def _test_github_connection(self):
        """测试GitHub API连接"""
        try:
            url = f"{self.github_api_base}/repos/{self.repository_full_name}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("✅ GitHub API连接测试成功")
                return True
            else:
                self.logger.warning(f"⚠️ GitHub API连接测试失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ GitHub API连接测试异常: {e}")
            return False
    
    def _make_github_request(self, url: str) -> Optional[Dict[str, Any]]:
        """发送GitHub API请求"""
        try:
            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"❌ GitHub API请求失败: {response.status_code} - {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ GitHub API请求异常: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self.cache_timestamp:
            return False
        
        current_time = datetime.now().timestamp()
        return (current_time - self.cache_timestamp) < self.cache_duration
    
    async def get_repository_files(self, path: str = "") -> List[Dict[str, Any]]:
        """获取仓库文件树结构"""
        try:
            self.logger.info(f"🌳 获取仓库文件树: {path or 'root'}")
            
            # 检查缓存
            if self._is_cache_valid() and self.files_cache:
                self.logger.info("📋 使用缓存的文件列表")
                return self.files_cache
            
            def get_files_recursive(current_path: str = "", max_depth: int = 3, current_depth: int = 0) -> List[Dict[str, Any]]:
                """递归获取文件，限制深度避免过深"""
                files = []
                
                if current_depth >= max_depth:
                    return files
                
                try:
                    url = f"{self.github_api_base}/repos/{self.repository_full_name}/contents/{current_path}"
                    contents = self._make_github_request(url)
                    
                    if not contents:
                        return files
                    
                    for item in contents:
                        file_info = {
                            'name': item.get('name', ''),
                            'path': item.get('path', ''),
                            'type': item.get('type', ''),
                            'size': item.get('size', 0),
                            'download_url': item.get('download_url', ''),
                            'sha': item.get('sha', ''),
                            'url': item.get('url', ''),
                            'depth': current_depth
                        }
                        
                        files.append(file_info)
                        
                        if item.get('type') == 'dir' and current_depth < max_depth - 1:
                            # 递归获取子目录文件
                            subdir_files = get_files_recursive(
                                item.get('path', ''), 
                                max_depth, 
                                current_depth + 1
                            )
                            files.extend(subdir_files)
                
                except Exception as e:
                    self.logger.error(f"❌ 获取路径 {current_path} 失败: {e}")
                
                return files
            
            all_files = get_files_recursive(path)
            
            # 更新缓存
            self.files_cache = all_files
            self.cache_timestamp = datetime.now().timestamp()
            
            self.logger.info(f"✅ 获取到 {len(all_files)} 个文件/目录")
            return all_files
            
        except Exception as e:
            self.logger.error(f"❌ 获取仓库文件失败: {e}")
            return []
    
    async def get_file_content(self, file_path: str) -> str:
        """获取文件内容"""
        try:
            self.logger.info(f"📄 获取文件内容: {file_path}")
            
            url = f"{self.github_api_base}/repos/{self.repository_full_name}/contents/{file_path}"
            file_data = self._make_github_request(url)
            
            if not file_data:
                return "# 文件不存在或无法访问"
            
            # GitHub API返回base64编码的内容
            if file_data.get('encoding') == 'base64':
                try:
                    content = base64.b64decode(file_data.get('content', '')).decode('utf-8')
                    self.logger.info(f"✅ 文件内容获取成功: {len(content)} 字符")
                    return content
                except UnicodeDecodeError:
                    # 如果是二进制文件，返回提示信息
                    return f"# 二进制文件: {file_path}\n\n文件大小: {file_data.get('size', 0)} 字节\n类型: 二进制文件，无法显示内容"
            else:
                # 直接返回内容
                return file_data.get('content', '')
                
        except Exception as e:
            self.logger.error(f"❌ 获取文件内容失败 {file_path}: {e}")
            return f"# 无法加载文件内容\n\n错误: {str(e)}"

    async def get_repository_info(self) -> Dict[str, Any]:
        """获取仓库基本信息"""
        try:
            self.logger.info("🔍 获取GitHub仓库信息")
            
            # 获取基本仓库信息
            repo_url = f"{self.github_api_base}/repos/{self.repository_full_name}"
            repo_data = self._make_github_request(repo_url)
            
            if not repo_data:
                self.logger.error("❌ 无法获取仓库基本信息")
                return {}
            
            return {
                'name': repo_data.get('name', ''),
                'full_name': repo_data.get('full_name', ''),
                'description': repo_data.get('description', ''),
                'private': repo_data.get('private', False),
                'default_branch': repo_data.get('default_branch', 'main'),
                'language': repo_data.get('language', ''),
                'size': repo_data.get('size', 0),
                'created_at': repo_data.get('created_at', ''),
                'updated_at': repo_data.get('updated_at', ''),
                'clone_url': repo_data.get('clone_url', ''),
                'html_url': repo_data.get('html_url', '')
            }
            
        except Exception as e:
            self.logger.error(f"❌ 获取仓库信息失败: {e}")
            return {}

# 测试函数
async def test_github_connector():
    """测试GitHub连接器"""
    logging.basicConfig(level=logging.INFO)
    
    config = {}
    github = GitHubConnector(config)
    
    try:
        await github.initialize()
        
        # 测试获取文件列表
        files = await github.get_repository_files()
        print(f"✅ 获取到 {len(files)} 个文件")
        
        # 显示前几个文件
        for i, file in enumerate(files[:10]):
            print(f"  {i+1}. {file['type']}: {file['path']}")
        
        # 测试获取文件内容
        if files:
            first_file = next((f for f in files if f['type'] == 'file'), None)
            if first_file:
                content = await github.get_file_content(first_file['path'])
                print(f"✅ 文件内容预览: {content[:100]}...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_github_connector())

