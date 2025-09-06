"""
Elite Dangerous Journal Parser

Handles discovery, reading, and parsing of Elite Dangerous journal files.
Uses orjson for high-performance JSON parsing of journal entries.
"""

import glob
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import orjson

logger = logging.getLogger(__name__)


class JournalParser:
    """
    Elite Dangerous journal file parser.
    
    Provides:
    - Journal file discovery and sorting by timestamp
    - High-performance JSON parsing with orjson
    - Error handling for malformed entries
    - Support for both .log and .log.backup files
    - Incremental file reading with position tracking
    """
    
    def __init__(self, journal_path: Path):
        """
        Initialize the journal parser.
        
        Args:
            journal_path: Path to Elite Dangerous journal directory
        """
        self.journal_path = Path(journal_path)
        self.file_positions = {}  # Track reading positions
        self.last_scan_time = None
        
        # Compile regex patterns for efficiency
        self.journal_pattern = re.compile(r'Journal\.(\d{12})\.(\d{2})\.log(\.backup)?$')
        self.fileheader_pattern = re.compile(r'fileheader', re.IGNORECASE)
        
        logger.info(f"Journal parser initialized for: {journal_path}")
    
    def find_journal_files(self) -> List[Path]:
        """
        Find all journal files sorted by creation time.
        
        Returns:
            List[Path]: Journal files sorted by timestamp (oldest first)
        """
        try:
            journal_files = []
            
            # Find all journal files (including backups)
            patterns = [
                self.journal_path / "Journal.*.log",
                self.journal_path / "Journal.*.log.backup"
            ]
            
            for pattern in patterns:
                files = glob.glob(str(pattern))
                journal_files.extend([Path(f) for f in files])
            
            # Sort by extracted timestamp from filename
            sorted_files = sorted(journal_files, key=self._extract_timestamp_from_filename)
            
            logger.debug(f"Found {len(sorted_files)} journal files")
            return sorted_files
            
        except Exception as e:
            logger.error(f"Error finding journal files: {e}")
            return []
    
    def get_latest_journal(self) -> Optional[Path]:
        """
        Get the most recent journal file.
        
        Returns:
            Optional[Path]: Latest journal file or None if not found
        """
        try:
            journal_files = self.find_journal_files()
            if not journal_files:
                logger.warning("No journal files found")
                return None
            
            # Return the most recent file (last in sorted list)
            latest = journal_files[-1]
            logger.debug(f"Latest journal file: {latest}")
            return latest
            
        except Exception as e:
            logger.error(f"Error getting latest journal: {e}")
            return None
    
    def get_active_journal(self) -> Optional[Path]:
        """
        Get the currently active (non-backup) journal file.
        
        Returns:
            Optional[Path]: Active journal file or None if not found
        """
        try:
            all_files = self.find_journal_files()
            
            # Filter for non-backup files only
            active_files = [f for f in all_files if not f.name.endswith('.backup')]
            
            if not active_files:
                logger.warning("No active journal files found")
                return None
            
            # Return the most recent active file
            latest_active = sorted(active_files, key=self._extract_timestamp_from_filename)[-1]
            logger.debug(f"Active journal file: {latest_active}")
            return latest_active
            
        except Exception as e:
            logger.error(f"Error getting active journal: {e}")
            return None
    
    def parse_journal_entry(self, line: str) -> Optional[Dict]:
        """
        Parse a single journal entry using orjson.
        
        Args:
            line: JSON line from journal file
            
        Returns:
            Optional[Dict]: Parsed journal entry or None if invalid
        """
        try:
            if not line.strip():
                return None
            
            # Use orjson for high-performance parsing
            entry = orjson.loads(line.strip().encode('utf-8'))\n            \n            # Validate basic structure\n            if not isinstance(entry, dict) or 'timestamp' not in entry:\n                logger.debug(f\"Invalid entry structure: {line[:100]}...\")\n                return None\n            \n            return entry\n            \n        except orjson.JSONDecodeError as e:\n            logger.warning(f\"JSON decode error: {e} in line: {line[:100]}...\")\n            return None\n        except Exception as e:\n            logger.error(f\"Unexpected error parsing entry: {e}\")\n            return None\n    \n    def read_journal_file(self, file_path: Path, start_position: int = 0) -> Tuple[List[Dict], int]:\n        \"\"\"\n        Read and parse journal file from specified position.\n        \n        Args:\n            file_path: Path to journal file\n            start_position: Byte position to start reading from\n            \n        Returns:\n            Tuple[List[Dict], int]: (parsed entries, final file position)\n        \"\"\"\n        try:\n            if not file_path.exists():\n                logger.warning(f\"Journal file not found: {file_path}\")\n                return [], start_position\n            \n            entries = []\n            current_position = start_position\n            \n            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:\n                # Seek to starting position\n                f.seek(start_position)\n                \n                # Read line by line\n                for line_num, line in enumerate(f, 1):\n                    entry = self.parse_journal_entry(line)\n                    if entry:\n                        # Add metadata\n                        entry['_source_file'] = str(file_path)\n                        entry['_file_position'] = current_position\n                        entry['_line_number'] = line_num\n                        \n                        entries.append(entry)\n                    \n                    # Update position\n                    current_position = f.tell()\n                \n                logger.info(f\"Read {len(entries)} entries from {file_path.name} (from position {start_position})\")\n                return entries, current_position\n                \n        except Exception as e:\n            logger.error(f\"Error reading journal file {file_path}: {e}\")\n            return [], start_position\n    \n    def read_journal_file_complete(self, file_path: Path) -> List[Dict]:\n        \"\"\"\n        Read entire journal file and parse all entries.\n        \n        Args:\n            file_path: Path to journal file\n            \n        Returns:\n            List[Dict]: All parsed journal entries\n        \"\"\"\n        entries, _ = self.read_journal_file(file_path, 0)\n        return entries\n    \n    def get_new_entries(self, file_path: Path) -> List[Dict]:\n        \"\"\"\n        Get new entries from a journal file since last read.\n        \n        Args:\n            file_path: Path to journal file\n            \n        Returns:\n            List[Dict]: New entries since last read\n        \"\"\"\n        try:\n            file_key = str(file_path)\n            last_position = self.file_positions.get(file_key, 0)\n            \n            entries, new_position = self.read_journal_file(file_path, last_position)\n            \n            # Update stored position\n            self.file_positions[file_key] = new_position\n            \n            if entries:\n                logger.debug(f\"Found {len(entries)} new entries in {file_path.name}\")\n            \n            return entries\n            \n        except Exception as e:\n            logger.error(f\"Error getting new entries from {file_path}: {e}\")\n            return []\n    \n    def validate_journal_entry(self, entry: Dict) -> bool:\n        \"\"\"\n        Validate journal entry structure and required fields.\n        \n        Args:\n            entry: Parsed journal entry\n            \n        Returns:\n            bool: True if entry is valid\n        \"\"\"\n        try:\n            # Check required fields\n            required_fields = ['timestamp', 'event']\n            for field in required_fields:\n                if field not in entry:\n                    logger.debug(f\"Missing required field '{field}' in entry\")\n                    return False\n            \n            # Validate timestamp format\n            timestamp_str = entry['timestamp']\n            try:\n                datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))\n            except ValueError:\n                logger.debug(f\"Invalid timestamp format: {timestamp_str}\")\n                return False\n            \n            # Validate event field\n            if not isinstance(entry['event'], str) or not entry['event'].strip():\n                logger.debug(\"Invalid event field\")\n                return False\n            \n            return True\n            \n        except Exception as e:\n            logger.debug(f\"Error validating entry: {e}\")\n            return False\n    \n    def get_file_header(self, file_path: Path) -> Optional[Dict]:\n        \"\"\"\n        Get the FileHeader entry from a journal file.\n        \n        Args:\n            file_path: Path to journal file\n            \n        Returns:\n            Optional[Dict]: FileHeader entry or None if not found\n        \"\"\"\n        try:\n            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:\n                # FileHeader is typically the first entry\n                for line in f:\n                    entry = self.parse_journal_entry(line)\n                    if entry and entry.get('event') == 'Fileheader':\n                        return entry\n                    # Stop after checking first few lines\n                    if f.tell() > 1000:\n                        break\n            \n            logger.debug(f\"No FileHeader found in {file_path.name}\")\n            return None\n            \n        except Exception as e:\n            logger.error(f\"Error reading FileHeader from {file_path}: {e}\")\n            return None\n    \n    def get_journal_summary(self) -> Dict:\n        \"\"\"\n        Get a summary of available journal files and their status.\n        \n        Returns:\n            Dict: Summary information about journal files\n        \"\"\"\n        try:\n            journal_files = self.find_journal_files()\n            \n            summary = {\n                'total_files': len(journal_files),\n                'active_files': 0,\n                'backup_files': 0,\n                'latest_file': None,\n                'latest_active': None,\n                'date_range': {'earliest': None, 'latest': None},\n                'file_sizes': {},\n                'total_size_mb': 0\n            }\n            \n            if not journal_files:\n                return summary\n            \n            total_size = 0\n            timestamps = []\n            \n            for file_path in journal_files:\n                # Count file types\n                if file_path.name.endswith('.backup'):\n                    summary['backup_files'] += 1\n                else:\n                    summary['active_files'] += 1\n                \n                # Get file size\n                try:\n                    size = file_path.stat().st_size\n                    summary['file_sizes'][file_path.name] = size\n                    total_size += size\n                except OSError:\n                    pass\n                \n                # Extract timestamp\n                timestamp = self._extract_timestamp_from_filename(file_path)\n                if timestamp:\n                    timestamps.append(timestamp)\n            \n            # Set summary fields\n            summary['latest_file'] = str(journal_files[-1]) if journal_files else None\n            summary['latest_active'] = str(self.get_active_journal() or '')\n            summary['total_size_mb'] = round(total_size / (1024 * 1024), 2)\n            \n            if timestamps:\n                summary['date_range']['earliest'] = min(timestamps)\n                summary['date_range']['latest'] = max(timestamps)\n            \n            logger.debug(f\"Journal summary: {summary['total_files']} files, {summary['total_size_mb']} MB\")\n            return summary\n            \n        except Exception as e:\n            logger.error(f\"Error generating journal summary: {e}\")\n            return {'error': str(e)}\n    \n    def _extract_timestamp_from_filename(self, file_path: Path) -> Optional[datetime]:\n        \"\"\"\n        Extract timestamp from journal filename.\n        \n        Args:\n            file_path: Path to journal file\n            \n        Returns:\n            Optional[datetime]: Extracted timestamp or None if invalid\n        \"\"\"\n        try:\n            match = self.journal_pattern.search(file_path.name)\n            if not match:\n                logger.debug(f\"Invalid journal filename format: {file_path.name}\")\n                return None\n            \n            timestamp_str = match.group(1)  # YYMMDDHHMMSS\n            part_num = int(match.group(2))   # Part number\n            \n            # Parse timestamp: YYMMDDHHMMSS\n            year = 2000 + int(timestamp_str[0:2])\n            month = int(timestamp_str[2:4])\n            day = int(timestamp_str[4:6])\n            hour = int(timestamp_str[6:8])\n            minute = int(timestamp_str[8:10])\n            second = int(timestamp_str[10:12])\n            \n            # Create datetime and adjust for part number (add seconds for parts)\n            timestamp = datetime(year, month, day, hour, minute, second)\n            timestamp = timestamp.replace(microsecond=part_num * 1000)\n            \n            return timestamp\n            \n        except (ValueError, IndexError) as e:\n            logger.debug(f\"Error parsing timestamp from {file_path.name}: {e}\")\n            return None\n    \n    def reset_positions(self):\n        \"\"\"\n        Reset all file reading positions (start fresh).\n        \"\"\"\n        self.file_positions.clear()\n        logger.info(\"Reset all journal file positions\")\n    \n    def set_file_position(self, file_path: Path, position: int):\n        \"\"\"\n        Set the reading position for a specific file.\n        \n        Args:\n            file_path: Path to journal file\n            position: Byte position to set\n        \"\"\"\n        file_key = str(file_path)\n        self.file_positions[file_key] = position\n        logger.debug(f\"Set position for {file_path.name}: {position}\")\n    \n    def get_file_position(self, file_path: Path) -> int:\n        \"\"\"\n        Get the current reading position for a file.\n        \n        Args:\n            file_path: Path to journal file\n            \n        Returns:\n            int: Current reading position in bytes\n        \"\"\"\n        file_key = str(file_path)\n        return self.file_positions.get(file_key, 0)