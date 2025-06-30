#!/usr/bin/env python3
"""
SmartUI Manus Integration
SmartUI与SmartInvention Manus模式的集成接口

提供SmartUI问答、实时响应、任务管理等功能
Version: 1.0.0
Author: Manus AI
Date: 2025-01-01
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

# 导入增强版SmartInvention MCP
from smartinvention_mcp_enhanced import SmartinventionManusModeMCP

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartUIQuestionClassifier:
    """SmartUI问题分类器"""
    
    def __init__(self):
        self.question_patterns = {
            "task_status": {
                "keywords": ["任务", "task", "状态", "status", "进度", "progress", "最新"],
                "patterns": [
                    r"最新.*任务",
                    r"任务.*状态",
                    r"进度.*如何",
                    r"task.*status",
                    r"latest.*task"
                ]
            },
            "file_checkin": {
                "keywords": ["文件", "file", "checkin", "提交", "检入", "签入", "需要"],
                "patterns": [
                    r"文件.*checkin",
                    r"需要.*提交",
                    r"哪些.*文件",
                    r"file.*status",
                    r"checkin.*状态"
                ]
            },
            "conversation_history": {
                "keywords": ["对话", "conversation", "聊天", "chat", "历史", "history", "记录"],
                "patterns": [
                    r"对话.*历史",
                    r"聊天.*记录",
                    r"conversation.*history",
                    r"chat.*log"
                ]
            },
            "agent_info": {
                "keywords": ["agent", "代理", "机器人", "bot", "助手", "AI"],
                "patterns": [
                    r"agent.*信息",
                    r"代理.*状态",
                    r"AI.*助手",
                    r"机器人.*情况"
                ]
            },
            "modification_tracking": {
                "keywords": ["修改", "modification", "变更", "change", "更新", "update"],
                "patterns": [
                    r"修改.*记录",
                    r"变更.*历史",
                    r"modification.*log",
                    r"change.*history"
                ]
            },
            "standards_compliance": {
                "keywords": ["标准", "standard", "规范", "specification", "合规", "compliance"],
                "patterns": [
                    r"标准.*检查",
                    r"规范.*验证",
                    r"compliance.*check",
                    r"standard.*review"
                ]
            }
        }
    
    def classify_question(self, question: str) -> Dict[str, Any]:
        """分类问题并提取关键信息"""
        question_lower = question.lower()
        
        classification_result = {
            "primary_category": "general",
            "confidence": 0.0,
            "matched_keywords": [],
            "matched_patterns": [],
            "extracted_entities": {}
        }
        
        max_score = 0
        best_category = "general"
        
        for category, config in self.question_patterns.items():
            score = 0
            matched_keywords = []
            matched_patterns = []
            
            # 检查关键词匹配
            for keyword in config["keywords"]:
                if keyword in question_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # 检查模式匹配
            for pattern in config["patterns"]:
                if re.search(pattern, question_lower):
                    score += 2  # 模式匹配权重更高
                    matched_patterns.append(pattern)
            
            if score > max_score:
                max_score = score
                best_category = category
                classification_result["matched_keywords"] = matched_keywords
                classification_result["matched_patterns"] = matched_patterns
        
        classification_result["primary_category"] = best_category
        classification_result["confidence"] = min(max_score / 5.0, 1.0)  # 归一化到0-1
        
        # 提取实体信息
        classification_result["extracted_entities"] = self._extract_entities(question)
        
        return classification_result
    
    def _extract_entities(self, question: str) -> Dict[str, Any]:
        """从问题中提取实体信息"""
        entities = {
            "task_ids": [],
            "file_names": [],
            "time_references": [],
            "numbers": []
        }
        
        # 提取任务ID模式
        task_patterns = [
            r"任务\s*(\d+)",
            r"task\s*(\d+)",
            r"T(\d+)",
            r"#(\d+)"
        ]
        
        for pattern in task_patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            entities["task_ids"].extend(matches)
        
        # 提取文件名
        file_patterns = [
            r"(\w+\.\w+)",  # 文件名.扩展名
            r"([a-zA-Z_]\w*\.py)",  # Python文件
            r"([a-zA-Z_]\w*\.js)",  # JavaScript文件
            r"([a-zA-Z_]\w*\.html)"  # HTML文件
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, question)
            entities["file_names"].extend(matches)
        
        # 提取时间引用
        time_patterns = [
            r"最新的?(\d+)个?",
            r"latest\s*(\d+)",
            r"过去(\d+)天",
            r"(\d+)\s*天前"
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            entities["time_references"].extend(matches)
        
        # 提取数字
        number_pattern = r"\b(\d+)\b"
        entities["numbers"] = re.findall(number_pattern, question)
        
        return entities

class SmartUIResponseGenerator:
    """SmartUI响应生成器"""
    
    def __init__(self, mcp_instance: SmartinventionManusModeMCP):
        self.mcp = mcp_instance
        self.classifier = SmartUIQuestionClassifier()
    
    async def generate_response(self, question: str, context: Dict = None) -> Dict[str, Any]:
        """生成智能响应"""
        try:
            # 分类问题
            classification = self.classifier.classify_question(question)
            category = classification["primary_category"]
            
            # 根据分类生成响应
            if category == "task_status":
                return await self._handle_task_status_question(question, classification, context)
            elif category == "file_checkin":
                return await self._handle_file_checkin_question(question, classification, context)
            elif category == "conversation_history":
                return await self._handle_conversation_question(question, classification, context)
            elif category == "agent_info":
                return await self._handle_agent_question(question, classification, context)
            elif category == "modification_tracking":
                return await self._handle_modification_question(question, classification, context)
            elif category == "standards_compliance":
                return await self._handle_standards_question(question, classification, context)
            else:
                return await self._handle_general_question(question, classification, context)
        
        except Exception as e:
            logger.error(f"生成响应失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "question": question,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_task_status_question(self, question: str, classification: Dict, context: Dict) -> Dict[str, Any]:
        """处理任务状态相关问题"""
        try:
            # 从实体中提取限制数量
            entities = classification.get("extracted_entities", {})
            numbers = entities.get("numbers", [])
            limit = int(numbers[0]) if numbers else 5
            
            # 获取最新任务数据
            result = await self.mcp.handle_request("get_latest_tasks_with_checkin", {"limit": limit})
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "获取任务数据失败",
                    "question": question
                }
            
            tasks = result.get("tasks", [])
            
            # 生成响应
            response_data = {
                "success": True,
                "question": question,
                "category": "task_status",
                "classification": classification,
                "data": {
                    "tasks": tasks,
                    "summary": self._generate_task_summary(tasks)
                },
                "answer": self._generate_task_answer(question, tasks, classification),
                "timestamp": datetime.now().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"处理任务状态问题失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_file_checkin_question(self, question: str, classification: Dict, context: Dict) -> Dict[str, Any]:
        """处理文件checkin相关问题"""
        try:
            # 获取checkin汇总
            result = await self.mcp.handle_request("get_checkin_summary", {})
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "获取checkin数据失败",
                    "question": question
                }
            
            summary = result.get("summary", {})
            
            response_data = {
                "success": True,
                "question": question,
                "category": "file_checkin",
                "classification": classification,
                "data": {
                    "checkin_summary": summary
                },
                "answer": self._generate_checkin_answer(question, summary, classification),
                "timestamp": datetime.now().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"处理文件checkin问题失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_conversation_question(self, question: str, classification: Dict, context: Dict) -> Dict[str, Any]:
        """处理对话历史相关问题"""
        try:
            # 获取对话历史
            result = await self.mcp.handle_request("get_conversations", {"limit": 50})
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "获取对话数据失败",
                    "question": question
                }
            
            conversations = result.get("conversations", [])
            
            response_data = {
                "success": True,
                "question": question,
                "category": "conversation_history",
                "classification": classification,
                "data": {
                    "conversations": conversations[:10],  # 只返回前10条
                    "total_count": len(conversations)
                },
                "answer": self._generate_conversation_answer(question, conversations, classification),
                "timestamp": datetime.now().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"处理对话问题失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_agent_question(self, question: str, classification: Dict, context: Dict) -> Dict[str, Any]:
        """处理Agent相关问题"""
        try:
            # 获取Agent汇总
            result = await self.mcp.handle_request("get_agent_summary", {})
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "获取Agent数据失败",
                    "question": question
                }
            
            summary = result.get("summary", {})
            
            response_data = {
                "success": True,
                "question": question,
                "category": "agent_info",
                "classification": classification,
                "data": {
                    "agent_summary": summary
                },
                "answer": self._generate_agent_answer(question, summary, classification),
                "timestamp": datetime.now().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"处理Agent问题失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_modification_question(self, question: str, classification: Dict, context: Dict) -> Dict[str, Any]:
        """处理修改记录相关问题"""
        try:
            # 获取最新任务的修改记录
            tasks_result = await self.mcp.handle_request("get_latest_tasks_with_checkin", {"limit": 5})
            
            if not tasks_result.get("success"):
                return {
                    "success": False,
                    "error": "获取修改数据失败",
                    "question": question
                }
            
            tasks = tasks_result.get("tasks", [])
            
            # 收集修改信息
            modification_summary = {
                "total_tasks": len(tasks),
                "total_files": sum(task.get("checkin_summary", {}).get("total_files", 0) for task in tasks),
                "modified_files": sum(task.get("checkin_summary", {}).get("modified", 0) for task in tasks),
                "pending_files": sum(task.get("checkin_summary", {}).get("pending", 0) for task in tasks)
            }
            
            response_data = {
                "success": True,
                "question": question,
                "category": "modification_tracking",
                "classification": classification,
                "data": {
                    "modification_summary": modification_summary,
                    "tasks": tasks
                },
                "answer": self._generate_modification_answer(question, modification_summary, classification),
                "timestamp": datetime.now().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"处理修改问题失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_standards_question(self, question: str, classification: Dict, context: Dict) -> Dict[str, Any]:
        """处理标准合规相关问题"""
        try:
            # 获取Manus标准
            result = await self.mcp.handle_request("get_manus_standards", {})
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "获取标准数据失败",
                    "question": question
                }
            
            standards = result.get("standards", {})
            
            response_data = {
                "success": True,
                "question": question,
                "category": "standards_compliance",
                "classification": classification,
                "data": {
                    "standards": standards
                },
                "answer": self._generate_standards_answer(question, standards, classification),
                "timestamp": datetime.now().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"处理标准问题失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_general_question(self, question: str, classification: Dict, context: Dict) -> Dict[str, Any]:
        """处理通用问题"""
        try:
            response_data = {
                "success": True,
                "question": question,
                "category": "general",
                "classification": classification,
                "data": {
                    "available_categories": list(self.classifier.question_patterns.keys()),
                    "suggestion": "请尝试询问任务状态、文件checkin、对话历史、Agent信息等相关问题"
                },
                "answer": f"我理解您询问的是：{question}。我可以帮您查询任务状态、文件checkin状态、对话历史、Agent信息、修改记录和标准合规等信息。请告诉我您具体想了解什么？",
                "timestamp": datetime.now().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"处理通用问题失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_task_summary(self, tasks: List[Dict]) -> Dict[str, Any]:
        """生成任务汇总"""
        summary = {
            "total_tasks": len(tasks),
            "status_distribution": {},
            "total_files": 0,
            "checkin_status_summary": {
                "checked_in": 0,
                "pending": 0,
                "modified": 0,
                "unknown": 0
            }
        }
        
        for task in tasks:
            # 统计任务状态
            status = task.get("status", "unknown")
            summary["status_distribution"][status] = summary["status_distribution"].get(status, 0) + 1
            
            # 统计文件checkin状态
            checkin_summary = task.get("checkin_summary", {})
            summary["total_files"] += checkin_summary.get("total_files", 0)
            summary["checkin_status_summary"]["checked_in"] += checkin_summary.get("checked_in", 0)
            summary["checkin_status_summary"]["pending"] += checkin_summary.get("pending", 0)
            summary["checkin_status_summary"]["modified"] += checkin_summary.get("modified", 0)
            summary["checkin_status_summary"]["unknown"] += checkin_summary.get("unknown", 0)
        
        return summary
    
    def _generate_task_answer(self, question: str, tasks: List[Dict], classification: Dict) -> str:
        """生成任务相关答案"""
        if not tasks:
            return "当前没有找到任务数据。"
        
        entities = classification.get("extracted_entities", {})
        
        if "最新" in question or "latest" in question.lower():
            task_names = [task.get("title", "未知任务") for task in tasks[:5]]
            return f"最新的{len(task_names)}个任务是：{', '.join(task_names)}。这些任务共包含{sum(task.get('checkin_summary', {}).get('total_files', 0) for task in tasks)}个文件。"
        
        elif "状态" in question or "status" in question.lower():
            summary = self._generate_task_summary(tasks)
            status_text = ", ".join([f"{status}: {count}个" for status, count in summary["status_distribution"].items()])
            return f"任务状态分布：{status_text}。文件checkin状态：已签入{summary['checkin_status_summary']['checked_in']}个，待处理{summary['checkin_status_summary']['pending']}个。"
        
        else:
            return f"找到{len(tasks)}个相关任务，总共包含{sum(task.get('checkin_summary', {}).get('total_files', 0) for task in tasks)}个文件。"
    
    def _generate_checkin_answer(self, question: str, summary: Dict, classification: Dict) -> str:
        """生成checkin相关答案"""
        if "error" in summary:
            return f"获取checkin信息时出现错误：{summary['error']}"
        
        total_files = summary.get("total_files", 0)
        status_dist = summary.get("status_distribution", {})
        
        if "需要" in question or "哪些" in question:
            pending = status_dist.get("pending", 0)
            modified = status_dist.get("modified", 0)
            return f"当前有{pending}个文件待checkin，{modified}个文件已修改需要重新checkin。总共{total_files}个文件中，需要处理的文件有{pending + modified}个。"
        
        else:
            status_text = ", ".join([f"{status}: {count}个" for status, count in status_dist.items()])
            return f"文件checkin状态分布：{status_text}。总计{total_files}个文件。"
    
    def _generate_conversation_answer(self, question: str, conversations: List[Dict], classification: Dict) -> str:
        """生成对话相关答案"""
        if not conversations:
            return "当前没有找到对话记录。"
        
        return f"找到{len(conversations)}条对话记录。最近的对话包含了任务讨论、文件操作、系统配置等内容。"
    
    def _generate_agent_answer(self, question: str, summary: Dict, classification: Dict) -> str:
        """生成Agent相关答案"""
        if "error" in summary:
            return f"获取Agent信息时出现错误：{summary['error']}"
        
        total_agents = summary.get("total_agents", 0)
        task_dist = summary.get("task_distribution", {})
        
        return f"当前系统中有{total_agents}个Agent。任务分布：{', '.join([f'任务{task}: {count}个Agent' for task, count in task_dist.items()])}。"
    
    def _generate_modification_answer(self, question: str, summary: Dict, classification: Dict) -> str:
        """生成修改记录相关答案"""
        total_files = summary.get("total_files", 0)
        modified_files = summary.get("modified_files", 0)
        pending_files = summary.get("pending_files", 0)
        
        return f"在{summary.get('total_tasks', 0)}个任务中，共有{total_files}个文件，其中{modified_files}个文件已修改，{pending_files}个文件待处理。"
    
    def _generate_standards_answer(self, question: str, standards: Dict, classification: Dict) -> str:
        """生成标准合规相关答案"""
        if not standards:
            return "当前没有找到标准数据。"
        
        standards_count = len([k for k in standards.keys() if k.endswith("_standards")])
        return f"系统中配置了{standards_count}类标准，包括编码标准、安全标准、测试标准等。所有标准都基于真实的Manus数据制定。"

# 初始化MCP实例
mcp_config = {
    "manus": {
        "base_url": "https://manus.im",
        "app_url": "https://manus.im/app/oXk20YJhBI530ArzGBJEJC",
        "auto_login": True
    }
}

mcp_instance = SmartinventionManusModeMCP(mcp_config)
response_generator = SmartUIResponseGenerator(mcp_instance)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "success": True,
        "service": "SmartUI Manus Integration",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/smartui-question', methods=['POST'])
def handle_smartui_question():
    """处理SmartUI问题的主要端点"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        context = data.get('context', {})
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        # 使用异步方式处理问题
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                response_generator.generate_response(question, context)
            )
        finally:
            loop.close()
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"处理SmartUI问题失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/manus-status', methods=['GET'])
def get_manus_status():
    """获取Manus模式状态"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 获取各种状态信息
            tasks_result = loop.run_until_complete(
                mcp_instance.handle_request("get_latest_tasks_with_checkin", {"limit": 5})
            )
            
            checkin_result = loop.run_until_complete(
                mcp_instance.handle_request("get_checkin_summary", {})
            )
            
            agent_result = loop.run_until_complete(
                mcp_instance.handle_request("get_agent_summary", {})
            )
            
        finally:
            loop.close()
        
        status = {
            "success": True,
            "manus_mode": "active",
            "tasks": tasks_result.get("tasks", [])[:3],  # 只返回前3个任务
            "checkin_summary": checkin_result.get("summary", {}),
            "agent_summary": agent_result.get("summary", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"获取Manus状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/initialize-mcp', methods=['POST'])
def initialize_mcp():
    """初始化MCP实例"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(mcp_instance.initialize())
        finally:
            loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"初始化MCP失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("启动SmartUI Manus Integration服务...")
    
    # 初始化MCP实例
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            init_result = loop.run_until_complete(mcp_instance.initialize())
            logger.info(f"MCP初始化结果: {init_result}")
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"MCP初始化失败: {e}")
    
    app.run(host='0.0.0.0', port=5003, debug=False)

