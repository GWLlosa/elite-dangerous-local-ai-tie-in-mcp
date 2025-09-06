"""
Elite Dangerous Journal Processing Package

This package handles monitoring, parsing, and processing of Elite Dangerous
journal files for real-time integration with the MCP server.

Modules:
- monitor: Real-time journal file monitoring (Milestone 4)
- parser: Journal file discovery and JSON parsing (Milestone 3 - IMPLEMENTED)
- events: Event classification and processing (Milestone 5)
"""

# Package version
__version__ = "0.1.0"

# Implemented exports (Milestone 3)
from .parser import JournalParser

# Future exports - will be implemented in later milestones
# from .monitor import JournalMonitor, JournalEventHandler
# from .events import EventProcessor, EventCategory, ProcessedEvent

__all__ = [
    "JournalParser",
    # Will be populated as classes are implemented
]