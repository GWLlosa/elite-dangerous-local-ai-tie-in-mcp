#!/usr/bin/env python3
"""
Compare events found in journal files with events in EVENT_CATEGORIES mapping.
Identify gaps in event coverage.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from journal.events import EventProcessor, EventCategory

# Events found in the last 7 days of journal files (from gap_report_event_type_coverage.md)
EVENTS_IN_JOURNAL = [
    'AfmuRepairs', 'AsteroidCracked', 'Backpack', 'BookTaxi', 'Bounty', 'BuyAmmo',
    'BuyDrones', 'Cargo', 'CargoTransfer', 'CarrierJump', 'CarrierJumpRequest',
    'CarrierLocation', 'CarrierStats', 'CollectCargo', 'Commander', 'CommitCrime',
    'CommunityGoal', 'CommunityGoalJoin', 'CrewAssign', 'CrimeVictim', 'DataScanned',
    'Died', 'DiscoveryScan', 'Disembark', 'DockFighter', 'Docked', 'DockingCancelled',
    'DockingGranted', 'DockingRequested', 'EjectCargo', 'Embark', 'EngineerCraft',
    'EngineerProgress', 'EscapeInterdiction', 'FSDJump', 'FSDTarget', 'FSSAllBodiesFound',
    'FSSDiscoveryScan', 'FSSSignalDiscovered', 'FetchRemoteModule', 'Fileheader',
    'FuelScoop', 'HeatDamage', 'HeatWarning', 'HullDamage', 'Interdicted', 'Interdiction',
    'LaunchDrone', 'LaunchFighter', 'LoadGame', 'Loadout', 'Location', 'Market',
    'MarketSell', 'MaterialCollected', 'MaterialDiscovered', 'Materials', 'MiningRefined',
    'MissionAccepted', 'MissionCompleted', 'MissionRedirected', 'Missions', 'ModuleBuy',
    'ModuleInfo', 'ModuleRetrieve', 'ModuleStore', 'MultiSellExplorationData', 'Music',
    'NavBeaconScan', 'NavRoute', 'NavRouteClear', 'NpcCrewPaidWage', 'Outfitting',
    'Passengers', 'Powerplay', 'Progress', 'ProspectedAsteroid', 'Rank', 'ReceiveText',
    'RedeemVoucher', 'RefuelAll', 'Repair', 'RepairAll', 'Reputation', 'ReservoirReplenished',
    'RestockVehicle', 'Resurrect', 'SAAScanComplete', 'SAASignalsFound', 'Scan',
    'ScanBaryCentre', 'Scanned', 'SetUserShipName', 'ShieldState', 'ShipLocker',
    'ShipRedeemed', 'ShipTargeted', 'Shipyard', 'ShipyardRedeem', 'ShipyardSwap',
    'ShipyardTransfer', 'Shutdown', 'StartJump', 'Statistics', 'StoredModules',
    'StoredShips', 'SuitLoadout', 'SupercruiseDestinationDrop', 'SupercruiseEntry',
    'SupercruiseExit', 'USSDrop', 'UnderAttack', 'Undocked'
]

def main():
    processor = EventProcessor()

    print("=" * 70)
    print("EVENT COVERAGE COMPARISON")
    print("=" * 70)
    print()

    # Get events in EVENT_CATEGORIES
    mapped_events = set(processor.EVENT_CATEGORIES.keys())
    journal_events = set(EVENTS_IN_JOURNAL)

    print(f"Events in journal files: {len(journal_events)}")
    print(f"Events in EVENT_CATEGORIES: {len(mapped_events)}")
    print()

    # Find gaps
    unmapped_events = journal_events - mapped_events
    mapped_but_not_seen = mapped_events - journal_events

    if unmapped_events:
        print("=" * 70)
        print(f"UNMAPPED EVENTS ({len(unmapped_events)})")
        print("=" * 70)
        print("These events appear in journal files but are NOT in EVENT_CATEGORIES:")
        print()
        for event in sorted(unmapped_events):
            print(f"  - {event}")
        print()

        # Create a bug report for this
        gap_reports_dir = Path("gap-reports")
        gap_reports_dir.mkdir(exist_ok=True)
        report_path = gap_reports_dir / "gap_report_unmapped_events.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Bug Report: Unmapped Event Types

## Summary
HIGH **Severity**: HIGH

**Issue Type**: unmapped_event_types

**Date**: 2025-10-04

## Description
{len(unmapped_events)} event types were found in Elite Dangerous journal files but are NOT present in the EVENT_CATEGORIES mapping in src/journal/events.py.

This means these events will be categorized as EventCategory.OTHER instead of their proper category, which can cause issues with:
- Event filtering and querying
- Activity summaries
- Resource endpoints
- Data organization

## Unmapped Events

The following events need to be added to EVENT_CATEGORIES:

""")
            for event in sorted(unmapped_events):
                f.write(f"- `{event}`\n")

            f.write(f"""

## Impact
- Events are not properly categorized
- Activity summaries may be incomplete
- Filtering by category will miss these events

## Recommended Fix
Add these event types to the EVENT_CATEGORIES dictionary in src/journal/events.py with their appropriate categories.

### Suggested Categorization

Based on event naming patterns:

**Navigation/Travel:**
- BookTaxi
- FetchRemoteModule
- SupercruiseDestinationDrop

**Ship/Module:**
- ModuleInfo
- SetUserShipName
- ShipLocker
- ShipRedeemed
- ShipyardRedeem
- StoredModules

**Combat:**
- DataScanned
- HeatDamage
- HeatWarning
- LaunchDrone
- Scanned

**Crew/Social:**
- NpcCrewPaidWage

**On-Foot/Odyssey:**
- Disembark
- Embark
- ReservoirReplenished
- SuitLoadout

**Exploration:**
- NavBeaconScan
- ScanBaryCentre

**Trading/Market:**
- RefuelAll

**Carrier:**
- CarrierLocation

**Powerplay:**
- Powerplay (general event)

**Miscellaneous:**
- Backpack
- CommunityGoal
- CommunityGoalJoin
- CommitCrime
- CrimeVictim
- FSSSignalDiscovered
- RedeemVoucher
- ShipyardTransfer

## Priority
HIGH - These events represent actual gameplay activities that should be properly categorized.

## Next Steps
1. Review each event type
2. Assign appropriate EventCategory
3. Add to EVENT_CATEGORIES mapping
4. Create unit tests to verify categorization
5. Verify activity summaries include these events
""")
        print(f"[+] Created bug report: gap_report_unmapped_events.md")
    else:
        print("[+] All journal events are mapped in EVENT_CATEGORIES!")

    if mapped_but_not_seen:
        print("=" * 70)
        print(f"MAPPED BUT NOT SEEN ({len(mapped_but_not_seen)})")
        print("=" * 70)
        print("These events are in EVENT_CATEGORIES but were NOT seen in recent journal files:")
        print("(This is normal - not all events occur in every play session)")
        print()
        for event in sorted(mapped_but_not_seen):
            category = processor.EVENT_CATEGORIES[event]
            print(f"  - {event} ({category.value})")
        print()

if __name__ == "__main__":
    main()
