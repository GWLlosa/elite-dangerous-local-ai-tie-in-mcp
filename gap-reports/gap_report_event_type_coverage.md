# Gap Report: Event Type Coverage Analysis

## Summary
🔴 **Severity**: HIGH

**Issue Type**: event_coverage_analysis

**Date**: 2025-10-04T14:29:55.943043

## Description
Comprehensive analysis of all event types present in Elite Dangerous journal files over the last 7 days.

## Statistics
- **Files Analyzed**: 17
- **Total Events**: 14,372
- **Unique Event Types**: 113

## All Event Types Found
The following 113 event types were found in the journal files:

- `AfmuRepairs`
- `AsteroidCracked`
- `Backpack`
- `BookTaxi`
- `Bounty`
- `BuyAmmo`
- `BuyDrones`
- `Cargo`
- `CargoTransfer`
- `CarrierJump`
- `CarrierJumpRequest`
- `CarrierLocation`
- `CarrierStats`
- `CollectCargo`
- `Commander`
- `CommitCrime`
- `CommunityGoal`
- `CommunityGoalJoin`
- `CrewAssign`
- `CrimeVictim`
- `DataScanned`
- `Died`
- `DiscoveryScan`
- `Disembark`
- `DockFighter`
- `Docked`
- `DockingCancelled`
- `DockingGranted`
- `DockingRequested`
- `EjectCargo`
- `Embark`
- `EngineerCraft`
- `EngineerProgress`
- `EscapeInterdiction`
- `FSDJump`
- `FSDTarget`
- `FSSAllBodiesFound`
- `FSSDiscoveryScan`
- `FSSSignalDiscovered`
- `FetchRemoteModule`
- `Fileheader`
- `FuelScoop`
- `HeatDamage`
- `HeatWarning`
- `HullDamage`
- `Interdicted`
- `Interdiction`
- `LaunchDrone`
- `LaunchFighter`
- `LoadGame`
- `Loadout`
- `Location`
- `Market`
- `MarketSell`
- `MaterialCollected`
- `MaterialDiscovered`
- `Materials`
- `MiningRefined`
- `MissionAccepted`
- `MissionCompleted`
- `MissionRedirected`
- `Missions`
- `ModuleBuy`
- `ModuleInfo`
- `ModuleRetrieve`
- `ModuleStore`
- `MultiSellExplorationData`
- `Music`
- `NavBeaconScan`
- `NavRoute`
- `NavRouteClear`
- `NpcCrewPaidWage`
- `Outfitting`
- `Passengers`
- `Powerplay`
- `Progress`
- `ProspectedAsteroid`
- `Rank`
- `ReceiveText`
- `RedeemVoucher`
- `RefuelAll`
- `Repair`
- `RepairAll`
- `Reputation`
- `ReservoirReplenished`
- `RestockVehicle`
- `Resurrect`
- `SAAScanComplete`
- `SAASignalsFound`
- `Scan`
- `ScanBaryCentre`
- `Scanned`
- `SetUserShipName`
- `ShieldState`
- `ShipLocker`
- `ShipRedeemed`
- `ShipTargeted`
- `Shipyard`
- `ShipyardRedeem`
- `ShipyardSwap`
- `ShipyardTransfer`
- `Shutdown`
- `StartJump`
- `Statistics`
- `StoredModules`
- `StoredShips`
- `SuitLoadout`
- `SupercruiseDestinationDrop`
- `SupercruiseEntry`
- `SupercruiseExit`
- `USSDrop`
- `UnderAttack`
- `Undocked`

## Event Fields Analysis

This section documents all fields found for each event type. This can be used to verify
that the MCP is capturing all available data from each event.


### AfmuRepairs
**Fields** (6): `FullyRepaired`, `Health`, `Module`, `Module_Localised`, `event`, `timestamp`


### AsteroidCracked
**Fields** (3): `Body`, `event`, `timestamp`


### Backpack
**Fields** (6): `Components`, `Consumables`, `Data`, `Items`, `event`, `timestamp`


### BookTaxi
**Fields** (5): `Cost`, `DestinationLocation`, `DestinationSystem`, `event`, `timestamp`


