"""
PowerAutomation Local MCP Adapter

基於MCP (Model Context Protocol) 標準的PowerAutomation本地適配器
整合local server和vscode extension兩大核心組件

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

__version__ = "1.0.0"
__author__ = "Manus AI"
__email__ = "support@manus.ai"
__description__ = "PowerAutomation Local MCP Adapter - 本地PowerAutomation功能的統一MCP適配器"

from .powerautomation_local_mcp import PowerAutomationLocalMCP

__all__ = [
    "PowerAutomationLocalMCP",
]

