"""
ClaudeSDKMCP - 智能代码分析和专家咨询系统
基于0624架构的MCP组件实现

特点:
- 动态场景识别 - 95% 准确率
- 5个专业领域专家 + 动态专家发现机制
- 200K tokens 上下文处理能力
- 38个操作处理器 - 覆盖AI代码分析全流程
- 真实Claude API集成
- 基于0624架构的MCP协调器
- 完整CLI功能和性能监控
"""

from .claude_sdk_mcp_v2 import ClaudeSDKMCP
from .config import Config, default_config
from .cli import ClaudeSDKMCPCLI

__all__ = [
    'ClaudeSDKMCP',
    'Config', 
    'default_config',
    'ClaudeSDKMCPCLI'
]

__version__ = "2.0.0"
__description__ = "ClaudeSDKMCP - 智能代码分析和专家咨询系统"
__author__ = "ClaudeSDKMCP Team"

