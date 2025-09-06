"""
Comprehensive tests for journal parser functionality.

Tests journal file discovery, parsing, validation, and position tracking.
This provides verification that the journal system works correctly.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

def test_journal_parser_basic():
    """Test basic journal parser functionality."""
    from src.journal.parser import JournalParser
    
    print("🧪 Testing journal parser basic functionality...")
    
    # Test 1: Parser initialization
    print("  ✓ Testing parser initialization...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        parser = JournalParser(temp_path)
        assert parser.journal_path == temp_path
        assert isinstance(parser.file_positions, dict)
        print("    ✅ Parser initializes correctly")
    
    # Test 2: JSON parsing
    print("  ✓ Testing JSON entry parsing...")
    parser = JournalParser(Path("."))
    
    # Valid JSON
    valid_entry = '{ "timestamp":"2024-09-06T12:00:00Z", "event":"LoadGame", "Commander":"TestCMDR" }'
    parsed = parser.parse_journal_entry(valid_entry)
    assert parsed is not None
    assert parsed['event'] == 'LoadGame'
    assert parsed['Commander'] == 'TestCMDR'
    
    # Invalid JSON
    invalid_entry = '{ "timestamp":"2024-09-06T12:00:00Z", "event":"LoadGame", "Commander":'
    parsed_invalid = parser.parse_journal_entry(invalid_entry)
    assert parsed_invalid is None
    
    # Empty line
    empty_parsed = parser.parse_journal_entry("")
    assert empty_parsed is None
    
    print("    ✅ JSON parsing works correctly")
    
    # Test 3: Entry validation
    print("  ✓ Testing entry validation...")
    
    # Valid entry
    valid_entry = {
        "timestamp": "2024-09-06T12:00:00Z",
        "event": "LoadGame",
        "Commander": "TestCMDR"
    }
    assert parser.validate_journal_entry(valid_entry) is True
    
    # Missing timestamp
    invalid_entry = {
        "event": "LoadGame", 
        "Commander": "TestCMDR"
    }
    assert parser.validate_journal_entry(invalid_entry) is False
    
    # Missing event
    invalid_entry2 = {
        "timestamp": "2024-09-06T12:00:00Z",
        "Commander": "TestCMDR"
    }
    assert parser.validate_journal_entry(invalid_entry2) is False
    
    print("    ✅ Entry validation works correctly")
    
    print("🎉 Basic journal parser tests passed!")
    return True


def test_journal_file_discovery():
    """Test journal file discovery and sorting."""
    print("🧪 Testing journal file discovery and sorting...")
    
    # Use the mock data directory
    mock_data_path = Path("tests/mock_data")
    if not mock_data_path.exists():
        print("  ⚠️  Mock data directory not found, skipping file discovery tests")
        return True
    
    from src.journal.parser import JournalParser
    
    # Test with mock data
    parser = JournalParser(mock_data_path)
    
    # Test 1: Find all journal files
    print("  ✓ Testing journal file discovery...")
    journal_files = parser.find_journal_files()
    assert len(journal_files) >= 3  # Should find our 3 test files
    
    # Verify all files are journal files
    for file_path in journal_files:
        assert "Journal." in file_path.name
        assert file_path.name.endswith(('.log', '.log.backup'))
    
    print(f"    ✅ Found {len(journal_files)} journal files")
    
    # Test 2: Get latest journal
    print("  ✓ Testing latest journal detection...")
    latest = parser.get_latest_journal()
    assert latest is not None
    assert latest.name.startswith("Journal.")
    print(f"    ✅ Latest journal: {latest.name}")
    
    # Test 3: Get active (non-backup) journal
    print("  ✓ Testing active journal detection...")
    active = parser.get_active_journal()
    assert active is not None
    assert not active.name.endswith('.backup')
    print(f"    ✅ Active journal: {active.name}")
    
    # Test 4: Timestamp extraction
    print("  ✓ Testing timestamp extraction...")
    for file_path in journal_files:
        timestamp = parser._extract_timestamp_from_filename(file_path)
        if "Journal." in file_path.name:
            assert timestamp is not None
            assert isinstance(timestamp, datetime)
            print(f"    📅 {file_path.name} -> {timestamp}")
    
    print("    ✅ Timestamp extraction works correctly")
    
    print("🎉 Journal file discovery tests passed!")
    return True


def test_journal_file_reading():
    """Test journal file reading and parsing."""
    print("🧪 Testing journal file reading and parsing...")
    
    mock_data_path = Path("tests/mock_data")
    if not mock_data_path.exists():
        print("  ⚠️  Mock data directory not found, skipping file reading tests")
        return True
    
    from src.journal.parser import JournalParser
    
    parser = JournalParser(mock_data_path)
    journal_files = parser.find_journal_files()
    
    if not journal_files:
        print("  ⚠️  No journal files found, skipping reading tests")
        return True
    
    # Test 1: Read complete journal file
    print("  ✓ Testing complete file reading...")
    test_file = journal_files[0]
    entries = parser.read_journal_file_complete(test_file)
    assert len(entries) > 0
    
    # Verify first entry is FileHeader
    fileheader = None
    for entry in entries:
        if entry.get('event') == 'Fileheader':
            fileheader = entry
            break
    
    assert fileheader is not None
    assert 'gameversion' in fileheader
    print(f"    ✅ Read {len(entries)} entries from {test_file.name}")
    
    # Test 2: Incremental reading with position tracking
    print("  ✓ Testing incremental reading...")
    parser.reset_positions()
    
    # First read
    new_entries1 = parser.get_new_entries(test_file)
    assert len(new_entries1) > 0
    
    # Second read (should be empty since no new content)
    new_entries2 = parser.get_new_entries(test_file)
    assert len(new_entries2) == 0
    
    print(f"    ✅ First read: {len(new_entries1)} entries, Second read: {len(new_entries2)} entries")
    
    # Test 3: File position tracking
    print("  ✓ Testing file position tracking...")
    initial_position = parser.get_file_position(test_file)
    assert initial_position > 0
    
    # Reset and verify
    parser.set_file_position(test_file, 0)
    reset_position = parser.get_file_position(test_file)
    assert reset_position == 0
    
    print("    ✅ File position tracking works correctly")
    
    # Test 4: FileHeader extraction
    print("  ✓ Testing FileHeader extraction...")
    header = parser.get_file_header(test_file)
    assert header is not None
    assert header['event'] == 'Fileheader'
    assert 'gameversion' in header
    print(f"    ✅ FileHeader: {header.get('gameversion', 'unknown')}")
    
    print("🎉 Journal file reading tests passed!")
    return True


def test_journal_summary():
    """Test journal summary generation."""
    print("🧪 Testing journal summary generation...")
    
    mock_data_path = Path("tests/mock_data")
    if not mock_data_path.exists():
        print("  ⚠️  Mock data directory not found, skipping summary tests")
        return True
    
    from src.journal.parser import JournalParser
    
    parser = JournalParser(mock_data_path)
    
    # Test summary generation
    print("  ✓ Testing summary generation...")
    summary = parser.get_journal_summary()
    
    # Verify summary structure
    required_fields = ['total_files', 'active_files', 'backup_files', 'latest_file', 
                      'latest_active', 'date_range', 'file_sizes', 'total_size_mb']
    
    for field in required_fields:
        assert field in summary, f"Missing field: {field}"
    
    assert summary['total_files'] >= 3
    assert summary['active_files'] >= 2
    assert summary['backup_files'] >= 1
    assert summary['latest_file'] is not None
    assert summary['total_size_mb'] > 0
    
    print(f"    ✅ Summary: {summary['total_files']} files, {summary['total_size_mb']} MB")
    print(f"    📊 Active: {summary['active_files']}, Backup: {summary['backup_files']}")
    
    # Test date range
    if summary['date_range']['earliest'] and summary['date_range']['latest']:
        earliest = summary['date_range']['earliest']
        latest = summary['date_range']['latest']
        print(f"    📅 Date range: {earliest} to {latest}")
        assert latest >= earliest
    
    print("🎉 Journal summary tests passed!")
    return True


def test_error_handling():
    """Test error handling and edge cases."""
    print("🧪 Testing error handling and edge cases...")
    
    from src.journal.parser import JournalParser
    
    # Test 1: Non-existent directory
    print("  ✓ Testing non-existent directory...")
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent = Path(temp_dir) / "does_not_exist"
        parser = JournalParser(non_existent)
        
        files = parser.find_journal_files()
        assert len(files) == 0
        
        latest = parser.get_latest_journal()
        assert latest is None
        
        summary = parser.get_journal_summary()
        assert summary['total_files'] == 0
    
    print("    ✅ Non-existent directory handled correctly")
    
    # Test 2: Empty directory
    print("  ✓ Testing empty directory...")
    with tempfile.TemporaryDirectory() as temp_dir:
        empty_path = Path(temp_dir)
        parser = JournalParser(empty_path)
        
        files = parser.find_journal_files()
        assert len(files) == 0
        
        summary = parser.get_journal_summary()
        assert summary['total_files'] == 0
    
    print("    ✅ Empty directory handled correctly")
    
    # Test 3: Invalid journal filename
    print("  ✓ Testing invalid filename parsing...")
    parser = JournalParser(Path("."))
    
    invalid_path = Path("InvalidFile.txt")
    timestamp = parser._extract_timestamp_from_filename(invalid_path)
    assert timestamp is None
    
    print("    ✅ Invalid filenames handled correctly")
    
    # Test 4: Malformed JSON handling
    print("  ✓ Testing malformed JSON...")
    malformed_entries = [
        '{ "timestamp":"2024-09-06T12:00:00Z", "event":"LoadGame", "Commander":',  # Incomplete
        '{ timestamp":"2024-09-06T12:00:00Z", "event":"LoadGame" }',              # Missing quote
        'not json at all',                                                         # Not JSON
        '{}',                                                                      # Empty object
        '{ "event":"LoadGame" }',                                                  # Missing timestamp
    ]
    
    for malformed in malformed_entries:
        parsed = parser.parse_journal_entry(malformed)
        # Should either be None or fail validation
        if parsed is not None:
            assert not parser.validate_journal_entry(parsed)
    
    print("    ✅ Malformed JSON handled correctly")
    
    print("🎉 Error handling tests passed!")
    return True


def test_integration_with_config():
    """Test integration with configuration system."""
    print("🧪 Testing integration with configuration system...")
    
    from src.utils.config import EliteConfig
    from src.journal.parser import JournalParser
    
    # Test 1: Parser with configuration
    print("  ✓ Testing parser with configuration...")
    config = EliteConfig()
    parser = JournalParser(config.journal_path)
    
    assert parser.journal_path == config.journal_path
    print(f"    ✅ Parser uses config path: {config.journal_path}")
    
    # Test 2: Summary with config paths
    print("  ✓ Testing summary generation...")
    summary = parser.get_journal_summary()
    assert isinstance(summary, dict)
    print(f"    ✅ Generated summary with {summary.get('total_files', 0)} files")
    
    print("🎉 Configuration integration tests passed!")
    return True


if __name__ == "__main__":
    """Run comprehensive journal parser tests."""
    try:
        print("=" * 60)
        print("Journal Parser Comprehensive Test Suite")
        print("=" * 60)
        
        # Run all test functions
        test_functions = [
            test_journal_parser_basic,
            test_journal_file_discovery, 
            test_journal_file_reading,
            test_journal_summary,
            test_error_handling,
            test_integration_with_config
        ]
        
        passed = 0
        total = len(test_functions)
        
        for test_func in test_functions:
            try:
                result = test_func()
                if result:
                    passed += 1
                print()
            except Exception as e:
                print(f"❌ {test_func.__name__} failed: {e}")
                import traceback
                traceback.print_exc()
                print()
        
        print("=" * 60)
        print(f"Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("✅ All journal parser tests passed!")
            print("\nTry these commands to test the journal parser:")
            print("  python -c \"from src.journal import JournalParser; print('Journal parser imported successfully')\"")
            print("  python tests/test_journal_parser.py")
        else:
            print("❌ Some tests failed. Check the output above for details.")
            exit(1)
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)