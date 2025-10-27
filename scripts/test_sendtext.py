"""
Test script to check if SendText events have the same issue as ReceiveText.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from journal.events import EventProcessor

def test_sendtext_extraction():
    """Test that SendText event message content is extracted."""

    # Sample SendText event from Elite Dangerous journal
    sendtext_event = {
        "timestamp": "2025-07-30T19:33:06Z",
        "event": "SendText",
        "To": "local",
        "Message": "how much do you need in the bank to \"Buy an FC and not super stress over the bills\" these days?",
        "Sent": True
    }

    processor = EventProcessor()

    print("Testing SendText event processing...")
    print("=" * 70)

    processed = processor.process_event(sendtext_event)

    print(f"Event Type: {processed.event_type}")
    print(f"Category: {processed.category.value}")
    print(f"Summary: {processed.summary}")
    print(f"Key Data: {processed.key_data}")
    print(f"Is Valid: {processed.is_valid}")

    print("\n" + "=" * 70)

    # Check if message content is in key_data
    if "message" in processed.key_data:
        print(f"[SUCCESS] Message content found in key_data")
    else:
        print(f"[FAILED] Message content NOT found in key_data")
        print(f"Expected: Message field should contain: {sendtext_event['Message']}")

    # Check if recipient is in key_data
    if "to" in processed.key_data:
        print(f"[SUCCESS] Recipient found in key_data")
    else:
        print(f"[FAILED] Recipient NOT found in key_data")
        print(f"Expected: To field should contain: {sendtext_event['To']}")

    # Check if sent status is in key_data
    if "sent" in processed.key_data:
        print(f"[SUCCESS] Sent status found in key_data")
    else:
        print(f"[INFO] Sent status NOT found in key_data (may not be critical)")

    print("\n" + "=" * 70)
    if not processed.key_data:
        print("CONCLUSION: SendText has the SAME issue as ReceiveText - needs fix")
    else:
        print("CONCLUSION: SendText is working correctly")

if __name__ == "__main__":
    test_sendtext_extraction()
