"""
Domain MCP 主服務器 - 整合所有核心組件
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
import sys
import os
import time
from typing import Dict, List, Any

# 添加核心模組路徑
sys.path.append('/home/ubuntu/aicore0622/PowerAutomation/core')

from domain_mcp_registry import (
    DomainMCPRegistry, DomainInfo, DomainResult, DomainMatch
)
from intelligent_domain_classifier import (
    IntelligentDomainClassifier, DomainClassificationRequest, DomainExpert
)
from self_evolution_system import SelfEvolutionSystem
from domain_mcp_implementations import TechDomainMCP, BusinessDomainMCP, CreativeDomainMCP

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 全局組件
domain_registry = None
domain_classifier = None
evolution_system = None

async def initialize_domain_mcp_system():
    """初始化Domain MCP系統"""
    global domain_registry, domain_classifier, evolution_system
    
    logger.info("🚀 初始化Domain MCP系統...")
    
    # 1. 初始化註冊表
    domain_registry = DomainMCPRegistry()
    
    # 2. 初始化智能分類器
    domain_classifier = IntelligentDomainClassifier()
    
    # 3. 初始化自我進化系統
    evolution_system = SelfEvolutionSystem()
    
    # 4. 註冊Domain MCP實例
    await register_domain_mcps()
    
    logger.info("✅ Domain MCP系統初始化完成")

async def register_domain_mcps():
    """註冊所有Domain MCP實例"""
    
    # 技術領域MCP
    tech_mcp = TechDomainMCP()
    tech_info = DomainInfo(
        domain_id="technology",
        domain_name="技術領域",
        capabilities=[
            "代碼分析和優化", "架構設計建議", "技術選型指導",
            "性能優化建議", "安全性評估", "最佳實踐推薦"
        ],
        confidence_threshold=0.7,
        keywords=[
            "代碼", "程式", "架構", "API", "數據庫", "性能", "優化",
            "python", "javascript", "react", "flask", "docker"
        ],
        description="專業的軟體技術領域處理，包括代碼分析、架構設計、性能優化等"
    )
    await domain_registry.register_domain_mcp(tech_info, tech_mcp)
    
    # 業務領域MCP
    business_mcp = BusinessDomainMCP()
    business_info = DomainInfo(
        domain_id="business",
        domain_name="業務領域",
        capabilities=[
            "商業模式分析", "市場策略建議", "競爭分析",
            "ROI評估", "風險評估", "業務流程優化"
        ],
        confidence_threshold=0.6,
        keywords=[
            "商業", "業務", "市場", "競爭", "策略", "ROI",
            "客戶", "產品", "銷售", "營銷", "投資"
        ],
        description="專業的商業領域分析，包括商業模式、市場策略、風險評估等"
    )
    await domain_registry.register_domain_mcp(business_info, business_mcp)
    
    # 創意領域MCP
    creative_mcp = CreativeDomainMCP()
    creative_info = DomainInfo(
        domain_id="creative",
        domain_name="創意領域",
        capabilities=[
            "創意概念生成", "設計建議", "內容創作",
            "品牌策略", "用戶體驗設計", "視覺設計指導"
        ],
        confidence_threshold=0.5,
        keywords=[
            "創意", "設計", "創作", "品牌", "視覺", "用戶體驗",
            "UI", "UX", "故事", "內容", "創新"
        ],
        description="專業的創意設計領域，包括創意生成、設計指導、品牌策略等"
    )
    await domain_registry.register_domain_mcp(creative_info, creative_mcp)
    
    logger.info(f"✅ 已註冊 {len(domain_registry.domain_mcps)} 個Domain MCP")

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    })

@app.route('/api/classify', methods=['POST'])
def classify_request():
    """智能領域分類"""
    try:
        data = request.get_json()
        request_text = data.get('request', '')
        
        if not request_text:
            return jsonify({"error": "請求內容不能為空"}), 400
        
        # 創建分類請求
        classification_request = DomainClassificationRequest(
            request_text=request_text,
            context=data.get('context', {}),
            user_preferences=data.get('preferences', {}),
            previous_domains=data.get('previous_domains', [])
        )
        
        # 執行分類
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            domain_classifier.classify_request(classification_request)
        )
        loop.close()
        
        return jsonify({
            "primary_domain": result.primary_domain,
            "confidence": result.confidence,
            "secondary_domains": result.secondary_domains,
            "reasoning": result.reasoning,
            "expert_insights": result.expert_insights
        })
        
    except Exception as e:
        logger.error(f"分類請求失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_request():
    """處理領域請求"""
    try:
        data = request.get_json()
        request_text = data.get('request', '')
        max_domains = data.get('max_domains', 3)
        
        if not request_text:
            return jsonify({"error": "請求內容不能為空"}), 400
        
        # 執行處理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            domain_registry.process_request_with_domains(
                request_text, 
                context=data.get('context', {})
            )
        )
        loop.close()
        
        # 格式化結果
        formatted_results = []
        for result in results:
            formatted_results.append({
                "domain_id": result.domain_id,
                "result_type": result.result_type,
                "content": result.content,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "recommendations": result.recommendations,
                "metadata": result.metadata
            })
        
        return jsonify({
            "results": formatted_results,
            "total_domains": len(formatted_results),
            "processing_summary": {
                "avg_confidence": sum(r.confidence for r in results) / len(results) if results else 0,
                "total_processing_time": sum(r.processing_time for r in results),
                "domains_involved": [r.domain_id for r in results]
            }
        })
        
    except Exception as e:
        logger.error(f"處理請求失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/evolve', methods=['POST'])
def trigger_evolution():
    """觸發自我進化"""
    try:
        data = request.get_json()
        request_text = data.get('request', '')
        actual_performance = data.get('performance', 0.6)
        
        if not request_text:
            return jsonify({"error": "請求內容不能為空"}), 400
        
        # 執行自我進化
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        evolution_result = loop.run_until_complete(
            evolution_system.process_request_with_evolution(request_text, actual_performance)
        )
        loop.close()
        
        # 格式化進化結果
        formatted_gaps = []
        for gap_result in evolution_result.get('gaps', []):
            gap = gap_result['gap']
            adapter = gap_result['adapter']
            invitation = gap_result['expert_invitation']
            
            formatted_gaps.append({
                "gap_id": gap.gap_id,
                "description": gap.description,
                "severity": gap.gap_severity,
                "current_performance": gap.current_performance,
                "target_performance": gap.target_performance,
                "adapter_generated": {
                    "adapter_id": adapter.adapter_id,
                    "name": adapter.name,
                    "expert_optimized": adapter.expert_optimized
                },
                "expert_invitation": {
                    "status": invitation['status'],
                    "expert_profile": gap.suggested_expert_profile
                }
            })
        
        return jsonify({
            "evolution_triggered": True,
            "gaps_identified": evolution_result['gaps_identified'],
            "gaps": formatted_gaps,
            "comparison": evolution_result['comparison']
        })
        
    except Exception as e:
        logger.error(f"自我進化失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/experts', methods=['GET'])
def get_experts():
    """獲取專家列表"""
    try:
        experts = domain_classifier.expert_registry.get_all_experts()
        
        formatted_experts = []
        for expert in experts:
            formatted_experts.append({
                "expert_id": expert.expert_id,
                "name": expert.name,
                "domain_id": expert.domain_id,
                "expertise_areas": expert.expertise_areas,
                "credentials": expert.credentials,
                "active": expert.active
            })
        
        return jsonify({
            "experts": formatted_experts,
            "total_experts": len(formatted_experts)
        })
        
    except Exception as e:
        logger.error(f"獲取專家列表失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/experts/invite', methods=['POST'])
def invite_expert():
    """邀請新專家"""
    try:
        data = request.get_json()
        
        # 執行專家邀請
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        invitation_message = loop.run_until_complete(
            domain_classifier.invite_expert(data)
        )
        loop.close()
        
        return jsonify({
            "invitation_sent": True,
            "message": invitation_message
        })
        
    except Exception as e:
        logger.error(f"邀請專家失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """獲取系統狀態"""
    try:
        # 獲取註冊表狀態
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        registry_status = loop.run_until_complete(domain_registry.get_registry_status())
        classifier_stats = loop.run_until_complete(domain_classifier.get_classification_statistics())
        evolution_status = loop.run_until_complete(evolution_system.get_evolution_status())
        
        loop.close()
        
        return jsonify({
            "system_status": "running",
            "registry": registry_status,
            "classifier": classifier_stats,
            "evolution": evolution_status,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"獲取系統狀態失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/demo', methods=['POST'])
def demo_request():
    """演示請求處理"""
    try:
        data = request.get_json()
        demo_type = data.get('type', 'tech')
        
        # 預設演示請求
        demo_requests = {
            'tech': "請幫我設計一個微服務架構，需要支持高並發和可擴展性",
            'business': "我想分析一下電商平台的商業模式和盈利策略",
            'creative': "請幫我設計一個科技公司的品牌視覺識別系統"
        }
        
        request_text = demo_requests.get(demo_type, demo_requests['tech'])
        
        # 1. 先進行分類
        classification_request = DomainClassificationRequest(request_text=request_text)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 分類
        classification_result = loop.run_until_complete(
            domain_classifier.classify_request(classification_request)
        )
        
        # 處理
        processing_results = loop.run_until_complete(
            domain_registry.process_request_with_domains(request_text)
        )
        
        # 自我進化（模擬性能評分）
        evolution_result = loop.run_until_complete(
            evolution_system.process_request_with_evolution(request_text, 0.75)
        )
        
        loop.close()
        
        return jsonify({
            "demo_type": demo_type,
            "request": request_text,
            "classification": {
                "primary_domain": classification_result.primary_domain,
                "confidence": classification_result.confidence,
                "reasoning": classification_result.reasoning
            },
            "processing": {
                "results_count": len(processing_results),
                "domains_involved": [r.domain_id for r in processing_results],
                "avg_confidence": sum(r.confidence for r in processing_results) / len(processing_results) if processing_results else 0
            },
            "evolution": {
                "gaps_identified": evolution_result['gaps_identified'],
                "needs_improvement": evolution_result['comparison']['needs_improvement']
            }
        })
        
    except Exception as e:
        logger.error(f"演示請求失敗: {e}")
        return jsonify({"error": str(e)}), 500

def run_server():
    """運行服務器"""
    # 初始化系統
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_domain_mcp_system())
    loop.close()
    
    logger.info("🌟 Domain MCP服務器啟動中...")
    logger.info("📡 API端點:")
    logger.info("  - GET  /health           - 健康檢查")
    logger.info("  - POST /api/classify     - 智能領域分類")
    logger.info("  - POST /api/process      - 處理領域請求")
    logger.info("  - POST /api/evolve       - 觸發自我進化")
    logger.info("  - GET  /api/experts      - 獲取專家列表")
    logger.info("  - POST /api/experts/invite - 邀請新專家")
    logger.info("  - GET  /api/status       - 獲取系統狀態")
    logger.info("  - POST /api/demo         - 演示請求處理")
    
    # 啟動Flask服務器
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    run_server()