### Bounty
**Fields** (9): `PilotName`, `PilotName_Localised`, `Rewards`, `Target`, `Target_Localised`, `TotalReward`, `VictimFaction`, `event`, `timestamp`


### BuyAmmo
**Fields** (3): `Cost`, `event`, `timestamp`


### BuyDrones
**Fields** (6): `BuyPrice`, `Count`, `TotalCost`, `Type`, `event`, `timestamp`


### Cargo
**Fields** (5): `Count`, `Inventory`, `Vessel`, `event`, `timestamp`


### CargoTransfer
**Fields** (3): `Transfers`, `event`, `timestamp`


### CarrierJump
**Fields** (28): `Body`, `BodyID`, `BodyType`, `ControllingPower`, `Docked`, `Factions`, `OnFoot`, `Population`, `PowerplayState`, `PowerplayStateControlProgress`, `PowerplayStateReinforcement`, `PowerplayStateUndermining`, `Powers`, `StarPos`, `StarSystem`, `SystemAddress`, `SystemAllegiance`, `SystemEconomy`, `SystemEconomy_Localised`, `SystemFaction`, `SystemGovernment`, `SystemGovernment_Localised`, `SystemSecondEconomy`, `SystemSecondEconomy_Localised`, `SystemSecurity`, `SystemSecurity_Localised`, `event`, `timestamp`


### CarrierJumpRequest
**Fields** (9): `Body`, `BodyID`, `CarrierID`, `CarrierType`, `DepartureTime`, `SystemAddress`, `SystemName`, `event`, `timestamp`


### CarrierLocation
**Fields** (7): `BodyID`, `CarrierID`, `CarrierType`, `StarSystem`, `SystemAddress`, `event`, `timestamp`


### CarrierStats
**Fields** (17): `AllowNotorious`, `Callsign`, `CarrierID`, `CarrierType`, `Crew`, `DockingAccess`, `Finance`, `FuelLevel`, `JumpRangeCurr`, `JumpRangeMax`, `ModulePacks`, `Name`, `PendingDecommission`, `ShipPacks`, `SpaceUsage`, `event`, `timestamp`


### CollectCargo
**Fields** (5): `Stolen`, `Type`, `Type_Localised`, `event`, `timestamp`


### Commander
**Fields** (4): `FID`, `Name`, `event`, `timestamp`


### CommitCrime
**Fields** (7): `Bounty`, `CrimeType`, `Faction`, `Victim`, `Victim_Localised`, `event`, `timestamp`


### CommunityGoal
**Fields** (3): `CurrentGoals`, `event`, `timestamp`


### CommunityGoalJoin
**Fields** (5): `CGID`, `Name`, `System`, `event`, `timestamp`


### CrewAssign
**Fields** (5): `CrewID`, `Name`, `Role`, `event`, `timestamp`


### CrimeVictim
**Fields** (5): `Bounty`, `CrimeType`, `Offender`, `event`, `timestamp`


### DataScanned
**Fields** (4): `Type`, `Type_Localised`, `event`, `timestamp`


### Died
**Fields** (4): `KillerName`, `KillerShip`, `event`, `timestamp`


### DiscoveryScan
**Fields** (4): `Bodies`, `SystemAddress`, `event`, `timestamp`


### Disembark
**Fields** (15): `Body`, `BodyID`, `ID`, `MarketID`, `Multicrew`, `OnPlanet`, `OnStation`, `SRV`, `StarSystem`, `StationName`, `StationType`, `SystemAddress`, `Taxi`, `event`, `timestamp`


### DockFighter
**Fields** (3): `ID`, `event`, `timestamp`


### Docked
**Fields** (19): `DistFromStarLS`, `LandingPads`, `MarketID`, `Multicrew`, `StarSystem`, `StationAllegiance`, `StationEconomies`, `StationEconomy`, `StationEconomy_Localised`, `StationFaction`, `StationGovernment`, `StationGovernment_Localised`, `StationName`, `StationServices`, `StationType`, `SystemAddress`, `Taxi`, `event`, `timestamp`


### DockingCancelled
**Fields** (5): `MarketID`, `StationName`, `StationType`, `event`, `timestamp`


