"""
AICore 0624 Components Package
包含所有MCP組件的實現
"""

from .general_processor_mcp import GeneralProcessorMCP, create_general_processor_mcp, LegacyProcessorAdapter
from .claude_sdk_mcp.claude_sdk_mcp_v2 import ClaudeSDKMCP

__all__ = [
    'GeneralProcessorMCP',
    'create_general_processor_mcp', 
    'LegacyProcessorAdapter',
    'ClaudeSDKMCP'
]

__version__ = "2.0.0"
__description__ = "AICore 0624 MCP組件集合 - 包含ClaudeSDKMCP v2.0.0"

