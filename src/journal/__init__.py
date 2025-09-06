"""Journal Processing Package

Elite Dangerous journal file discovery, parsing, and real-time monitoring.

This package provides:
- Journal file discovery and parsing (parser.py)
- Real-time file system monitoring (monitor.py)  
- Event processing and classification (events.py - future)
- Data storage and retrieval (coming in Milestone 6)

Example Usage:
    from src.journal import JournalParser, JournalMonitor
    
    # Parse journal files
    parser = JournalParser(journal_path)
    files = parser.find_journal_files()
    entries = parser.read_journal_file(files[0])
    
    # Monitor journal files in real-time
    async def handle_events(data, event_type):
        print(f"Received {event_type}: {len(data)} items")
    
    monitor = JournalMonitor(journal_path, handle_events)
    await monitor.start_monitoring()
"""

from .parser import JournalParser
from .monitor import JournalMonitor, JournalEventHandler, create_journal_monitor

__all__ = [
    'JournalParser',
    'JournalMonitor', 
    'JournalEventHandler',
    'create_journal_monitor'
]

__version__ = '1.0.0'
__author__ = 'Elite Dangerous Local AI Tie-In MCP'
