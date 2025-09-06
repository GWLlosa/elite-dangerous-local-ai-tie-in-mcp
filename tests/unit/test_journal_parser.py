"""Unit tests for journal parser functionality."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.journal.parser import JournalParser


@pytest.fixture
def temp_journal_dir():
    """Create temporary directory with sample journal files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        journal_dir = Path(temp_dir)
        
        # Create sample journal files with different timestamps
        journal_files = [
            "Journal.20240906120000.01.log",
            "Journal.20240906110000.01.log", 
            "Journal.20240905120000.01.log.backup"
        ]
        
        # Sample journal entries
        sample_entries = [
            '{"timestamp":"2024-09-06T12:00:00Z","event":"Fileheader","part":1,"language":"English/UK","Odyssey":true,"gameversion":"4.0.0.1450","build":"r292932/r0 "}',
            '{"timestamp":"2024-09-06T12:01:00Z","event":"LoadGame","Commander":"TestCMDR","Ship":"Sidewinder","ShipID":1,"FID":"F1234567","Horizons":true,"Odyssey":true}',
            '{"timestamp":"2024-09-06T12:02:00Z","event":"Location","StarSystem":"Sol","SystemAddress":10477373803,"StarPos":[0.0,0.0,0.0],"Body":"Earth","BodyID":2,"BodyType":"Planet"}',
            '{"timestamp":"2024-09-06T12:03:00Z","event":"FSDJump","StarSystem":"Alpha Centauri","SystemAddress":123456789,"StarPos":[1.25,2.09,-4.22],"JumpDist":4.38}'
        ]
        
        # Write sample files
        for i, filename in enumerate(journal_files):
            file_path = journal_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write a few sample entries to each file
                for j in range(min(len(sample_entries), 2)):
                    entry_idx = (i * 2 + j) % len(sample_entries)
                    f.write(sample_entries[entry_idx] + '\n')
        
        # Create Status.json
        status_data = {
            "timestamp": "2024-09-06T12:05:00Z",
            "event": "Status",
            "Flags": 16777240,
            "Pips": [2, 8, 2],
            "FireGroup": 0,
            "GuiFocus": 0,
            "Fuel": {"FuelMain": 32.0, "FuelReservoir": 0.63},
            "Cargo": 0.0
        }
        
        status_file = journal_dir / "Status.json"
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f)
        
        yield journal_dir


@pytest.fixture
def parser(temp_journal_dir):
    """Create JournalParser instance with temp directory."""
    return JournalParser(temp_journal_dir)


