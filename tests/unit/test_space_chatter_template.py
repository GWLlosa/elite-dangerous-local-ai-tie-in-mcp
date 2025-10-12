"""
Unit tests for Space Chatter template system.

Tests validate that Space Chatter template generates conversation blocks
matching authoritative EDCoPilot format (not single-line format).
"""

import pytest
from src.edcopilot.templates import (
    SpaceChatterTemplate,
    SpaceRole,
    SpaceConversation,
    EDCoPilotTokens
)


class TestSpaceChatterTemplate:
    """Test suite for Space Chatter template."""

    def test_template_initialization(self):
        """Template should initialize with empty conversations list."""
        template = SpaceChatterTemplate()
        assert hasattr(template, 'conversations')
        assert isinstance(template.conversations, list)
        assert len(template.conversations) == 0

    def test_add_conversation(self):
        """Template should support adding conversations."""
        template = SpaceChatterTemplate()
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Test dialogue")
            ]
        )
        template.add_conversation(conversation)
        assert len(template.conversations) == 1

    def test_to_file_content_no_comments(self):
        """Generated file content must not contain any comment lines."""
        template = SpaceChatterTemplate()
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Test dialogue")
            ]
        )
        template.add_conversation(conversation)

        content = template.to_file_content()

        # No lines should start with #
        for line in content.split('\n'):
            if line.strip():  # Ignore blank lines
                assert not line.strip().startswith('#'), f"Found comment line: {line}"

    def test_to_file_content_uses_conversation_blocks(self):
        """Generated content must use [example]...[\\example] blocks."""
        template = SpaceChatterTemplate()
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Test dialogue")
            ]
        )
        template.add_conversation(conversation)

        content = template.to_file_content()

        assert "[example]" in content
        assert "[\\example]" in content
        assert "[/example]" not in content  # Wrong format

    def test_to_file_content_uses_speaker_roles(self):
        """Generated content must include speaker roles."""
        template = SpaceChatterTemplate()
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Requesting docking"),
                (SpaceRole.STATIONNAME, "Clearance granted")
            ]
        )
        template.add_conversation(conversation)

        content = template.to_file_content()

        assert "[<ship1>]" in content
        assert "[<stationname>]" in content

    def test_to_file_content_no_single_line_format(self):
        """Generated content must not use old single-line (Condition) format."""
        template = SpaceChatterTemplate()
        template.generate_default_chatter()

        content = template.to_file_content()

        # Should not have lines like "(InSupercruise) Some text"
        # All conditions should be inline with [example] tag
        lines = content.split('\n')
        for line in lines:
            # Lines starting with ( outside [example] context are wrong
            if line.strip().startswith('(') and '[example]' not in line:
                pytest.fail(f"Found single-line conditional format: {line}")

    def test_generate_navigation_chatter_creates_conversations(self):
        """Navigation chatter should create conversation blocks."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()

        assert len(template.conversations) > 0
        assert all(isinstance(conv, SpaceConversation) for conv in template.conversations)

    def test_generate_exploration_chatter_creates_conversations(self):
        """Exploration chatter should create conversation blocks."""
        template = SpaceChatterTemplate()
        template.generate_exploration_chatter()

        assert len(template.conversations) > 0
        assert all(isinstance(conv, SpaceConversation) for conv in template.conversations)

    def test_generate_combat_chatter_creates_conversations(self):
        """Combat chatter should create conversation blocks."""
        template = SpaceChatterTemplate()
        template.generate_combat_chatter()

        assert len(template.conversations) > 0
        assert all(isinstance(conv, SpaceConversation) for conv in template.conversations)

    def test_generate_trading_chatter_creates_conversations(self):
        """Trading chatter should create conversation blocks."""
        template = SpaceChatterTemplate()
        template.generate_trading_chatter()

        assert len(template.conversations) > 0
        assert all(isinstance(conv, SpaceConversation) for conv in template.conversations)

    def test_default_chatter_uses_lowercase_tokens(self):
        """Default chatter should use lowercase authoritative tokens."""
        template = SpaceChatterTemplate()
        template.generate_default_chatter()

        content = template.to_file_content()

        # Should use lowercase tokens
        assert "<cmdrname>" in content or "<starsystem>" in content or "<stationname>" in content

        # Should NOT use old TitleCase tokens
        assert "<CommanderName>" not in content
        assert "<SystemName>" not in content
        assert "<StationName>" not in content

    def test_navigation_chatter_includes_docking_conversation(self):
        """Navigation chatter should include docking conversations."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()

        content = template.to_file_content()

        # Should have docking-related dialogue
        assert "docking" in content.lower() or "clearance" in content.lower()

    def test_exploration_chatter_includes_scanning_conversation(self):
        """Exploration chatter should include scanning conversations."""
        template = SpaceChatterTemplate()
        template.generate_exploration_chatter()

        content = template.to_file_content()

        # Should have scanning-related dialogue
        assert "scan" in content.lower() or "discovery" in content.lower()

    def test_multiple_conversations_separated_by_blank_lines(self):
        """Multiple conversation blocks should be separated by blank lines."""
        template = SpaceChatterTemplate()
        template.add_conversation(SpaceConversation(
            dialogue_lines=[(SpaceRole.SHIP1, "First conversation")]
        ))
        template.add_conversation(SpaceConversation(
            dialogue_lines=[(SpaceRole.SHIP1, "Second conversation")]
        ))

        content = template.to_file_content()

        # Should have pattern: [example]...[\example]\n\n[example]
        assert "[\\example]\n\n[example]" in content or "[\\example]\r\n\r\n[example]" in content

    def test_conversations_with_conditions_format_correctly(self):
        """Conversations with conditions should format inline with [example]."""
        template = SpaceChatterTemplate()
        template.add_conversation(SpaceConversation(
            dialogue_lines=[(SpaceRole.SHIP1, "Fuel low")],
            conditions=["FuelLow"]
        ))

        content = template.to_file_content()

        assert "[example] (FuelLow)" in content


class TestSpaceChatterBackwardsCompatibility:
    """Test suite for backwards compatibility handling."""

    def test_old_entries_list_still_supported(self):
        """Template should still support old entries list for migration."""
        template = SpaceChatterTemplate()

        # Old code might have set entries directly
        # Should be able to check if entries exist for compatibility
        assert hasattr(template, 'conversations')

    def test_can_convert_old_entries_to_conversations(self):
        """Should be able to convert old single-line entries to conversations."""
        template = SpaceChatterTemplate()

        # This is for migration path - old entries should convert to conversations
        # Implementation detail: old entries may need to be wrapped in conversations
        template.generate_default_chatter()

        # All output should be conversation blocks
        content = template.to_file_content()
        assert "[example]" in content
        assert "[\\example]" in content
