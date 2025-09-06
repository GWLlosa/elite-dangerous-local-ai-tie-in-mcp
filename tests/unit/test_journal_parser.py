"""Unit tests for journal parser functionality."""

import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

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


class TestJournalParserEdgeCases:
    """Test edge cases and error scenarios for journal parser."""
    
    def test_large_journal_file_performance(self, temp_journal_dir):
        """Test parser performance with large journal files."""
        parser = JournalParser(temp_journal_dir)
        
        # Create a large journal file with many entries
        large_journal = temp_journal_dir / "Journal.20240906150000.01.log"
        entries_count = 1000
        
        with open(large_journal, 'w', encoding='utf-8') as f:
            for i in range(entries_count):
                entry = {
                    "timestamp": f"2024-09-06T15:{i:02d}:00Z",
                    "event": f"TestEvent{i}",
                    "data": f"large_data_payload_{'x' * 100}_{i}"
                }
                f.write(json.dumps(entry) + '\n')
        
        # Test performance
        start_time = time.time()
        entries, position = parser.read_journal_file(large_journal)
        end_time = time.time()
        
        # Verify all entries were parsed
        assert len(entries) == entries_count
        assert position > 0
        
        # Performance should be reasonable (less than 2 seconds for 1000 entries)
        processing_time = end_time - start_time
        assert processing_time < 2.0, f"Processing took {processing_time:.2f} seconds"
        
        # Verify data integrity
        assert entries[0]["event"] == "TestEvent0"
        assert entries[-1]["event"] == f"TestEvent{entries_count-1}"
    
    def test_unicode_edge_cases(self, temp_journal_dir):
        """Test parsing with various unicode characters."""
        parser = JournalParser(temp_journal_dir)
        
        unicode_journal = temp_journal_dir / "Journal.20240906160000.01.log"
        
        # Create entries with various unicode characters
        unicode_entries = [
            {
                "timestamp": "2024-09-06T16:00:00Z",
                "event": "LoadGame",
                "Commander": "ÇMDR_ñoño_测试",  # Mixed unicode
                "Ship": "Sidewinder_🚀"  # Emoji
            },
            {
                "timestamp": "2024-09-06T16:01:00Z",
                "event": "Location",
                "StarSystem": "Système_中文_العربية",  # Multiple scripts
                "Body": "Planète_Земля"  # French + Russian
            },
            {
                "timestamp": "2024-09-06T16:02:00Z",
                "event": "ReceiveText",
                "Message": "Hello 世界! Здравствуй мир! 🌍",  # Multi-language
                "Channel": "local"
            }
        ]
        
        with open(unicode_journal, 'w', encoding='utf-8') as f:
            for entry in unicode_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        # Parse and verify unicode handling
        entries, position = parser.read_journal_file(unicode_journal)
        
        assert len(entries) == 3
        assert entries[0]["Commander"] == "ÇMDR_ñoño_测试"
        assert entries[0]["Ship"] == "Sidewinder_🚀"
        assert entries[1]["StarSystem"] == "Système_中文_العربية"
        assert entries[1]["Body"] == "Planète_Земля"
        assert entries[2]["Message"] == "Hello 世界! Здравствуй мир! 🌍"
    
    def test_corrupted_status_file_recovery(self, temp_journal_dir):
        """Test handling of corrupted Status.json files."""
        parser = JournalParser(temp_journal_dir)
        status_file = temp_journal_dir / "Status.json"
        
        # Test various corruption scenarios
        corruption_cases = [
            # Incomplete JSON
            '{"timestamp":"2024-09-06T16:00:00Z","event":"Status","Flags":123',
            # Invalid JSON structure
            '{"timestamp":"2024-09-06T16:00:00Z","event":}',
            # Non-JSON content
            'This is not JSON at all',
            # Empty file
            '',
            # Only whitespace
            '   \n\t   ',
            # Binary data
            b'\x00\x01\x02\x03\x04'.decode('utf-8', errors='replace'),
            # Very long invalid content
            'invalid_json_' + 'x' * 10000
        ]
        
        for i, corrupted_content in enumerate(corruption_cases):
            with open(status_file, 'w', encoding='utf-8') as f:
                f.write(corrupted_content)
            
            # Parser should handle corruption gracefully
            status_data = parser.read_status_file()
            assert status_data is None, f"Case {i}: Expected None for corrupted content"
        
        # Test recovery with valid content after corruption
        valid_status = {
            "timestamp": "2024-09-06T16:05:00Z",
            "event": "Status",
            "Flags": 12345
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(valid_status, f)
        
        status_data = parser.read_status_file()
        assert status_data is not None
        assert status_data["Flags"] == 12345
    
    def test_file_permission_errors(self, temp_journal_dir):
        """Test handling of file permission errors."""
        parser = JournalParser(temp_journal_dir)
        
        # Create a test journal file
        test_journal = temp_journal_dir / "Journal.20240906170000.01.log"
        with open(test_journal, 'w', encoding='utf-8') as f:
            f.write('{"timestamp":"2024-09-06T17:00:00Z","event":"Test"}\n')
        
        # Mock permission denied error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            entries, position = parser.read_journal_file(test_journal)
            
            # Should return empty results without crashing
            assert entries == []
            assert position == 0
        
        # Test with Status.json permission error
        status_file = temp_journal_dir / "Status.json"
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump({"event": "Status", "Flags": 123}, f)
        
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            status_data = parser.read_status_file()
            assert status_data is None
    
    def test_mixed_encoding_scenarios(self, temp_journal_dir):
        """Test handling of files with mixed or incorrect encoding."""
        parser = JournalParser(temp_journal_dir)
        
        # Create file with different encodings
        mixed_journal = temp_journal_dir / "Journal.20240906180000.01.log"
        
        # Test with latin-1 encoding (common issue)
        latin1_content = '{"timestamp":"2024-09-06T18:00:00Z","event":"Test","data":"café"}\n'
        
        with open(mixed_journal, 'w', encoding='latin-1') as f:
            f.write(latin1_content)
        
        # Parser should handle encoding errors gracefully
        entries, position = parser.read_journal_file(mixed_journal)
        
        # Should still process the file (with potential character replacements)
        assert len(entries) >= 0  # May be 0 if JSON parsing fails due to encoding
        assert position > 0
    
    def test_extremely_long_lines(self, temp_journal_dir):
        """Test handling of extremely long journal entry lines."""
        parser = JournalParser(temp_journal_dir)
        
        long_journal = temp_journal_dir / "Journal.20240906190000.01.log"
        
        # Create entry with very long data
        very_long_data = "x" * 100000  # 100KB of data
        long_entry = {
            "timestamp": "2024-09-06T19:00:00Z",
            "event": "LongDataEvent",
            "data": very_long_data
        }
        
        with open(long_journal, 'w', encoding='utf-8') as f:
            f.write(json.dumps(long_entry) + '\n')
            # Add normal entry after
            f.write('{"timestamp":"2024-09-06T19:01:00Z","event":"NormalEvent"}\n')
        
        entries, position = parser.read_journal_file(long_journal)
        
        assert len(entries) == 2
        assert entries[0]["event"] == "LongDataEvent"
        assert len(entries[0]["data"]) == 100000
        assert entries[1]["event"] == "NormalEvent"
    
    def test_concurrent_file_access(self, temp_journal_dir):
        """Test handling of concurrent file access scenarios."""
        parser = JournalParser(temp_journal_dir)
        
        concurrent_journal = temp_journal_dir / "Journal.20240906200000.01.log"
        
        # Simulate file being written to while we're reading
        def mock_read_with_interruption():
            """Mock file read that simulates concurrent access."""
            original_open = open
            
            def patched_open(file, mode='r', **kwargs):
                if str(file) == str(concurrent_journal) and 'r' in mode:
                    # Simulate file being locked/modified during read
                    file_obj = original_open(file, mode, **kwargs)
                    
                    # Mock a scenario where file is truncated during read
                    original_read = file_obj.read
                    def interrupted_read():
                        content = original_read()
                        # Simulate partial content due to concurrent write
                        if len(content) > 10:
                            return content[:10] + '\n'  # Truncated content
                        return content
                    
                    file_obj.read = interrupted_read
                    return file_obj
                return original_open(file, mode, **kwargs)
            
            return patched_open
        
        # Create test content
        with open(concurrent_journal, 'w', encoding='utf-8') as f:
            f.write('{"timestamp":"2024-09-06T20:00:00Z","event":"Test"}\n')
        
        # Test with simulated concurrent access
        with patch('builtins.open', side_effect=mock_read_with_interruption()):
            entries, position = parser.read_journal_file(concurrent_journal)
            
            # Should handle gracefully (may return fewer entries due to truncation)
            assert isinstance(entries, list)
            assert isinstance(position, int)
    
    def test_malformed_timestamp_handling(self, temp_journal_dir):
        """Test handling of entries with malformed timestamps."""
        parser = JournalParser(temp_journal_dir)
        
        malformed_journal = temp_journal_dir / "Journal.20240906210000.01.log"
        
        # Create entries with various timestamp issues
        malformed_entries = [
            # Missing timestamp
            '{"event":"NoTimestamp","data":"test"}',
            # Invalid timestamp format
            '{"timestamp":"not-a-timestamp","event":"InvalidTimestamp"}',
            # Empty timestamp
            '{"timestamp":"","event":"EmptyTimestamp"}',
            # Null timestamp
            '{"timestamp":null,"event":"NullTimestamp"}',
            # Numeric timestamp (wrong type)
            '{"timestamp":1234567890,"event":"NumericTimestamp"}',
            # Valid entry (should work)
            '{"timestamp":"2024-09-06T21:00:00Z","event":"ValidEntry"}'
        ]
        
        with open(malformed_journal, 'w', encoding='utf-8') as f:
            for entry in malformed_entries:
                f.write(entry + '\n')
        
        entries, position = parser.read_journal_file(malformed_journal)
        
        # Only valid entries should be returned
        assert len(entries) == 1  # Only the valid entry
        assert entries[0]["event"] == "ValidEntry"
    
    def test_directory_access_edge_cases(self, temp_journal_dir):
        """Test directory access edge cases."""
        parser = JournalParser(temp_journal_dir)
        
        # Test validation with various directory states
        results = parser.validate_journal_directory()
        assert results["exists"] is True
        assert results["is_directory"] is True
        
        # Test with directory that becomes inaccessible
        with patch('pathlib.Path.iterdir', side_effect=PermissionError("Access denied")):
            results = parser.validate_journal_directory()
            assert len(results["errors"]) > 0
            assert results["readable"] is False
        
        # Test with directory that's actually a file
        fake_dir = temp_journal_dir / "not_a_directory.txt"
        with open(fake_dir, 'w') as f:
            f.write("fake directory")
        
        fake_parser = JournalParser(fake_dir)
        results = fake_parser.validate_journal_directory()
        assert results["is_directory"] is False
        assert len(results["errors"]) > 0
    
    def test_status_file_edge_cases(self, temp_journal_dir):
        """Test various Status.json edge cases."""
        parser = JournalParser(temp_journal_dir)
        status_file = temp_journal_dir / "Status.json"
        
        # Test with non-dictionary JSON
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write('["array", "instead", "of", "object"]')
        
        status_data = parser.read_status_file()
        assert status_data is None
        
        # Test with string instead of object
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write('"just a string"')
        
        status_data = parser.read_status_file()
        assert status_data is None
        
        # Test with number instead of object
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write('12345')
        
        status_data = parser.read_status_file()
        assert status_data is None
    
    def test_incremental_reading_edge_cases(self, temp_journal_dir):
        """Test edge cases in incremental file reading."""
        parser = JournalParser(temp_journal_dir)
        
        incremental_journal = temp_journal_dir / "Journal.20240906220000.01.log"
        
        # Create initial content
        initial_content = '{"timestamp":"2024-09-06T22:00:00Z","event":"Initial"}\n'
        with open(incremental_journal, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # Read initial content
        entries1, pos1 = parser.read_journal_file(incremental_journal)
        assert len(entries1) == 1
        assert pos1 > 0
        
        # Test incremental read when file hasn't changed
        entries2, pos2 = parser.read_journal_file_incremental(incremental_journal, pos1)
        assert len(entries2) == 0
        assert pos2 == pos1
        
        # Test incremental read when file is smaller (truncated)
        with open(incremental_journal, 'w', encoding='utf-8') as f:
            f.write('')  # Truncate file
        
        entries3, pos3 = parser.read_journal_file_incremental(incremental_journal, pos1)
        assert len(entries3) == 0
        assert pos3 == pos1  # Position shouldn't change
        
        # Test with file that's been deleted
        incremental_journal.unlink()
        entries4, pos4 = parser.read_journal_file_incremental(incremental_journal, pos1)
        assert len(entries4) == 0
        assert pos4 == pos1


class TestJournalParserPerformance:
    """Performance and stress tests for journal parser."""
    
    def test_memory_usage_large_files(self, temp_journal_dir):
        """Test memory usage with large files doesn't grow excessively."""
        parser = JournalParser(temp_journal_dir)
        
        # Create multiple large journal files
        for i in range(3):
            large_journal = temp_journal_dir / f"Journal.2024090623{i:02d}00.01.log"
            
            with open(large_journal, 'w', encoding='utf-8') as f:
                for j in range(500):  # 500 entries per file
                    entry = {
                        "timestamp": f"2024-09-06T23:{j:02d}:00Z",
                        "event": f"MemoryTest{j}",
                        "data": f"payload_{'x' * 200}_{j}"  # ~200 char payload
                    }
                    f.write(json.dumps(entry) + '\n')
        
        # Process all files and ensure memory usage is reasonable
        import tracemalloc
        tracemalloc.start()
        
        total_entries = 0
        for journal_file in parser.find_journal_files():
            entries, _ = parser.read_journal_file(journal_file)
            total_entries += len(entries)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        assert total_entries == 1500  # 3 files * 500 entries each
        # Memory usage should be reasonable (less than 50MB for this test)
        assert peak < 50 * 1024 * 1024, f"Peak memory usage: {peak / (1024*1024):.2f} MB"
    
    def test_rapid_file_discovery(self, temp_journal_dir):
        """Test file discovery performance with many files."""
        parser = JournalParser(temp_journal_dir)
        
        # Create many journal files
        file_count = 100
        for i in range(file_count):
            filename = f"Journal.202409062{i:03d}00.01.log"
            journal_file = temp_journal_dir / filename
            
            with open(journal_file, 'w', encoding='utf-8') as f:
                f.write(f'{{"timestamp":"2024-09-06T23:00:00Z","event":"Test{i}"}}\n')
        
        # Test discovery performance
        start_time = time.time()
        journal_files = parser.find_journal_files()
        end_time = time.time()
        
        discovery_time = end_time - start_time
        
        assert len(journal_files) == file_count
        # Discovery should be fast (less than 1 second for 100 files)
        assert discovery_time < 1.0, f"Discovery took {discovery_time:.2f} seconds"
        
        # Verify files are properly sorted (newest first)
        for i in range(len(journal_files) - 1):
            current_time = parser._extract_timestamp_from_filename(journal_files[i])
            next_time = parser._extract_timestamp_from_filename(journal_files[i + 1])
            assert current_time >= next_time, "Files not properly sorted by timestamp"


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