class TestJournalParser:
    """Test cases for JournalParser class."""
    
    def test_initialization(self, temp_journal_dir):
        """Test parser initialization."""
        parser = JournalParser(temp_journal_dir)
        assert parser.journal_path == temp_journal_dir
        assert parser.encoding == "utf-8"
    
    def test_find_journal_files(self, parser):
        """Test journal file discovery."""
        # Test with backups included
        files = parser.find_journal_files(include_backups=True)
        assert len(files) == 3
        
        # Should be sorted newest first
        filenames = [f.name for f in files]
        assert filenames[0] == "Journal.20240906120000.01.log"
        assert filenames[1] == "Journal.20240906110000.01.log"
        assert filenames[2] == "Journal.20240905120000.01.log.backup"
        
        # Test without backups
        files_no_backup = parser.find_journal_files(include_backups=False)
        assert len(files_no_backup) == 2
        assert all(not f.name.endswith('.backup') for f in files_no_backup)
    
    def test_find_journal_files_empty_directory(self):
        """Test journal file discovery in empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            parser = JournalParser(Path(temp_dir))
            files = parser.find_journal_files()
            assert files == []
    
    def test_find_journal_files_nonexistent_directory(self):
        """Test journal file discovery with nonexistent directory."""
        parser = JournalParser(Path("/nonexistent/directory"))
        files = parser.find_journal_files()
        assert files == []
    
    def test_get_latest_journal(self, parser):
        """Test getting latest journal file."""
        latest = parser.get_latest_journal(include_backups=False)
        assert latest is not None
        assert latest.name == "Journal.20240906120000.01.log"
        
        # Test with backups
        latest_with_backup = parser.get_latest_journal(include_backups=True)
        assert latest_with_backup is not None
        assert latest_with_backup.name == "Journal.20240906120000.01.log"
    
    def test_parse_journal_entry_valid(self, parser):
        """Test parsing valid journal entries."""
        valid_entry = '{"timestamp":"2024-09-06T12:00:00Z","event":"Test","data":"value"}'
        result = parser.parse_journal_entry(valid_entry)
        
        assert result is not None
        assert result["timestamp"] == "2024-09-06T12:00:00Z"
        assert result["event"] == "Test"
        assert result["data"] == "value"
    
    def test_parse_journal_entry_invalid_json(self, parser):
        """Test parsing invalid JSON."""
        invalid_entries = [
            '{"timestamp":"2024-09-06T12:00:00Z","event":"Test"',  # Incomplete JSON
            'not json at all',  # Not JSON
            '',  # Empty string
            '   ',  # Whitespace only
        ]
        
        for entry in invalid_entries:
            result = parser.parse_journal_entry(entry)
            assert result is None
    
    def test_parse_journal_entry_missing_required_fields(self, parser):
        """Test parsing entries missing required fields."""
        missing_timestamp = '{"event":"Test","data":"value"}'
        missing_event = '{"timestamp":"2024-09-06T12:00:00Z","data":"value"}'
        
        assert parser.parse_journal_entry(missing_timestamp) is None
        assert parser.parse_journal_entry(missing_event) is None
    
    def test_read_journal_file(self, parser):
        """Test reading complete journal file."""
        latest_file = parser.get_latest_journal()
        entries, final_position = parser.read_journal_file(latest_file)
        
        assert len(entries) == 2  # We wrote 2 entries per file
        assert final_position > 0
        assert all('timestamp' in entry for entry in entries)
        assert all('event' in entry for entry in entries)
    
    def test_read_journal_file_nonexistent(self, parser):
        """Test reading nonexistent file."""
        nonexistent = Path("/nonexistent/file.log")
        entries, position = parser.read_journal_file(nonexistent)
        
        assert entries == []
        assert position == 0
    
    def test_read_journal_file_incremental(self, parser, temp_journal_dir):
        """Test incremental file reading."""
        # Create a test file
        test_file = temp_journal_dir / "test_incremental.log"
        initial_content = '{"timestamp":"2024-09-06T12:00:00Z","event":"Test1"}\n'
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # Read initial content
        entries1, pos1 = parser.read_journal_file(test_file)
        assert len(entries1) == 1
        assert pos1 > 0
        
        # Add more content
        additional_content = '{"timestamp":"2024-09-06T12:01:00Z","event":"Test2"}\n'
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write(additional_content)
        
        # Read incremental
        entries2, pos2 = parser.read_journal_file_incremental(test_file, pos1)
        assert len(entries2) == 1
        assert entries2[0]["event"] == "Test2"
        assert pos2 > pos1
        
        # Test no new content
        entries3, pos3 = parser.read_journal_file_incremental(test_file, pos2)
        assert len(entries3) == 0
        assert pos3 == pos2
    
    def test_read_status_file(self, parser):
        """Test reading Status.json file."""
        status = parser.read_status_file()
        
        assert status is not None
        assert "timestamp" in status
        assert "event" in status
        assert status["event"] == "Status"
        assert "Flags" in status
    
    def test_read_status_file_nonexistent(self):
        """Test reading Status.json when it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            parser = JournalParser(Path(temp_dir))
            status = parser.read_status_file()
            assert status is None
    
    def test_extract_timestamp_from_filename(self, parser):
        """Test timestamp extraction from filenames."""
        test_files = [
            Path("Journal.20240906120000.01.log"),
            Path("Journal.20231225235959.99.log.backup"),
            Path("Journal.20200101000000.01.log"),
        ]
        
        expected_timestamps = [
            datetime(2024, 9, 6, 12, 0, 0),
            datetime(2023, 12, 25, 23, 59, 59),
            datetime(2020, 1, 1, 0, 0, 0),
        ]
        
        for file_path, expected in zip(test_files, expected_timestamps):
            result = parser._extract_timestamp_from_filename(file_path)
            assert result == expected
    
    def test_extract_timestamp_invalid_filename(self, parser):
        """Test timestamp extraction with invalid filenames."""
        invalid_files = [
            Path("not_a_journal.log"),
            Path("Journal.invalid.log"),
            Path("Journal.20241301123456.01.log"),  # Invalid date
        ]
        
        for file_path in invalid_files:
            result = parser._extract_timestamp_from_filename(file_path)
            assert result == datetime.fromtimestamp(0)  # Epoch fallback
    
    def test_get_file_info(self, parser):
        """Test getting file information."""
        latest_file = parser.get_latest_journal()
        info = parser.get_file_info(latest_file)
        
        assert info["exists"] is True
        assert info["name"] == latest_file.name
        assert info["size"] > 0
        assert info["readable"] is True
        assert "modified" in info
        assert "journal_timestamp" in info
        assert info["is_backup"] is False
    
    def test_get_file_info_nonexistent(self, parser):
        """Test getting info for nonexistent file."""
        nonexistent = Path("/nonexistent/file.log")
        info = parser.get_file_info(nonexistent)
        
        assert info["exists"] is False
        assert "error" in info
    
    def test_validate_journal_directory(self, parser):
        """Test journal directory validation."""
        results = parser.validate_journal_directory()
        
        assert results["exists"] is True
        assert results["is_directory"] is True
        assert results["readable"] is True
        assert results["journal_files_count"] == 3
        assert results["status_file_exists"] is True
        assert results["latest_journal"] is not None
        assert len(results["errors"]) == 0
    
    def test_validate_journal_directory_nonexistent(self):
        """Test validation of nonexistent directory."""
        parser = JournalParser(Path("/nonexistent/directory"))
        results = parser.validate_journal_directory()
        
        assert results["exists"] is False
        assert len(results["errors"]) > 0