### DockingGranted
**Fields** (6): `LandingPad`, `MarketID`, `StationName`, `StationType`, `event`, `timestamp`


### DockingRequested
**Fields** (6): `LandingPads`, `MarketID`, `StationName`, `StationType`, `event`, `timestamp`


### EjectCargo
**Fields** (6): `Abandoned`, `Count`, `Type`, `Type_Localised`, `event`, `timestamp`


### Embark
**Fields** (15): `Body`, `BodyID`, `ID`, `MarketID`, `Multicrew`, `OnPlanet`, `OnStation`, `SRV`, `StarSystem`, `StationName`, `StationType`, `SystemAddress`, `Taxi`, `event`, `timestamp`


### EngineerCraft
**Fields** (12): `BlueprintID`, `BlueprintName`, `Engineer`, `EngineerID`, `Ingredients`, `Level`, `Modifiers`, `Module`, `Quality`, `Slot`, `event`, `timestamp`


### EngineerProgress
**Fields** (3): `Engineers`, `event`, `timestamp`


### EscapeInterdiction
**Fields** (4): `Interdictor`, `IsPlayer`, `event`, `timestamp`


### FSDJump
**Fields** (34): `Body`, `BodyID`, `BodyType`, `Conflicts`, `ControllingPower`, `Factions`, `FuelLevel`, `FuelUsed`, `JumpDist`, `Multicrew`, `Population`, `PowerplayConflictProgress`, `PowerplayState`, `PowerplayStateControlProgress`, `PowerplayStateReinforcement`, `PowerplayStateUndermining`, `Powers`, `StarPos`, `StarSystem`, `SystemAddress`, `SystemAllegiance`, `SystemEconomy`, `SystemEconomy_Localised`, `SystemFaction`, `SystemGovernment`, `SystemGovernment_Localised`, `SystemSecondEconomy`, `SystemSecondEconomy_Localised`, `SystemSecurity`, `SystemSecurity_Localised`, `Taxi`, `ThargoidWar`, `event`, `timestamp`


### FSDTarget
**Fields** (6): `Name`, `RemainingJumpsInRoute`, `StarClass`, `SystemAddress`, `event`, `timestamp`


### FSSAllBodiesFound
**Fields** (5): `Count`, `SystemAddress`, `SystemName`, `event`, `timestamp`


### FSSDiscoveryScan
**Fields** (7): `BodyCount`, `NonBodyCount`, `Progress`, `SystemAddress`, `SystemName`, `event`, `timestamp`


### FSSSignalDiscovered
**Fields** (7): `IsStation`, `SignalName`, `SignalName_Localised`, `SignalType`, `SystemAddress`, `event`, `timestamp`


### FetchRemoteModule
**Fields** (10): `ServerId`, `Ship`, `ShipID`, `StorageSlot`, `StoredItem`, `StoredItem_Localised`, `TransferCost`, `TransferTime`, `event`, `timestamp`


### Fileheader
**Fields** (7): `Odyssey`, `build`, `event`, `gameversion`, `language`, `part`, `timestamp`


### FuelScoop
**Fields** (4): `Scooped`, `Total`, `event`, `timestamp`


### HeatDamage
**Fields** (2): `event`, `timestamp`


### HeatWarning
**Fields** (2): `event`, `timestamp`


### HullDamage
**Fields** (5): `Fighter`, `Health`, `PlayerPilot`, `event`, `timestamp`


### Interdicted
**Fields** (6): `Faction`, `Interdictor`, `IsPlayer`, `Submitted`, `event`, `timestamp`


### Interdiction
**Fields** (6): `Faction`, `IsPlayer`, `Power`, `Success`, `event`, `timestamp`


### LaunchDrone
**Fields** (3): `Type`, `event`, `timestamp`


### LaunchFighter
**Fields** (5): `ID`, `Loadout`, `PlayerControlled`, `event`, `timestamp`


### LoadGame
**Fields** (20): `Commander`, `Credits`, `FID`, `FuelCapacity`, `FuelLevel`, `GameMode`, `Horizons`, `Loan`, `Odyssey`, `Ship`, `ShipID`, `ShipIdent`, `ShipName`, `Ship_Localised`, `StartDead`, `build`, `event`, `gameversion`, `language`, `timestamp`


