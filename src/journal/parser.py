"""Journal File Discovery and Parsing

Handles discovery, reading, and parsing of Elite Dangerous journal files
with robust error handling and performance optimization.
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
    Elite Dangerous journal file parser with discovery and reading capabilities.
    
    Features:
    - Automatic journal file discovery with timestamp sorting
    - Robust JSON parsing using orjson for performance
    - Support for both .log and .log.backup files
    - File encoding detection and error handling
    - Efficient file reading with position tracking
    """
    
    def __init__(self, journal_path: Path):
        """
        Initialize journal parser with directory path.
        
        Args:
            journal_path: Path to Elite Dangerous journal directory
        """
        self.journal_path = Path(journal_path)
        self.encoding = "utf-8"
        
        logger.info(f"Initialized journal parser for: {self.journal_path}")
    
    def find_journal_files(self, include_backups: bool = True) -> List[Path]:
        """
        Find all journal files sorted by creation time (newest first).
        
        Args:
            include_backups: Whether to include .log.backup files
            
        Returns:
            List[Path]: Sorted list of journal file paths
        """
        try:
            if not self.journal_path.exists():
                logger.warning(f"Journal directory does not exist: {self.journal_path}")
                return []
            
            # Pattern for journal files: Journal.YYYYMMDDHHMMSS.NN.log
            patterns = ["Journal.*.log"]
            if include_backups:
                patterns.append("Journal.*.log.backup")
            
            journal_files = []
            for pattern in patterns:
                search_path = self.journal_path / pattern
                found_files = glob.glob(str(search_path))
                journal_files.extend([Path(f) for f in found_files])
            
            # Filter files to only include those with valid journal filename patterns
            valid_journal_files = []
            for file_path in journal_files:
                if self._is_valid_journal_filename(file_path):
                    valid_journal_files.append(file_path)
                else:
                    logger.debug(f"Skipping file with invalid journal pattern: {file_path.name}")
            
            # Sort by timestamp extracted from filename (newest first)
            valid_journal_files.sort(key=self._extract_timestamp_from_filename, reverse=True)
            
            logger.debug(f"Found {len(valid_journal_files)} valid journal files")
            return valid_journal_files
            
        except Exception as e:
            logger.error(f"Error finding journal files: {e}")
            return []
    
    def _is_valid_journal_filename(self, file_path: Path) -> bool:
        """
        Check if filename matches valid journal pattern.
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if filename is valid journal pattern
        """
        filename = file_path.name
        
        # Valid patterns: support both legacy and ISO-like formats
        patterns = [
            r'^Journal\.\d{14}\.\d{2}\.log$',
            r'^Journal\.\d{14}\.\d{2}\.log\.backup$',
            r'^Journal\.\d{4}-\d{2}-\d{2}T\d{6}\.\d{2}\.log$',
            r'^Journal\.\d{4}-\d{2}-\d{2}T\d{6}\.\d{2}\.log\.backup$'
        ]
        
        for pattern in patterns:
            if re.match(pattern, filename):
                return True
        
        return False
    
    def get_latest_journal(self, include_backups: bool = False) -> Optional[Path]:
        """
        Get the most recent journal file.

        Args:
            include_backups: Whether to consider backup files
            
        Returns:
            Optional[Path]: Path to latest journal file, or None if not found
        """
        try:
            journal_files = self.find_journal_files(include_backups=include_backups)
            
            if not journal_files:
                logger.warning("No journal files found")
                return None
            
            latest_file = journal_files[0]  # Already sorted newest first
            logger.info(f"Latest journal file: {latest_file.name}")
            return latest_file
            
        except Exception as e:
            logger.error(f"Error getting latest journal: {e}")
            return None
    
    def _is_valid_timestamp(self, timestamp_value) -> bool:
        """
        Validate that timestamp is a properly formatted string.
        
        Args:
            timestamp_value: The timestamp value to validate
            
        Returns:
            bool: True if timestamp is valid format
        """
        # Must be a string
        if not isinstance(timestamp_value, str):
            return False
        
        # Must not be empty
        if not timestamp_value.strip():
            return False
        
        # Must match basic ISO 8601 pattern (simplified check)
        # Elite Dangerous uses: YYYY-MM-DDTHH:MM:SSZ format
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$'
        if not re.match(iso_pattern, timestamp_value):
            return False
        
        return True
    
    def parse_journal_entry(self, line: str) -> Optional[Dict]:
        """
        Parse a single journal entry using orjson for performance.

        Args:
            line: Raw JSON line from journal file
            
        Returns:
            Optional[Dict]: Parsed journal entry, or None if invalid
        """
        try:
            # Strip whitespace and skip empty lines
            line = line.strip()
            if not line:
                return None
            
            # Parse JSON using orjson for performance
            entry = orjson.loads(line)
            
            # Validate basic structure
            if not isinstance(entry, dict):
                logger.warning(f"Journal entry is not a dictionary: {type(entry)}")
                return None
            
            # Ensure timestamp exists and is valid
            if 'timestamp' not in entry:
                logger.warning("Journal entry missing timestamp")
                return None
            
            if not self._is_valid_timestamp(entry['timestamp']):
                logger.warning(f"Journal entry has invalid timestamp format: {entry.get('timestamp')}")
                return None
            
            # Ensure event type exists
            if 'event' not in entry:
                logger.warning("Journal entry missing event type")
                return None
            
            return entry
            
        except orjson.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e} for line: {line[:100]}...")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing journal entry: {e}")
            return None
    
    def read_journal_file(self, file_path: Path, start_position: int = 0) -> Tuple[List[Dict], int]:
        """
        Read and parse entire journal file from specified position.

        Args:
            file_path: Path to journal file
            start_position: File position to start reading from (for incremental reads)
            
        Returns:
            Tuple[List[Dict], int]: (parsed entries, final file position)
        """
        try:
            if not file_path or not Path(file_path).exists():
                logger.error(f"Journal file does not exist: {file_path}")
                return [], start_position
            
            entries = []
            
            with open(file_path, 'r', encoding=self.encoding, errors='replace') as f:
                # Seek to start position if specified
                if start_position > 0:
                    f.seek(start_position)
                
                line_count = 0
                for line in f:
                    line_count += 1
                    entry = self.parse_journal_entry(line)
                    if entry:
                        entries.append(entry)
                
                # Get final file position
                final_position = f.tell()
            
            logger.info(f"Read {len(entries)} valid entries from {line_count} lines in {file_path.name}")
            return entries, final_position
            
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {file_path}: {e}")
            return [], start_position
        except Exception as e:
            logger.error(f"Error reading journal file {file_path}: {e}")
            return [], start_position
    
    def read_journal_file_incremental(self, file_path: Path, last_position: int) -> Tuple[List[Dict], int]:
        """
        Read only new entries from journal file since last position.

        Args:
            file_path: Path to journal file
            last_position: Last known file position
            
        Returns:
            Tuple[List[Dict], int]: (new entries, current file position)
        """
        try:
            if not file_path.exists():
                return [], last_position
            
            # Check if file has grown
            current_size = file_path.stat().st_size
            if current_size <= last_position:
                return [], last_position
            
            # Read only new content
            new_entries, new_position = self.read_journal_file(file_path, last_position)
            
            if new_entries:
                logger.debug(f"Read {len(new_entries)} new entries from {file_path.name}")
            
            return new_entries, new_position
            
        except Exception as e:
            logger.error(f"Error reading incremental updates from {file_path}: {e}")
            return [], last_position
    
    def get_status_file_path(self) -> Path:
        """
        Get path to Status.json file in journal directory.

        Returns:
            Path: Path to Status.json file
        """
        return self.journal_path / "Status.json"
    
    def read_status_file(self) -> Optional[Dict]:
        """
        Read and parse the current Status.json file.

        Returns:
            Optional[Dict]: Current status data, or None if not available
        """
        try:
            status_file = self.get_status_file_path()
            
            if not status_file.exists():
                logger.debug("Status.json file not found")
                return None
            
            with open(status_file, 'r', encoding=self.encoding) as f:
                content = f.read().strip()
                if not content:
                    return None
                
                status_data = orjson.loads(content)
                
                # Validate basic structure
                if not isinstance(status_data, dict):
                    logger.warning(f"Status.json is not a dictionary: {type(status_data)}")
                    return None
                
                return status_data
                
        except orjson.JSONDecodeError as e:
            logger.warning(f"JSON decode error in Status.json: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading Status.json: {e}")
            return None
    
    def _extract_timestamp_from_filename(self, file_path: Path) -> datetime:
        """
        Extract timestamp from journal filename for sorting.

        Args:
            file_path: Path to journal file

        Returns:
            datetime: Extracted timestamp (epoch if parsing fails)
        """
        try:
            # Patterns:
            # 1) Journal.YYYYMMDDHHMMSS.NN.log[.backup]
            # 2) Journal.YYYY-MM-DDTHHMMSS.NN.log[.backup]
            filename = file_path.name