@pytest.mark.asyncio
class TestJournalParserAsync:
    """Async test cases (for future async operations)."""
    
    async def test_parser_ready_for_async(self, parser):
        """Test that parser is ready for async operations."""
        # This is a placeholder for when we add async operations
        # Currently just validates the parser works in async context
        latest = parser.get_latest_journal()
        assert latest is not None


# Mock data for testing
MOCK_JOURNAL_ENTRIES = [
    {
        "timestamp": "2024-09-06T12:00:00Z",
        "event": "Fileheader",
        "part": 1,
        "language": "English/UK",
        "Odyssey": True,
        "gameversion": "4.0.0.1450",
        "build": "r292932/r0 "
    },
    {
        "timestamp": "2024-09-06T12:01:00Z",
        "event": "LoadGame",
        "Commander": "TestCMDR",
        "Ship": "Sidewinder",
        "ShipID": 1,
        "FID": "F1234567",
        "Horizons": True,
        "Odyssey": True
    },
    {
        "timestamp": "2024-09-06T12:02:00Z",
        "event": "Location",
        "StarSystem": "Sol",
        "SystemAddress": 10477373803,
        "StarPos": [0.0, 0.0, 0.0],
        "Body": "Earth",
        "BodyID": 2,
        "BodyType": "Planet"
    },
    {
        "timestamp": "2024-09-06T12:03:00Z",
        "event": "FSDJump",
        "StarSystem": "Alpha Centauri",
        "SystemAddress": 123456789,
        "StarPos": [1.25, 2.09, -4.22],
        "JumpDist": 4.38
    }
]


def create_mock_journal_file(file_path: Path, entries: list):
    """Helper function to create mock journal files for testing."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
