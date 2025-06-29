"""
SmartUI MCP - AI-First IDE 后端服务
PowerAutomation Local 组件
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging
from datetime import datetime

# 添加PowerAutomation_local路径
current_dir = os.path.dirname(os.path.abspath(__file__))
powerautomation_local_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(powerautomation_local_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SmartUIMCP:
    """SmartUI MCP 主类"""
    
    def __init__(self):
        self.name = "SmartUI MCP"
        self.version = "2.0.0"
        self.description = "AI-First IDE 后端服务 - PowerAutomation Local 组件"
        self.connectors = {}
        self.init_connectors()
    
    def init_connectors(self):
        """初始化连接器"""
        logger.info(f"🚀 启动 {self.name} v{self.version}")
        logger.info("🚀 初始化 SmartUI MCP（PowerAutomation Local）")
        
        # 尝试初始化ManusConnector
        try:
            from core.manus_connector import ManusConnector
            self.connectors['manus'] = ManusConnector()
            logger.info("✅ ManusConnector初始化成功")
        except Exception as e:
            logger.warning("⚠️ ManusConnector不可用")
            print("Warning: ManusConnector not available")
        
        # 初始化GitHubConnector
        try:
            logger.info("🔗 初始化GitHubConnector")
            from core.github_connector_final_fix import GitHubConnector
            self.connectors['github'] = GitHubConnector(
                repo_name="alexchuang650730/aicore0624",
                github_token=os.getenv('GITHUB_TOKEN', '')
            )
            logger.info("✅ GitHubConnector初始化成功")
        except Exception as e:
            logger.error(f"❌ GitHubConnector初始化失败: {e}")
        
        # 初始化SmartUIConnector
        try:
            logger.info("🔗 初始化SmartUIConnector")
            from core.smartui_connector import SmartUIConnector
            self.connectors['smartui'] = SmartUIConnector()
            logger.info("✅ SmartUIConnector初始化成功")
        except Exception as e:
            logger.error(f"❌ SmartUIConnector初始化失败: {e}")
        
        logger.info("🎉 SmartUI MCP初始化完成（PowerAutomation Local）")

# 全局SmartUI MCP实例
smartui_mcp = SmartUIMCP()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': smartui_mcp.name,
        'version': smartui_mcp.version,
        'timestamp': datetime.now().isoformat(),
        'connectors': {
            name: connector is not None 
            for name, connector in smartui_mcp.connectors.items()
        }
    })

@app.route('/api/auth/check', methods=['GET'])
def auth_check():
    """认证检查端点"""
    return jsonify({
        'authenticated': True,
        'user': 'admin',
        'service': smartui_mcp.name,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def status():
    """状态检查端点"""
    return jsonify({
        'service': smartui_mcp.name,
        'version': smartui_mcp.version,
        'description': smartui_mcp.description,
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'powerautomation_local': True
    })

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """获取项目列表"""
    return jsonify({
        'projects': [
            {'id': 1, 'name': 'PowerAutomation Project', 'status': 'active'},
            {'id': 2, 'name': 'SmartUI Development', 'status': 'active'},
            {'id': 3, 'name': 'AI-First IDE', 'status': 'active'}
        ]
    })

@app.route('/api/generate', methods=['POST'])
def generate_code():
    """代码生成端点"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    # 模拟代码生成（可以集成真实的AI服务）
    response = {
        'code': f'# Generated code for: {prompt}\n# PowerAutomation Local - SmartUI MCP\nprint("Hello, AI-First IDE!")',
        'explanation': f'这是根据您的需求 "{prompt}" 生成的代码示例。',
        'service': smartui_mcp.name,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(response)

@app.route('/api/mcp/info', methods=['GET'])
def mcp_info():
    """MCP信息端点"""
    return jsonify({
        'name': smartui_mcp.name,
        'version': smartui_mcp.version,
        'description': smartui_mcp.description,
        'type': 'SmartUI MCP',
        'powerautomation_local': True,
        'connectors': list(smartui_mcp.connectors.keys()),
        'endpoints': [
            '/health',
            '/api/auth/check',
            '/api/status',
            '/api/projects',
            '/api/generate',
            '/api/mcp/info'
        ]
    })

def start_server(host='0.0.0.0', port=5001, debug=False):
    """启动SmartUI MCP服务器"""
    logger.info(f"🌐 启动{smartui_mcp.name}服务器 (端口: {port})")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_server()