<<<<<<< HEAD
            # Extract timestamp part using regex - handles both formats
            # Try ISO-like format first
            match_iso = re.search(r'Journal\.(\d{4}-\d{2}-\d{2}T\d{6})\.', filename)
            if match_iso:
                timestamp_str = match_iso.group(1)
                return datetime.strptime(timestamp_str, "%Y-%m-%dT%H%M%S")

            # Try legacy compact format without dashes
            match_legacy = re.search(r'Journal\.(\d{14})\.', filename)
            if match_legacy:
                legacy_str = match_legacy.group(1)
                return datetime.strptime(legacy_str, "%Y%m%d%H%M%S")

            logger.warning(f"Could not extract timestamp from filename: {filename}")
            return datetime.fromtimestamp(0)  # Epoch as fallback

        except Exception as e:
            logger.warning(f"Error parsing timestamp from {file_path.name}: {e}")
            return datetime.fromtimestamp(0)  # Epoch as fallback
    
    def get_file_info(self, file_path: Path) -> Dict:
        """
        Get detailed information about a journal file.

        Args:
            file_path: Path to journal file
            
        Returns:
            Dict: File information including size, timestamp, etc.
        """
        try:
            if not file_path.exists():
                return {'exists': False, 'error': 'File not found'}
            
            stat = file_path.stat()
            timestamp = self._extract_timestamp_from_filename(file_path)
            
            return {
                'exists': True,
                'path': str(file_path),
                'name': file_path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'journal_timestamp': timestamp,
                'is_backup': file_path.name.endswith('.backup'),
                'readable': file_path.is_file() and stat.st_size > 0
            }
            
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def validate_journal_directory(self) -> Dict:
        """
        Validate journal directory and provide detailed status.

        Returns:
            Dict: Validation results and directory information
        """
        try:
            results = {
                'path': str(self.journal_path),
                'exists': self.journal_path.exists(),
                'is_directory': False,
                'readable': False,
                'journal_files_count': 0,
                'latest_journal': None,
                'status_file_exists': False,
                'errors': []
            }
            
            if not results['exists']:
                results['errors'].append(f"Directory does not exist: {self.journal_path}")
                return results
            
            results['is_directory'] = self.journal_path.is_dir()
            if not results['is_directory']:
                results['errors'].append("Path is not a directory")
                return results
            
            try:
                # Test readability
                list(self.journal_path.iterdir())
                results['readable'] = True
            except PermissionError:
                results['errors'].append("Directory not readable (permission denied)")
                return results
            
            # Count journal files
            journal_files = self.find_journal_files()
            results['journal_files_count'] = len(journal_files)
            
            if journal_files:
                latest = journal_files[0]  # Already sorted newest first
                results['latest_journal'] = self.get_file_info(latest)
            
            # Check for Status.json
            status_file = self.get_status_file_path()
            results['status_file_exists'] = status_file.exists()
            
            logger.info(f"Journal directory validation complete: {results['journal_files_count']} files found")
            return results
            
        except Exception as e:
            logger.error(f"Error validating journal directory: {e}")
            return {
                'path': str(self.journal_path),
                'exists': False,
                'error': str(e),
                'errors': [str(e)]
            }
