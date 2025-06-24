"""
AICore 0622 Components Package
包含所有MCP組件的實現
"""

from .general_processor_mcp import GeneralProcessorMCP, create_general_processor_mcp, LegacyProcessorAdapter

__all__ = [
    'GeneralProcessorMCP',
    'create_general_processor_mcp', 
    'LegacyProcessorAdapter'
]

__version__ = "2.0.0"
__description__ = "AICore 0622 MCP組件集合"