### Loadout
**Fields** (15): `CargoCapacity`, `FuelCapacity`, `HullHealth`, `HullValue`, `MaxJumpRange`, `Modules`, `ModulesValue`, `Rebuy`, `Ship`, `ShipID`, `ShipIdent`, `ShipName`, `UnladenMass`, `event`, `timestamp`


### Location
**Fields** (45): `Body`, `BodyID`, `BodyType`, `Conflicts`, `ControllingPower`, `DistFromStarLS`, `Docked`, `Factions`, `MarketID`, `Multicrew`, `OnFoot`, `Population`, `PowerplayConflictProgress`, `PowerplayState`, `PowerplayStateControlProgress`, `PowerplayStateReinforcement`, `PowerplayStateUndermining`, `Powers`, `StarPos`, `StarSystem`, `StationAllegiance`, `StationEconomies`, `StationEconomy`, `StationEconomy_Localised`, `StationFaction`, `StationGovernment`, `StationGovernment_Localised`, `StationName`, `StationServices`, `StationType`, `SystemAddress`, `SystemAllegiance`, `SystemEconomy`, `SystemEconomy_Localised`, `SystemFaction`, `SystemGovernment`, `SystemGovernment_Localised`, `SystemSecondEconomy`, `SystemSecondEconomy_Localised`, `SystemSecurity`, `SystemSecurity_Localised`, `Taxi`, `ThargoidWar`, `event`, `timestamp`


### Market
**Fields** (6): `MarketID`, `StarSystem`, `StationName`, `StationType`, `event`, `timestamp`


### MarketSell
**Fields** (9): `AvgPricePaid`, `Count`, `MarketID`, `SellPrice`, `TotalSale`, `Type`, `Type_Localised`, `event`, `timestamp`


### MaterialCollected
**Fields** (6): `Category`, `Count`, `Name`, `Name_Localised`, `event`, `timestamp`


### MaterialDiscovered
**Fields** (5): `Category`, `DiscoveryNumber`, `Name`, `event`, `timestamp`


### Materials
**Fields** (5): `Encoded`, `Manufactured`, `Raw`, `event`, `timestamp`


### MiningRefined
**Fields** (4): `Type`, `Type_Localised`, `event`, `timestamp`


### MissionAccepted
**Fields** (25): `Commodity`, `Commodity_Localised`, `Count`, `DestinationStation`, `DestinationSystem`, `Expiry`, `Faction`, `Influence`, `KillCount`, `LocalisedName`, `MissionID`, `Name`, `PassengerCount`, `PassengerType`, `PassengerVIPs`, `PassengerWanted`, `Reputation`, `Reward`, `Target`, `TargetFaction`, `TargetType`, `TargetType_Localised`, `Wing`, `event`, `timestamp`


### MissionCompleted
**Fields** (19): `Commodity`, `Commodity_Localised`, `Count`, `DestinationStation`, `DestinationSystem`, `Faction`, `FactionEffects`, `KillCount`, `LocalisedName`, `MaterialsReward`, `MissionID`, `Name`, `Reward`, `Target`, `TargetFaction`, `TargetType`, `TargetType_Localised`, `event`, `timestamp`


### MissionRedirected
**Fields** (9): `LocalisedName`, `MissionID`, `Name`, `NewDestinationStation`, `NewDestinationSystem`, `OldDestinationStation`, `OldDestinationSystem`, `event`, `timestamp`


### Missions
**Fields** (5): `Active`, `Complete`, `Failed`, `event`, `timestamp`


### ModuleBuy
**Fields** (14): `BuyItem`, `BuyItem_Localised`, `BuyPrice`, `MarketID`, `SellItem`, `SellItem_Localised`, `SellPrice`, `Ship`, `ShipID`, `Slot`, `StoredItem`, `StoredItem_Localised`, `event`, `timestamp`


### ModuleInfo
**Fields** (2): `event`, `timestamp`


