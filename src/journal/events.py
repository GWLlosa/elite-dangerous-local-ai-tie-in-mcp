"""
Elite Dangerous journal event processing and classification.

This module provides comprehensive event categorization, summarization,
and data extraction for all major Elite Dangerous journal event types.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class EventCategory(Enum):
    """Event category classifications for Elite Dangerous events."""
    
    # Core categories
    SYSTEM = "system"  # Game state, startup, shutdown
    NAVIGATION = "navigation"  # Jump, dock, undock, location changes
    EXPLORATION = "exploration"  # Scan, discovery, mapping
    COMBAT = "combat"  # Combat-related events
    TRADING = "trading"  # Buy, sell, market interactions
    MISSION = "mission"  # Mission accept, complete, fail
    ENGINEERING = "engineering"  # Engineering and modifications
    MINING = "mining"  # Mining and refinery operations
    PASSENGER = "passenger"  # Passenger missions and cabin events
    SQUADRON = "squadron"  # Squadron and wing events
    POWERPLAY = "powerplay"  # Powerplay activities
    CREW = "crew"  # Multi-crew and NPC crew events
    SOCIAL = "social"  # Friends, communication
    SHIP = "ship"  # Ship purchase, modification, transfer
    SUIT = "suit"  # Odyssey on-foot activities
    CARRIER = "carrier"  # Fleet carrier operations
    OTHER = "other"  # Uncategorized events


@dataclass
class ProcessedEvent:
    """Processed journal event with categorization and summary."""
    
    # Raw event data
    raw_event: Dict[str, Any]
    
    # Processed fields
    event_type: str
    timestamp: datetime
    category: EventCategory
    summary: str
    
    # Extracted key data
    key_data: Dict[str, Any] = field(default_factory=dict)
    
    # Validation status
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)


class EventProcessor:
    """Process and categorize Elite Dangerous journal events."""
    
    # Event type to category mapping
    EVENT_CATEGORIES = {
        # System events
        "Fileheader": EventCategory.SYSTEM,
        "LoadGame": EventCategory.SYSTEM,
        "Shutdown": EventCategory.SYSTEM,
        "Music": EventCategory.SYSTEM,
        "Continued": EventCategory.SYSTEM,
        "Commander": EventCategory.SYSTEM,
        "Rank": EventCategory.SYSTEM,
        "Progress": EventCategory.SYSTEM,
        "Reputation": EventCategory.SYSTEM,
        "Statistics": EventCategory.SYSTEM,
        "ClearSavedGame": EventCategory.SYSTEM,
        "NewCommander": EventCategory.SYSTEM,
        
        # Navigation events
        "FSDJump": EventCategory.NAVIGATION,
        "StartJump": EventCategory.NAVIGATION,
        "SupercruiseEntry": EventCategory.NAVIGATION,
        "SupercruiseExit": EventCategory.NAVIGATION,
        "SupercruiseDestinationDrop": EventCategory.NAVIGATION,
        "Docked": EventCategory.NAVIGATION,
        "Undocked": EventCategory.NAVIGATION,
        "DockingRequested": EventCategory.NAVIGATION,
        "DockingGranted": EventCategory.NAVIGATION,
        "DockingDenied": EventCategory.NAVIGATION,
        "DockingCancelled": EventCategory.NAVIGATION,
        "DockingTimeout": EventCategory.NAVIGATION,
        "Location": EventCategory.NAVIGATION,
        "ApproachBody": EventCategory.NAVIGATION,
        "LeaveBody": EventCategory.NAVIGATION,
        "Liftoff": EventCategory.NAVIGATION,
        "Touchdown": EventCategory.NAVIGATION,
        "NavRoute": EventCategory.NAVIGATION,
        "NavRouteClear": EventCategory.NAVIGATION,
        "BookTaxi": EventCategory.NAVIGATION,
        "FSDTarget": EventCategory.NAVIGATION,
        "USSDrop": EventCategory.NAVIGATION,
        "FetchRemoteModule": EventCategory.NAVIGATION,
        
        # Exploration events
        "Scan": EventCategory.EXPLORATION,
        "FSSDiscoveryScan": EventCategory.EXPLORATION,
        "FSSAllBodiesFound": EventCategory.EXPLORATION,
        "FSSBodySignals": EventCategory.EXPLORATION,
        "FSSSignalDiscovered": EventCategory.EXPLORATION,
        "SAASignalsFound": EventCategory.EXPLORATION,
        "SAAScanComplete": EventCategory.EXPLORATION,
        "MaterialDiscovered": EventCategory.EXPLORATION,
        "MaterialCollected": EventCategory.EXPLORATION,
        "MaterialDiscarded": EventCategory.EXPLORATION,
        "MultiSellExplorationData": EventCategory.EXPLORATION,
        "SellExplorationData": EventCategory.EXPLORATION,
        "DiscoveryScan": EventCategory.EXPLORATION,
        "Screenshot": EventCategory.EXPLORATION,
        "Codex": EventCategory.EXPLORATION,
        "NavBeaconScan": EventCategory.EXPLORATION,
        "ScanBaryCentre": EventCategory.EXPLORATION,
        
        # Combat events
        "Bounty": EventCategory.COMBAT,
        "CapShipBond": EventCategory.COMBAT,
        "CombatPromotion": EventCategory.COMBAT,
        "Died": EventCategory.COMBAT,
        "Resurrect": EventCategory.COMBAT,
        "EscapeInterdiction": EventCategory.COMBAT,
        "FactionKillBond": EventCategory.COMBAT,
        "FighterDestroyed": EventCategory.COMBAT,
        "FighterRebuilt": EventCategory.COMBAT,
        "HullDamage": EventCategory.COMBAT,
        "Interdicted": EventCategory.COMBAT,
        "Interdiction": EventCategory.COMBAT,
        "PVPKill": EventCategory.COMBAT,
        "ShieldState": EventCategory.COMBAT,
        "ShipTargeted": EventCategory.COMBAT,
        "UnderAttack": EventCategory.COMBAT,
        "SRVDestroyed": EventCategory.COMBAT,
        "DataScanned": EventCategory.COMBAT,
        "HeatDamage": EventCategory.COMBAT,
        "HeatWarning": EventCategory.COMBAT,
        "LaunchDrone": EventCategory.COMBAT,
        "Scanned": EventCategory.COMBAT,
        
        # Trading events
        "MarketBuy": EventCategory.TRADING,
        "MarketSell": EventCategory.TRADING,
        "Market": EventCategory.TRADING,
        "BuyTradeData": EventCategory.TRADING,
        "CollectCargo": EventCategory.TRADING,
        "EjectCargo": EventCategory.TRADING,
        "Cargo": EventCategory.TRADING,
        "Trade": EventCategory.TRADING,
        "RefuelAll": EventCategory.TRADING,
        "RedeemVoucher": EventCategory.TRADING,
        "BuyDrones": EventCategory.TRADING,
        "CargoTransfer": EventCategory.TRADING,
        
        # Mission events
        "MissionAccepted": EventCategory.MISSION,
        "MissionCompleted": EventCategory.MISSION,
        "MissionFailed": EventCategory.MISSION,
        "MissionAbandoned": EventCategory.MISSION,
        "MissionRedirected": EventCategory.MISSION,
        "Missions": EventCategory.MISSION,
        "CommunityGoal": EventCategory.MISSION,
        "CommunityGoalJoin": EventCategory.MISSION,
        
        # Engineering events
        "EngineerContribution": EventCategory.ENGINEERING,
        "EngineerCraft": EventCategory.ENGINEERING,
        "EngineerProgress": EventCategory.ENGINEERING,
        "EngineerApply": EventCategory.ENGINEERING,
        "EngineerLegacyConvert": EventCategory.ENGINEERING,
        
        # Mining events
        "Mined": EventCategory.MINING,
        "MiningRefined": EventCategory.MINING,
        "AsteroidCracked": EventCategory.MINING,
        "ProspectedAsteroid": EventCategory.MINING,
        "RefineryOpen": EventCategory.MINING,
        
        # Ship events
        "ShipyardBuy": EventCategory.SHIP,
        "ShipyardNew": EventCategory.SHIP,
        "ShipyardSell": EventCategory.SHIP,
        "ShipyardTransfer": EventCategory.SHIP,
        "ShipyardSwap": EventCategory.SHIP,
        "Shipyard": EventCategory.SHIP,
        "StoredShips": EventCategory.SHIP,
        "Loadout": EventCategory.SHIP,
        "ModuleBuy": EventCategory.SHIP,
        "ModuleSell": EventCategory.SHIP,
        "ModuleSwap": EventCategory.SHIP,
        "ModuleStore": EventCategory.SHIP,
        "ModuleRetrieve": EventCategory.SHIP,
        "MassModuleStore": EventCategory.SHIP,
        "Outfitting": EventCategory.SHIP,
        "Repair": EventCategory.SHIP,
        "RepairAll": EventCategory.SHIP,
        "Synthesis": EventCategory.SHIP,
        "RestockVehicle": EventCategory.SHIP,
        "RebootRepair": EventCategory.SHIP,
        "Refuel": EventCategory.SHIP,
        "BuyAmmo": EventCategory.SHIP,
        "LaunchSRV": EventCategory.SHIP,
        "DockSRV": EventCategory.SHIP,
        "LaunchFighter": EventCategory.SHIP,
        "DockFighter": EventCategory.SHIP,
        "VehicleSwitch": EventCategory.SHIP,
        "AfmuRepairs": EventCategory.SHIP,
        "FuelScoop": EventCategory.SHIP,
        "SetUserShipName": EventCategory.SHIP,
        "ShipLocker": EventCategory.SHIP,
        "ShipRedeemed": EventCategory.SHIP,
        "ShipyardRedeem": EventCategory.SHIP,
        "ModuleInfo": EventCategory.SHIP,
        "StoredModules": EventCategory.SHIP,
        
        # Squadron events
        "SquadronCreated": EventCategory.SQUADRON,
        "SquadronStartup": EventCategory.SQUADRON,
        "WingAdd": EventCategory.SQUADRON,
        "WingJoin": EventCategory.SQUADRON,
        "WingLeave": EventCategory.SQUADRON,
        "WingInvite": EventCategory.SQUADRON,
        
        # Crew events
        "CrewAssign": EventCategory.CREW,
        "CrewFire": EventCategory.CREW,
        "CrewHire": EventCategory.CREW,
        "CrewLaunchFighter": EventCategory.CREW,
        "CrewMemberJoins": EventCategory.CREW,
        "CrewMemberQuits": EventCategory.CREW,
        "CrewMemberRoleChange": EventCategory.CREW,
        "JoinACrew": EventCategory.CREW,
        "QuitACrew": EventCategory.CREW,
        "KickCrewMember": EventCategory.CREW,
        "ChangeCrewRole": EventCategory.CREW,
        "EndCrewSession": EventCategory.CREW,
        "NpcCrewPaidWage": EventCategory.CREW,
        
        # Passenger events
        "PassengerManifest": EventCategory.PASSENGER,
        "Passengers": EventCategory.PASSENGER,
        
        # Powerplay events
        "PowerplayCollect": EventCategory.POWERPLAY,
        "PowerplayDefect": EventCategory.POWERPLAY,
        "PowerplayDeliver": EventCategory.POWERPLAY,
        "PowerplayFastTrack": EventCategory.POWERPLAY,
        "PowerplayJoin": EventCategory.POWERPLAY,
        "PowerplayLeave": EventCategory.POWERPLAY,
        "PowerplaySalary": EventCategory.POWERPLAY,
        "PowerplayVote": EventCategory.POWERPLAY,
        "PowerplayVoucher": EventCategory.POWERPLAY,
        "Powerplay": EventCategory.POWERPLAY,
        
        # Fleet Carrier events
        "CarrierBuy": EventCategory.CARRIER,
        "CarrierStats": EventCategory.CARRIER,
        "CarrierJump": EventCategory.CARRIER,
        "CarrierDecommission": EventCategory.CARRIER,
        "CarrierCancelDecommission": EventCategory.CARRIER,
        "CarrierBankTransfer": EventCategory.CARRIER,
        "CarrierDepositFuel": EventCategory.CARRIER,
        "CarrierCrewServices": EventCategory.CARRIER,
        "CarrierFinance": EventCategory.CARRIER,
        "CarrierShipPack": EventCategory.CARRIER,
        "CarrierModulePack": EventCategory.CARRIER,
        "CarrierTradeOrder": EventCategory.CARRIER,
        "CarrierDockingPermission": EventCategory.CARRIER,
        "CarrierNameChange": EventCategory.CARRIER,
        "CarrierJumpRequest": EventCategory.CARRIER,
        "CarrierJumpCancelled": EventCategory.CARRIER,
        "CarrierLocation": EventCategory.CARRIER,
        
        # Social events
        "Friends": EventCategory.SOCIAL,
        "ReceiveText": EventCategory.SOCIAL,
        "SendText": EventCategory.SOCIAL,
        "Promotion": EventCategory.SOCIAL,
        
        # Suit/Odyssey events
        "SuitPurchased": EventCategory.SUIT,
        "SuitLoadout": EventCategory.SUIT,
        "LoadoutEquipModule": EventCategory.SUIT,
        "LoadoutRemoveModule": EventCategory.SUIT,
        "UseConsumable": EventCategory.SUIT,
        "BackpackChange": EventCategory.SUIT,
        "BookDropship": EventCategory.SUIT,
        "CancelDropship": EventCategory.SUIT,
        "CollectItems": EventCategory.SUIT,
        "Disembark": EventCategory.SUIT,
        "Embark": EventCategory.SUIT,
        "FCMaterials": EventCategory.SUIT,
        "TradeMicroResources": EventCategory.SUIT,
        "TransferMicroResources": EventCategory.SUIT,
        "UpgradeWeapon": EventCategory.SUIT,
        "UpgradeSuit": EventCategory.SUIT,
        "Backpack": EventCategory.SUIT,
        "ReservoirReplenished": EventCategory.SUIT,
        
        # Other/Unknown events - ensure this category has at least one mapping
        "Unknown": EventCategory.OTHER,
        "CommitCrime": EventCategory.OTHER,
        "CrimeVictim": EventCategory.OTHER,
        "Materials": EventCategory.OTHER,
    }
    
    def __init__(self):
        """Initialize the event processor."""
        self.unknown_events = set()
    
    def process_event(self, event: Dict[str, Any]) -> ProcessedEvent:
        """
        Process a journal event and extract key information.
        
        Args:
            event: Raw journal event dictionary
            
        Returns:
            ProcessedEvent with categorization and summary
        """
        # Extract basic info - handle None event type
        event_type = event.get("event") or "Unknown"
        timestamp = self._parse_timestamp(event.get("timestamp", ""))
        
        # Validate event
        validation_errors = self._validate_event(event)
        is_valid = len(validation_errors) == 0
        
        # Force invalid events to be classified as "Unknown"
        if not is_valid:
            event_type = "Unknown"
        
        # Categorize event
        category = self._categorize_event(event_type)
        
        # Extract key data
        key_data = self._extract_key_data(event, event_type)
        
        # Generate summary
        summary = self._generate_summary(event, event_type, key_data)
        
        # Log unknown events
        if category == EventCategory.OTHER and event_type not in self.unknown_events:
            self.unknown_events.add(event_type)
            logger.debug(f"Unknown event type encountered: {event_type}")
        
        return ProcessedEvent(
            raw_event=event,
            event_type=event_type,
            timestamp=timestamp,
            category=category,
            summary=summary,
            key_data=key_data,
            is_valid=is_valid,
            validation_errors=validation_errors
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse timestamp string to datetime object.
        
        Args:
            timestamp_str: ISO format timestamp string
            
        Returns:
            Parsed datetime object (timezone-aware)
        """
        if not timestamp_str:
            return datetime.now(timezone.utc)
        
        try:
            # Handle both with and without timezone
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            
            # Parse and ensure timezone-aware
            dt = datetime.fromisoformat(timestamp_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse timestamp: {timestamp_str}")
            return datetime.now(timezone.utc)
    
    def _validate_event(self, event: Dict[str, Any]) -> List[str]:
        """
        Validate event structure and required fields.
        
        Args:
            event: Event dictionary to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check required fields existence and validity
        if "event" not in event:
            errors.append("Missing required field: 'event'")
        elif event["event"] is None or event["event"] == "":
            errors.append("Event field cannot be None or empty string")
        elif not isinstance(event["event"], str):
            errors.append(f"Event field must be string, got {type(event['event']).__name__}")
        
        if "timestamp" not in event:
            errors.append("Missing required field: 'timestamp'")
        elif event["timestamp"] is None or event["timestamp"] == "":
            errors.append("Timestamp field cannot be None or empty string")
        else:
            # Validate timestamp format
            try:
                self._parse_timestamp(event["timestamp"])
            except Exception:
                errors.append(f"Invalid timestamp format: {event.get('timestamp')}")
        
        return errors
    
    def _categorize_event(self, event_type: str) -> EventCategory:
        """
        Categorize an event based on its type.
        
        Args:
            event_type: Event type string
            
        Returns:
            Event category
        """
        return self.EVENT_CATEGORIES.get(event_type, EventCategory.OTHER)
    
    def _extract_key_data(self, event: Dict[str, Any], event_type: str) -> Dict[str, Any]:
        """
        Extract key data fields based on event type.
        
        Args:
            event: Raw event dictionary
            event_type: Event type string
            
        Returns:
            Dictionary of extracted key data
        """
        key_data = {}
        
        # Navigation events
        if event_type == "FSDJump":
            key_data["system"] = event.get("StarSystem")
            key_data["distance"] = event.get("JumpDist")
            key_data["fuel_used"] = event.get("FuelUsed")
            key_data["fuel_level"] = event.get("FuelLevel")
            
        elif event_type == "Docked":
            key_data["station"] = event.get("StationName")
            key_data["system"] = event.get("StarSystem")
            key_data["station_type"] = event.get("StationType")
            
        elif event_type == "Location":
            key_data["system"] = event.get("StarSystem")
            key_data["body"] = event.get("Body")
            key_data["docked"] = event.get("Docked", False)
            key_data["station"] = event.get("StationName")
            
        # Exploration events
        elif event_type == "Scan":
            key_data["body_name"] = event.get("BodyName")
            key_data["body_type"] = event.get("PlanetClass") or event.get("StarType")
            key_data["distance"] = event.get("DistanceFromArrivalLS")
            key_data["terraformable"] = event.get("TerraformState") == "Terraformable"
            key_data["landable"] = event.get("Landable", False)
            
        elif event_type in ["SellExplorationData", "MultiSellExplorationData"]:
            key_data["value"] = event.get("TotalEarnings")
            key_data["bonus"] = event.get("Bonus", 0)
            key_data["systems"] = event.get("Systems", [])
            key_data["discovered"] = event.get("Discovered", 0)
            
        # Combat events
        elif event_type == "Bounty":
            key_data["target"] = event.get("Target")
            key_data["faction"] = event.get("VictimFaction")
            key_data["reward"] = event.get("TotalReward")
            
        elif event_type == "Died":
            key_data["killer"] = event.get("KillerName")
            key_data["killer_ship"] = event.get("KillerShip")
            key_data["combat_rank"] = event.get("CombatRank")
            
        # Trading events
        elif event_type in ["MarketBuy", "MarketSell"]:
            key_data["commodity"] = event.get("Type")
            key_data["count"] = event.get("Count")
            key_data["price"] = event.get("BuyPrice") or event.get("SellPrice")
            key_data["total"] = event.get("TotalCost") or event.get("TotalSale")
            
        # Mission events
        elif event_type == "MissionAccepted":
            key_data["name"] = event.get("Name")
            key_data["faction"] = event.get("Faction")
            key_data["reward"] = event.get("Reward")
            key_data["expiry"] = event.get("Expiry")
            
        elif event_type == "MissionCompleted":
            key_data["name"] = event.get("Name")
            key_data["faction"] = event.get("Faction")
            key_data["reward"] = event.get("Reward")
            
        # Ship events
        elif event_type in ["ShipyardBuy", "ShipyardNew"]:
            key_data["ship"] = event.get("ShipType")
            key_data["price"] = event.get("ShipPrice")
            
        elif event_type == "Loadout":
            key_data["ship"] = event.get("Ship")
            key_data["ship_name"] = event.get("ShipName")
            key_data["ship_id"] = event.get("ShipIdent")
            key_data["value"] = event.get("HullValue")
            
        # Engineering events
        elif event_type == "EngineerCraft":
            key_data["engineer"] = event.get("Engineer")
            key_data["module"] = event.get("Slot")
            key_data["blueprint"] = event.get("BlueprintName")
            key_data["level"] = event.get("Level")
            
        # Mining events
        elif event_type == "MiningRefined":
            key_data["material"] = event.get("Type")

        # Trading events - CargoTransfer
        elif event_type == "CargoTransfer":
            # Extract transfers from the Transfers array
            transfers = []
            for transfer in event.get("Transfers", []):
                transfers.append({
                    "commodity": transfer.get("Type", "").lower(),
                    "commodity_localized": transfer.get("Type_Localised", ""),
                    "count": transfer.get("Count", 0),
                    "direction": transfer.get("Direction", "")
                })
            key_data["transfers"] = transfers

        # System events
        elif event_type == "LoadGame":
            key_data["commander"] = event.get("Commander")
            key_data["ship_type"] = event.get("Ship")
            key_data["ship_name"] = event.get("ShipName")
            key_data["ship_id"] = event.get("ShipIdent")
            key_data["credits"] = event.get("Credits")
            key_data["fuel_level"] = event.get("FuelLevel")
            key_data["fuel_capacity"] = event.get("FuelCapacity")
            key_data["game_mode"] = event.get("GameMode")
            key_data["loan"] = event.get("Loan")

        return key_data
    
    def _generate_summary(self, event: Dict[str, Any], event_type: str, 
                         key_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of the event.
        
        Args:
            event: Raw event dictionary
            event_type: Event type string
            key_data: Extracted key data
            
        Returns:
            Human-readable summary string
        """
        # Navigation summaries
        if event_type == "FSDJump":
            system = key_data.get("system", "unknown system")
            distance = key_data.get("distance")
            if distance is not None:
                return f"Jumped to {system} ({distance:.2f}ly)"
            else:
                return f"Jumped to {system}"
            
        elif event_type == "Docked":
            station = key_data.get("station", "unknown station")
            system = key_data.get("system", "unknown system")
            return f"Docked at {station} in {system}"
            
        elif event_type == "Undocked":
            station = event.get("StationName", "station")
            return f"Undocked from {station}"
            
        # Exploration summaries
        elif event_type == "Scan":
            body = key_data.get("body_name", "unknown body")
            body_type = key_data.get("body_type", "unknown type")
            extras = []
            if key_data.get("terraformable"):
                extras.append("terraformable")
            if key_data.get("landable"):
                extras.append("landable")
            extra_str = f" ({', '.join(extras)})" if extras else ""
            return f"Scanned {body} - {body_type}{extra_str}"
            
        elif event_type in ["SellExplorationData", "MultiSellExplorationData"]:
            value = key_data.get("value") or 0
            return f"Sold exploration data for {value:,} credits"
            
        # Combat summaries
        elif event_type == "Bounty":
            target = key_data.get("target", "target")
            reward = key_data.get("reward") or 0
            return f"Collected bounty on {target} for {reward:,} credits"
            
        elif event_type == "Died":
            killer = key_data.get("killer", "unknown")
            killer_ship = key_data.get("killer_ship", "")
            ship_str = f" flying {killer_ship}" if killer_ship else ""
            return f"Destroyed by {killer}{ship_str}"
            
        # Trading summaries
        elif event_type == "MarketBuy":
            commodity = key_data.get("commodity", "commodity")
            count = key_data.get("count") or 0
            total = key_data.get("total") or 0
            return f"Bought {count}t of {commodity} for {total:,} credits"
            
        elif event_type == "MarketSell":
            commodity = key_data.get("commodity", "commodity")
            count = key_data.get("count") or 0
            total = key_data.get("total") or 0
            return f"Sold {count}t of {commodity} for {total:,} credits"

        # CargoTransfer summaries
        elif event_type == "CargoTransfer":
            transfers = key_data.get("transfers", [])
            if not transfers:
                return "Cargo transfer occurred"

            # Single transfer - detailed summary
            if len(transfers) == 1:
                transfer = transfers[0]
                commodity = transfer.get("commodity_localized") or transfer.get("commodity", "cargo")
                count = transfer.get("count", 0)
                direction = transfer.get("direction", "")

                if direction == "tocarrier":
                    return f"Transferred {count}t {commodity} to carrier"
                elif direction == "toship":
                    return f"Transferred {count}t {commodity} from carrier to ship"
                else:
                    return f"Transferred {count}t {commodity}"

            # Multiple transfers - summary
            else:
                total_count = sum(t.get("count", 0) for t in transfers)
                direction = transfers[0].get("direction", "")

                if direction == "tocarrier":
                    return f"Transferred {len(transfers)} items ({total_count}t total) to carrier"
                elif direction == "toship":
                    return f"Transferred {len(transfers)} items ({total_count}t total) from carrier to ship"
                else:
                    return f"Transferred {len(transfers)} items ({total_count}t total)"

        # Mission summaries
        elif event_type == "MissionAccepted":
            name = key_data.get("name", "mission")
            faction = key_data.get("faction", "faction")
            reward = key_data.get("reward") or 0
            return f"Accepted mission from {faction} for {reward:,} credits"
            
        elif event_type == "MissionCompleted":
            faction = key_data.get("faction", "faction")
            reward = key_data.get("reward") or 0
            return f"Completed mission for {faction}, earned {reward:,} credits"
            
        # Ship summaries
        elif event_type in ["ShipyardBuy", "ShipyardNew"]:
            ship = key_data.get("ship", "ship")
            price = key_data.get("price") or 0
            return f"Purchased {ship} for {price:,} credits"
            
        elif event_type == "Loadout":
            ship = key_data.get("ship", "ship")
            name = key_data.get("ship_name", "")
            name_str = f" '{name}'" if name else ""
            return f"Loadout for {ship}{name_str}"
            
        # Engineering summaries
        elif event_type == "EngineerCraft":
            engineer = key_data.get("engineer", "engineer")
            module = key_data.get("module", "module")
            blueprint = key_data.get("blueprint", "modification")
            level = key_data.get("level") or 0
            return f"{engineer} applied {blueprint} level {level} to {module}"
            
        # System events
        elif event_type == "LoadGame":
            commander = event.get("Commander", "Commander")
            ship = event.get("Ship", "ship")
            return f"{commander} loaded game in {ship}"
            
        elif event_type == "Location":
            system = key_data.get("system", "unknown system")
            if key_data.get("docked"):
                station = key_data.get("station", "station")
                return f"Located at {station} in {system}"
            else:
                return f"Located in {system}"
        
        # Default summary
        return f"{event_type} event occurred"
    
    def get_unknown_events(self) -> List[str]:
        """
        Get list of unknown event types encountered.
        
        Returns:
            List of unknown event type strings
        """
        return sorted(list(self.unknown_events))
    
    def clear_unknown_events(self):
        """Clear the list of unknown events."""
        self.unknown_events.clear()


def categorize_events(events: List[Dict[str, Any]]) -> Dict[EventCategory, List[ProcessedEvent]]:
    """
    Categorize a list of events by their category.
    
    Args:
        events: List of raw event dictionaries
        
    Returns:
        Dictionary mapping categories to lists of processed events
    """
    processor = EventProcessor()
    categorized = {category: [] for category in EventCategory}
    
    for event in events:
        processed = processor.process_event(event)
        categorized[processed.category].append(processed)
    
    return categorized


def summarize_events(events: List[Dict[str, Any]], max_summaries: int = 10) -> List[str]:
    """
    Generate summaries for a list of events.
    
    Args:
        events: List of raw event dictionaries
        max_summaries: Maximum number of summaries to generate
        
    Returns:
        List of event summary strings
    """
    processor = EventProcessor()
    summaries = []
    
    for event in events[:max_summaries]:
        processed = processor.process_event(event)
        summaries.append(f"[{processed.timestamp.strftime('%H:%M:%S')}] {processed.summary}")
    
    return summaries


def get_event_statistics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate statistics about a collection of events.
    
    Args:
        events: List of raw event dictionaries
        
    Returns:
        Dictionary with event statistics
    """
    processor = EventProcessor()
    stats = {
        "total_events": len(events),
        "categories": {},
        "event_types": {},
        "invalid_events": 0,
        "unknown_events": [],
        "time_range": None
    }
    
    if not events:
        return stats
    
    processed_events = []
    for event in events:
        processed = processor.process_event(event)
        processed_events.append(processed)
        
        # Count by category
        category_name = processed.category.value
        stats["categories"][category_name] = stats["categories"].get(category_name, 0) + 1
        
        # Count by event type
        stats["event_types"][processed.event_type] = stats["event_types"].get(processed.event_type, 0) + 1
        
        # Count invalid events
        if not processed.is_valid:
            stats["invalid_events"] += 1
    
    # Get time range - normalize all timestamps to remove timezone info for consistency
    if processed_events:
        timestamps = [e.timestamp.replace(tzinfo=None) for e in processed_events]
        stats["time_range"] = {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat()
        }
    
    # Get unknown events
    stats["unknown_events"] = processor.get_unknown_events()
    
    return stats
