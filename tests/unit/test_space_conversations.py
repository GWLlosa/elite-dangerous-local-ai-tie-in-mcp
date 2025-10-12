"""
Unit tests for Space Chatter conversation block system.

Tests validate that space chatter uses conversation blocks with speaker roles
matching the authoritative EDCoPilot format.
"""

import pytest
from src.edcopilot.templates import SpaceRole, SpaceConversation


class TestSpaceRole:
    """Test suite for space speaker roles."""

    def test_space_roles_exist(self):
        """All authoritative space roles should be defined."""
        assert hasattr(SpaceRole, 'SHIP1')
        assert hasattr(SpaceRole, 'SHIP2')
        assert hasattr(SpaceRole, 'STATIONNAME')

    def test_ship1_role_format(self):
        """[<ship1>] should be the format for first ship speaker."""
        assert SpaceRole.SHIP1.value == "[<ship1>]"

    def test_ship2_role_format(self):
        """[<ship2>] should be the format for second ship speaker."""
        assert SpaceRole.SHIP2.value == "[<ship2>]"

    def test_stationname_role_format(self):
        """[<stationname>] should be the format for station speaker."""
        assert SpaceRole.STATIONNAME.value == "[<stationname>]"


class TestSpaceConversation:
    """Test suite for space conversation blocks."""

    def test_conversation_initialization(self):
        """Space conversation should initialize with dialogue lines."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Requesting docking clearance"),
                (SpaceRole.STATIONNAME, "Clearance granted")
            ]
        )
        assert len(conversation.dialogue_lines) == 2
        assert conversation.dialogue_lines[0][0] == SpaceRole.SHIP1
        assert conversation.dialogue_lines[0][1] == "Requesting docking clearance"

    def test_conversation_with_conditions(self):
        """Space conversation should support optional conditions."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Departing station")
            ],
            conditions=["not-deep-space"]
        )
        assert conversation.conditions == ["not-deep-space"]

    def test_format_simple_conversation(self):
        """Format simple two-line conversation correctly."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Control, requesting docking clearance."),
                (SpaceRole.STATIONNAME, "Clearance granted. Proceed to pad.")
            ]
        )
        output = conversation.format_for_edcopilot()

        expected = """[example]
[<ship1>] Control, requesting docking clearance.
[<stationname>] Clearance granted. Proceed to pad.
[\\example]"""

        assert output == expected

    def test_format_multi_line_conversation(self):
        """Format conversation with three speakers correctly."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Flight control, this is Apex Interstellar."),
                (SpaceRole.STATIONNAME, "Copy Apex. Landing pad assigned."),
                (SpaceRole.SHIP1, "Acknowledged. Proceeding to pad.")
            ]
        )
        output = conversation.format_for_edcopilot()

        expected = """[example]
[<ship1>] Flight control, this is Apex Interstellar.
[<stationname>] Copy Apex. Landing pad assigned.
[<ship1>] Acknowledged. Proceeding to pad.
[\\example]"""

        assert output == expected

    def test_format_with_conditions(self):
        """Format conversation with inline conditions correctly."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Departing station. o7 commanders.")
            ],
            conditions=["not-deep-space"]
        )
        output = conversation.format_for_edcopilot()

        # Conditions should be inline with [example] tag
        expected = """[example] (not-deep-space)
[<ship1>] Departing station. o7 commanders.
[\\example]"""

        assert output == expected

    def test_format_with_multiple_conditions(self):
        """Format conversation with multiple conditions using & separator."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Fuel reserves critical!")
            ],
            conditions=["InSupercruise", "FuelLow"]
        )
        output = conversation.format_for_edcopilot()

        expected = """[example] (InSupercruise&FuelLow)
[<ship1>] Fuel reserves critical!
[\\example]"""

        assert output == expected

    def test_format_uses_backslash_example_end(self):
        """Conversation blocks must use [\\example] not [/example]."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Test dialogue")
            ]
        )
        output = conversation.format_for_edcopilot()

        assert "[\\example]" in output
        assert "[/example]" not in output

    def test_no_comments_in_output(self):
        """Conversation format must not include any comment lines."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Test dialogue")
            ]
        )
        output = conversation.format_for_edcopilot()

        # No lines should start with #
        for line in output.split('\n'):
            assert not line.strip().startswith('#')

    def test_tokens_preserved_in_dialogue(self):
        """Tokens should be preserved in dialogue text."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "<stationname> control, this is <callsign>."),
                (SpaceRole.STATIONNAME, "<callsign>, this is <stationname> control.")
            ]
        )
        output = conversation.format_for_edcopilot()

        assert "<stationname>" in output
        assert "<callsign>" in output


class TestSpaceConversationValidation:
    """Test suite for space conversation validation."""

    def test_empty_dialogue_lines_rejected(self):
        """Conversation with no dialogue lines should be rejected."""
        with pytest.raises((ValueError, TypeError)):
            SpaceConversation(dialogue_lines=[])

    def test_dialogue_requires_speaker_and_text(self):
        """Each dialogue line must have speaker role and text."""
        conversation = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Valid dialogue")
            ]
        )
        # Should not raise
        assert len(conversation.dialogue_lines) == 1
