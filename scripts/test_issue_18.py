"""
Investigation script for Issue #18: CarrierStats and CarrierFinance Events Return Empty key_data

This script tests whether carrier events are properly extracting data into key_data fields.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from journal.events import EventProcessor
from datetime import datetime, timezone


def test_carrier_stats_event():
    """Test CarrierStats event processing"""
    print("\n=== Testing CarrierStats Event ===")

    # Sample CarrierStats event (based on Elite Dangerous Journal Manual)
    carrier_stats_event = {
        "timestamp": "2025-10-09T04:01:48Z",
        "event": "CarrierStats",
        "CarrierID": 3700005632,
        "Callsign": "K1F-37B",
        "Name": "Example Carrier",
        "DockingAccess": "all",
        "AllowNotorious": False,
        "FuelLevel": 800,
        "JumpRangeCurr": 500.00,
        "JumpRangeMax": 500.00,
        "Finance": {
            "CarrierBalance": 1500000000,
            "ReserveBalance": 100000000,
            "AvailableBalance": 1400000000,
            "ReservePercent": 0,
            "TaxRate_rearm": 0,
            "TaxRate_refuel": 0,
            "TaxRate_repair": 0
        },
        "Crew": [
            {
                "CrewRole": "BlackMarket",
                "Activated": True,
                "Enabled": True,
                "CrewName": "Test Fence"
            }
        ],
        "ShipPacks": [
            {
                "PackTheme": "ExplorationPack",
                "PackTier": 1
            }
        ],
        "ModulePacks": [
            {
                "PackTheme": "MiningUtilities",
                "PackTier": 1
            }
        ]
    }

    processor = EventProcessor()
    processed = processor.process_event(carrier_stats_event)

    print(f"Event Type: {processed.event_type}")
    print(f"Category: {processed.category.value}")
    print(f"Summary: {processed.summary}")
    print(f"key_data: {processed.key_data}")
    print(f"Is Valid: {processed.is_valid}")

    # Check if key_data is empty (the bug)
    if not processed.key_data:
        print("[FAILED] key_data is EMPTY - BUG REPRODUCED!")
        return False
    else:
        print("[SUCCESS] key_data contains data")
        return True


def test_carrier_finance_event():
    """Test CarrierFinance event processing"""
    print("\n=== Testing CarrierFinance Event ===")

    # Sample CarrierFinance event
    carrier_finance_event = {
        "timestamp": "2025-10-09T04:00:55Z",
        "event": "CarrierFinance",
        "CarrierID": 3700005632,
        "TaxRate_pioneersupplies": 0,
        "TaxRate_shipyard": 0,
        "TaxRate_rearm": 0,
        "TaxRate_outfitting": 0,
        "TaxRate_refuel": 0,
        "TaxRate_repair": 0,
        "CarrierBalance": 1500000000,
        "ReserveBalance": 100000000,
        "AvailableBalance": 1400000000,
        "ReservePercent": 0
    }

    processor = EventProcessor()
    processed = processor.process_event(carrier_finance_event)

    print(f"Event Type: {processed.event_type}")
    print(f"Category: {processed.category.value}")
    print(f"Summary: {processed.summary}")
    print(f"key_data: {processed.key_data}")
    print(f"Is Valid: {processed.is_valid}")

    # Check if key_data is empty (the bug)
    if not processed.key_data:
        print("[FAILED] key_data is EMPTY - BUG REPRODUCED!")
        return False
    else:
        print("[SUCCESS] key_data contains data")
        return True


def test_carrier_crew_services_event():
    """Test CarrierCrewServices event processing"""
    print("\n=== Testing CarrierCrewServices Event ===")

    # Sample CarrierCrewServices event
    carrier_crew_event = {
        "timestamp": "2025-10-09T04:02:15Z",
        "event": "CarrierCrewServices",
        "CarrierID": 3700005632,
        "CrewName": "Bartender",
        "Operation": "ActivateCrew"
    }

    processor = EventProcessor()
    processed = processor.process_event(carrier_crew_event)

    print(f"Event Type: {processed.event_type}")
    print(f"Category: {processed.category.value}")
    print(f"Summary: {processed.summary}")
    print(f"key_data: {processed.key_data}")
    print(f"Is Valid: {processed.is_valid}")

    # Check if key_data is empty (the bug)
    if not processed.key_data:
        print("[FAILED] key_data is EMPTY - BUG REPRODUCED!")
        return False
    else:
        print("[SUCCESS] key_data contains data")
        return True


def test_carrier_module_pack_event():
    """Test CarrierModulePack event processing"""
    print("\n=== Testing CarrierModulePack Event ===")

    # Sample CarrierModulePack event
    carrier_module_event = {
        "timestamp": "2025-10-09T04:03:20Z",
        "event": "CarrierModulePack",
        "CarrierID": 3700005632,
        "Operation": "buypack",
        "PackTheme": "MiningUtilities",
        "PackTier": 1,
        "Cost": 500000
    }

    processor = EventProcessor()
    processed = processor.process_event(carrier_module_event)

    print(f"Event Type: {processed.event_type}")
    print(f"Category: {processed.category.value}")
    print(f"Summary: {processed.summary}")
    print(f"key_data: {processed.key_data}")
    print(f"Is Valid: {processed.is_valid}")

    # Check if key_data is empty (the bug)
    if not processed.key_data:
        print("[FAILED] key_data is EMPTY - BUG REPRODUCED!")
        return False
    else:
        print("[SUCCESS] key_data contains data")
        return True


def test_current_coordinates_issue():
    """Test the current_coordinates AttributeError"""
    print("\n=== Testing current_coordinates AttributeError ===")

    try:
        from utils.data_store import GameState

        game_state = GameState()
        game_state.coordinates = {"x": 100.0, "y": 200.0, "z": 300.0}

        # Try to access current_coordinates (should fail)
        try:
            coords = game_state.current_coordinates
            print(f"[UNEXPECTED] current_coordinates exists: {coords}")
            return False
        except AttributeError as e:
            print(f"[SUCCESS] AttributeError reproduced: {e}")
            print(f"[INFO] GameState has 'coordinates', not 'current_coordinates'")
            return True

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Issue #18 Investigation Script")
    print("Testing CarrierStats, CarrierFinance, and related events")
    print("=" * 60)

    results = {
        "CarrierStats": test_carrier_stats_event(),
        "CarrierFinance": test_carrier_finance_event(),
        "CarrierCrewServices": test_carrier_crew_services_event(),
        "CarrierModulePack": test_carrier_module_pack_event(),
        "current_coordinates": test_current_coordinates_issue()
    }

    print("\n" + "=" * 60)
    print("INVESTIGATION SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    all_bugs_reproduced = not all(results.values())

    if all_bugs_reproduced:
        print("\n[RESULT] Issue #18 has been SUCCESSFULLY REPRODUCED")
        print("Root causes identified:")
        print("1. _extract_key_data() missing handlers for carrier events")
        print("2. GameState.coordinates accessed as current_coordinates in mcp_resources.py")
    else:
        print("\n[RESULT] Issue #18 could NOT be reproduced")

    return 0 if all_bugs_reproduced else 1


if __name__ == "__main__":
    sys.exit(main())
