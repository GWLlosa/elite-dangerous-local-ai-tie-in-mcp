"""
Utilities Package

Shared utilities and configuration management for the Elite Dangerous
Local AI Tie-In MCP server.

Modules:
- config: Configuration management and validation
- data_store: In-memory event storage and retrieval (Milestone 6)
"""

# Package version
__version__ = "0.1.0"

# Configuration management exports
from .config import EliteConfig, load_config, create_sample_config

# Future exports - will be implemented in later milestones
# from .data_store import EventStore

__all__ = [
    "EliteConfig",
    "load_config", 
    "create_sample_config",
    # Data store will be added in Milestone 6
]