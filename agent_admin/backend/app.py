"""
Agentic Agent 管理中心 - 清理版後端API服務

移除UI相關功能，保留核心組件:
- Enhanced Interaction Log Manager
- Simplified RL SRT Adapter  
- Replay Classifier
- 增強版簡化Agent架構

作者: Agentic Agent Team
版本: 2.1.0 - 清理版
日期: 2025-06-23
"""

import os
import sys
import json
import time
import asyncio
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# 添加PowerAutomation到Python路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'PowerAutomation'))

# 導入新整合的組件
try:
    from enhanced_interaction_log_manager import EnhancedInteractionLogManager
    from simplified_rl_srt_adapter import SimplifiedRLSRTAdapter
    from replay_classifier import ReplayDataParser, IntelligentReplayClassifier, ReplayRLSRTIntegrator
except ImportError as e:
    print(f"警告: 無法導入新組件: {e}")

try:
    from core.enhanced_agent_core import EnhancedAgentCore
    from tools.enhanced_tool_registry import EnhancedToolRegistry
    from actions.action_executor import ActionExecutor
    from config.enhanced_config import EnhancedConfig
except ImportError as e:
    print(f"警告: 無法導入簡化Agent模組: {e}")
    print("將使用模擬模式運行")

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_admin_backend")

# 創建Flask應用
app = Flask(__name__)
CORS(app)

# 全局變量
interaction_log_manager = None
rl_srt_adapter = None
replay_integrator = None
agent_core = None
tool_registry = None
action_executor = None

# ==================== 初始化函數 ====================

def initialize_components():
    """初始化所有組件"""
    global interaction_log_manager, rl_srt_adapter, replay_integrator
    global agent_core, tool_registry, action_executor
    
    try:
        logger.info("🚀 開始初始化Agent Admin Backend組件...")
        
        # 初始化Enhanced Interaction Log Manager
        interaction_log_manager = EnhancedInteractionLogManager()
        logger.info("✅ Enhanced Interaction Log Manager 初始化完成")
        
        # 初始化Simplified RL SRT Adapter
        rl_srt_adapter = SimplifiedRLSRTAdapter()
        logger.info("✅ Simplified RL SRT Adapter 初始化完成")
        
        # 初始化Replay Integrator
        replay_integrator = ReplayRLSRTIntegrator(
            rl_adapter=rl_srt_adapter,
            log_manager=interaction_log_manager
        )
        logger.info("✅ Replay RLSRT Integrator 初始化完成")
        
        # 初始化簡化Agent架構組件
        try:
            config = EnhancedConfig()
            tool_registry = EnhancedToolRegistry()
            action_executor = ActionExecutor(tool_registry)
            agent_core = EnhancedAgentCore(config, tool_registry, action_executor)
            logger.info("✅ 簡化Agent架構 初始化完成")
        except Exception as e:
            logger.warning(f"簡化Agent架構初始化失敗: {e}")
            logger.info("將在模擬模式下運行")
        
        logger.info("🎉 所有組件初始化完成！")
        
    except Exception as e:
        logger.error(f"❌ 組件初始化失敗: {e}")
        raise

