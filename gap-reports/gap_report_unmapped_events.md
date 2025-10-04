# Bug Report: Unmapped Event Types

## Summary
HIGH **Severity**: HIGH

**Issue Type**: unmapped_event_types

**Date**: 2025-10-04

## Description
34 event types were found in Elite Dangerous journal files but are NOT present in the EVENT_CATEGORIES mapping in src/journal/events.py.

This means these events will be categorized as EventCategory.OTHER instead of their proper category, which can cause issues with:
- Event filtering and querying
- Activity summaries
- Resource endpoints
- Data organization

## Unmapped Events

The following events need to be added to EVENT_CATEGORIES:

- `Backpack`
- `BookTaxi`
- `BuyDrones`
- `CargoTransfer`
- `CarrierLocation`
- `CommitCrime`
- `CommunityGoal`
- `CommunityGoalJoin`
- `CrimeVictim`
- `DataScanned`
- `FSDTarget`
- `FSSSignalDiscovered`
- `FetchRemoteModule`
- `FuelScoop`
- `HeatDamage`
- `HeatWarning`
- `LaunchDrone`
- `Materials`
- `ModuleInfo`
- `NavBeaconScan`
- `NpcCrewPaidWage`
- `Powerplay`
- `RedeemVoucher`
- `RefuelAll`
- `ReservoirReplenished`
- `ScanBaryCentre`
- `Scanned`
- `SetUserShipName`
- `ShipLocker`
- `ShipRedeemed`
- `ShipyardRedeem`
- `StoredModules`
- `SupercruiseDestinationDrop`
- `USSDrop`


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
