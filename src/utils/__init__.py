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

# Import main classes
from .config import EliteConfig
from .data_store import (
    DataStore, 
    EventFilter, 
    GameState, 
    QuerySortOrder, 
    EventStorageError,
    get_data_store,
    reset_data_store
)

__all__ = [
    "EliteConfig",
    "DataStore",
    "EventFilter", 
    "GameState",
    "QuerySortOrder",
    "EventStorageError",
    "get_data_store",
    "reset_data_store"
]