# ==================== 健康檢查API端點 ====================

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.1.0',
            'components': {
                'interaction_log_manager': interaction_log_manager is not None,
                'rl_srt_adapter': rl_srt_adapter is not None,
                'replay_integrator': replay_integrator is not None,
                'agent_core': agent_core is not None,
                'tool_registry': tool_registry is not None,
                'action_executor': action_executor is not None
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ==================== 系統信息API端點 ====================

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """獲取系統信息"""
    try:
        system_info = {
            'application': 'Agent Admin Backend',
            'version': '2.1.0',
            'description': '清理版後端API服務，移除UI功能',
            'components': [
                'Enhanced Interaction Log Manager',
                'Simplified RL SRT Adapter',
                'Replay Classifier',
                '增強版簡化Agent架構'
            ],
            'api_endpoints': [
                '/health',
                '/api/system/info',
                '/api/system/status',
                '/api/replay/process',
                '/api/replay/classify',
                '/api/learning/recommend',
                '/api/learning/statistics'
            ],
            'removed_features': [
                'Workflow Recording UI',
                'Web Frontend',
                'Static File Serving'
            ]
        }
        
        return jsonify({
            'success': True,
            'data': system_info
        })
        
    except Exception as e:
        logger.error(f"獲取系統信息失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """獲取系統狀態"""
    try:
        status = {
            'uptime': time.time(),
            'components_status': {
                'interaction_log_manager': {
                    'status': 'active' if interaction_log_manager else 'inactive',
                    'name': 'Enhanced Interaction Log Manager',
                    'description': '增強版交互日誌管理器'
                },
                'rl_srt_adapter': {
                    'status': 'active' if rl_srt_adapter else 'inactive',
                    'name': 'Simplified RL SRT Adapter',
                    'description': '簡化版強化學習SRT適配器'
                },
                'replay_integrator': {
                    'status': 'active' if replay_integrator else 'inactive',
                    'name': 'Replay RLSRT Integrator',
                    'description': 'Replay數據與RLSRT整合器'
                },
                'agent_core': {
                    'status': 'active' if agent_core else 'inactive',
                    'name': 'Enhanced Agent Core',
                    'description': '增強版Agent核心'
                }
            },
            'memory_usage': 'N/A',
            'active_sessions': 0
        }
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"獲取系統狀態失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== Replay Processing API端點 ====================

@app.route('/api/replay/process', methods=['POST'])
def process_replay_data():
    """處理replay數據進行學習"""
    try:
        data = request.get_json()
        replay_url = data.get('replay_url')
        replay_data = data.get('replay_data')
        
        if not replay_url and not replay_data:
            return jsonify({
                'success': False,
                'error': '需要提供replay_url或replay_data'
            }), 400
        
        # 處理replay數據
        learning_report = replay_integrator.process_replay_for_learning(
            replay_url or replay_data
        )
        
        return jsonify({
            'success': True,
            'data': learning_report
        })
        
    except Exception as e:
        logger.error(f"處理replay數據失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/replay/classify', methods=['POST'])
def classify_replay():
    """分類replay數據"""
    try:
        data = request.get_json()
        replay_data = data.get('replay_data')
        
        classifier = IntelligentReplayClassifier()
        classification_result = classifier.classify_and_learn(replay_data)
        
        return jsonify({
            'success': True,
            'data': classification_result
        })
        
    except Exception as e:
        logger.error(f"分類replay數據失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== RL SRT Learning API端點 ====================

@app.route('/api/learning/recommend', methods=['POST'])
def get_learning_recommendation():
    """獲取學習推薦"""
    try:
        data = request.get_json()
        context = data.get('context', {})
        
        recommendation = rl_srt_adapter.get_recommendation(context)
        
        return jsonify({
            'success': True,
            'data': {
                'recommended_action': recommendation.recommended_action,
                'confidence_score': recommendation.confidence_score,
                'reasoning': recommendation.reasoning,
                'alternative_actions': recommendation.alternative_actions,
                'expected_outcome': recommendation.expected_outcome,
                'strategy_type': recommendation.strategy_type.value,
                'learning_feedback': recommendation.learning_feedback
            }
        })
        
    except Exception as e:
        logger.error(f"獲取學習推薦失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/learning/statistics', methods=['GET'])
def get_learning_statistics():
    """獲取學習統計"""
    try:
        statistics = rl_srt_adapter.get_learning_statistics()
        
        return jsonify({
            'success': True,
            'data': statistics
        })
        
    except Exception as e:
        logger.error(f"獲取學習統計失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/learning/feedback', methods=['POST'])
def submit_learning_feedback():
    """提交學習反饋"""
    try:
        data = request.get_json()
        action_id = data.get('action_id')
        feedback_type = data.get('feedback_type')
        feedback_data = data.get('feedback_data', {})
        
        result = rl_srt_adapter.process_feedback(action_id, feedback_type, feedback_data)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"提交學習反饋失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 錯誤處理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'API端點不存在',
        'message': '請檢查API路徑是否正確'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '內部服務器錯誤',
        'message': '請聯繫系統管理員'
    }), 500

# ==================== 主程序 ====================

if __name__ == '__main__':
    try:
        # 初始化組件
        initialize_components()
        
        # 啟動Flask應用
        logger.info("🚀 啟動Agent Admin Backend (清理版)...")
        app.run(
            host='0.0.0.0',
            port=8081,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"❌ 應用啟動失敗: {e}")
        sys.exit(1)