### ModuleRetrieve
**Fields** (11): `Hot`, `MarketID`, `RetrievedItem`, `RetrievedItem_Localised`, `Ship`, `ShipID`, `Slot`, `SwapOutItem`, `SwapOutItem_Localised`, `event`, `timestamp`


### ModuleStore
**Fields** (9): `Hot`, `MarketID`, `Ship`, `ShipID`, `Slot`, `StoredItem`, `StoredItem_Localised`, `event`, `timestamp`


### MultiSellExplorationData
**Fields** (6): `BaseValue`, `Bonus`, `Discovered`, `TotalEarnings`, `event`, `timestamp`


### Music
**Fields** (3): `MusicTrack`, `event`, `timestamp`


### NavBeaconScan
**Fields** (4): `NumBodies`, `SystemAddress`, `event`, `timestamp`


### NavRoute
**Fields** (2): `event`, `timestamp`


### NavRouteClear
**Fields** (2): `event`, `timestamp`


### NpcCrewPaidWage
**Fields** (5): `Amount`, `NpcCrewId`, `NpcCrewName`, `event`, `timestamp`


### Outfitting
**Fields** (5): `MarketID`, `StarSystem`, `StationName`, `event`, `timestamp`


### Passengers
**Fields** (3): `Manifest`, `event`, `timestamp`


### Powerplay
**Fields** (6): `Merits`, `Power`, `Rank`, `TimePledged`, `event`, `timestamp`


### Progress
**Fields** (10): `CQC`, `Combat`, `Empire`, `Exobiologist`, `Explore`, `Federation`, `Soldier`, `Trade`, `event`, `timestamp`


### ProspectedAsteroid
**Fields** (7): `Content`, `Content_Localised`, `Materials`, `MotherlodeMaterial`, `Remaining`, `event`, `timestamp`


### Rank
**Fields** (10): `CQC`, `Combat`, `Empire`, `Exobiologist`, `Explore`, `Federation`, `Soldier`, `Trade`, `event`, `timestamp`


### ReceiveText
**Fields** (7): `Channel`, `From`, `From_Localised`, `Message`, `Message_Localised`, `event`, `timestamp`


### RedeemVoucher
**Fields** (5): `Amount`, `Factions`, `Type`, `event`, `timestamp`


### RefuelAll
**Fields** (4): `Amount`, `Cost`, `event`, `timestamp`


### Repair
**Fields** (4): `Cost`, `Items`, `event`, `timestamp`


### RepairAll
**Fields** (3): `Cost`, `event`, `timestamp`


### Reputation
**Fields** (6): `Alliance`, `Empire`, `Federation`, `Independent`, `event`, `timestamp`


### ReservoirReplenished
**Fields** (4): `FuelMain`, `FuelReservoir`, `event`, `timestamp`


### RestockVehicle
**Fields** (8): `Cost`, `Count`, `ID`, `Loadout`, `Type`, `Type_Localised`, `event`, `timestamp`


### Resurrect
**Fields** (5): `Bankrupt`, `Cost`, `Option`, `event`, `timestamp`


### SAAScanComplete
**Fields** (7): `BodyID`, `BodyName`, `EfficiencyTarget`, `ProbesUsed`, `SystemAddress`, `event`, `timestamp`


### SAASignalsFound
**Fields** (7): `BodyID`, `BodyName`, `Genuses`, `Signals`, `SystemAddress`, `event`, `timestamp`


### Scan
**Fields** (44): `AbsoluteMagnitude`, `Age_MY`, `AscendingNode`, `Atmosphere`, `AtmosphereComposition`, `AtmosphereType`, `AxialTilt`, `BodyID`, `BodyName`, `Composition`, `DistanceFromArrivalLS`, `Eccentricity`, `Landable`, `Luminosity`, `MassEM`, `Materials`, `MeanAnomaly`, `OrbitalInclination`, `OrbitalPeriod`, `Parents`, `Periapsis`, `PlanetClass`, `Radius`, `ReserveLevel`, `Rings`, `RotationPeriod`, `ScanType`, `SemiMajorAxis`, `StarSystem`, `StarType`, `StellarMass`, `Subclass`, `SurfaceGravity`, `SurfacePressure`, `SurfaceTemperature`, `SystemAddress`, `TerraformState`, `TidalLock`, `Volcanism`, `WasDiscovered`, `WasFootfalled`, `WasMapped`, `event`, `timestamp`


