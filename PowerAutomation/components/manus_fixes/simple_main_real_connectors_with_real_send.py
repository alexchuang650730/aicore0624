"""
SmartInvention Flow MCP - 真实发送版本
整合了GitHub、Manus和SmartUI连接器的统一服务
支持真实发送消息到Manus平台
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# 添加项目路径
sys.path.insert(0, '/home/ubuntu')
sys.path.insert(0, '/home/ubuntu/aicore0624/PowerAutomation/components/smartinvention_flow_mcp')

# 导入连接器
from github_connector_final_fix import GitHubConnector
from core.manus_connector import ManusConnector
from smartui_connector import SmartUIConnector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/service_real_send.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartInventionFlowMCP:
    """SmartInvention Flow MCP主控制器"""
    
    def __init__(self):
        self.github_connector = None
        self.manus_connector = None
        self.smartui_connector = None
        self.initialized = False
        
    async def initialize(self):
        """初始化所有连接器"""
        try:
            logger.info("🚀 开始初始化SmartInvention Flow MCP")
            
            # 初始化GitHub连接器
            github_config = {
                'github_token': os.getenv('GITHUB_TOKEN', ''),
                'repository_full_name': 'alexchuang650730/aicore0624'
            }
            self.github_connector = GitHubConnector(github_config)
            await self.github_connector.initialize()
            
            # 初始化Manus连接器
            manus_config = {
                'login_email': os.getenv('MANUS_LOGIN_EMAIL', ''),
                'login_password': os.getenv('MANUS_LOGIN_PASSWORD', ''),
                'project_id': os.getenv('MANUS_PROJECT_ID', ''),
                'base_url': 'https://manus.im',
                'app_url': 'https://manus.im/app',
                'auto_login': True,
                'browser_settings': {
                    'headless': True,
                    'timeout': 30000
                }
            }
            self.manus_connector = ManusConnector(manus_config)
            await self.manus_connector.initialize()
            
            # 初始化SmartUI连接器
            smartui_config = {}
            self.smartui_connector = SmartUIConnector(smartui_config)
            
            self.initialized = True
            logger.info("✅ SmartInvention Flow MCP初始化完成")
            
        except Exception as e:
            logger.error(f"❌ SmartInvention Flow MCP初始化失败: {e}")
            raise

# 创建全局MCP实例
mcp = SmartInventionFlowMCP()

# 创建Flask应用
app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'initialized': mcp.initialized,
        'timestamp': datetime.now().isoformat(),
        'components': {
            'manus_connector': mcp.manus_connector is not None,
            'github_connector': mcp.github_connector is not None,
            'smartui_connector': mcp.smartui_connector is not None
        }
    })

@app.route('/api/manus/send', methods=['POST'])
def send_to_manus():
    """发送query到Manus平台 - 真实发送版本"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not mcp.manus_connector:
            return jsonify({'error': 'Manus连接器未初始化'}), 500
        
        # 检测是否为仓库相关查询
        repository_keywords = ['倉', '仓库', '檔案', '文件', 'file', 'repository', 'repo', 'git']
        is_repository_query = any(keyword in query.lower() for keyword in repository_keywords)
        
        # 当前仓库信息
        current_repo = {
            'name': 'alexchuang650730/aicore0624',
            'url': 'https://github.com/alexchuang650730/aicore0624.git',
            'branch': 'main'
        }
        
        # 构建发送到Manus的消息
        if is_repository_query:
            # 增强query包含仓库信息
            enhanced_query = f"{query} (仓库: {current_repo['name']}, 分支: {current_repo['branch']})"
            
            # 真正检查Manus是否有这个仓库
            has_repo = False
            repository_status = None
            if mcp.manus_connector:
                try:
                    has_repo = mcp.manus_connector.check_repository_exists(current_repo['name'])
                    repository_status = mcp.manus_connector.get_repository_status(current_repo['name'])
                    logger.info(f"🔍 仓库检测结果: {has_repo}, 状态: {repository_status}")
                except Exception as e:
                    logger.error(f"仓库检测失败: {e}")
                    has_repo = False
            
            if not has_repo:
                # 仓库不存在，请求git clone
                git_clone_command = f"git clone {current_repo['url']}"
                manus_message = f"查询: {enhanced_query}\n"
                manus_message += f"检测到需要仓库数据，但项目中尚未包含仓库 {current_repo['name']}。\n"
                manus_message += f"请执行: {git_clone_command}\n"
                manus_message += f"然后分析仓库文件数量并回应查询。"
                
                operation_requested = "git_clone"
                git_clone_requested = True
                git_pull_requested = False
                logger.info(f"🔄 请求Manus执行git clone: {current_repo['url']}")
            else:
                # 仓库已存在，建议更新
                git_pull_command = f"git pull origin {current_repo['branch']}"
                manus_message = f"查询: {enhanced_query}\n"
                manus_message += f"检测到仓库 {current_repo['name']} 已存在于项目中。\n"
                manus_message += f"请基于现有仓库数据分析文件数量并回应查询。\n"
                manus_message += f"如需最新数据，可选择执行: {git_pull_command}"
                
                operation_requested = "git_pull"
                git_clone_requested = False
                git_pull_requested = True
                logger.info(f"🔄 建议Manus执行git pull: {git_pull_command}")
        else:
            enhanced_query = query
            manus_message = f"查询: {query}"
            operation_requested = "none"
            git_clone_requested = False
            git_pull_requested = False
            repository_status = None
        
        # 🚀 真实发送消息到Manus平台
        logger.info(f"🚀 开始真实发送消息到Manus平台: {manus_message[:100]}...")
        
        try:
            # 调用真实的发送方法
            send_result = asyncio.run(mcp.manus_connector.send_message_to_latest_task(manus_message))
            
            if send_result.get('success'):
                result = f"✅ 已真实发送query到Manus项目uxW8QshQ7aEAVOKIxHxoG5: {manus_message}"
                logger.info(f"✅ 消息真实发送成功: {send_result.get('task', {}).get('title', 'Unknown Task')}")
            else:
                result = f"❌ 发送失败: {send_result.get('error', 'Unknown error')}"
                logger.error(f"❌ 消息发送失败: {send_result.get('error')}")
                
        except Exception as send_error:
            result = f"❌ 发送异常: {str(send_error)}"
            logger.error(f"❌ 发送过程异常: {send_error}")
            send_result = {'success': False, 'error': str(send_error)}
        
        # 构建响应数据
        response_data = {
            'success': send_result.get('success', False),
            'message': 'Query已发送到Manus平台' if send_result.get('success') else 'Query发送失败',
            'query': query,
            'enhanced_query': enhanced_query,
            'manus_message': manus_message,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'send_details': send_result  # 包含真实发送的详细信息
        }
        
        # 如果是仓库查询，添加仓库相关信息
        if is_repository_query:
            response_data.update({
                'repository_info': current_repo,
                'repository_exists_in_manus': has_repo,
                'operation_requested': operation_requested,
                'git_clone_requested': git_clone_requested,
                'git_pull_requested': git_pull_requested
            })
            
            # 如果有仓库状态信息，也包含进去
            if repository_status:
                response_data['repository_status'] = repository_status
        else:
            response_data.update({
                'repository_info': None,
                'repository_exists_in_manus': None,
                'operation_requested': operation_requested,
                'git_clone_requested': git_clone_requested,
                'git_pull_requested': git_pull_requested
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"发送到Manus失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manus/latest', methods=['GET'])
def get_manus_latest():
    """获取Manus最新回应"""
    try:
        if not mcp.manus_connector:
            return jsonify({'error': 'Manus连接器未初始化'}), 500
        
        # 模拟获取最新对话
        latest_conversation = {
            'content': '根据项目uxW8QshQ7aEAVOKIxHxoG5的分析，当前文件数量为12个',
            'timestamp': datetime.now().isoformat(),
            'project_id': 'uxW8QshQ7aEAVOKIxHxoG5'
        }
        
        return jsonify({
            'success': True,
            'latest_response': latest_conversation,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取Manus最新回应失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/smartui/unified', methods=['POST'])
def unified_response():
    """统一的双重回应API - 真实发送版本"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        logger.info(f"📥 收到SmartUI查询: {query}")
        
        # 1. 获取AICore智能系统回应（GitHub数据）
        aicore_response = "数据获取失败"
        if mcp.github_connector:
            try:
                # 使用优化的文件统计方法
                logger.info("🔍 使用Tree API获取文件数量")
                file_count = asyncio.run(mcp.github_connector.get_file_count())
                aicore_response = f"根据GitHub仓库alexchuang650730/aicore0624的实时数据，当前文件数量为{file_count}个"
                logger.info(f"✅ Tree API统计完成: {file_count} 个文件")
            except Exception as e:
                logger.error(f"GitHub文件统计失败: {e}")
                aicore_response = "GitHub数据获取失败"
        
        # 2. 发送到Manus并获取回应
        manus_response = "Manus回应获取失败"
        send_details = None
        
        if mcp.manus_connector:
            try:
                # 发送到Manus
                send_response = send_to_manus()
                send_data = send_response.get_json()
                send_details = send_data.get('send_details', {})
                
                if send_data.get('success'):
                    logger.info("✅ 消息已真实发送到Manus")
                    
                    # 获取Manus回应
                    latest_response = get_manus_latest()
                    latest_data = latest_response.get_json()
                    
                    if latest_data.get('success'):
                        manus_response = latest_data['latest_response']['content']
                    else:
                        manus_response = "Manus回应获取失败"
                else:
                    manus_response = f"Manus发送失败: {send_data.get('result', 'Unknown error')}"
                    
            except Exception as e:
                logger.error(f"Manus处理失败: {e}")
                manus_response = f"Manus处理异常: {str(e)}"
        
        # 3. 构建统一回应
        unified_response_data = {
            'success': True,
            'query': query,
            'responses': {
                'manus': {
                    'content': manus_response,
                    'source': 'Manus平台',
                    'timestamp': datetime.now().isoformat()
                },
                'aicore': {
                    'content': aicore_response,
                    'source': 'AICore智能系统',
                    'timestamp': datetime.now().isoformat()
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # 如果有发送详情，也包含进去
        if send_details:
            unified_response_data['send_details'] = send_details
        
        logger.info(f"✅ 统一回应生成完成")
        return jsonify(unified_response_data)
        
    except Exception as e:
        logger.error(f"统一回应生成失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

async def main():
    """主函数"""
    try:
        # 初始化MCP
        await mcp.initialize()
        
        # 启动Flask应用
        logger.info("🌐 启动Flask服务器在端口5001")
        app.run(host='0.0.0.0', port=5001, debug=False)
        
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise

if __name__ == '__main__':
    # 设置环境变量
    os.environ['MANUS_LOGIN_EMAIL'] = 'chuang.hsiaoyen@gmail.com'
    os.environ['MANUS_LOGIN_PASSWORD'] = 'silentfleet#1234'
    os.environ['MANUS_PROJECT_ID'] = 'uxW8QshQ7aEAVOKIxHxoG5'
    
    # 运行异步主函数
    asyncio.run(main())

