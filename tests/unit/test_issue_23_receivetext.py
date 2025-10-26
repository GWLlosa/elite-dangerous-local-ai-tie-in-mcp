"""
Unit tests for Issue #23: ReceiveText events tracked but message content not exposed.

GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

Problem: ReceiveText events are being tracked and categorized correctly, but the
         message content, sender, and channel information are not being extracted
         into the key_data dictionary, making them inaccessible via the API.

Expected: key_data should contain:
          - message: The actual message text (Message_Localised or Message)
          - from: Sender information (From_Localised or From)
          - channel: Communication channel (npc, player, local, etc.)

Actual (before fix): key_data is empty ({})
"""

import pytest
from datetime import datetime, timezone
from src.journal.events import EventProcessor, EventCategory


class TestIssue23ReceiveTextEvents:
    """Test suite for ReceiveText event data extraction (Issue #23)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = EventProcessor()

    def test_issue_23_receivetext_npc_channel_message_extraction(self):
        """
        Test for Issue #23: ReceiveText NPC Channel Message Extraction

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

        Problem: NPC channel messages not extracted to key_data
        Expected: Message, sender, and channel should be in key_data
        Actual (before fix): key_data is empty
        """
        event = {
            "timestamp": "2025-10-26T03:38:09Z",
            "event": "ReceiveText",
            "From": "$npc_name_decorate:#name=Malard;",
            "From_Localised": "Malard",
            "Message": "$MinerCriticalDamage02;",
            "Message_Localised": "All I was doing was mining!",
            "Channel": "npc"
        }

        processed = self.processor.process_event(event)

        # Verify event categorization
        assert processed.event_type == "ReceiveText"
        assert processed.category == EventCategory.SOCIAL
        assert processed.is_valid is True

        # Verify key_data extraction
        assert "message" in processed.key_data, "Message should be extracted to key_data"
        assert processed.key_data["message"] == "All I was doing was mining!"

        assert "from" in processed.key_data, "Sender should be extracted to key_data"
        assert processed.key_data["from"] == "Malard"

        assert "channel" in processed.key_data, "Channel should be extracted to key_data"
        assert processed.key_data["channel"] == "npc"

    def test_issue_23_receivetext_player_channel_message_extraction(self):
        """
        Test for Issue #23: ReceiveText Player Channel Message Extraction

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

        Problem: Player channel messages not extracted to key_data
        Expected: Message, sender, and channel should be in key_data
        Actual (before fix): key_data is empty
        """
        event = {
            "timestamp": "2025-07-30T14:52:02Z",
            "event": "ReceiveText",
            "From": "DANISHVIKING3",
            "Message": "scan show you have no warrants o7",
            "Channel": "player"
        }

        processed = self.processor.process_event(event)

        # Verify event categorization
        assert processed.event_type == "ReceiveText"
        assert processed.category == EventCategory.SOCIAL
        assert processed.is_valid is True

        # Verify key_data extraction
        assert "message" in processed.key_data, "Message should be extracted to key_data"
        assert processed.key_data["message"] == "scan show you have no warrants o7"

        assert "from" in processed.key_data, "Sender should be extracted to key_data"
        assert processed.key_data["from"] == "DANISHVIKING3"

        assert "channel" in processed.key_data, "Channel should be extracted to key_data"
        assert processed.key_data["channel"] == "player"

    def test_issue_23_receivetext_captains_log_extraction(self):
        """
        Test for Issue #23: Captain's Log (ReceiveText) Message Extraction

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

        Problem: Captain's Log entries not accessible through API
        Expected: Captain's Log message content should be in key_data
        Actual (before fix): key_data is empty
        """
        event = {
            "timestamp": "2025-10-26T03:38:09Z",
            "event": "ReceiveText",
            "From": "",
            "Message": "Captain's log, stardate 102625.3. We've begun our exploration of the Blae Drye sector.",
            "Message_Localised": "Captain's log, stardate 102625.3. We've begun our exploration of the Blae Drye sector.",
            "Channel": "npc"
        }

        processed = self.processor.process_event(event)

        # Verify event categorization
        assert processed.event_type == "ReceiveText"
        assert processed.category == EventCategory.SOCIAL

        # Verify key_data extraction
        assert "message" in processed.key_data, "Captain's Log message should be extracted"
        assert processed.key_data["message"] == "Captain's log, stardate 102625.3. We've begun our exploration of the Blae Drye sector."

        assert "channel" in processed.key_data
        assert processed.key_data["channel"] == "npc"

        # From field may be empty for Captain's Log
        assert "from" in processed.key_data

    def test_issue_23_receivetext_prefers_localised_message(self):
        """
        Test for Issue #23: ReceiveText Should Prefer Localised Message

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

        Problem: Should use Message_Localised when available (human-readable)
        Expected: Message_Localised takes precedence over Message
        """
        event = {
            "timestamp": "2025-10-26T03:40:00Z",
            "event": "ReceiveText",
            "From": "$npc_name_decorate:#name=Test NPC;",
            "From_Localised": "Test NPC",
            "Message": "$SomeInternalKey;",
            "Message_Localised": "Human readable message",
            "Channel": "npc"
        }

        processed = self.processor.process_event(event)

        # Should prefer Message_Localised over Message
        assert processed.key_data["message"] == "Human readable message"
        assert processed.key_data["from"] == "Test NPC"

    def test_issue_23_receivetext_fallback_to_raw_message(self):
        """
        Test for Issue #23: ReceiveText Falls Back to Raw Message

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

        Problem: Should handle cases where Message_Localised is missing
        Expected: Falls back to Message field if Message_Localised not present
        """
        event = {
            "timestamp": "2025-10-26T03:40:00Z",
            "event": "ReceiveText",
            "From": "PlayerName",
            "Message": "Raw message text",
            "Channel": "local"
        }

        processed = self.processor.process_event(event)

        # Should use Message when Message_Localised is not available
        assert processed.key_data["message"] == "Raw message text"
        assert processed.key_data["from"] == "PlayerName"

    def test_issue_23_receivetext_handles_empty_from_field(self):
        """
        Test for Issue #23: ReceiveText Handles Empty From Field

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

        Problem: Some messages (like channel notifications) have empty From field
        Expected: Should handle empty From field gracefully
        """
        event = {
            "timestamp": "2025-04-12T19:24:44Z",
            "event": "ReceiveText",
            "From": "",
            "Message": "$COMMS_entered:#name=Inti;",
            "Message_Localised": "Entered Channel: Inti",
            "Channel": "npc"
        }

        processed = self.processor.process_event(event)

        # Should extract message even with empty From
        assert processed.key_data["message"] == "Entered Channel: Inti"
        assert processed.key_data["channel"] == "npc"
        assert "from" in processed.key_data  # Should be present, even if empty

    def test_issue_23_receivetext_summary_generation(self):
        """
        Test for Issue #23: ReceiveText Summary Should Be Meaningful

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

        Problem: Generic "ReceiveText event occurred" summary not useful
        Expected: Summary should include sender and/or message preview
        Actual (before fix): "ReceiveText event occurred"
        """
        event = {
            "timestamp": "2025-10-26T03:40:00Z",
            "event": "ReceiveText",
            "From": "TestPlayer",
            "Message": "This is a test message",
            "Channel": "player"
        }

        processed = self.processor.process_event(event)

        # Summary should be more meaningful than generic message
        assert processed.summary != "ReceiveText event occurred"
        assert "TestPlayer" in processed.summary or "test message" in processed.summary.lower()

    def test_issue_23_receivetext_different_channels(self):
        """
        Test for Issue #23: ReceiveText Supports Different Channel Types

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/23

        Problem: All channel types should be extracted to key_data
        Expected: npc, player, local, system, etc. channels all supported
        """
        channels = ["npc", "player", "local", "system", "squadron", "wing"]

        for channel in channels:
            event = {
                "timestamp": "2025-10-26T03:40:00Z",
                "event": "ReceiveText",
                "From": "Sender",
                "Message": f"Message on {channel} channel",
                "Channel": channel
            }

            processed = self.processor.process_event(event)

            assert processed.key_data["channel"] == channel, f"Channel {channel} should be extracted"
            assert processed.key_data["message"] == f"Message on {channel} channel"
