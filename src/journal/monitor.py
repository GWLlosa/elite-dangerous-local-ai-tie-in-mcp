"""Real-time Journal Monitoring

Provides real-time monitoring of Elite Dangerous journal files using
watchdog file system events with position tracking and rotation handling.
"""

import asyncio
import logging
from pathlib import Path
from typing import Callable, Dict, Optional, Set
from datetime import datetime, timedelta
import threading

from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
from watchdog.observers import Observer

from .parser import JournalParser

logger = logging.getLogger(__name__)


class JournalEventHandler(FileSystemEventHandler):
    """
    File system event handler for journal file changes.
    
    Features:
    - Position tracking to avoid re-reading entries
    - Journal file rotation detection
    - Status.json monitoring
    - Callback-based event delivery
    """
    
    def __init__(self, callback: Callable, parser: JournalParser, event_loop: asyncio.AbstractEventLoop):
        """
        Initialize journal event handler.
        
        Args:
            callback: Function to call with new journal entries
            parser: JournalParser instance for file operations
            event_loop: Event loop for scheduling async tasks
        """
        super().__init__()
        self.callback = callback
        self.parser = parser
        self.event_loop = event_loop
        self.current_positions: Dict[str, int] = {}
        self.monitored_files: Set[str] = set()
        # Initialize to past time so first status check won't be throttled
        self.last_status_check = datetime.now() - timedelta(seconds=1.0)
        
        logger.info("Initialized journal event handler")
    
    def on_modified(self, event):
        """
        Handle journal file modifications.
        
        Args:
            event: File system modification event
        """
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Handle different file types
        if file_path.name.startswith('Journal.') and file_path.name.endswith('.log'):
            self._schedule_coroutine(self._handle_journal_modification(file_path))
        elif file_path.name == 'Status.json':
            self._schedule_coroutine(self._handle_status_modification(file_path))
    
    def on_created(self, event):
        """
        Handle new journal file creation (file rotation).
        
        Args:
            event: File system creation event
        """
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        if file_path.name.startswith('Journal.') and file_path.name.endswith('.log'):
            logger.info(f"New journal file detected: {file_path.name}")
            self._schedule_coroutine(self._handle_journal_creation(file_path))
    
    def _schedule_coroutine(self, coro):
        """
        Schedule a coroutine on the main event loop from a thread.
        
        Args:
            coro: Coroutine to schedule
        """
        try:
            if self.event_loop and not self.event_loop.is_closed():
                asyncio.run_coroutine_threadsafe(coro, self.event_loop)
        except Exception as e:
            logger.error(f"Error scheduling coroutine: {e}")
    
    async def _handle_journal_modification(self, file_path: Path):
        """
        Handle journal file modification with position tracking.
        
        Args:
            file_path: Path to modified journal file
        """
        try:
            file_key = str(file_path)
            
            # Get last position for this file
            last_position = self.current_positions.get(file_key, 0)
            
            # Read new entries since last position
            new_entries, new_position = self.parser.read_journal_file_incremental(
                file_path, last_position
            )
            
            if new_entries:
                logger.debug(f"Processing {len(new_entries)} new entries from {file_path.name}")
                
                # Update position
                self.current_positions[file_key] = new_position
                
                # Call callback with new entries
                await self._safe_callback(new_entries, 'journal_entries')
            
        except Exception as e:
            logger.error(f"Error handling journal modification for {file_path}: {e}")
    
    async def _handle_journal_creation(self, file_path: Path):
        """
        Handle new journal file creation (rotation).
        
        Args:
            file_path: Path to newly created journal file
        """
        try:
            file_key = str(file_path)
            
            # Add to monitored files
            self.monitored_files.add(file_key)
            
            # Initialize position tracking
            self.current_positions[file_key] = 0
            
            # Read any existing content
            entries, position = self.parser.read_journal_file(file_path)
            
            if entries:
                logger.info(f"Read {len(entries)} entries from new journal file: {file_path.name}")
                
                # Update position
                self.current_positions[file_key] = position
                
                # Call callback with entries
                await self._safe_callback(entries, 'journal_entries')
            
            # Notify about file rotation
            await self._safe_callback([{
                'event_type': 'file_rotation',
                'new_file': str(file_path),
                'timestamp': datetime.now().isoformat()
            }], 'system_events')
            
        except Exception as e:
            logger.error(f"Error handling journal creation for {file_path}: {e}")
    
    async def _handle_status_modification(self, file_path: Path):
        """
        Handle Status.json file modification.
        
        Args:
            file_path: Path to Status.json file
        """
        try:
            # Throttle status updates to avoid spam
            now = datetime.now()
            if now - self.last_status_check < timedelta(seconds=0.5):
                return
            
            self.last_status_check = now
            
            # Read status data from the specific file
            status_data = self._read_status_file(file_path)
            
            if status_data:
                logger.debug("Status.json updated")
                
                # Call callback with status update
                await self._safe_callback([status_data], 'status_update')
            
        except Exception as e:
            logger.error(f"Error handling Status.json modification: {e}")
    
    def _read_status_file(self, file_path: Path) -> Optional[Dict]:
        """
        Read and parse a Status.json file from specific path.
        
        Args:
            file_path: Path to Status.json file
            
        Returns:
            Optional[Dict]: Parsed status data, or None if not available
        """
        try:
            if not file_path.exists():
                logger.debug(f"Status file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return None
                
                import orjson
                status_data = orjson.loads(content)
                
                # Validate basic structure
                if not isinstance(status_data, dict):
                    logger.warning(f"Status file is not a dictionary: {type(status_data)}")
                    return None
                
                return status_data
                
        except Exception as e:
            logger.error(f"Error reading status file {file_path}: {e}")
            return None
    
    async def _safe_callback(self, data, event_type: str):
        """
        Safely call the callback function with error handling.
        
        Args:
            data: Data to pass to callback
            event_type: Type of event for callback routing
        """
        try:
            if asyncio.iscoroutinefunction(self.callback):
                await self.callback(data, event_type)
            else:
                self.callback(data, event_type)
        except Exception as e:
            logger.error(f"Error in callback for {event_type}: {e}")


class JournalMonitor:
    """
    Real-time Elite Dangerous journal file monitor.
    
    Features:
    - Automatic journal file discovery and monitoring
    - Real-time event processing with callbacks
    - File rotation handling
    - Status.json monitoring
    - Graceful startup and shutdown
    """
    
    def __init__(self, journal_path: Path, event_callback: Callable):
        """
        Initialize journal monitor.
        
        Args:
            journal_path: Path to Elite Dangerous journal directory
            event_callback: Callback function for journal events
        """
        self.journal_path = Path(journal_path)
        self.event_callback = event_callback
        self.parser = JournalParser(journal_path)
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[JournalEventHandler] = None
        self.is_monitoring = False
        self._stop_event = asyncio.Event()
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        
        logger.info(f"Initialized journal monitor for: {self.journal_path}")
    
    async def start_monitoring(self) -> bool:
        """
        Start monitoring journal directory.
        
        Returns:
            bool: True if monitoring started successfully
        """
        try:
            if self.is_monitoring:
                logger.warning("Monitoring already active")
                return True
            
            # Get current event loop
            self._event_loop = asyncio.get_running_loop()
            
            # Validate journal directory
            validation_results = self.parser.validate_journal_directory()
            if not validation_results['exists']:
                logger.error(f"Cannot start monitoring: {validation_results['errors']}")
                return False
            
            # Create event handler with event loop
            self.event_handler = JournalEventHandler(
                self.event_callback, 
                self.parser, 
                self._event_loop
            )
            
            # Initialize position tracking for existing files
            await self._initialize_position_tracking()
            
            # Create and start observer
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.journal_path),
                recursive=False
            )
            
            self.observer.start()
            self.is_monitoring = True
            self._stop_event.clear()
            
            logger.info("Journal monitoring started successfully")
            
            # Process any existing entries in latest journal
            await self._process_existing_entries()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start journal monitoring: {e}")
            await self.stop_monitoring()
            return False
    
    async def stop_monitoring(self):
        """Stop monitoring and cleanup resources."""
        try:
            self.is_monitoring = False
            self._stop_event.set()
            
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5.0)
                self.observer = None
            
            self.event_handler = None
            self._event_loop = None
            
            logger.info("Journal monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping journal monitoring: {e}")
    
    async def wait_for_stop(self):
        """Wait for monitoring to be stopped."""
        await self._stop_event.wait()
    
    def is_active(self) -> bool:
        """
        Check if monitoring is currently active.
        
        Returns:
            bool: True if monitoring is active
        """
        return self.is_monitoring and self.observer is not None and self.observer.is_alive()
    
    async def _initialize_position_tracking(self):
        """Initialize position tracking for existing journal files."""
        try:
            journal_files = self.parser.find_journal_files(include_backups=False)
            
            for file_path in journal_files:
                file_key = str(file_path)
                self.event_handler.monitored_files.add(file_key)
                
                # For existing files, set position to end to avoid re-processing
                # unless this is the latest file
                if file_path == journal_files[0]:  # Latest file
                    # Start from beginning for latest file initial processing
                    self.event_handler.current_positions[file_key] = 0
                else:
                    # For older files, start from end
                    try:
                        file_size = file_path.stat().st_size
                        self.event_handler.current_positions[file_key] = file_size
                    except Exception:
                        self.event_handler.current_positions[file_key] = 0
            
            logger.debug(f"Initialized position tracking for {len(journal_files)} files")
            
        except Exception as e:
            logger.error(f"Error initializing position tracking: {e}")
    
    async def _process_existing_entries(self):
        """Process any existing entries in the latest journal file."""
        try:
            latest_journal = self.parser.get_latest_journal(include_backups=False)
            
            if latest_journal:
                file_key = str(latest_journal)
                
                # Read existing entries
                entries, position = self.parser.read_journal_file(latest_journal)
                
                if entries:
                    logger.info(f"Processing {len(entries)} existing entries from {latest_journal.name}")
                    
                    # Update position
                    self.event_handler.current_positions[file_key] = position
                    
                    # Call callback with existing entries
                    await self.event_handler._safe_callback(entries, 'journal_entries')
                
                # Also read current status
                status_data = self.parser.read_status_file()
                if status_data:
                    await self.event_handler._safe_callback([status_data], 'status_update')
            
        except Exception as e:
            logger.error(f"Error processing existing entries: {e}")
    
    def get_monitoring_status(self) -> Dict:
        """
        Get detailed monitoring status information.
        
        Returns:
            Dict: Status information including file counts and positions
        """
        try:
            status = {
                'is_monitoring': self.is_monitoring,
                'is_active': self.is_active(),
                'journal_path': str(self.journal_path),
                'monitored_files_count': 0,
                'current_positions': {},
                'latest_journal': None,
                'status_file_exists': False
            }
            
            if self.event_handler:
                status['monitored_files_count'] = len(self.event_handler.monitored_files)
                status['current_positions'] = dict(self.event_handler.current_positions)
            
            # Get latest journal info
            latest_journal = self.parser.get_latest_journal(include_backups=False)
            if latest_journal:
                status['latest_journal'] = self.parser.get_file_info(latest_journal)
            
            # Check status file
            status_file = self.parser.get_status_file_path()
            status['status_file_exists'] = status_file.exists()
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {
                'is_monitoring': False,
                'is_active': False,
                'error': str(e)
            }


def create_journal_monitor(journal_path: Path, callback: Callable) -> JournalMonitor:
    """
    Factory function to create a journal monitor instance.
    
    Args:
        journal_path: Path to journal directory
        callback: Event callback function
        
    Returns:
        JournalMonitor: Configured monitor instance
    """
    return JournalMonitor(journal_path, callback)
