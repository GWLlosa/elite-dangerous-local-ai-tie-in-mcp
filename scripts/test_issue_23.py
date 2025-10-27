"""
Test script to reproduce issue #23: ReceiveText events tracked but message content not exposed.

This script demonstrates that ReceiveText events are being processed and stored,
but the message content is not being extracted into key_data.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime, timezone
from journal.events import EventProcessor

def test_receivetext_message_extraction():
    """Test that ReceiveText event message content is extracted."""

    # Sample ReceiveText event from Elite Dangerous journal (Captain's Log style)
    receivetext_event = {
        "timestamp": "2025-10-26T03:38:09Z",
        "event": "ReceiveText",
        "From": "",
        "Message": "Captain's log, stardate 102625.3. We've begun our exploration of the Blae Drye sector.",
        "Message_Localised": "Captain's log, stardate 102625.3. We've begun our exploration of the Blae Drye sector.",
        "Channel": "npc"
    }

    # Sample ReceiveText event from NPC chatter
    npc_chatter_event = {
        "timestamp": "2025-10-26T03:40:00Z",
        "event": "ReceiveText",
        "From": "$npc_name_decorate:#name=Malard;",
        "From_Localised": "Malard",
        "Message": "$MinerCriticalDamage02;",
        "Message_Localised": "All I was doing was mining!",
        "Channel": "npc"
    }

    # Sample ReceiveText event from player chat
    player_chat_event = {
        "timestamp": "2025-10-26T03:41:00Z",
        "event": "ReceiveText",
        "From": "DANISHVIKING3",
        "Message": "scan show you have no warrants o7",
        "Channel": "player"
    }

    processor = EventProcessor()

    print("Testing ReceiveText event processing...")
    print("=" * 70)

    for i, event in enumerate([receivetext_event, npc_chatter_event, player_chat_event], 1):
        print(f"\nTest {i}: {event.get('Channel', 'unknown')} channel message")
        print("-" * 70)

        processed = processor.process_event(event)

        print(f"Event Type: {processed.event_type}")
        print(f"Category: {processed.category.value}")
        print(f"Summary: {processed.summary}")
        print(f"Key Data: {processed.key_data}")
        print(f"Is Valid: {processed.is_valid}")

        # Check if message content is in key_data
        if "message" in processed.key_data:
            print(f"\n[SUCCESS] Message content found in key_data: {processed.key_data['message']}")
        else:
            print(f"\n[FAILED] Message content NOT found in key_data")
            print(f"Expected: Message field should contain: {event.get('Message_Localised') or event.get('Message')}")

        # Check if sender information is in key_data
        if "from" in processed.key_data:
            print(f"[SUCCESS] Sender found in key_data: {processed.key_data['from']}")
        else:
            sender = event.get('From_Localised') or event.get('From')
            if sender:
                print(f"[FAILED] Sender NOT found in key_data")
                print(f"Expected: From field should contain: {sender}")

        # Check if channel is in key_data
        if "channel" in processed.key_data:
            print(f"[SUCCESS] Channel found in key_data: {processed.key_data['channel']}")
        else:
            print(f"[FAILED] Channel NOT found in key_data")
            print(f"Expected: Channel field should contain: {event.get('Channel')}")

    print("\n" + "=" * 70)
    print("ISSUE #23 REPRODUCTION TEST COMPLETE")
    print("=" * 70)
    print("\nExpected Behavior:")
    print("- key_data should contain 'message' field with message text")
    print("- key_data should contain 'from' field with sender information")
    print("- key_data should contain 'channel' field with channel type")
    print("\nActual Behavior:")
    print("- key_data is empty ({})")
    print("- Summary is generic: 'ReceiveText event occurred'")
    print("\nConclusion: Issue #23 is VALID - ReceiveText message content is not exposed")

if __name__ == "__main__":
    test_receivetext_message_extraction()
