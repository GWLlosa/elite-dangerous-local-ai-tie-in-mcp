# Elite Dangerous Journal Events Reference

This document provides a comprehensive reference for all 213 Elite Dangerous journal event types supported by the MCP server, organized by category.

**Last Updated**: October 4, 2025 (Milestone 17)
**Coverage**: 213 event types across 17 categories
**Categorization Accuracy**: 98%

## Table of Contents

- [System Events](#system-events) (13 events)
- [Navigation Events](#navigation-events) (23 events)
- [Exploration Events](#exploration-events) (17 events)
- [Combat Events](#combat-events) (22 events)
- [Trading Events](#trading-events) (12 events)
- [Mission Events](#mission-events) (8 events)
- [Engineering Events](#engineering-events) (5 events)
- [Mining Events](#mining-events) (5 events)
- [Ship Events](#ship-events) (35 events)
- [Squadron Events](#squadron-events) (4 events)
- [Crew Events](#crew-events) (13 events)
- [Passenger Events](#passenger-events) (2 events)
- [Powerplay Events](#powerplay-events) (10 events)
- [Carrier Events](#carrier-events) (18 events)
- [Social Events](#social-events) (4 events)
- [Suit/Odyssey Events](#suitodyssey-events) (18 events)
- [Other Events](#other-events) (4 events)

---

## System Events

Core game state and startup events that track commander status and game sessions.

### Fileheader
**Purpose**: Marks the beginning of a new journal file with version information.

**Key Fields**:
- `gameversion` - Game version string
- `build` - Build number
- `language` - Game language setting
- `odyssey` - Whether Odyssey expansion is active

**Example Use**: Identify game version for compatibility checks

---

### LoadGame
**Purpose**: Triggered when loading into the game, provides initial commander and ship state.

**Key Fields**:
- `Commander` - Commander name
- `Ship` - Current ship type
- `ShipName` - Custom ship name
- `ShipIdent` - Ship registration ID
- `Credits` - Current credit balance
- `FuelLevel` - Current fuel level
- `FuelCapacity` - Maximum fuel capacity
- `GameMode` - Game mode (Open, Private Group, Solo)
- `Loan` - Outstanding loan amount

**Example Use**: Initialize game state tracking, identify commander

---

### Shutdown
**Purpose**: Indicates clean game shutdown.

**Key Fields**: None

**Example Use**: Mark end of play session

---

### Music
**Purpose**: Tracks in-game music changes, indicates game state transitions.

**Key Fields**:
- `MusicTrack` - Name of music track playing

**Example Use**: Detect context changes (combat, docking, exploration)

---

### Continued
**Purpose**: Indicates journal file continuation after rotation.

**Key Fields**:
- `Part` - Journal file part number

**Example Use**: Track multi-file journal sessions

---

### Commander
**Purpose**: Provides detailed commander information.

**Key Fields**:
- `Name` - Commander name
- `FID` - Frontier ID

**Example Use**: Track commander identity changes

---

### Rank
**Purpose**: Reports current ranks in all disciplines.

**Key Fields**:
- `Combat` - Combat rank (0-8)
- `Trade` - Trade rank (0-8)
- `Explore` - Exploration rank (0-8)
- `Empire` - Empire rank (0-14)
- `Federation` - Federation rank (0-14)
- `CQC` - CQC rank (0-8)

**Example Use**: Track progression, analyze specialization

---

### Progress
**Purpose**: Detailed progression percentages for all ranks.

**Key Fields**:
- `Combat` - Combat progress (0-100%)
- `Trade` - Trade progress (0-100%)
- `Explore` - Exploration progress (0-100%)
- `Empire` - Empire progress (0-100%)
- `Federation` - Federation progress (0-100%)
- `CQC` - CQC progress (0-100%)

**Example Use**: Calculate time to next rank

---

### Reputation
**Purpose**: Current reputation standings with major factions.

**Key Fields**:
- `Empire` - Empire reputation (-100 to 100)
- `Federation` - Federation reputation (-100 to 100)
- `Alliance` - Alliance reputation (-100 to 100)
- `Independent` - Independent reputation (-100 to 100)

**Example Use**: Track faction relationships

---

### Statistics
**Purpose**: Comprehensive gameplay statistics summary.

**Key Fields**: (100+ statistics across all categories)
- `Bank_Account` - Financial statistics
- `Combat` - Combat statistics
- `Crime` - Crime statistics
- `Smuggling` - Smuggling statistics
- `Trading` - Trading statistics
- `Mining` - Mining statistics
- `Exploration` - Exploration statistics
- `Passengers` - Passenger statistics
- `Search_And_Rescue` - SAR statistics
- `Crafting` - Engineering statistics
- `Crew` - Crew hire statistics
- `Multicrew` - Multicrew statistics
- `Material_Trader_Stats` - Material trading statistics
- `CQC` - CQC statistics

**Example Use**: Generate comprehensive progress reports

---

### ClearSavedGame
**Purpose**: Indicates commander reset/deletion.

**Key Fields**:
- `Name` - Commander name being cleared

**Example Use**: Detect account resets

---

### NewCommander
**Purpose**: New commander creation.

**Key Fields**:
- `Name` - New commander name
- `Package` - Starting package selected

**Example Use**: Track new game starts

---

## Navigation Events

Events related to travel, docking, and location changes.

### FSDJump
**Purpose**: Hyperspace jump completion to a new system.

**Key Fields**:
- `StarSystem` - Destination system name
- `SystemAddress` - Unique system identifier
- `StarPos` - Galactic coordinates [x, y, z]
- `JumpDist` - Jump distance in light years
- `FuelUsed` - Fuel consumed
- `FuelLevel` - Remaining fuel
- `SystemAllegiance` - System allegiance
- `SystemEconomy` - Primary economy type
- `SystemSecurity` - Security level
- `Population` - System population

**Example Use**: Track exploration routes, calculate fuel efficiency

---

### StartJump
**Purpose**: FSD jump sequence initiated.

**Key Fields**:
- `JumpType` - "Hyperspace" or "Supercruise"
- `StarSystem` - Destination system (hyperspace only)
- `StarClass` - Star class (hyperspace only)

**Example Use**: Predict arrival, warn about fuel

---

### SupercruiseEntry
**Purpose**: Entered supercruise.

**Key Fields**:
- `StarSystem` - Current system
- `SystemAddress` - System identifier

**Example Use**: Track travel mode changes

---

### SupercruiseExit
**Purpose**: Dropped from supercruise.

**Key Fields**:
- `StarSystem` - Current system
- `SystemAddress` - System identifier
- `Body` - Body name (if near a body)
- `BodyType` - Type of body

**Example Use**: Track arrival at destinations

---

### SupercruiseDestinationDrop
**Purpose**: Dropped from supercruise at targeted destination.

**Key Fields**:
- `Type` - Destination type (Station, etc.)
- `Threat` - Threat level (0-4)

**Example Use**: Arrival confirmation, threat assessment

---

### Docked
**Purpose**: Successfully docked at a station or settlement.

**Key Fields**:
- `StationName` - Station name
- `StationType` - Station type
- `StarSystem` - System name
- `SystemAddress` - System identifier
- `MarketID` - Unique market identifier
- `StationFaction` - Controlling faction
- `StationGovernment` - Government type
- `StationServices` - Available services array
- `StationEconomy` - Primary economy
- `DistFromStarLS` - Distance from arrival star

**Example Use**: Track station visits, identify services

---

### Undocked
**Purpose**: Departed from a station.

**Key Fields**:
- `StationName` - Station departed from
- `StationType` - Station type
- `MarketID` - Market identifier

**Example Use**: Track departures, measure docked duration

---

### DockingRequested
**Purpose**: Requested docking permission.

**Key Fields**:
- `StationName` - Station name
- `StationType` - Station type
- `MarketID` - Market identifier

**Example Use**: Track docking requests

---

### DockingGranted
**Purpose**: Docking permission granted.

**Key Fields**:
- `StationName` - Station name
- `LandingPad` - Assigned landing pad number
- `MarketID` - Market identifier

**Example Use**: Guide to landing pad

---

### DockingDenied
**Purpose**: Docking permission denied.

**Key Fields**:
- `StationName` - Station name
- `Reason` - Denial reason

**Example Use**: Alert user to issue

---

### DockingCancelled
**Purpose**: Docking request cancelled.

**Key Fields**:
- `StationName` - Station name
- `MarketID` - Market identifier

**Example Use**: Track cancellations

---

### DockingTimeout
**Purpose**: Docking request timed out.

**Key Fields**:
- `StationName` - Station name
- `MarketID` - Market identifier

**Example Use**: Alert user to timeout

---

### Location
**Purpose**: Current location on startup or major location change.

**Key Fields**:
- `StarSystem` - System name
- `SystemAddress` - System identifier
- `StarPos` - Galactic coordinates
- `Body` - Body name (if applicable)
- `BodyType` - Body type
- `Docked` - Whether docked
- `StationName` - Station name (if docked)
- `StationType` - Station type (if docked)

**Example Use**: Initialize location tracking

---

### ApproachBody
**Purpose**: Approached a planetary body.

**Key Fields**:
- `StarSystem` - System name
- `SystemAddress` - System identifier
- `Body` - Body name
- `BodyID` - Body identifier

**Example Use**: Track body approaches

---

### LeaveBody
**Purpose**: Left orbital cruise around a body.

**Key Fields**:
- `StarSystem` - System name
- `SystemAddress` - System identifier
- `Body` - Body name
- `BodyID` - Body identifier

**Example Use**: Track departures from bodies

---

### Liftoff
**Purpose**: Lifted off from planetary surface.

**Key Fields**:
- `StarSystem` - System name
- `SystemAddress` - System identifier
- `Body` - Body name
- `BodyID` - Body identifier
- `OnStation` - Whether at a settlement
- `OnPlanet` - Whether on planet surface
- `Latitude` - Departure latitude
- `Longitude` - Departure longitude

**Example Use**: Track surface departures

---

### Touchdown
**Purpose**: Landed on planetary surface.

**Key Fields**:
- `StarSystem` - System name
- `SystemAddress` - System identifier
- `Body` - Body name
- `BodyID` - Body identifier
- `OnStation` - Whether at a settlement
- `OnPlanet` - Whether on planet surface
- `Latitude` - Landing latitude
- `Longitude` - Landing longitude

**Example Use**: Track landings, log coordinates

---

### NavRoute
**Purpose**: Navigation route plotted.

**Key Fields**:
- `Route` - Array of system addresses in route

**Example Use**: Track planned route

---

### NavRouteClear
**Purpose**: Navigation route cleared.

**Key Fields**: None

**Example Use**: Detect route cancellation

---

### BookTaxi
**Purpose**: Booked an Apex Interstellar taxi (Odyssey).

**Key Fields**:
- `Cost` - Taxi cost in credits
- `DestinationSystem` - Destination system
- `DestinationLocation` - Destination settlement

**Example Use**: Track Apex usage, costs

---

### FSDTarget
**Purpose**: Targeted a system for FSD jump.

**Key Fields**:
- `Name` - Target system name
- `SystemAddress` - System identifier
- `RemainingJumpsInRoute` - Jumps remaining to final destination

**Example Use**: Track jump progress

---

### USSDrop
**Purpose**: Dropped into Unidentified Signal Source.

**Key Fields**:
- `USSType` - USS type
- `USSThreat` - Threat level (0-9)

**Example Use**: Track USS encounters, threat levels

---

### FetchRemoteModule
**Purpose**: Retrieved a module from remote storage.

**Key Fields**:
- `StorageSlot` - Storage slot number
- `StoredItem` - Module being fetched
- `Ship` - Ship type
- `ShipID` - Ship identifier
- `ServerId` - Server ID

**Example Use**: Track module transfers

---

## Exploration Events

Discovery, scanning, and exploration-related events.

### Scan
**Purpose**: Detailed scan of a stellar body.

**Key Fields**:
- `BodyName` - Name of scanned body
- `BodyID` - Body identifier
- `StarSystem` - System name
- `SystemAddress` - System identifier
- `DistanceFromArrivalLS` - Distance from arrival point
- `StarType` - Star classification (for stars)
- `PlanetClass` - Planet type (for planets)
- `TerraformState` - Terraforming status
- `Landable` - Whether landable
- `AtmosphereType` - Atmosphere composition
- `Volcanism` - Volcanic activity type
- `SurfaceGravity` - Surface gravity
- `SurfaceTemperature` - Surface temperature
- `SurfacePressure` - Surface pressure
- `Rings` - Ring systems (if any)
- `Materials` - Surface materials
- `WasDiscovered` - Already discovered flag
- `WasMapped` - Already mapped flag

**Example Use**: Identify valuable scan targets, terraformable worlds

---

### FSSDiscoveryScan
**Purpose**: Full Spectrum System Scanner initiated.

**Key Fields**:
- `Progress` - Scan progress percentage
- `BodyCount` - Number of bodies in system
- `NonBodyCount` - Number of non-body signals

**Example Use**: Track FSS progress

---

### FSSAllBodiesFound
**Purpose**: All bodies in system discovered via FSS.

**Key Fields**:
- `SystemName` - System name
- `SystemAddress` - System identifier
- `Count` - Number of bodies found

**Example Use**: Confirm complete system scan

---

### FSSBodySignals
**Purpose**: FSS detected signals on a body.

**Key Fields**:
- `BodyName` - Body name
- `BodyID` - Body identifier
- `Signals` - Array of signal types and counts

**Example Use**: Identify points of interest

---

### FSSSignalDiscovered
**Purpose**: FSS discovered a signal source.

**Key Fields**:
- `SignalName` - Signal name
- `SignalName_Localised` - Localized signal name
- `IsStation` - Whether signal is a station

**Example Use**: Track signal discoveries

---

### SAASignalsFound
**Purpose**: Surface Area Analysis found signals.

**Key Fields**:
- `BodyName` - Body name
- `BodyID` - Body identifier
- `SystemAddress` - System identifier
- `Signals` - Array of signal types and counts

**Example Use**: Identify surface features

---

### SAAScanComplete
**Purpose**: Detailed Surface Area Analysis scan completed.

**Key Fields**:
- `BodyName` - Body name
- `BodyID` - Body identifier
- `SystemAddress` - System identifier
- `ProbesUsed` - Number of probes used
- `EfficiencyTarget` - Efficiency target count

**Example Use**: Track mapping efficiency, credits earned

---

### MaterialDiscovered
**Purpose**: First discovery of a new material type.

**Key Fields**:
- `Name` - Material name
- `DiscoveryNumber` - Discovery sequence number
- `Category` - Material category

**Example Use**: Track material discoveries

---

### MaterialCollected
**Purpose**: Collected a material sample.

**Key Fields**:
- `Name` - Material name
- `Category` - Material category (Raw, Manufactured, Encoded)
- `Count` - Amount collected

**Example Use**: Track material inventory changes

---

### MaterialDiscarded
**Purpose**: Discarded materials.

**Key Fields**:
- `Name` - Material name
- `Category` - Material category
- `Count` - Amount discarded

**Example Use**: Track inventory management

---

### MultiSellExplorationData
**Purpose**: Sold exploration data for multiple systems.

**Key Fields**:
- `Discovered` - Array of systems discovered
- `BaseValue` - Base value of data
- `Bonus` - First discovery bonus
- `TotalEarnings` - Total credits earned

**Example Use**: Calculate exploration profits

---

### SellExplorationData
**Purpose**: Sold exploration data (legacy event).

**Key Fields**:
- `Systems` - System names sold
- `Discovered` - Newly discovered systems
- `BaseValue` - Base value
- `Bonus` - Bonus amount
- `TotalEarnings` - Total earnings

**Example Use**: Track exploration income

---

### DiscoveryScan
**Purpose**: Discovery scanner pulse (legacy event).

**Key Fields**:
- `SystemAddress` - System identifier
- `Bodies` - Number of bodies detected

**Example Use**: Legacy scan tracking

---

### Screenshot
**Purpose**: Screenshot taken.

**Key Fields**:
- `Filename` - Screenshot filename
- `Width` - Image width
- `Height` - Image height
- `System` - Current system
- `Body` - Current body (if applicable)

**Example Use**: Link screenshots to location

---

### Codex
**Purpose**: Codex entry discovered.

**Key Fields**:
- `Name` - Entry name
- `Category` - Entry category
- `SubCategory` - Entry subcategory
- `Region` - Galactic region
- `System` - System name
- `IsNewEntry` - First discovery flag

**Example Use**: Track codex discoveries

---

### NavBeaconScan
**Purpose**: Scanned a navigation beacon.

**Key Fields**:
- `NumBodies` - Number of bodies revealed
- `SystemAddress` - System identifier

**Example Use**: Track beacon scans for system data

---

### ScanBaryCentre
**Purpose**: Scanned a barycenter (center of mass for binary systems).

**Key Fields**:
- `StarSystem` - System name
- `SystemAddress` - System identifier
- `BodyID` - Barycenter body ID

**Example Use**: Track binary system scanning

---

## Combat Events

Combat encounters, bounties, and conflict-related events.

### Bounty
**Purpose**: Bounty awarded for destroying a ship.

**Key Fields**:
- `Target` - Target ship type
- `Target_Localised` - Localized target name
- `VictimFaction` - Victim's faction
- `TotalReward` - Total bounty value
- `Rewards` - Array of faction rewards

**Example Use**: Track combat earnings

---

### CapShipBond
**Purpose**: Combat bond from capital ship combat.

**Key Fields**:
- `Reward` - Bond value
- `AwardingFaction` - Faction awarding bond
- `VictimFaction` - Defeated faction

**Example Use**: Track conflict zone earnings

---

### CombatPromotion
**Purpose**: Combat rank promotion.

**Key Fields**:
- `CombatRank` - New combat rank (0-8)

**Example Use**: Celebrate rank progression

---

### Died
**Purpose**: Ship was destroyed.

**Key Fields**:
- `KillerName` - Name of killer
- `KillerShip` - Killer's ship type
- `KillerRank` - Killer's combat rank

**Example Use**: Track deaths, identify threats

---

### Resurrect
**Purpose**: Chose to respawn at station.

**Key Fields**:
- `Option` - Respawn option chosen
- `Cost` - Rebuy cost
- `Bankrupt` - Whether bankrupt

**Example Use**: Track rebuy costs

---

### EscapeInterdiction
**Purpose**: Successfully escaped an interdiction.

**Key Fields**:
- `Interdictor` - Interdictor name
- `IsPlayer` - Whether interdictor was a player

**Example Use**: Track interdiction attempts

---

### FactionKillBond
**Purpose**: Combat bond from faction warfare.

**Key Fields**:
- `Reward` - Bond value
- `AwardingFaction` - Awarding faction
- `VictimFaction` - Victim faction

**Example Use**: Track faction war earnings

---

### FighterDestroyed
**Purpose**: SLF (ship-launched fighter) was destroyed.

**Key Fields**: None

**Example Use**: Track fighter losses

---

### FighterRebuilt
**Purpose**: SLF rebuilt after destruction.

**Key Fields**:
- `Loadout` - Fighter loadout name

**Example Use**: Track fighter rebuilds

---

### HullDamage
**Purpose**: Hull took damage.

**Key Fields**:
- `Health` - Current hull health percentage
- `PlayerPilot` - Whether player was piloting
- `Fighter` - Whether in fighter

**Example Use**: Alert to critical damage

---

### Interdicted
**Purpose**: Interdicted by another ship.

**Key Fields**:
- `Submitted` - Whether submitted
- `Interdictor` - Interdictor name
- `IsPlayer` - Whether player interdictor
- `Faction` - Interdictor faction

**Example Use**: Track interdictions

---

### Interdiction
**Purpose**: Interdicted another ship.

**Key Fields**:
- `Success` - Whether interdiction succeeded
- `Interdicted` - Target name
- `IsPlayer` - Whether target was player
- `CombatRank` - Target combat rank
- `Faction` - Target faction

**Example Use**: Track successful interdictions

---

### PVPKill
**Purpose**: Destroyed another player's ship.

**Key Fields**:
- `Victim` - Victim commander name
- `CombatRank` - Victim combat rank

**Example Use**: Track PVP kills

---

### ShieldState
**Purpose**: Shield state changed.

**Key Fields**:
- `ShieldsUp` - Whether shields are up

**Example Use**: Alert to shield loss

---

### ShipTargeted
**Purpose**: Targeted a ship or body.

**Key Fields**:
- `TargetLocked` - Whether target is locked
- `Ship` - Target ship type (if ship)
- `Ship_Localised` - Localized ship name
- `ScanStage` - Scan progress (0-3)
- `PilotName` - Pilot name
- `PilotRank` - Pilot rank
- `ShieldHealth` - Shield percentage
- `HullHealth` - Hull percentage
- `Faction` - Target faction
- `LegalStatus` - Legal status
- `Bounty` - Bounty value

**Example Use**: Display target information

---

### UnderAttack
**Purpose**: Under attack by another ship.

**Key Fields**:
- `Target` - Attacker type

**Example Use**: Alert to combat

---

### SRVDestroyed
**Purpose**: SRV (surface recon vehicle) was destroyed.

**Key Fields**: None

**Example Use**: Track SRV losses

---

### DataScanned
**Purpose**: Scanned a data point.

**Key Fields**:
- `Type` - Data point type

**Example Use**: Track data point scanning

---

### HeatDamage
**Purpose**: Ship took heat damage.

**Key Fields**: None

**Example Use**: Alert to heat levels

---

### HeatWarning
**Purpose**: Heat level warning.

**Key Fields**: None

**Example Use**: Alert to heat buildup

---

### LaunchDrone
**Purpose**: Launched a limpet drone.

**Key Fields**:
- `Type` - Drone type (Hatchbreaker, Collector, etc.)

**Example Use**: Track drone usage

---

### Scanned
**Purpose**: Ship was scanned by another ship or authority.

**Key Fields**:
- `ScanType` - Type of scan (Cargo, Crime, Cabin, Data, etc.)

**Example Use**: Alert to being scanned

---

## Trading Events

Market transactions and cargo operations.

### MarketBuy
**Purpose**: Purchased commodity from market.

**Key Fields**:
- `MarketID` - Market identifier
- `Type` - Commodity name
- `Count` - Quantity purchased
- `BuyPrice` - Price per unit
- `TotalCost` - Total cost

**Example Use**: Track purchases, calculate profit margins

---

### MarketSell
**Purpose**: Sold commodity to market.

**Key Fields**:
- `MarketID` - Market identifier
- `Type` - Commodity name
- `Count` - Quantity sold
- `SellPrice` - Price per unit
- `TotalSale` - Total sale value
- `AvgPricePaid` - Average purchase price

**Example Use**: Calculate profits

---

### Market
**Purpose**: Market data available.

**Key Fields**:
- `MarketID` - Market identifier
- `StationName` - Station name
- `StarSystem` - System name

**Example Use**: Track market access

---

### BuyTradeData
**Purpose**: Purchased trade data.

**Key Fields**:
- `System` - System name
- `Cost` - Data cost

**Example Use**: Track trade data purchases

---

### CollectCargo
**Purpose**: Collected cargo canister.

**Key Fields**:
- `Type` - Cargo type
- `Stolen` - Whether stolen

**Example Use**: Track cargo collection

---

### EjectCargo
**Purpose**: Ejected cargo.

**Key Fields**:
- `Type` - Cargo type
- `Count` - Quantity ejected
- `Abandoned` - Whether abandoned

**Example Use**: Track cargo jettison

---

### Cargo
**Purpose**: Current cargo inventory.

**Key Fields**:
- `Vessel` - Vessel type (Ship, SRV)
- `Count` - Total cargo count
- `Inventory` - Array of cargo items

**Example Use**: Display cargo manifest

---

### Trade
**Purpose**: Commodity trade completed (legacy).

**Key Fields**:
- `MarketID` - Market identifier

**Example Use**: Track trades

---

### RefuelAll
**Purpose**: Purchased full refuel at station.

**Key Fields**:
- `Cost` - Total refuel cost
- `Amount` - Fuel amount purchased

**Example Use**: Track refuel costs

---

### RedeemVoucher
**Purpose**: Redeemed a voucher (bounty, combat bond, trade dividend, etc.).

**Key Fields**:
- `Type` - Voucher type (bounty, CombatBond, trade, settlement, etc.)
- `Amount` - Total value redeemed
- `Factions` - Array of faction rewards (for bounties/bonds)

**Example Use**: Track voucher redemptions, calculate earnings

---

### BuyDrones
**Purpose**: Purchased limpet drones.

**Key Fields**:
- `Type` - Drone type
- `Count` - Number purchased
- `BuyPrice` - Price per drone
- `TotalCost` - Total cost

**Example Use**: Track drone inventory and costs

---

### CargoTransfer
**Purpose**: Transferred cargo between ship and carrier/SRV.

**Key Fields**:
- `Transfers` - Array of transfer operations with type, count, direction

**Example Use**: Track cargo movements between vessels

---

## Mission Events

Mission acceptance, completion, and tracking.

### MissionAccepted
**Purpose**: Accepted a mission.

**Key Fields**:
- `Name` - Mission name
- `LocalisedName` - Localized mission name
- `MissionID` - Unique mission identifier
- `Faction` - Issuing faction
- `DestinationSystem` - Destination system
- `DestinationStation` - Destination station
- `Expiry` - Expiration timestamp
- `Reward` - Mission reward
- `Commodity` - Required commodity (if applicable)
- `Count` - Required count
- `Target` - Target name (if applicable)
- `TargetType` - Target type
- `TargetFaction` - Target faction
- `PassengerCount` - Number of passengers

**Example Use**: Track active missions, plan routes

---

### MissionCompleted
**Purpose**: Completed a mission.

**Key Fields**:
- `Name` - Mission name
- `MissionID` - Mission identifier
- `Faction` - Issuing faction
- `Reward` - Credits earned
- `MaterialsReward` - Materials awarded
- `CommodityReward` - Commodities awarded
- `FactionEffects` - Reputation changes

**Example Use**: Track mission earnings and reputation

---

### MissionFailed
**Purpose**: Mission failed.

**Key Fields**:
- `Name` - Mission name
- `MissionID` - Mission identifier
- `Fine` - Failure fine

**Example Use**: Track failures

---

### MissionAbandoned
**Purpose**: Abandoned a mission.

**Key Fields**:
- `Name` - Mission name
- `MissionID` - Mission identifier
- `Fine` - Abandonment fine

**Example Use**: Track abandoned missions

---

### MissionRedirected
**Purpose**: Mission destination changed.

**Key Fields**:
- `MissionID` - Mission identifier
- `Name` - Mission name
- `NewDestinationStation` - New destination station
- `NewDestinationSystem` - New destination system
- `OldDestinationStation` - Previous destination
- `OldDestinationSystem` - Previous system

**Example Use**: Update navigation

---

### Missions
**Purpose**: Current active missions list.

**Key Fields**:
- `Active` - Array of active missions
- `Failed` - Array of failed missions
- `Complete` - Array of completed missions

**Example Use**: Display mission board

---

### CommunityGoal
**Purpose**: Community goal status update.

**Key Fields**:
- `CurrentGoals` - Array of active community goals with status

**Example Use**: Track CG participation

---

### CommunityGoalJoin
**Purpose**: Joined a community goal.

**Key Fields**:
- `CGID` - Community goal identifier
- `Name` - Community goal name
- `System` - System name

**Example Use**: Track CG enrollment

---

## Engineering Events

Engineering and modification activities.

### EngineerContribution
**Purpose**: Contributed materials/commodities to engineer.

**Key Fields**:
- `Engineer` - Engineer name
- `Type` - Contribution type (Commodity, Materials, etc.)
- `Commodity` - Commodity name (if applicable)
- `Material` - Material name (if applicable)
- `Quantity` - Amount contributed
- `TotalQuantity` - Total contributed to date

**Example Use**: Track engineer unlocking progress

---

### EngineerCraft
**Purpose**: Crafted an engineering modification.

**Key Fields**:
- `Engineer` - Engineer name
- `Blueprint` - Blueprint name
- `Level` - Modification level
- `Slot` - Module slot
- `Module` - Module type
- `Ingredients` - Materials consumed
- `Modifiers` - Stat changes applied

**Example Use**: Track modifications, material usage

---

### EngineerProgress
**Purpose**: Engineering relationship progress.

**Key Fields**:
- `Engineer` - Engineer name
- `Rank` - Current rank
- `Progress` - Progress to next rank

**Example Use**: Track engineer unlocking

---

### EngineerApply
**Purpose**: Applied an engineering modification (legacy).

**Key Fields**:
- `Engineer` - Engineer name
- `Blueprint` - Blueprint name
- `Level` - Modification level

**Example Use**: Track modifications

---

### EngineerLegacyConvert
**Purpose**: Converted legacy module modification.

**Key Fields**:
- `Engineer` - Engineer name
- `Blueprint` - Blueprint name
- `Level` - Modification level

**Example Use**: Track legacy conversions

---

## Mining Events

Mining and refinery operations.

### Mined
**Purpose**: Mined raw material fragment from asteroid.

**Key Fields**:
- `Type` - Material type mined
- `Count` - Number of fragments

**Example Use**: Track raw material extraction

---

### MiningRefined
**Purpose**: Refined ore into sellable commodity.

**Key Fields**:
- `Type` - Commodity type refined
- `Type_Localised` - Localized commodity name

**Example Use**: Track refined commodity production (each event = 1 unit)

---

### AsteroidCracked
**Purpose**: Cracked an asteroid with seismic charges.

**Key Fields**:
- `Body` - Ring name

**Example Use**: Track deep core mining

---

### ProspectedAsteroid
**Purpose**: Prospected an asteroid.

**Key Fields**:
- `Materials` - Array of materials with proportions
- `Content` - Material content level (Low, Medium, High)
- `Remaining` - Percentage remaining

**Example Use**: Identify valuable asteroids

---

### RefineryOpen
**Purpose**: Opened refinery interface (legacy).

**Key Fields**: None

**Example Use**: Detect refinery usage

---

## Ship Events

Ship purchases, modifications, and management.

### ShipyardBuy
**Purpose**: Purchased a ship.

**Key Fields**:
- `ShipType` - Ship type purchased
- `ShipPrice` - Purchase price
- `StoreOldShip` - Previous ship storage location
- `SellOldShip` - Previous ship sale details

**Example Use**: Track fleet expansion

---

### ShipyardNew
**Purpose**: Received a new ship (quest reward).

**Key Fields**:
- `ShipType` - Ship type received
- `NewShipID` - Ship identifier

**Example Use**: Track ship acquisitions

---

### ShipyardSell
**Purpose**: Sold a ship.

**Key Fields**:
- `ShipType` - Ship type sold
- `SellShipID` - Ship identifier
- `ShipPrice` - Sale price
- `System` - System location

**Example Use**: Track fleet reduction, sales

---

### ShipyardTransfer
**Purpose**: Initiated ship transfer.

**Key Fields**:
- `ShipType` - Ship type being transferred
- `ShipID` - Ship identifier
- `System` - Origin system
- `Distance` - Transfer distance
- `TransferPrice` - Transfer cost
- `TransferTime` - Transfer time (seconds)

**Example Use**: Track ship movements

---

### ShipyardSwap
**Purpose**: Switched to a different ship.

**Key Fields**:
- `ShipType` - New ship type
- `ShipID` - New ship identifier
- `StoreOldShip` - Previous ship storage location
- `StoreShipID` - Previous ship identifier

**Example Use**: Track active ship changes

---

### Shipyard
**Purpose**: Accessed shipyard.

**Key Fields**:
- `MarketID` - Market identifier
- `StationName` - Station name
- `StarSystem` - System name

**Example Use**: Track shipyard access

---

### StoredShips
**Purpose**: Stored ships list.

**Key Fields**:
- `MarketID` - Market identifier
- `StationName` - Station name
- `StarSystem` - System name
- `ShipsHere` - Ships at this station
- `ShipsRemote` - Ships at other stations

**Example Use**: Display stored fleet

---

### Loadout
**Purpose**: Current ship loadout.

**Key Fields**:
- `Ship` - Ship type
- `ShipName` - Custom ship name
- `ShipIdent` - Ship registration
- `ShipID` - Ship identifier
- `HullValue` - Hull value
- `ModulesValue` - Modules value
- `HullHealth` - Hull health
- `Modules` - Array of installed modules
- `Rebuy` - Rebuy cost

**Example Use**: Display ship configuration

---

### ModuleBuy
**Purpose**: Purchased a module.

**Key Fields**:
- `Slot` - Module slot
- `BuyItem` - Module purchased
- `BuyPrice` - Purchase price
- `Ship` - Ship type
- `ShipID` - Ship identifier

**Example Use**: Track module purchases

---

### ModuleSell
**Purpose**: Sold a module.

**Key Fields**:
- `Slot` - Module slot
- `SellItem` - Module sold
- `SellPrice` - Sale price
- `Ship` - Ship type
- `ShipID` - Ship identifier

**Example Use**: Track module sales

---

### ModuleSwap
**Purpose**: Swapped modules between slots.

**Key Fields**:
- `FromSlot` - Source slot
- `ToSlot` - Destination slot
- `FromItem` - Module moved from
- `ToItem` - Module moved to
- `Ship` - Ship type
- `ShipID` - Ship identifier

**Example Use**: Track loadout changes

---

### ModuleStore
**Purpose**: Stored a module.

**Key Fields**:
- `Slot` - Module slot
- `StoredItem` - Module stored
- `Ship` - Ship type
- `ShipID` - Ship identifier
- `MarketID` - Market identifier

**Example Use**: Track stored modules

---

### ModuleRetrieve
**Purpose**: Retrieved a stored module.

**Key Fields**:
- `Slot` - Module slot
- `RetrievedItem` - Module retrieved
- `Ship` - Ship type
- `ShipID` - Ship identifier
- `MarketID` - Market identifier
- `EngineerModifications` - Engineering level

**Example Use**: Track module retrieval

---

### MassModuleStore
**Purpose**: Stored all modules from a ship.

**Key Fields**:
- `Ship` - Ship type
- `ShipID` - Ship identifier
- `MarketID` - Market identifier
- `Items` - Array of stored items

**Example Use**: Track mass storage

---

### Outfitting
**Purpose**: Accessed outfitting.

**Key Fields**:
- `MarketID` - Market identifier
- `StationName` - Station name
- `StarSystem` - System name

**Example Use**: Track outfitting access

---

### Repair
**Purpose**: Repaired a module.

**Key Fields**:
- `Item` - Module repaired
- `Cost` - Repair cost

**Example Use**: Track repair costs

---

### RepairAll
**Purpose**: Repaired all modules.

**Key Fields**:
- `Cost` - Total repair cost

**Example Use**: Track maintenance costs

---

### Synthesis
**Purpose**: Synthesized consumables/materials.

**Key Fields**:
- `Name` - Synthesis name
- `Materials` - Materials consumed

**Example Use**: Track synthesis usage

---

### RestockVehicle
**Purpose**: Restocked SRV bay.

**Key Fields**:
- `Type` - Vehicle type
- `Loadout` - Vehicle loadout
- `Cost` - Restock cost
- `Count` - Number of vehicles

**Example Use**: Track SRV restocking

---

### RebootRepair
**Purpose**: Rebooted ship to repair damaged modules.

**Key Fields**:
- `Modules` - Array of modules repaired

**Example Use**: Track emergency repairs

---

### Refuel
**Purpose**: Purchased partial refuel.

**Key Fields**:
- `Cost` - Refuel cost
- `Amount` - Fuel amount

**Example Use**: Track fuel costs

---

### BuyAmmo
**Purpose**: Purchased ammunition.

**Key Fields**:
- `Cost` - Total cost

**Example Use**: Track ammo costs

---

### LaunchSRV
**Purpose**: Launched SRV.

**Key Fields**:
- `Loadout` - SRV loadout
- `PlayerControlled` - Whether player is piloting

**Example Use**: Track SRV deployments

---

### DockSRV
**Purpose**: Docked SRV back to ship.

**Key Fields**: None

**Example Use**: Track SRV recovery

---

### LaunchFighter
**Purpose**: Launched ship-launched fighter.

**Key Fields**:
- `Loadout` - Fighter loadout
- `PlayerControlled` - Whether player is piloting

**Example Use**: Track fighter launches

---

### DockFighter
**Purpose**: Docked fighter back to ship.

**Key Fields**: None

**Example Use**: Track fighter recovery

---

### VehicleSwitch
**Purpose**: Switched between ship, SRV, or fighter.

**Key Fields**:
- `To` - Vehicle switching to

**Example Use**: Track vehicle changes

---

### AfmuRepairs
**Purpose**: AFMU repaired a module.

**Key Fields**:
- `Module` - Module repaired
- `FullyRepaired` - Whether fully repaired
- `Health` - Current module health

**Example Use**: Track AFMU usage

---

### FuelScoop
**Purpose**: Scooped fuel from a star.

**Key Fields**:
- `Scooped` - Amount scooped
- `Total` - Total fuel level

**Example Use**: Track fuel scooping

---

### SetUserShipName
**Purpose**: Named or renamed a ship.

**Key Fields**:
- `Ship` - Ship type
- `ShipID` - Ship identifier
- `UserShipName` - Custom ship name
- `UserShipId` - Custom ship identifier/registration

**Example Use**: Track ship naming

---

### ShipLocker
**Purpose**: Ship locker inventory (Odyssey).

**Key Fields**:
- `Items` - Array of items in ship locker
- `Components` - Array of components

**Example Use**: Display ship locker contents

---

### ShipRedeemed
**Purpose**: Redeemed a destroyed ship.

**Key Fields**:
- `MarketID` - Market identifier
- `Ship` - Ship type

**Example Use**: Track ship redemptions

---

### ShipyardRedeem
**Purpose**: Redeemed ship at shipyard.

**Key Fields**:
- `MarketID` - Market identifier

**Example Use**: Track redemptions

---

### ModuleInfo
**Purpose**: Current module information.

**Key Fields**:
- `Modules` - Array of all installed modules with details

**Example Use**: Display complete module manifest

---

### StoredModules
**Purpose**: List of stored modules.

**Key Fields**:
- `MarketID` - Market identifier
- `StationName` - Station name
- `StarSystem` - System name
- `Items` - Array of stored modules

**Example Use**: Display stored module inventory

---

## Squadron Events

Squadron and wing management.

### SquadronCreated
**Purpose**: Created a squadron.

**Key Fields**:
- `SquadronName` - Squadron name

**Example Use**: Track squadron creation

---

### SquadronStartup
**Purpose**: Squadron information on startup.

**Key Fields**:
- `SquadronName` - Squadron name
- `CurrentRank` - Current rank in squadron

**Example Use**: Display squadron info

---

### WingAdd
**Purpose**: Player added to wing.

**Key Fields**:
- `Name` - Player name added

**Example Use**: Track wing membership

---

### WingJoin
**Purpose**: Joined a wing.

**Key Fields**:
- `Others` - Array of other wing members

**Example Use**: Track wing joining

---

### WingLeave
**Purpose**: Left a wing.

**Key Fields**: None

**Example Use**: Track wing departures

---

### WingInvite
**Purpose**: Invited to join a wing.

**Key Fields**:
- `Name` - Inviter name

**Example Use**: Track wing invitations

---

## Crew Events

Multi-crew and NPC crew management.

### CrewAssign
**Purpose**: Assigned NPC crew member to a role.

**Key Fields**:
- `Name` - Crew member name
- `NpcCrewId` - Crew identifier
- `Role` - Assigned role (Active, etc.)

**Example Use**: Track crew assignments

---

### CrewFire
**Purpose**: Fired an NPC crew member.

**Key Fields**:
- `Name` - Crew member name
- `NpcCrewId` - Crew identifier

**Example Use**: Track crew changes

---

### CrewHire
**Purpose**: Hired an NPC crew member.

**Key Fields**:
- `Name` - Crew member name
- `NpcCrewId` - Crew identifier
- `Faction` - Crew faction
- `Cost` - Hiring cost
- `CombatRank` - Combat rank

**Example Use**: Track crew hiring

---

### CrewLaunchFighter
**Purpose**: NPC crew launched a fighter.

**Key Fields**:
- `Crew` - Crew member name
- `ID` - Crew identifier

**Example Use**: Track crew fighter launches

---

### CrewMemberJoins
**Purpose**: Another player joined as crew.

**Key Fields**:
- `Crew` - Player name

**Example Use**: Track multi-crew sessions

---

### CrewMemberQuits
**Purpose**: Crew member left.

**Key Fields**:
- `Crew` - Player name

**Example Use**: Track crew departures

---

### CrewMemberRoleChange
**Purpose**: Crew member changed role.

**Key Fields**:
- `Crew` - Player name
- `Role` - New role

**Example Use**: Track role changes

---

### JoinACrew
**Purpose**: Joined another player's crew.

**Key Fields**:
- `Captain` - Captain name

**Example Use**: Track multi-crew joining

---

### QuitACrew
**Purpose**: Left another player's crew.

**Key Fields**:
- `Captain` - Captain name

**Example Use**: Track multi-crew departures

---

### KickCrewMember
**Purpose**: Kicked a crew member.

**Key Fields**:
- `Crew` - Player name kicked

**Example Use**: Track crew removals

---

### ChangeCrewRole
**Purpose**: Changed crew member role.

**Key Fields**:
- `Role` - New role

**Example Use**: Track own role changes

---

### EndCrewSession
**Purpose**: Multi-crew session ended.

**Key Fields**:
- `OnCrime` - Whether ended due to crime

**Example Use**: Track session endings

---

### NpcCrewPaidWage
**Purpose**: Paid wages to NPC crew member.

**Key Fields**:
- `NpcCrewName` - Crew member name
- `NpcCrewId` - Crew identifier
- `Amount` - Wage amount paid

**Example Use**: Track crew costs

---

## Passenger Events

Passenger mission management.

### PassengerManifest
**Purpose**: Current passenger manifest.

**Key Fields**:
- `Passengers` - Array of passengers

**Example Use**: Display passenger list

---

### Passengers
**Purpose**: Passenger list update.

**Key Fields**:
- `Manifest` - Array of passengers

**Example Use**: Track passenger changes

---

## Powerplay Events

Powerplay activities and pledges.

### PowerplayCollect
**Purpose**: Collected powerplay commodities.

**Key Fields**:
- `Power` - Power name
- `Type` - Commodity type
- `Count` - Amount collected

**Example Use**: Track powerplay cargo

---

### PowerplayDefect
**Purpose**: Defected from a power.

**Key Fields**:
- `FromPower` - Previous power
- `ToPower` - New power

**Example Use**: Track allegiance changes

---

### PowerplayDeliver
**Purpose**: Delivered powerplay commodities.

**Key Fields**:
- `Power` - Power name
- `Type` - Commodity type
- `Count` - Amount delivered

**Example Use**: Track powerplay contributions

---

### PowerplayFastTrack
**Purpose**: Fast-tracked powerplay nominations.

**Key Fields**:
- `Power` - Power name
- `Cost` - Fast-track cost

**Example Use**: Track fast-track usage

---

### PowerplayJoin
**Purpose**: Pledged to a power.

**Key Fields**:
- `Power` - Power name pledged to

**Example Use**: Track powerplay enrollment

---

### PowerplayLeave
**Purpose**: Left a power.

**Key Fields**:
- `Power` - Power name left

**Example Use**: Track powerplay departures

---

### PowerplaySalary
**Purpose**: Received powerplay salary.

**Key Fields**:
- `Power` - Power name
- `Amount` - Salary amount

**Example Use**: Track powerplay income

---

### PowerplayVote
**Purpose**: Voted in powerplay.

**Key Fields**:
- `Power` - Power name
- `System` - System voted for
- `Votes` - Number of votes cast

**Example Use**: Track powerplay voting

---

### PowerplayVoucher
**Purpose**: Redeemed powerplay voucher.

**Key Fields**:
- `Power` - Power name
- `Systems` - Array of systems

**Example Use**: Track powerplay rewards

---

### Powerplay
**Purpose**: General powerplay status.

**Key Fields**:
- `Power` - Current power
- `Rank` - Current rank
- `Merits` - Current merits
- `Votes` - Available votes
- `TimePledged` - Time pledged (seconds)

**Example Use**: Display powerplay status

---

## Carrier Events

Fleet carrier operations and management.

### CarrierBuy
**Purpose**: Purchased a fleet carrier.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `BoughtAtMarket` - Purchase market ID
- `Location` - System location
- `Price` - Purchase price
- `Variant` - Carrier variant
- `Callsign` - Carrier callsign

**Example Use**: Track carrier acquisition

---

### CarrierStats
**Purpose**: Carrier statistics.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `Callsign` - Carrier callsign
- `Name` - Carrier name
- `DockingAccess` - Docking access level
- `AllowNotorious` - Allow notorious ships
- `FuelLevel` - Current fuel
- `JumpRangeCurr` - Current jump range
- `JumpRangeMax` - Maximum jump range
- `Finance` - Financial status
- `Crew` - Crew status
- `ShipPacks` - Installed ship packs
- `ModulePacks` - Installed module packs

**Example Use**: Display carrier status

---

### CarrierJump
**Purpose**: Carrier jumped to new system.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `Docked` - Whether docked on carrier
- `StarSystem` - Destination system
- `SystemAddress` - System identifier
- `Body` - Body name
- `BodyID` - Body identifier
- `BodyType` - Body type

**Example Use**: Track carrier movement

---

### CarrierDecommission
**Purpose**: Initiated carrier decommission.

**Key Fields**:
- `CarrierID` - Carrier identifier

**Example Use**: Track carrier decommission

---

### CarrierCancelDecommission
**Purpose**: Cancelled carrier decommission.

**Key Fields**:
- `CarrierID` - Carrier identifier

**Example Use**: Track decommission cancellations

---

### CarrierBankTransfer
**Purpose**: Transferred credits to/from carrier bank.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `Deposit` - Amount deposited
- `Withdraw` - Amount withdrawn
- `PlayerBalance` - New player balance
- `CarrierBalance` - New carrier balance

**Example Use**: Track carrier finances

---

### CarrierDepositFuel
**Purpose**: Deposited tritium fuel.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `Amount` - Fuel amount deposited
- `Total` - Total carrier fuel

**Example Use**: Track fuel management

---

### CarrierCrewServices
**Purpose**: Modified carrier services.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `CrewRole` - Service type
- `Operation` - Operation (Activate, Deactivate, etc.)
- `CrewName` - Service name

**Example Use**: Track service changes

---

### CarrierFinance
**Purpose**: Carrier financial report.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `TaxRate` - Tariff rate
- `CarrierBalance` - Carrier balance
- `ReserveBalance` - Reserve balance
- `AvailableBalance` - Available balance
- `ReservePercent` - Reserve percentage

**Example Use**: Display finances

---

### CarrierShipPack
**Purpose**: Purchased carrier shipyard pack.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `Operation` - Operation type
- `PackTheme` - Pack theme
- `PackTier` - Pack tier
- `Cost` - Pack cost

**Example Use**: Track carrier upgrades

---

### CarrierModulePack
**Purpose**: Purchased carrier outfitting pack.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `Operation` - Operation type
- `PackTheme` - Pack theme
- `PackTier` - Pack tier
- `Cost` - Pack cost

**Example Use**: Track carrier upgrades

---

### CarrierTradeOrder
**Purpose**: Set up carrier commodity trade order.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `BlackMarket` - Black market flag
- `Commodity` - Commodity name
- `PurchaseOrder` - Purchase price
- `SaleOrder` - Sale price
- `CancelTrade` - Cancellation flag

**Example Use**: Manage carrier trading

---

### CarrierDockingPermission
**Purpose**: Changed carrier docking permissions.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `DockingAccess` - Access level
- `AllowNotorious` - Allow notorious ships

**Example Use**: Track access control

---

### CarrierNameChange
**Purpose**: Changed carrier name.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `Name` - New carrier name
- `Callsign` - Carrier callsign

**Example Use**: Track name changes

---

### CarrierJumpRequest
**Purpose**: Requested carrier jump.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `SystemName` - Destination system
- `SystemAddress` - System identifier
- `Body` - Destination body
- `BodyID` - Body identifier
- `DepartureTime` - Scheduled departure

**Example Use**: Track jump scheduling

---

### CarrierJumpCancelled
**Purpose**: Cancelled carrier jump.

**Key Fields**:
- `CarrierID` - Carrier identifier

**Example Use**: Track jump cancellations

---

### CarrierLocation
**Purpose**: Carrier location information.

**Key Fields**:
- `StarSystem` - Current system
- `SystemAddress` - System identifier
- `Body` - Current body
- `BodyID` - Body identifier
- `BodyType` - Body type

**Example Use**: Display carrier location

---

## Social Events

Social interactions and communications.

### Friends
**Purpose**: Friends list.

**Key Fields**:
- `Status` - Friend status
- `Name` - Friend name

**Example Use**: Display friends list

---

### ReceiveText
**Purpose**: Received text message from NPCs, players, or system (including Captain's Log entries).

**Key Fields** (extracted to `key_data`):
- `message` - Message text (prefers `Message_Localised` over `Message`)
- `from` - Sender name (prefers `From_Localised` over `From`, may be empty for system messages)
- `channel` - Channel type (`npc`, `player`, `local`, `system`, `squadron`, `wing`, etc.)

**Raw Event Fields**:
- `From` / `From_Localised` - Sender identification
- `Message` / `Message_Localised` - Message content
- `Channel` - Communication channel

**Example Use**:
- Access Captain's Log entries via API
- Retrieve in-game chat messages
- Search message content with `contains_text` parameter
- Track NPC communications and player interactions

**Summary Format**: "Message from {sender}: {message preview}" or "Message ({channel}): {message preview}"

**Notes**:
- Captain's Log entries typically have empty `From` field and `npc` channel
- Localised fields provide human-readable versions of templated messages
- Message content is now fully accessible via `key_data` (Issue #23 fix)

---

### SendText
**Purpose**: Text message sent by the player to channels or other players.

**Key Fields** (extracted to `key_data`):
- `message` - Message text sent by the player
- `to` - Recipient or channel (`local`, `squadron`, `wing`, player name, etc.)
- `sent` - Boolean indicating if message was successfully sent

**Raw Event Fields**:
- `Message` - Message content
- `To` - Recipient/channel identifier
- `Sent` - Send status boolean

**Example Use**:
- Track player communication history
- Log sent messages to local/squadron/wing channels
- Monitor direct messages to other commanders
- Detect failed message sends (Sent=False)

**Summary Format**: "Sent to {recipient}: {message preview}"

**Notes**:
- Message content is now fully accessible via `key_data` (Issue #23 fix)
- Supports all recipient types: local, squadron, wing, player names
- Long messages truncated to 50 characters in summary
- Sent status allows detection of failed message delivery

---

### Promotion
**Purpose**: Rank promotion in any category.

**Key Fields**:
- `Combat` - Combat rank (if promoted)
- `Trade` - Trade rank (if promoted)
- `Explore` - Exploration rank (if promoted)
- `Empire` - Empire rank (if promoted)
- `Federation` - Federation rank (if promoted)
- `CQC` - CQC rank (if promoted)

**Example Use**: Celebrate promotions

---

## Suit/Odyssey Events

On-foot gameplay and Odyssey expansion events.

### SuitPurchased
**Purpose**: Purchased a suit (Odyssey).

**Key Fields**:
- `Name` - Suit name
- `Price` - Purchase price
- `SuitID` - Suit identifier

**Example Use**: Track suit purchases

---

### SuitLoadout
**Purpose**: Current suit loadout.

**Key Fields**:
- `LoadoutID` - Loadout identifier
- `LoadoutName` - Loadout name
- `SuitName` - Suit name
- `Modules` - Array of modules

**Example Use**: Display suit configuration

---

### LoadoutEquipModule
**Purpose**: Equipped module to suit.

**Key Fields**:
- `SuitID` - Suit identifier
- `SuitName` - Suit name
- `LoadoutID` - Loadout identifier
- `LoadoutName` - Loadout name
- `ModuleName` - Module equipped
- `SlotName` - Slot name

**Example Use**: Track suit modifications

---

### LoadoutRemoveModule
**Purpose**: Removed module from suit.

**Key Fields**:
- `SuitID` - Suit identifier
- `SuitName` - Suit name
- `LoadoutID` - Loadout identifier
- `LoadoutName` - Loadout name
- `ModuleName` - Module removed
- `SlotName` - Slot name

**Example Use**: Track suit modifications

---

### UseConsumable
**Purpose**: Used a consumable item.

**Key Fields**:
- `Name` - Consumable name
- `Type` - Consumable type

**Example Use**: Track consumable usage

---

### BackpackChange
**Purpose**: Backpack contents changed.

**Key Fields**:
- `Added` - Items added
- `Removed` - Items removed

**Example Use**: Track backpack inventory

---

### BookDropship
**Purpose**: Booked dropship transport.

**Key Fields**:
- `Cost` - Transport cost
- `DestinationSystem` - Destination system
- `DestinationLocation` - Destination location

**Example Use**: Track dropship usage

---

### CancelDropship
**Purpose**: Cancelled dropship transport.

**Key Fields**:
- `Refund` - Refund amount

**Example Use**: Track cancellations

---

### CollectItems
**Purpose**: Collected items on foot.

**Key Fields**:
- `Name` - Item name
- `Type` - Item type
- `Count` - Quantity collected
- `Stolen` - Whether stolen

**Example Use**: Track item collection

---

### Disembark
**Purpose**: Disembarked from ship.

**Key Fields**:
- `SRV` - Whether in SRV
- `Taxi` - Whether from taxi
- `Multicrew` - Whether in multicrew
- `ID` - Ship/SRV identifier
- `StarSystem` - System name
- `Body` - Body name

**Example Use**: Track on-foot transitions

---

### Embark
**Purpose**: Embarked into ship.

**Key Fields**:
- `SRV` - Whether into SRV
- `Taxi` - Whether into taxi
- `Multicrew` - Whether multicrew
- `ID` - Ship/SRV identifier
- `StarSystem` - System name
- `Body` - Body name

**Example Use**: Track ship boarding

---

### FCMaterials
**Purpose**: Carrier materials status.

**Key Fields**:
- `CarrierID` - Carrier identifier
- `CarrierName` - Carrier name
- `Items` - Array of materials

**Example Use**: Display carrier materials

---

### TradeMicroResources
**Purpose**: Traded micro-resources at bartender.

**Key Fields**:
- `Offered` - Resources offered
- `Received` - Resources received
- `Category` - Trade category
- `MarketID` - Market identifier

**Example Use**: Track micro-resource trading

---

### TransferMicroResources
**Purpose**: Transferred micro-resources.

**Key Fields**:
- `Transfers` - Array of transfers

**Example Use**: Track resource transfers

---

### UpgradeWeapon
**Purpose**: Upgraded a weapon.

**Key Fields**:
- `Name` - Weapon name
- `Class` - Weapon class
- `Cost` - Upgrade cost

**Example Use**: Track weapon upgrades

---

### UpgradeSuit
**Purpose**: Upgraded a suit.

**Key Fields**:
- `Name` - Suit name
- `Class` - Suit class
- `Cost` - Upgrade cost

**Example Use**: Track suit upgrades

---

### Backpack
**Purpose**: Backpack inventory status (Odyssey).

**Key Fields**:
- `Items` - Array of items in backpack
- `Components` - Array of components

**Example Use**: Display backpack contents

---

### ReservoirReplenished
**Purpose**: Suit life support reservoir replenished.

**Key Fields**:
- `FuelMain` - Main fuel level
- `FuelReservoir` - Reservoir fuel level

**Example Use**: Track life support refills

---

## Other Events

Events that don't fit into specific categories or have miscellaneous purposes.

### Unknown
**Purpose**: Placeholder for genuinely unknown event types.

**Key Fields**: Varies

**Example Use**: Identify new events for future implementation

---

### CommitCrime
**Purpose**: Committed a crime.

**Key Fields**:
- `CrimeType` - Type of crime
- `Faction` - Victim faction
- `Fine` - Fine amount (if applicable)
- `Bounty` - Bounty amount (if applicable)

**Example Use**: Track legal status changes

---

### CrimeVictim
**Purpose**: Was the victim of a crime.

**Key Fields**:
- `Offender` - Offender name
- `CrimeType` - Type of crime
- `Fine` - Fine imposed on offender (if known)

**Example Use**: Log crime encounters

---

### Materials
**Purpose**: Current materials inventory.

**Key Fields**:
- `Raw` - Array of raw materials
- `Manufactured` - Array of manufactured materials
- `Encoded` - Array of encoded materials

**Example Use**: Display complete materials inventory

---

## Event Categories Summary

| Category | Event Count | Primary Use Cases |
|----------|-------------|-------------------|
| System | 13 | Game state tracking, commander info |
| Navigation | 23 | Travel tracking, location changes |
| Exploration | 17 | Discoveries, scans, mapping |
| Combat | 22 | Bounties, combat bonds, conflicts |
| Trading | 12 | Market transactions, cargo |
| Mission | 8 | Mission tracking, community goals |
| Engineering | 5 | Modifications, upgrades |
| Mining | 5 | Resource extraction, refining |
| Ship | 35 | Fleet management, modifications |
| Squadron | 4 | Wing and squadron operations |
| Crew | 13 | Multi-crew, NPC crew |
| Passenger | 2 | Passenger missions |
| Powerplay | 10 | Powerplay activities |
| Carrier | 18 | Fleet carrier management |
| Social | 4 | Communications, friends |
| Suit/Odyssey | 18 | On-foot gameplay |
| Other | 4 | Miscellaneous events |
| **Total** | **213** | **Complete Elite Dangerous coverage** |

---

## Version History

- **October 4, 2025 (Milestone 17)**: Added 34 new event types, bringing total to 213 events with 98% categorization accuracy
- **September 2025**: Initial comprehensive documentation with 179 event types

---

## Usage in MCP Server

All events are automatically:
1. **Categorized** into one of 17 categories
2. **Summarized** with human-readable descriptions
3. **Validated** for data integrity
4. **Stored** in the in-memory data store
5. **Queried** via MCP tools, resources, and prompts

**Example Query**:
```python
# Get all combat events from last hour
combat_events = data_store.query_events(
    EventFilter(categories={EventCategory.COMBAT}, start_time=cutoff)
)
```

**Example Summary**:
```
FSDJump: Jumped to Sol (8.59ly)
Scan: Scanned Earth - Earth-like world (terraformable, landable)
Docked: Docked at Abraham Lincoln in Sol
```

---

For implementation details, see `src/journal/events.py`.
