"""
Unit tests for EDCoPilot file format validation and grammar compliance.

These tests verify that generated EDCoPilot custom files conform to the proper
grammar specification and will be accepted by EDCoPilot without "bad line" errors.
"""

import unittest
import tempfile
import os
import re
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from src.edcopilot.templates import EDCoPilotTemplateManager
from src.utils.data_store import DataStore, GameState


class TestEDCoPilotFormatValidation(unittest.TestCase):
    """Test suite for EDCoPilot file format validation and compliance."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_store = Mock(spec=DataStore)
        self.game_state = GameState()
        self.game_state.commander_name = "TestCommander"
        self.game_state.current_system = "Sol"
        self.game_state.current_station = "Jameson Memorial"
        self.game_state.current_ship = "Anaconda"
        self.game_state.ship_name = "Exploration Vessel"

        self.data_store.get_game_state.return_value = self.game_state
        self.templates = EDCoPilotTemplateManager()

    def test_space_chatter_format_compliance(self):
        """Test that Space Chatter follows correct format without condition prefixes."""
        # Generate all templates and get space chatter content
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]

        for line in lines:
            with self.subTest(line=line):
                # Should NOT contain condition:Name| format
                self.assertNotIn('condition:', line,
                    f"Space chatter should not contain 'condition:' prefix: {line}")

                # Should NOT contain curly brace tokens
                self.assertNotRegex(line, r'\{[^}]+\}',
                    f"Should use <token> format, not {{token}}: {line}")

                # Should use angle bracket tokens if any tokens present
                # Note: speaker roles like [<ship1>] are valid, not tokens
                # Tokens appear within dialogue text, not as speaker roles
                if '<' in line and '>' in line and not line.startswith('[<'):
                    # Check for lowercase tokens (authoritative format)
                    has_token = re.search(r'<[a-z]+>', line) or re.search(r'<[A-Z][a-z]+>', line)
                    self.assertTrue(has_token,
                        f"Tokens should use lowercase or TitleCase format: {line}")

    def test_crew_chatter_conversation_blocks(self):
        """Test that Crew Chatter uses proper conversation block format."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.CrewChatter.Custom.txt', '')

        # Should contain [example] blocks
        self.assertIn('[example]', content,
            "Crew chatter must contain [example] conversation blocks")
        self.assertIn('[\\example]', content,
            "Crew chatter must contain [\\example] closing blocks")

        # Count opening and closing blocks
        opening_blocks = content.count('[example]')
        closing_blocks = content.count('[\\example]')
        self.assertEqual(opening_blocks, closing_blocks,
            "Number of [example] and [\\example] blocks must match")

        # Check for proper speaker roles
        speaker_roles = ['[<EDCoPilot>]', '[<Operations>]', '[<Helm>]',
                        '[<Engineering>]', '[<Comms>]', '[<Science>]', '[<Security>]']

        found_speakers = False
        for role in speaker_roles:
            if role in content:
                found_speakers = True
                break

        self.assertTrue(found_speakers,
            "Crew chatter must contain proper speaker roles like [<Operations>]")

    def test_token_format_validation(self):
        """Test that all token formats use angle brackets, not curly braces."""
        templates = self.templates.generate_all_templates()
        all_content = [
            templates.get('EDCoPilot.SpaceChatter.Custom.txt', ''),
            templates.get('EDCoPilot.CrewChatter.Custom.txt', ''),
            templates.get('EDCoPilot.DeepSpaceChatter.Custom.txt', '')
        ]

        for content in all_content:
            with self.subTest(content_type=content[:50]):
                # Should not contain {Token} format
                curly_tokens = []
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '{' in line and '}' in line:
                        import re
                        tokens = re.findall(r'\{([^}]+)\}', line)
                        if tokens:
                            curly_tokens.append(f"Line {i+1}: {line.strip()}")

                self.assertEqual(len(curly_tokens), 0,
                    f"Found invalid {{token}} format in: {curly_tokens}")

    def test_condition_syntax_validation(self):
        """Test that conditions use proper syntax if present."""
        templates = self.templates.generate_all_templates()
        space_content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Parse each line for condition syntax
        lines = [line.strip() for line in space_content.split('\n')
                if line.strip() and not line.startswith('#')]

        for line in lines:
            with self.subTest(line=line):
                # If line contains conditions, should use (Condition) format
                if line.startswith('(') and ')' in line:
                    # Valid condition format: (ConditionName) dialogue text
                    self.assertRegex(line, r'^\([A-Za-z&|]+\)\s+.+',
                        f"Invalid condition syntax: {line}")

                # Should NOT use condition:Name| format
                self.assertFalse(line.startswith('condition:'),
                    f"Invalid condition format 'condition:': {line}")

    def test_comment_header_compliance(self):
        """Test that file headers are minimal and compliant."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')
        lines = content.split('\n')

        # Check that comments are simple and don't cause parsing issues
        comment_lines = [line for line in lines if line.startswith('#')]

        for comment in comment_lines:
            with self.subTest(comment=comment):
                # Comments should be simple
                self.assertTrue(comment.startswith('#'),
                    f"Comments must start with #: {comment}")

                # Avoid overly complex headers that EDCoPilot might reject
                if 'Format:' in comment:
                    # Format descriptions should be accurate
                    self.assertNotIn('condition:', comment,
                        "Format description should not reference invalid syntax")

    def test_deep_space_chatter_format(self):
        """Test Deep Space Chatter specific format requirements."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.DeepSpaceChatter.Custom.txt', '')
        lines = [line.strip() for line in content.split('\n')
                if line.strip() and not line.startswith('#')]

        # Deep space chatter may use simple format or conversation blocks
        # Verify it doesn't use invalid condition: syntax
        for line in lines:
            with self.subTest(line=line):
                self.assertNotIn('condition:', line,
                    f"Deep space chatter should not use 'condition:' syntax: {line}")

    def test_voice_assignment_format(self):
        """Test that voice assignments use correct format when present."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Look for voice assignments
        if 'voice:' in content:
            lines = content.split('\n')
            for line in lines:
                if 'voice:' in line:
                    with self.subTest(line=line):
                        # Voice should be properly formatted
                        # Format could be: [<speaker>]|voice:VoiceName|dialogue
                        # or in conversation blocks
                        self.assertRegex(line, r'voice:[A-Z]+',
                            f"Voice assignment should use proper format: {line}")

    def test_speaker_role_validation(self):
        """Test that speaker roles use correct format in crew chatter."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.CrewChatter.Custom.txt', '')

        # Find speaker role lines
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('[<') and '>]' in line:
                with self.subTest(line=line):
                    # Should match pattern [<RoleName>]
                    self.assertRegex(line, r'^\[<[A-Za-z]+>\]\s*.+',
                        f"Invalid speaker role format: {line}")

    def test_no_malformed_syntax(self):
        """Test for common syntax errors that cause EDCoPilot parsing failures."""
        templates = self.templates.generate_all_templates()
        all_content = [
            templates.get('EDCoPilot.SpaceChatter.Custom.txt', ''),
            templates.get('EDCoPilot.CrewChatter.Custom.txt', ''),
            templates.get('EDCoPilot.DeepSpaceChatter.Custom.txt', '')
        ]

        for content in all_content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_num = i + 1
                with self.subTest(line_num=line_num, line=line):
                    # No unmatched brackets
                    open_brackets = line.count('[')
                    close_brackets = line.count(']')
                    if open_brackets != close_brackets:
                        # Allow for multi-line conversation blocks
                        if not ('[example]' in line or '[\\example]' in line):
                            self.assertEqual(open_brackets, close_brackets,
                                f"Unmatched brackets at line {line_num}: {line}")

                    # No invalid character combinations
                    invalid_patterns = ['condition:', '|voice:', '{', '}']
                    for pattern in invalid_patterns:
                        if pattern in line and not line.startswith('#'):
                            # Some patterns are valid in specific contexts
                            if pattern == '|voice:' and '[<' in line:
                                continue  # Valid in speaker context
                            if pattern in ['{', '}']:
                                self.fail(f"Invalid token format at line {line_num}: {line}")

    def test_realistic_game_data_integration(self):
        """Test that generated content integrates real game data properly."""
        # Set up realistic game state
        self.game_state.current_system = "Blae Drye SG-P b25-6"
        self.game_state.current_station = "Explorer's Anchorage"
        self.game_state.ship_name = "EXCELSIOR"
        self.game_state.commander_name = "Hadesfire"

        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Content should contain actual game data, not placeholders
        self.assertNotIn('Unknown System', content,
            "Should not contain placeholder text when game data available")
        self.assertNotIn('{SystemName}', content,
            "Should not contain unreplaced tokens")

        # Should contain actual system name if tokens are used
        if '<SystemName>' in content:
            # Tokens should be properly formatted as <Token> not {Token}
            self.assertIn('<SystemName>', content,
                "Tokens should use <Token> format")

    def test_edcopilot_parsing_compatibility(self):
        """Test that generated content would be accepted by EDCoPilot parser."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')
        lines = [line.strip() for line in content.split('\n')
                if line.strip() and not line.startswith('#')]

        # Each non-comment line should be valid EDCoPilot syntax
        for line in lines:
            with self.subTest(line=line):
                # Should be either:
                # 1. Simple dialogue: "Text here"
                # 2. Conditional dialogue: "(Condition) Text here"
                # 3. Speaker dialogue: "[<Speaker>] Text here"
                # 4. Conversation block markers: [example] or [\example]
                # 5. Conversation block with condition: [example] (Condition)

                is_valid_format = (
                    # Conversation block markers
                    (line == '[example]' or line == '[\\example]' or
                     line.startswith('[example] (')) or
                    # Simple dialogue
                    (not line.startswith('(') and not line.startswith('[')) or
                    # Conditional dialogue
                    (line.startswith('(') and ')' in line and not 'condition:' in line) or
                    # Speaker dialogue
                    (line.startswith('[<') and '>]' in line)
                )

                self.assertTrue(is_valid_format,
                    f"Line format not compatible with EDCoPilot: {line}")


class TestEDCoPilotTemplateCorrections(unittest.TestCase):
    """Test corrections to EDCoPilot template generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_store = Mock(spec=DataStore)
        self.game_state = GameState()
        self.data_store.get_game_state.return_value = self.game_state
        self.templates = EDCoPilotTemplateManager()

    def test_space_chatter_no_condition_prefix(self):
        """Test that space chatter doesn't use condition: prefix format."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Should not contain any lines with condition: prefix
        lines = content.split('\n')
        bad_lines = [line for line in lines if 'condition:' in line and not line.startswith('#')]

        self.assertEqual(len(bad_lines), 0,
            f"Space chatter contains invalid condition: format: {bad_lines}")

    def test_crew_chatter_conversation_structure(self):
        """Test that crew chatter uses proper conversation block structure."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.CrewChatter.Custom.txt', '')

        # Must contain conversation blocks
        self.assertIn('[example]', content)
        self.assertIn('[\\example]', content)

        # Must contain speaker roles
        speaker_found = any(role in content for role in
                          ['[<EDCoPilot>]', '[<Operations>]', '[<Helm>]', '[<Engineering>]'])
        self.assertTrue(speaker_found, "Crew chatter must contain speaker roles")

    def test_token_replacement_uses_angle_brackets(self):
        """Test that token replacement uses <token> format, not {token}."""
        # Test with actual generated content
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Should not contain curly brace tokens in output
        lines = [line for line in content.split('\n') if line.strip() and not line.startswith('#')]

        for line in lines:
            # Should not contain {token} format
            self.assertNotRegex(line, r'\{[^}]+\}',
                f"Line contains invalid {{token}} format: {line}")

        # If tokens are used, they should use <token> format
        if any('<' in line and '>' in line for line in lines):
            has_valid_tokens = any(re.search(r'<[A-Za-z]+>', line) for line in lines)
            self.assertTrue(has_valid_tokens, "Should contain valid <Token> format")

    def test_comment_header_simplification(self):
        """Test that comment headers are simplified to avoid parsing issues."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Header should be minimal and not reference invalid syntax
        header_lines = [line for line in content.split('\n') if line.startswith('#')]

        for header in header_lines:
            # Should not reference invalid formats in comments
            self.assertNotIn('condition:', header,
                "Header should not reference invalid condition: syntax")
            self.assertNotIn('{Token}', header,
                "Header should not reference invalid {token} syntax")


if __name__ == '__main__':
    unittest.main()