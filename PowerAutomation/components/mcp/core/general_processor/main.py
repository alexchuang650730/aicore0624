"""
General_Processor MCP 組件
統一的通用處理器MCP組件，整合default_processor和general_processor的所有功能
"""

import time
import json
import logging
import asyncio
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    """處理模式"""
    DEFAULT = "default"      # 默認回退模式
    GENERAL = "general"      # 通用處理模式
    TEXT = "text"           # 文本處理模式
    JSON = "json"           # JSON處理模式
    AUTO = "auto"           # 自動選擇模式

@dataclass
class ProcessingResult:
    """處理結果"""
    success: bool
    data: Any
    mode_used: str
    execution_time: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return asdict(self)

class GeneralProcessorMCP:
    """
    統一的通用處理器MCP組件
    整合default_processor和general_processor的所有功能
    
    功能特點:
    1. 五種處理模式：Default, General, Text, JSON, Auto
    2. 智能模式選擇：自動檢測輸入類型並選擇最佳模式
    3. 專家洞察處理：專門處理包含專家分析的複雜數據
    4. 向後兼容：完全替代原有的default_processor和general_processor
    """
    
    def __init__(self):
        self.component_name = "General_Processor MCP"
        self.version = "2.0.0"
        self.description = "統一的通用處理器MCP組件，整合多種處理能力"
        
        # 能力定義
        self.capabilities = {
            "general_processing": {
                "description": "通用處理能力，支持多種數據格式",
                "input_types": ["text", "json", "auto"],
                "output_types": ["text", "json"],
                "modes": ["default", "general", "auto"]
            },
            "text_processing": {
                "description": "專業文本處理和分析能力",
                "input_types": ["text"],
                "output_types": ["text", "json"],
                "modes": ["text", "general", "auto"]
            },
            "json_processing": {
                "description": "JSON數據處理和轉換能力",
                "input_types": ["json"],
                "output_types": ["json", "text"],
                "modes": ["json", "default", "auto"]
            },
            "fallback_processing": {
                "description": "系統回退處理能力，確保穩定性",
                "input_types": ["any"],
                "output_types": ["text", "json"],
                "modes": ["default", "auto"]
            },
            "auto_processing": {
                "description": "智能自動處理能力，自動選擇最佳模式",
                "input_types": ["any"],
                "output_types": ["text", "json"],
                "modes": ["auto"]
            },
            "expert_insight_processing": {
                "description": "專家洞察處理能力，整合多專家分析",
                "input_types": ["dict_with_expert_insights"],
                "output_types": ["json"],
                "modes": ["general", "auto"]
            }
        }
        
        # 執行統計
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'mode_usage': {mode.value: 0 for mode in ProcessingMode},
            'average_execution_time': 0.0,
            'success_rate': 0.0,
            'last_execution_time': None
        }
        
        logger.info(f"{self.component_name} v{self.version} 初始化完成")
    
    async def process(self, data: Any, mode: str = "auto", options: Dict[str, Any] = None) -> ProcessingResult:
        """
        統一的處理接口
        
        Args:
            data: 要處理的數據
            mode: 處理模式 (default, general, text, json, auto)
            options: 額外選項
        
        Returns:
            ProcessingResult: 處理結果
        """
        start_time = time.time()
        options = options or {}
        
        logger.info(f"🔄 {self.component_name} 開始處理，模式: {mode}")
        
        try:
            # 驗證模式
            if mode not in [m.value for m in ProcessingMode]:
                logger.warning(f"未知模式 {mode}，回退到auto模式")
                mode = "auto"
            
            # 自動模式：智能選擇最佳處理模式
            if mode == "auto":
                mode = await self._auto_select_mode(data)
                logger.info(f"🎯 自動選擇模式: {mode}")
            
            # 根據模式執行處理
            if mode == "default":
                result_data = await self._default_processing(data, options)
            elif mode == "general":
                result_data = await self._general_processing(data, options)
            elif mode == "text":
                result_data = await self._text_processing(data, options)
            elif mode == "json":
                result_data = await self._json_processing(data, options)
            else:
                # 未知模式，回退到default
                logger.warning(f"處理模式 {mode} 不支持，回退到default模式")
                mode = "default"
                result_data = await self._default_processing(data, options)
            
            execution_time = time.time() - start_time
            
            # 創建處理結果
            result = ProcessingResult(
                success=True,
                data=result_data,
                mode_used=mode,
                execution_time=execution_time,
                metadata={
                    "component": self.component_name,
                    "version": self.version,
                    "input_type": type(data).__name__,
                    "processing_mode": mode,
                    "options_used": options,
                    "timestamp": time.time(),
                    "capabilities_applied": self._get_applied_capabilities(mode)
                }
            )
            
            # 更新統計
            self._update_execution_stats(result)
            
            logger.info(f"✅ 處理完成，模式: {mode}，耗時: {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ 處理失敗: {str(e)}")
            
            result = ProcessingResult(
                success=False,
                data=f"處理失敗: {str(e)}",
                mode_used=mode,
                execution_time=execution_time,
                metadata={
                    "component": self.component_name,
                    "error": str(e), 
                    "input_type": type(data).__name__,
                    "timestamp": time.time()
                }
            )
            
            self._update_execution_stats(result)
            return result
    
    async def _auto_select_mode(self, data: Any) -> str:
        """自動選擇最佳處理模式"""
        
        # 檢查數據類型和內容
        if isinstance(data, dict):
            # 檢查是否包含專家洞察
            if "expert_insights" in data or "expert_analysis" in data:
                return "general"  # 有專家洞察，使用通用模式
            elif "content" in data and "context" in data:
                return "general"  # 結構化請求數據
            else:
                return "json"     # 純JSON數據
        
        elif isinstance(data, str):
            # 嘗試解析為JSON
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict) and ("expert_insights" in parsed or "content" in parsed):
                    return "general"
                else:
                    return "json"
            except:
                # 檢查文本特徵
                if len(data) > 1000 or '\n' in data:
                    return "text"     # 長文本或多行文本
                else:
                    return "text"     # 短文本
        
        elif isinstance(data, list):
            return "json"         # 列表數據
        
        else:
            return "default"      # 其他類型，使用默認模式
    
    async def _default_processing(self, data: Any, options: Dict) -> Any:
        """默認處理模式 - 最強兼容性，確保系統穩定性"""
        logger.info("🛡️ 執行默認處理模式")
        
        # 處理各種數據類型
        if isinstance(data, dict):
            # 處理字典數據
            processed_data = {
                "processing_result": {
                    "status": "success",
                    "mode": "default",
                    "message": "數據已通過默認模式成功處理"
                },
                "original_data": data,
                "data_analysis": {
                    "type": "dictionary",
                    "key_count": len(data),
                    "keys": list(data.keys())[:10],  # 只顯示前10個鍵
                    "has_nested_data": any(isinstance(v, (dict, list)) for v in data.values())
                },
                "capabilities_applied": ["general_processing", "fallback_processing"],
                "processing_metadata": {
                    "component": self.component_name,
                    "mode": "default",
                    "timestamp": time.time()
                }
            }
            
            # 如果包含專家洞察，進行特殊處理
            if "expert_insights" in data:
                expert_summary = []
                for insight in data["expert_insights"]:
                    expert_summary.append({
                        "expert_type": insight.get('expert_type', 'unknown'),
                        "analysis_preview": insight.get('analysis', '')[:100] + "..." if len(insight.get('analysis', '')) > 100 else insight.get('analysis', ''),
                        "recommendation_count": len(insight.get('recommendations', []))
                    })
                
                processed_data["expert_analysis_summary"] = {
                    "total_experts": len(data["expert_insights"]),
                    "expert_summaries": expert_summary,
                    "processing_note": "專家洞察已通過默認模式處理"
                }
            
            return processed_data
        
        elif isinstance(data, str):
            # 處理文本數據
            return {
                "processing_result": {
                    "status": "success",
                    "mode": "default",
                    "message": "文本已通過默認模式處理"
                },
                "original_text": data,
                "text_analysis": {
                    "length": len(data),
                    "word_count": len(data.split()),
                    "line_count": len(data.split('\n')),
                    "preview": data[:200] + "..." if len(data) > 200 else data
                },
                "capabilities_applied": ["general_processing", "text_processing"],
                "processing_metadata": {
                    "component": self.component_name,
                    "mode": "default",
                    "timestamp": time.time()
                }
            }
        
        else:
            # 處理其他類型
            return {
                "processing_result": {
                    "status": "success",
                    "mode": "default",
                    "message": f"數據類型 {type(data).__name__} 已通過默認模式處理"
                },
                "original_data": str(data),
                "data_analysis": {
                    "type": type(data).__name__,
                    "string_representation": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                },
                "capabilities_applied": ["fallback_processing"],
                "processing_metadata": {
                    "component": self.component_name,
                    "mode": "default",
                    "timestamp": time.time()
                }
            }
    
    async def _general_processing(self, data: Any, options: Dict) -> Any:
        """通用處理模式 - 處理一般性任務和專家洞察"""
        logger.info("⚙️ 執行通用處理模式")
        
        if isinstance(data, dict) and ("expert_insights" in data or "expert_analysis" in data):
            # 處理包含專家洞察的數據
            content = data.get("content", "")
            context = data.get("context", {})
            expert_insights = data.get("expert_insights", data.get("expert_analysis", []))
            
            # 分析專家洞察
            expert_analysis = []
            all_recommendations = []
            confidence_scores = []
            
            for insight in expert_insights:
                expert_type = insight.get("expert_type", "unknown")
                analysis = insight.get("analysis", "")
                recommendations = insight.get("recommendations", [])
                confidence = insight.get("confidence", 0.8)
                
                expert_analysis.append({
                    "expert": expert_type,
                    "analysis_summary": analysis[:300] + "..." if len(analysis) > 300 else analysis,
                    "key_recommendations": recommendations[:5],  # 只取前5個建議
                    "confidence": confidence,
                    "recommendation_count": len(recommendations)
                })
                
                all_recommendations.extend(recommendations)
                confidence_scores.append(confidence)
            
            # 計算綜合信心度
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # 去重並排序建議
            unique_recommendations = list(dict.fromkeys(all_recommendations))  # 保持順序的去重
            
            return {
                "processing_result": {
                    "status": "success",
                    "mode": "general",
                    "message": f"通用模式成功處理了來自 {len(expert_insights)} 位專家的洞察"
                },
                "original_content": content,
                "context_summary": context,
                "expert_analysis": {
                    "total_experts": len(expert_insights),
                    "expert_details": expert_analysis,
                    "average_confidence": round(avg_confidence, 2)
                },
                "consolidated_recommendations": {
                    "total_recommendations": len(all_recommendations),
                    "unique_recommendations": unique_recommendations[:20],  # 只顯示前20個
                    "recommendation_sources": len(expert_insights)
                },
                "processing_summary": {
                    "experts_consulted": [exp["expert"] for exp in expert_analysis],
                    "total_insights": len(expert_insights),
                    "processing_quality": "high" if avg_confidence > 0.8 else "medium" if avg_confidence > 0.6 else "low"
                },
                "capabilities_applied": ["general_processing", "expert_insight_processing"],
                "processing_metadata": {
                    "component": self.component_name,
                    "mode": "general",
                    "timestamp": time.time()
                }
            }
        
        else:
            # 處理一般數據
            data_str = str(data)
            complexity = "simple" if len(data_str) < 100 else "medium" if len(data_str) < 1000 else "complex"
            
            return {
                "processing_result": {
                    "status": "success",
                    "mode": "general",
                    "message": "數據已通過通用模式成功處理"
                },
                "input_summary": data_str[:300] + "..." if len(data_str) > 300 else data_str,
                "data_characteristics": {
                    "type": type(data).__name__,
                    "size": len(data_str),
                    "complexity": complexity,
                    "estimated_processing_difficulty": complexity
                },
                "processing_analysis": {
                    "data_structure": "structured" if isinstance(data, (dict, list)) else "unstructured",
                    "processing_approach": "general_purpose",
                    "quality_assessment": "standard"
                },
                "capabilities_applied": ["general_processing"],
                "processing_metadata": {
                    "component": self.component_name,
                    "mode": "general",
                    "timestamp": time.time()
                }
            }
    
    async def _text_processing(self, data: Any, options: Dict) -> Any:
        """文本處理模式 - 專門處理文本數據"""
        logger.info("📝 執行文本處理模式")
        
        text = str(data)
        
        # 文本分析
        words = text.split()
        lines = text.split('\n')
        sentences = text.split('.')
        
        # 計算文本特徵
        features = {
            "basic_stats": {
                "character_count": len(text),
                "word_count": len(words),
                "line_count": len(lines),
                "sentence_count": len([s for s in sentences if s.strip()]),
                "paragraph_count": len([p for p in text.split('\n\n') if p.strip()])
            },
            "content_analysis": {
                "average_word_length": round(sum(len(word) for word in words) / len(words), 2) if words else 0,
                "average_sentence_length": round(len(words) / len([s for s in sentences if s.strip()]), 2) if sentences else 0,
                "has_numbers": any(char.isdigit() for char in text),
                "has_special_chars": any(not char.isalnum() and not char.isspace() for char in text),
                "has_urls": "http" in text.lower() or "www." in text.lower(),
                "has_emails": "@" in text and "." in text
            },
            "language_features": {
                "uppercase_ratio": round(sum(1 for c in text if c.isupper()) / len(text), 3) if text else 0,
                "punctuation_density": round(sum(1 for c in text if c in '.,!?;:') / len(text), 3) if text else 0,
                "whitespace_ratio": round(sum(1 for c in text if c.isspace()) / len(text), 3) if text else 0
            }
        }
        
        # 文本分類
        text_type = "unknown"
        if len(text) < 50:
            text_type = "short_text"
        elif len(lines) > 10:
            text_type = "multi_line_document"
        elif any(keyword in text.lower() for keyword in ["api", "function", "class", "import"]):
            text_type = "code_or_technical"
        elif any(keyword in text.lower() for keyword in ["分析", "建議", "專家", "處理"]):
            text_type = "analysis_or_report"
        else:
            text_type = "general_text"
        
        return {
            "processing_result": {
                "status": "success",
                "mode": "text",
                "message": f"文本處理完成：{features['basic_stats']['word_count']} 詞，{features['basic_stats']['character_count']} 字符"
            },
            "original_text": text,
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "text_features": features,
            "text_classification": {
                "type": text_type,
                "complexity": "simple" if len(text) < 200 else "medium" if len(text) < 1000 else "complex",
                "readability": "high" if features["content_analysis"]["average_word_length"] < 6 else "medium"
            },
            "processing_insights": {
                "dominant_content": "text_heavy" if len(words) > 100 else "concise",
                "structure_quality": "well_structured" if len(lines) > 1 and len([p for p in text.split('\n\n') if p.strip()]) > 1 else "simple",
                "information_density": "high" if len(words) / len(text) > 0.1 else "low"
            },
            "capabilities_applied": ["text_processing"],
            "processing_metadata": {
                "component": self.component_name,
                "mode": "text",
                "timestamp": time.time()
            }
        }
    
    async def _json_processing(self, data: Any, options: Dict) -> Any:
        """JSON處理模式 - 專門處理JSON數據"""
        logger.info("🔧 執行JSON處理模式")
        
        try:
            # 確保數據是JSON格式
            if isinstance(data, str):
                json_data = json.loads(data)
            else:
                json_data = data
            
            # JSON結構分析
            def analyze_json_structure(obj, depth=0, max_depth=5):
                if depth > max_depth:
                    return {"type": "deep_object", "depth_exceeded": True, "max_depth_reached": max_depth}
                
                if isinstance(obj, dict):
                    nested_analysis = {}
                    if depth < 2:  # 只分析前兩層
                        for k, v in list(obj.items())[:10]:  # 只分析前10個鍵
                            nested_analysis[k] = analyze_json_structure(v, depth+1, max_depth)
                    
                    return {
                        "type": "object",
                        "keys": list(obj.keys())[:20],  # 只顯示前20個鍵
                        "key_count": len(obj),
                        "nested_structure": nested_analysis,
                        "has_nested_objects": any(isinstance(v, dict) for v in obj.values()),
                        "has_arrays": any(isinstance(v, list) for v in obj.values())
                    }
                elif isinstance(obj, list):
                    element_types = []
                    sample_elements = []
                    for item in obj[:5]:  # 只檢查前5個元素
                        element_types.append(type(item).__name__)
                        if len(sample_elements) < 3:
                            sample_elements.append(analyze_json_structure(item, depth+1, max_depth))
                    
                    return {
                        "type": "array",
                        "length": len(obj),
                        "element_types": list(set(element_types)),
                        "sample_elements": sample_elements,
                        "is_homogeneous": len(set(element_types)) == 1
                    }
                else:
                    return {
                        "type": type(obj).__name__,
                        "value_preview": str(obj)[:100] + "..." if len(str(obj)) > 100 else str(obj),
                        "value_length": len(str(obj))
                    }
            
            structure_analysis = analyze_json_structure(json_data)
            
            # 計算JSON複雜度
            json_str = json.dumps(json_data, ensure_ascii=False)
            complexity_score = 0
            complexity_score += len(json_str) // 1000  # 大小因子
            complexity_score += str(json_data).count('{') + str(json_data).count('[')  # 嵌套因子
            
            complexity_level = "simple" if complexity_score < 5 else "medium" if complexity_score < 20 else "complex"
            
            return {
                "processing_result": {
                    "status": "success",
                    "mode": "json",
                    "message": "JSON數據結構分析完成"
                },
                "original_data": json_data,
                "structure_analysis": structure_analysis,
                "data_metrics": {
                    "total_size_bytes": len(json_str),
                    "total_size_chars": len(json_str),
                    "complexity_score": complexity_score,
                    "complexity_level": complexity_level,
                    "nesting_depth": self._calculate_max_depth(json_data),
                    "total_keys": self._count_total_keys(json_data),
                    "total_values": self._count_total_values(json_data)
                },
                "data_quality": {
                    "structure_validity": "valid",
                    "data_consistency": "consistent" if isinstance(json_data, (dict, list)) else "simple",
                    "information_richness": "high" if complexity_score > 10 else "medium" if complexity_score > 3 else "low"
                },
                "processing_insights": {
                    "recommended_usage": "structured_data_processing" if isinstance(json_data, dict) else "list_processing" if isinstance(json_data, list) else "simple_value",
                    "optimization_suggestions": self._get_json_optimization_suggestions(json_data, complexity_score)
                },
                "capabilities_applied": ["json_processing"],
                "processing_metadata": {
                    "component": self.component_name,
                    "mode": "json",
                    "timestamp": time.time()
                }
            }
            
        except json.JSONDecodeError as e:
            return {
                "processing_result": {
                    "status": "error",
                    "mode": "json",
                    "message": f"JSON解析失敗: {str(e)}"
                },
                "error_details": {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "error_position": getattr(e, 'pos', 'unknown')
                },
                "original_data": str(data)[:500] + "..." if len(str(data)) > 500 else str(data),
                "fallback_processing": {
                    "applied": True,
                    "method": "text_processing",
                    "note": "已轉為文本處理模式"
                },
                "capabilities_applied": ["json_processing", "fallback_processing"],
                "processing_metadata": {
                    "component": self.component_name,
                    "mode": "json",
                    "timestamp": time.time()
                }
            }
    
    def _calculate_max_depth(self, obj, current_depth=0):
        """計算JSON最大嵌套深度"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_max_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_max_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def _count_total_keys(self, obj):
        """計算JSON中總鍵數"""
        if isinstance(obj, dict):
            return len(obj) + sum(self._count_total_keys(v) for v in obj.values())
        elif isinstance(obj, list):
            return sum(self._count_total_keys(item) for item in obj)
        else:
            return 0
    
    def _count_total_values(self, obj):
        """計算JSON中總值數"""
        if isinstance(obj, dict):
            return len(obj) + sum(self._count_total_values(v) for v in obj.values())
        elif isinstance(obj, list):
            return len(obj) + sum(self._count_total_values(item) for item in obj)
        else:
            return 1
    
    def _get_json_optimization_suggestions(self, data, complexity_score):
        """獲取JSON優化建議"""
        suggestions = []
        
        if complexity_score > 20:
            suggestions.append("考慮分解為更小的數據塊")
            suggestions.append("使用數據壓縮技術")
        
        if isinstance(data, dict) and len(data) > 50:
            suggestions.append("考慮使用索引或分頁")
        
        if isinstance(data, list) and len(data) > 100:
            suggestions.append("考慮實現懶加載")
        
        if self._calculate_max_depth(data) > 5:
            suggestions.append("考慮扁平化數據結構")
        
        return suggestions if suggestions else ["數據結構已優化"]
    
    def _get_applied_capabilities(self, mode: str) -> List[str]:
        """獲取應用的能力列表"""
        capability_mapping = {
            "default": ["general_processing", "fallback_processing"],
            "general": ["general_processing", "expert_insight_processing"],
            "text": ["text_processing"],
            "json": ["json_processing"],
            "auto": ["auto_processing"]
        }
        return capability_mapping.get(mode, ["general_processing"])
    
    def _update_execution_stats(self, result: ProcessingResult):
        """更新執行統計"""
        self.execution_stats['total_executions'] += 1
        
        if result.success:
            self.execution_stats['successful_executions'] += 1
        else:
            self.execution_stats['failed_executions'] += 1
        
        # 更新模式使用統計
        mode = result.mode_used
        if mode in self.execution_stats['mode_usage']:
            self.execution_stats['mode_usage'][mode] += 1
        
        # 更新平均執行時間
        current_avg = self.execution_stats['average_execution_time']
        total_executions = self.execution_stats['total_executions']
        self.execution_stats['average_execution_time'] = (
            (current_avg * (total_executions - 1) + result.execution_time) / total_executions
        )
        
        # 更新成功率
        self.execution_stats['success_rate'] = (
            self.execution_stats['successful_executions'] / total_executions
        )
        
        # 更新最後執行時間
        self.execution_stats['last_execution_time'] = time.time()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """獲取能力描述"""
        return {
            "component_name": self.component_name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_modes": [mode.value for mode in ProcessingMode],
            "mode_descriptions": {
                "default": "默認回退模式，最強兼容性",
                "general": "通用處理模式，處理專家洞察",
                "text": "文本處理模式，專業文本分析",
                "json": "JSON處理模式，結構化數據分析",
                "auto": "自動選擇模式，智能模式選擇"
            },
            "statistics": self.execution_stats,
            "features": [
                "智能模式選擇",
                "專家洞察處理",
                "多格式數據支持",
                "向後兼容性",
                "實時統計監控"
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        current_time = time.time()
        last_execution = self.execution_stats.get('last_execution_time')
        
        # 計算健康狀態
        health_status = "healthy"
        if self.execution_stats['total_executions'] > 0:
            if self.execution_stats['success_rate'] < 0.8:
                health_status = "degraded"
            elif self.execution_stats['success_rate'] < 0.5:
                health_status = "unhealthy"
        
        return {
            "status": health_status,
            "component": self.component_name,
            "version": self.version,
            "uptime_status": "running",
            "health_metrics": {
                "total_executions": self.execution_stats['total_executions'],
                "success_rate": round(self.execution_stats['success_rate'], 3),
                "average_execution_time": round(self.execution_stats['average_execution_time'], 3),
                "last_execution_ago": round(current_time - last_execution, 2) if last_execution else None
            },
            "capabilities_status": {
                "total_capabilities": len(self.capabilities),
                "modes_available": len(ProcessingMode),
                "auto_mode_enabled": True
            },
            "performance_indicators": {
                "response_time": "optimal" if self.execution_stats['average_execution_time'] < 1.0 else "acceptable",
                "reliability": "high" if self.execution_stats['success_rate'] > 0.9 else "medium",
                "throughput": "normal"
            },
            "timestamp": current_time
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """獲取詳細統計信息"""
        return {
            "execution_statistics": self.execution_stats,
            "mode_distribution": {
                mode: {
                    "count": count,
                    "percentage": round(count / max(self.execution_stats['total_executions'], 1) * 100, 2)
                }
                for mode, count in self.execution_stats['mode_usage'].items()
            },
            "performance_metrics": {
                "average_execution_time": self.execution_stats['average_execution_time'],
                "success_rate": self.execution_stats['success_rate'],
                "total_processing_time": self.execution_stats['average_execution_time'] * self.execution_stats['total_executions']
            },
            "component_info": {
                "name": self.component_name,
                "version": self.version,
                "capabilities_count": len(self.capabilities),
                "modes_count": len(ProcessingMode)
            }
        }

# 工廠函數
def create_general_processor_mcp() -> GeneralProcessorMCP:
    """創建General_Processor MCP實例"""
    return GeneralProcessorMCP()

# 向後兼容性支持
class LegacyProcessorAdapter:
    """向後兼容性適配器"""
    
    def __init__(self, general_processor: GeneralProcessorMCP):
        self.general_processor = general_processor
    
    async def default_processor_process(self, data: Any) -> Dict[str, Any]:
        """模擬舊的default_processor行為"""
        result = await self.general_processor.process(data, mode="default")
        return result.to_dict()
    
    async def general_processor_process(self, data: Any) -> Dict[str, Any]:
        """模擬舊的general_processor行為"""
        result = await self.general_processor.process(data, mode="general")
        return result.to_dict()

# 示例使用
async def example_usage():
    """示例用法"""
    # 創建General_Processor MCP實例
    processor = create_general_processor_mcp()
    
    # 測試不同模式
    test_data = {
        "content": "測試內容",
        "expert_insights": [
            {
                "expert_type": "technical_expert",
                "analysis": "技術分析結果",
                "recommendations": ["建議1", "建議2"],
                "confidence": 0.9
            }
        ]
    }
    
    # 自動模式處理
    result = await processor.process(test_data)
    print(f"處理結果: {result.success}, 使用模式: {result.mode_used}")
    
    # 獲取能力信息
    capabilities = await processor.get_capabilities()
    print(f"組件能力: {len(capabilities['capabilities'])} 種")
    
    # 健康檢查
    health = await processor.health_check()
    print(f"健康狀態: {health['status']}")

if __name__ == "__main__":
    asyncio.run(example_usage())

