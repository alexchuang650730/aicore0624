"""
測試專家配置 - 自動識別測試相關請求並推薦 Test Flow MCP
"""

from datetime import datetime
from typing import List, Dict, Any
from components.dynamic_expert_registry import (
    ExpertProfile, ExpertCapability, ExpertType, ExpertStatus
)

def create_testing_expert() -> ExpertProfile:
    """創建測試專家配置"""
    
    # 定義測試專家的核心能力
    testing_capabilities = [
        ExpertCapability(
            name="unit_testing",
            description="單元測試設計和執行",
            skill_level="expert",
            domain="testing",
            keywords=["unit test", "unittest", "pytest", "test case", "單元測試"],
            confidence=0.95,
            source="base_system"
        ),
        ExpertCapability(
            name="integration_testing",
            description="整合測試設計和執行",
            skill_level="expert", 
            domain="testing",
            keywords=["integration test", "api test", "整合測試", "接口測試"],
            confidence=0.92,
            source="base_system"
        ),
        ExpertCapability(
            name="performance_testing",
            description="性能測試和負載測試",
            skill_level="advanced",
            domain="testing",
            keywords=["performance test", "load test", "stress test", "性能測試", "負載測試"],
            confidence=0.88,
            source="base_system"
        ),
        ExpertCapability(
            name="test_automation",
            description="測試自動化框架和工具",
            skill_level="expert",
            domain="testing",
            keywords=["test automation", "selenium", "cypress", "自動化測試", "測試框架"],
            confidence=0.93,
            source="base_system"
        ),
        ExpertCapability(
            name="test_flow_management",
            description="測試流程管理和協調",
            skill_level="expert",
            domain="testing",
            keywords=["test flow", "test management", "test coordination", "測試流程", "測試管理"],
            confidence=0.96,
            source="base_system"
        ),
        ExpertCapability(
            name="quality_assurance",
            description="質量保證和測試策略",
            skill_level="expert",
            domain="testing",
            keywords=["quality assurance", "qa", "test strategy", "質量保證", "測試策略"],
            confidence=0.94,
            source="base_system"
        ),
        ExpertCapability(
            name="test_data_management",
            description="測試數據管理和準備",
            skill_level="advanced",
            domain="testing",
            keywords=["test data", "data preparation", "mock data", "測試數據", "數據準備"],
            confidence=0.87,
            source="base_system"
        ),
        ExpertCapability(
            name="deployment_verification",
            description="部署驗證和驗收測試",
            skill_level="advanced",
            domain="testing",
            keywords=["deployment verification", "acceptance test", "部署驗證", "驗收測試"],
            confidence=0.89,
            source="base_system"
        )
    ]
    
    # 測試專家的知識庫
    testing_knowledge_base = {
        "type": "testing_expert",
        "content": [
            "測試是軟件開發生命週期中的關鍵環節",
            "自動化測試可以提高測試效率和覆蓋率",
            "測試驅動開發(TDD)是一種有效的開發方法",
            "持續集成中的測試自動化是DevOps的重要組成部分"
        ],
        "detailed_info": [
            "單元測試應該快速、獨立、可重複",
            "整合測試驗證組件間的交互",
            "性能測試包括負載測試、壓力測試和容量測試",
            "測試金字塔：單元測試 > 整合測試 > UI測試",
            "測試覆蓋率是質量的重要指標但不是唯一指標"
        ],
        "best_practices": [
            "編寫清晰的測試用例描述",
            "使用適當的測試數據和環境",
            "定期維護和更新測試套件",
            "實施測試左移策略",
            "建立有效的缺陷追蹤和報告機制"
        ],
        "tool_recommendations": [
            {
                "tool_name": "test_flow_mcp",
                "use_cases": [
                    "執行自動化測試流程",
                    "管理測試環境和數據",
                    "生成測試報告和分析",
                    "協調多種測試類型的執行",
                    "驗證部署和發布流程"
                ],
                "trigger_keywords": [
                    "測試", "test", "驗證", "verify", "檢查", "check",
                    "質量", "quality", "QA", "自動化", "automation",
                    "單元測試", "整合測試", "性能測試", "負載測試",
                    "部署驗證", "驗收測試", "回歸測試"
                ],
                "confidence": 0.95,
                "priority": "high"
            }
        ]
    }
    
    # 性能指標
    performance_metrics = {
        "success_rate": 0.92,
        "response_time": 0.8,
        "accuracy": 0.94,
        "user_satisfaction": 0.91,
        "usage_count": 0,
        "test_coverage_improvement": 0.85,
        "defect_detection_rate": 0.88
    }
    
    # 創建測試專家檔案
    testing_expert = ExpertProfile(
        id="testing_expert",
        name="Testing Expert",
        type=ExpertType.BASE_EXPERT,
        status=ExpertStatus.ACTIVE,
        capabilities=testing_capabilities,
        specializations=["testing", "quality_assurance", "automation"],
        knowledge_base=testing_knowledge_base,
        performance_metrics=performance_metrics,
        usage_history=[],
        created_at=datetime.now(),
        last_used=None,
        metadata={
            "base_expert": True,
            "auto_recommend_tools": True,
            "primary_tool": "test_flow_mcp",
            "expertise_level": "expert",
            "supported_test_types": [
                "unit_testing",
                "integration_testing", 
                "performance_testing",
                "automation_testing",
                "deployment_verification"
            ]
        }
    )
    
    return testing_expert