### ScanBaryCentre
**Fields** (12): `AscendingNode`, `BodyID`, `Eccentricity`, `MeanAnomaly`, `OrbitalInclination`, `OrbitalPeriod`, `Periapsis`, `SemiMajorAxis`, `StarSystem`, `SystemAddress`, `event`, `timestamp`


### Scanned
**Fields** (3): `ScanType`, `event`, `timestamp`


### SetUserShipName
**Fields** (6): `Ship`, `ShipID`, `UserShipId`, `UserShipName`, `event`, `timestamp`


### ShieldState
**Fields** (3): `ShieldsUp`, `event`, `timestamp`


### ShipLocker
**Fields** (6): `Components`, `Consumables`, `Data`, `Items`, `event`, `timestamp`


### ShipRedeemed
**Fields** (5): `NewShipID`, `ShipType`, `ShipType_Localised`, `event`, `timestamp`


### ShipTargeted
**Fields** (15): `Bounty`, `Faction`, `HullHealth`, `LegalStatus`, `PilotName`, `PilotName_Localised`, `PilotRank`, `Power`, `ScanStage`, `ShieldHealth`, `Ship`, `Ship_Localised`, `TargetLocked`, `event`, `timestamp`


### Shipyard
**Fields** (5): `MarketID`, `StarSystem`, `StationName`, `event`, `timestamp`


### ShipyardRedeem
**Fields** (6): `BundleID`, `MarketID`, `ShipType`, `ShipType_Localised`, `event`, `timestamp`


### ShipyardSwap
**Fields** (8): `MarketID`, `ShipID`, `ShipType`, `ShipType_Localised`, `StoreOldShip`, `StoreShipID`, `event`, `timestamp`


### ShipyardTransfer
**Fields** (11): `Distance`, `MarketID`, `ShipID`, `ShipMarketID`, `ShipType`, `ShipType_Localised`, `System`, `TransferPrice`, `TransferTime`, `event`, `timestamp`


### Shutdown
**Fields** (2): `event`, `timestamp`


### StartJump
**Fields** (7): `JumpType`, `StarClass`, `StarSystem`, `SystemAddress`, `Taxi`, `event`, `timestamp`


### Statistics
**Fields** (19): `Bank_Account`, `CQC`, `Combat`, `Crafting`, `Crew`, `Crime`, `Exobiology`, `Exploration`, `FLEETCARRIER`, `Material_Trader_Stats`, `Mining`, `Multicrew`, `Passengers`, `Search_And_Rescue`, `Smuggling`, `Squadron`, `Trading`, `event`, `timestamp`


### StoredModules
**Fields** (6): `Items`, `MarketID`, `StarSystem`, `StationName`, `event`, `timestamp`


### StoredShips
**Fields** (7): `MarketID`, `ShipsHere`, `ShipsRemote`, `StarSystem`, `StationName`, `event`, `timestamp`


### SuitLoadout
**Fields** (9): `LoadoutID`, `LoadoutName`, `Modules`, `SuitID`, `SuitMods`, `SuitName`, `SuitName_Localised`, `event`, `timestamp`


### SupercruiseDestinationDrop
**Fields** (6): `MarketID`, `Threat`, `Type`, `Type_Localised`, `event`, `timestamp`


### SupercruiseEntry
**Fields** (6): `Multicrew`, `StarSystem`, `SystemAddress`, `Taxi`, `event`, `timestamp`


### SupercruiseExit
**Fields** (9): `Body`, `BodyID`, `BodyType`, `Multicrew`, `StarSystem`, `SystemAddress`, `Taxi`, `event`, `timestamp`


### USSDrop
**Fields** (5): `USSThreat`, `USSType`, `USSType_Localised`, `event`, `timestamp`


### UnderAttack
**Fields** (3): `Target`, `event`, `timestamp`


### Undocked
**Fields** (7): `MarketID`, `Multicrew`, `StationName`, `StationType`, `Taxi`, `event`, `timestamp`

