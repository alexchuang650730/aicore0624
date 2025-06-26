"""
參數化MCP服務器 - 極簡版本
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
import time

# 參數化MCP核心
class ParameterizedMCP:
    def __init__(self, experts):
        self.experts = experts
    
    def identify(self, request_text):
        """識別需要的專家"""
        return [expert for expert in self.experts.keys() if expert in request_text]
    
    async def ask_expert(self, expert, request_text):
        """問專家"""
        prompt = self.experts[expert].format(request=request_text)
        
        # 模擬LLM調用 (實際應該調用Claude/Gemini)
        await asyncio.sleep(0.1)
        
        # 根據專家類型返回專業回答
        if expert == "保險":
            return """【保險專家分析】
• 人力需求: 核保作業約需3-5人/千件保單
• 自動化率: 業界平均60-70%，領先公司可達80%
• OCR審核: 約佔總人力15-20%，每月0.5-1人月/千件
• 成本效益: 自動化可節省30-40%人力成本
• 建議: 優先導入AI輔助決策系統"""
        
        elif expert == "行政":
            return """【行政專家分析】
• 流程優化: 標準化作業可提升20-30%效率
• 文件管理: 數位化可減少50%紙本作業
• 人員配置: 建議採用專業分工制度
• 品質控制: 建立多層次審核機制
• 建議: 導入工作流管理系統"""
        
        elif expert == "核保":
            return """【核保專家分析】
• 風險評估: 建立智能風險分級制度
• 審核效率: 簡單案件可達90%自動化
• 專業判斷: 複雜案件仍需人工審核
• 法規合規: 確保符合金管會規範
• 建議: 建立核保知識庫系統"""
        
        elif expert == "理賠":
            return """【理賠專家分析】
• 理賠流程: 標準案件可24小時內完成
• 自動化率: 小額理賠可達70%自動化
• 客戶體驗: 提供即時理賠進度查詢
• 風險控制: 建立反詐騙機制
• 建議: 導入智能理賠系統"""
        
        else:
            return f"【{expert}專家】針對請求進行專業分析..."
    
    async def process(self, request_text):
        """處理請求"""
        needed_experts = self.identify(request_text) or [list(self.experts.keys())[0]]
        answers = []
        
        for expert in needed_experts:
            answer = await self.ask_expert(expert, request_text)
            answers.append(answer)
        
        # 聚合答案
        if len(answers) == 1:
            return answers[0]
        else:
            result = "\n\n".join(answers)
            result += "\n\n【綜合建議】\n整合各專家觀點，建議採用階段性導入策略，優先提升自動化率，同時保持人工審核的關鍵作用。"
            return result

# Flask應用
app = Flask(__name__)
CORS(app)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化MCP
insurance_experts = {
    "保險": "你是資深保險專家，請基於保險業專業知識分析: {request}",
    "行政": "你是行政管理專家，請從行政效率角度分析: {request}",
    "核保": "你是核保專家，請從風險評估角度分析: {request}",
    "理賠": "你是理賠專家，請從理賠流程角度分析: {request}"
}

mcp = ParameterizedMCP(insurance_experts)

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "mcp_type": "parameterized",
        "experts": list(mcp.experts.keys()),
        "timestamp": time.time()
    })

@app.route('/api/process', methods=['POST'])
def process_request():
    """處理請求"""
    try:
        data = request.get_json()
        request_text = data.get('request', '')
        
        if not request_text:
            return jsonify({"error": "請求內容不能為空"}), 400
        
        # 執行MCP處理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        start_time = time.time()
        result = loop.run_until_complete(mcp.process(request_text))
        processing_time = time.time() - start_time
        
        # 識別使用的專家
        identified_experts = mcp.identify(request_text) or [list(mcp.experts.keys())[0]]
        
        loop.close()
        
        return jsonify({
            "result": result,
            "experts_used": identified_experts,
            "expert_count": len(identified_experts),
            "processing_time": processing_time,
            "mcp_type": "parameterized"
        })
        
    except Exception as e:
        logger.error(f"處理請求失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/experts', methods=['GET'])
def get_experts():
    """獲取專家列表"""
    return jsonify({
        "experts": list(mcp.experts.keys()),
        "expert_prompts": {k: v[:50] + "..." for k, v in mcp.experts.items()},
        "total_experts": len(mcp.experts)
    })

@app.route('/api/identify', methods=['POST'])
def identify_experts():
    """識別專家"""
    try:
        data = request.get_json()
        request_text = data.get('request', '')
        
        if not request_text:
            return jsonify({"error": "請求內容不能為空"}), 400
        
        identified = mcp.identify(request_text)
        
        return jsonify({
            "request": request_text,
            "identified_experts": identified,
            "expert_count": len(identified),
            "all_experts": list(mcp.experts.keys())
        })
        
    except Exception as e:
        logger.error(f"識別專家失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/demo', methods=['POST'])
def demo_request():
    """演示請求"""
    try:
        data = request.get_json()
        demo_type = data.get('type', 'insurance')
        
        demo_requests = {
            'insurance': "臺銀人壽保單行政作業SOP大概要花多少人處理表單，自動化比率在業界有多高？",
            'admin': "保險公司行政流程如何優化，提升作業效率？",
            'underwriting': "核保作業如何建立智能風險評估機制？",
            'claims': "理賠流程如何實現自動化，提升客戶體驗？"
        }
        
        request_text = demo_requests.get(demo_type, demo_requests['insurance'])
        
        # 處理演示請求
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        start_time = time.time()
        result = loop.run_until_complete(mcp.process(request_text))
        processing_time = time.time() - start_time
        
        identified_experts = mcp.identify(request_text)
        
        loop.close()
        
        return jsonify({
            "demo_type": demo_type,
            "request": request_text,
            "result": result,
            "experts_used": identified_experts,
            "processing_time": processing_time
        })
        
    except Exception as e:
        logger.error(f"演示請求失敗: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 參數化MCP服務器啟動中...")
    logger.info(f"📋 已配置專家: {list(mcp.experts.keys())}")
    logger.info("📡 API端點:")
    logger.info("  - GET  /health          - 健康檢查")
    logger.info("  - POST /api/process     - 處理請求")
    logger.info("  - GET  /api/experts     - 獲取專家列表")
    logger.info("  - POST /api/identify    - 識別專家")
    logger.info("  - POST /api/demo        - 演示請求")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