def get_testing_expert_tool_recommendations(request_content: str) -> List[Dict[str, Any]]:
    """根據請求內容獲取測試專家的工具推薦"""
    
    # 測試相關關鍵字
    testing_keywords = [
        "測試", "test", "驗證", "verify", "檢查", "check",
        "質量", "quality", "qa", "自動化", "automation",
        "單元測試", "unit test", "整合測試", "integration test",
        "性能測試", "performance test", "負載測試", "load test",
        "部署驗證", "deployment verification", "驗收測試", "acceptance test",
        "回歸測試", "regression test", "功能測試", "functional test"
    ]
    
    request_lower = request_content.lower()
    
    # 檢查是否包含測試相關關鍵字
    has_testing_keywords = any(keyword in request_lower for keyword in testing_keywords)
    
    if has_testing_keywords:
        # 計算匹配度
        matched_keywords = [kw for kw in testing_keywords if kw in request_lower]
        confidence = min(0.95, 0.7 + (len(matched_keywords) * 0.05))
        
        return [{
            "tool_name": "test_flow_mcp",
            "mode": "auto",
            "reason": f"檢測到測試相關需求，推薦使用 Test Flow MCP 進行測試流程管理",
            "priority": "high",
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "capabilities": [
                "自動化測試執行",
                "測試環境管理", 
                "測試數據準備",
                "測試報告生成",
                "部署驗證"
            ]
        }]
    
    return []

def should_recommend_test_flow_mcp(request_context: Dict[str, Any]) -> bool:
    """判斷是否應該推薦 Test Flow MCP"""
    
    # 檢查請求內容
    content = request_context.get("content", "").lower()
    
    # 檢查請求類型
    request_type = request_context.get("type", "").lower()
    
    # 檢查領域
    domains = request_context.get("domains", [])
    
    # 測試相關條件
    testing_conditions = [
        # 內容包含測試關鍵字
        any(keyword in content for keyword in [
            "test", "測試", "verify", "驗證", "check", "檢查",
            "quality", "質量", "qa", "automation", "自動化"
        ]),
        
        # 請求類型是測試相關
        any(test_type in request_type for test_type in [
            "test", "testing", "verification", "quality"
        ]),
        
        # 領域包含測試
        any(domain in domains for domain in [
            "testing", "quality_assurance", "automation"
        ])
    ]
    
    return any(testing_conditions)



# 導出測試專家配置常量
TESTING_EXPERT_CONFIG = create_testing_expert()

