"""
Integration tests for EDCoPilot grammar specification compliance.

These tests verify end-to-end compliance with the EDCoPilot grammar specification
and ensure generated files would be accepted by EDCoPilot without parsing errors.
"""

import unittest
import tempfile
import os
import re
from typing import List, Dict, Set
from unittest.mock import Mock

from src.edcopilot.templates import EDCoPilotTemplateManager
from src.utils.data_store import DataStore, GameState


class TestEDCoPilotGrammarCompliance(unittest.TestCase):
    """Integration tests for complete EDCoPilot grammar compliance."""

    def setUp(self):
        """Set up test fixtures with realistic game data."""
        self.data_store = Mock(spec=DataStore)
        self.game_state = GameState()

        # Set up realistic Elite Dangerous game state
        self.game_state.commander_name = "Hadesfire"
        self.game_state.current_system = "Blae Drye SG-P b25-6"
        self.game_state.current_station = "Explorer's Anchorage"
        self.game_state.current_ship = "Anaconda"
        self.game_state.ship_name = "EXCELSIOR"
        self.game_state.credits = 1234567890
        self.game_state.fuel_level = 75.5
        self.game_state.fuel_capacity = 64.0

        self.data_store.get_game_state.return_value = self.game_state
        self.templates = EDCoPilotTemplateManager()

    def test_space_chatter_full_grammar_compliance(self):
        """Test complete Space Chatter grammar compliance per specification."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Parse content into lines
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        comment_lines = [line for line in lines if line.startswith('#')]
        dialogue_lines = [line for line in lines if not line.startswith('#')]

        # 1. File structure validation
        self.assertTrue(len(comment_lines) > 0, "File must contain header comments")
        self.assertTrue(len(dialogue_lines) > 0, "File must contain dialogue lines")

        # 2. Grammar compliance for each dialogue line
        for line in dialogue_lines:
            with self.subTest(line=line):
                self._validate_space_chatter_line_grammar(line)

        # 3. Token replacement validation
        self._validate_token_replacement(content)

        # 4. No EDCoPilot parsing errors expected
        self._validate_no_parsing_errors(content, "SpaceChatter")

    def test_crew_chatter_full_grammar_compliance(self):
        """Test complete Crew Chatter grammar compliance per specification."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.CrewChatter.Custom.txt', '')

        # Must use conversation block format
        self.assertIn('[example]', content, "Crew chatter must use conversation blocks")
        self.assertIn('[\\example]', content, "Crew chatter must have closing blocks")

        # Parse conversation blocks
        blocks = self._extract_conversation_blocks(content)
        self.assertTrue(len(blocks) > 0, "Must contain at least one conversation block")

        for block in blocks:
            with self.subTest(block=block[:100]):
                self._validate_crew_chatter_block_grammar(block)

        # Validate overall structure
        self._validate_conversation_block_structure(content)
        self._validate_no_parsing_errors(content, "CrewChatter")

    def test_deep_space_chatter_grammar_compliance(self):
        """Test Deep Space Chatter grammar compliance."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.DeepSpaceChatter.Custom.txt', '')

        lines = [line.strip() for line in content.split('\n')
                if line.strip() and not line.startswith('#')]

        for line in lines:
            with self.subTest(line=line):
                # Deep space can use either format
                self._validate_dialogue_line_grammar(line, "DeepSpace")

        self._validate_no_parsing_errors(content, "DeepSpaceChatter")

    def test_token_format_specification_compliance(self):
        """Test that all tokens use specification-compliant format."""
        templates = self.templates.generate_all_templates()
        all_templates = [
            templates.get('EDCoPilot.SpaceChatter.Custom.txt', ''),
            templates.get('EDCoPilot.CrewChatter.Custom.txt', ''),
            templates.get('EDCoPilot.DeepSpaceChatter.Custom.txt', '')
        ]

        for content in all_templates:
            with self.subTest(content_type=content.split('\n')[0]):
                # No curly brace tokens allowed
                self.assertNotRegex(content, r'[^#]*\{[^}]+\}',
                    "Content must not contain {token} format outside comments")

                # If tokens present, must be angle bracket format
                angle_tokens = re.findall(r'<([A-Za-z]+)>', content)
                if angle_tokens:
                    for token in angle_tokens:
                        with self.subTest(token=token):
                            self.assertRegex(token, r'^[A-Z][A-Za-z]*$',
                                f"Token {token} must follow proper naming convention")

    def test_speaker_role_specification_compliance(self):
        """Test that speaker roles conform to specification."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.CrewChatter.Custom.txt', '')

        # Extract all speaker roles
        speaker_roles = re.findall(r'\[<([^>]+)>\]', content)

        # Valid speaker roles per specification
        valid_speakers = {
            'EDCoPilot', 'Operations', 'Helm', 'Engineering', 'Comms',
            'Number1', 'Science', 'Security'
        }

        for speaker in speaker_roles:
            with self.subTest(speaker=speaker):
                # Must be a valid speaker role or custom crew format
                is_valid = (
                    speaker in valid_speakers or
                    speaker.startswith('Crew:')
                )
                self.assertTrue(is_valid,
                    f"Speaker role '{speaker}' not in specification")

    def test_condition_syntax_specification_compliance(self):
        """Test that conditions use specification-compliant syntax."""
        templates = self.templates.generate_all_templates()
        content = templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Find conditional lines
        conditional_lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('(') and ')' in line and not line.startswith('#'):
                conditional_lines.append(line)

        for line in conditional_lines:
            with self.subTest(line=line):
                # Extract condition part
                condition_match = re.match(r'^\(([^)]+)\)\s*(.+)', line)
                self.assertIsNotNone(condition_match,
                    f"Invalid condition syntax: {line}")

                condition_part = condition_match.group(1)
                dialogue_part = condition_match.group(2)

                # Validate condition syntax
                self._validate_condition_syntax(condition_part)

                # Dialogue part should not be empty
                self.assertTrue(len(dialogue_part.strip()) > 0,
                    "Dialogue part cannot be empty")

    def test_file_generation_end_to_end_compliance(self):
        """Test complete end-to-end file generation compliance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate all file types
            templates = self.templates.generate_all_templates()
            files_to_test = [
                ('EDCoPilot.SpaceChatter.Custom.txt', templates.get('EDCoPilot.SpaceChatter.Custom.txt', '')),
                ('EDCoPilot.CrewChatter.Custom.txt', templates.get('EDCoPilot.CrewChatter.Custom.txt', '')),
                ('EDCoPilot.DeepSpaceChatter.Custom.txt', templates.get('EDCoPilot.DeepSpaceChatter.Custom.txt', ''))
            ]

            for filename, content in files_to_test:
                with self.subTest(filename=filename):
                    filepath = os.path.join(temp_dir, filename)

                    # Write file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)

                    # Validate file was written correctly
                    self.assertTrue(os.path.exists(filepath))

                    # Read back and validate
                    with open(filepath, 'r', encoding='utf-8') as f:
                        read_content = f.read()

                    self.assertEqual(content, read_content)
                    self._validate_file_structure(read_content, filename)

    def _validate_space_chatter_line_grammar(self, line: str):
        """Validate a single space chatter line against grammar rules."""
        # Space chatter format options:
        # 1. Simple: "Dialogue text"
        # 2. Conditional: "(Condition) Dialogue text"

        if line.startswith('('):
            # Conditional format
            self.assertRegex(line, r'^\([A-Za-z&|]+\)\s+.+',
                f"Invalid conditional format: {line}")
        else:
            # Simple format - just dialogue text
            self.assertGreater(len(line), 0, "Dialogue cannot be empty")

        # Must not use invalid syntax
        self.assertNotIn('condition:', line,
            f"Invalid 'condition:' syntax in: {line}")

    def _validate_crew_chatter_block_grammar(self, block: str):
        """Validate a crew chatter conversation block."""
        lines = [line.strip() for line in block.split('\n') if line.strip()]

        # Must have at least one speaker line
        speaker_lines = [line for line in lines if line.startswith('[<')]
        self.assertGreater(len(speaker_lines), 0,
            "Conversation block must contain speaker lines")

        for line in speaker_lines:
            with self.subTest(line=line):
                # Must match speaker format
                self.assertRegex(line, r'^\[<[A-Za-z:]+>\]\s*.+',
                    f"Invalid speaker format: {line}")

    def _validate_dialogue_line_grammar(self, line: str, context: str):
        """Validate dialogue line grammar for any context."""
        # General rules that apply to all dialogue
        self.assertGreater(len(line.strip()), 0, "Dialogue cannot be empty")
        self.assertNotIn('condition:', line, "Invalid condition: syntax")

    def _validate_token_replacement(self, content: str):
        """Validate that token replacement is working correctly."""
        # Should not contain unreplaced {tokens}
        unreplaced_tokens = re.findall(r'\{([^}]+)\}', content)
        comment_tokens = []
        content_tokens = []

        for line in content.split('\n'):
            if line.strip().startswith('#'):
                comment_tokens.extend(re.findall(r'\{([^}]+)\}', line))
            else:
                content_tokens.extend(re.findall(r'\{([^}]+)\}', line))

        # Unreplaced tokens in actual content are errors
        self.assertEqual(len(content_tokens), 0,
            f"Found unreplaced tokens in content: {content_tokens}")

    def _validate_conversation_block_structure(self, content: str):
        """Validate conversation block structure."""
        # Count blocks
        opening_blocks = content.count('[example]')
        closing_blocks = content.count('[\\example]')

        self.assertEqual(opening_blocks, closing_blocks,
            "Mismatched conversation block tags")
        self.assertGreater(opening_blocks, 0,
            "Crew chatter must contain conversation blocks")

    def _validate_condition_syntax(self, condition: str):
        """Validate condition syntax according to specification."""
        # Valid characters for conditions
        valid_pattern = r'^[A-Za-z&|]+$'
        self.assertRegex(condition, valid_pattern,
            f"Invalid characters in condition: {condition}")

        # If compound condition, validate parts
        if '&' in condition or '|' in condition:
            # Split and validate each part
            parts = re.split(r'[&|]', condition)
            for part in parts:
                self.assertGreater(len(part.strip()), 0,
                    f"Empty condition part in: {condition}")

    def _extract_conversation_blocks(self, content: str) -> List[str]:
        """Extract conversation blocks from crew chatter content."""
        blocks = []
        lines = content.split('\n')
        current_block = []
        in_block = False

        for line in lines:
            if '[example]' in line:
                in_block = True
                current_block = []
            elif '[\\example]' in line:
                if in_block and current_block:
                    blocks.append('\n'.join(current_block))
                in_block = False
                current_block = []
            elif in_block:
                current_block.append(line)

        return blocks

    def _validate_no_parsing_errors(self, content: str, file_type: str):
        """Validate that content would not cause EDCoPilot parsing errors."""
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1
            line = line.strip()

            if not line or line.startswith('#'):
                continue  # Skip empty and comment lines

            with self.subTest(line_num=line_num, line=line):
                # Check for patterns that cause EDCoPilot "bad line" errors
                error_patterns = [
                    (r'condition:', "Invalid condition: syntax"),
                    (r'\{[^}]+\}', "Invalid {token} format"),
                    (r'^\|', "Line cannot start with |"),
                    (r'\|\s*$', "Line cannot end with |")
                ]

                for pattern, error_msg in error_patterns:
                    self.assertNotRegex(line, pattern,
                        f"{error_msg} at line {line_num}: {line}")

    def _validate_file_structure(self, content: str, filename: str):
        """Validate overall file structure compliance."""
        lines = content.split('\n')

        # Should have header comments
        has_header = any(line.startswith('#') for line in lines[:10])
        self.assertTrue(has_header, f"{filename} should have header comments")

        # Should have non-comment content
        has_content = any(not line.startswith('#') and line.strip()
                         for line in lines)
        self.assertTrue(has_content, f"{filename} should have dialogue content")

        # File-specific validations
        if 'CrewChatter' in filename:
            self.assertIn('[example]', content,
                "CrewChatter files must use conversation blocks")
        elif 'SpaceChatter' in filename:
            # Space chatter should not use conversation blocks
            self.assertNotIn('[example]', content,
                "SpaceChatter should not use conversation blocks")


if __name__ == '__main__':
    unittest.main()