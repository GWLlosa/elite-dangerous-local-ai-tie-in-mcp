"""
MCP (Model Context Protocol) package for Elite Dangerous integration.

Provides tools, resources, and prompts for AI assistant integration
with Elite Dangerous game data through the MCP protocol.
"""

from .mcp_tools import MCPTools
from .mcp_resources import MCPResources, ResourceCache, ResourceType
from .mcp_prompts import MCPPrompts, PromptTemplate, PromptType

__all__ = [
    'MCPTools',
    'MCPResources', 
    'ResourceCache',
    'ResourceType',
    'MCPPrompts',
    'PromptTemplate',
    'PromptType'
]
