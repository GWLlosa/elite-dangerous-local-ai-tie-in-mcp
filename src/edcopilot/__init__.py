"""
EDCoPilot Integration Package

This package handles generation of custom EDCoPilot files based on Elite Dangerous
gameplay data, creating dynamic chatter, crew dialogue, and speech extensions.

Modules:
- generator: EDCoPilot custom file generation
- templates: Template system for dynamic content creation
- theme_storage: Theme persistence and configuration management
- theme_generator: AI-powered theme generation system
- theme_mcp_tools: MCP tools for Dynamic Multi-Crew Theme System
"""

# Package version
__version__ = "0.2.0"

# Core exports
from .generator import EDCoPilotContentGenerator as EDCoPilotGenerator
from .templates import (
    EDCoPilotTemplateManager, ChatterEntry, ChatterType,
    SpaceChatterTemplate, CrewChatterTemplate, DeepSpaceChatterTemplate
)
from .theme_storage import (
    ThemeStorage, CrewMemberTheme, ShipCrewConfig, CrewRole
)
from .theme_generator import (
    ThemeGenerator, ThemePromptGenerator, TemplateValidator
)
from .theme_mcp_tools import ThemeMCPTools

__all__ = [
    # Core functionality
    "EDCoPilotGenerator",

    # Template system
    "EDCoPilotTemplateManager",
    "ChatterEntry",
    "ChatterType",
    "SpaceChatterTemplate",
    "CrewChatterTemplate",
    "DeepSpaceChatterTemplate",

    # Theme system
    "ThemeStorage",
    "CrewMemberTheme",
    "ShipCrewConfig",
    "CrewRole",
    "ThemeGenerator",
    "ThemePromptGenerator",
    "TemplateValidator",
    "ThemeMCPTools"
]