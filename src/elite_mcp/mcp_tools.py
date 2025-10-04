"""
Elite Dangerous MCP Tools - Core functionality for AI assistant integration.

This module provides comprehensive MCP tools for querying and analyzing Elite Dangerous
journal data, including location tracking, activity summaries, and detailed analytics.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Set
from enum import Enum

try:
    from ..journal.events import EventCategory, ProcessedEvent
    from ..utils.data_store import EventFilter, QuerySortOrder, GameState
except ImportError:
    from src.journal.events import EventCategory, ProcessedEvent
    from src.utils.data_store import EventFilter, QuerySortOrder, GameState

logger = logging.getLogger(__name__)


class ActivityType(Enum):
    """Types of player activities for summary generation."""
    EXPLORATION = "exploration"
    TRADING = "trading"
    COMBAT = "combat"
    MINING = "mining"
    MISSIONS = "missions"
    ENGINEERING = "engineering"
    PASSENGER = "passenger"
    FLEET_CARRIER = "fleet_carrier"


class MCPTools:
    """
    Core MCP tools for Elite Dangerous data access and analysis.
    
    Provides comprehensive tools for:
    - Current game state queries
    - Event searching and filtering
    - Activity summaries and analytics
    - Journey tracking and navigation history
    - Performance metrics and statistics
    """
    
    def __init__(self, data_store):
        """
        Initialize MCP tools with data store reference.
        
        Args:
            data_store: Reference to the global data store
        """
        self.data_store = data_store
        logger.info("MCP Tools initialized")
    
    # ==================== Location and Status Tools ====================
    
    async def get_current_location(self) -> Dict[str, Any]:
        """
        Get comprehensive current location information.
        
        Returns:
            Dict containing current system, station, coordinates, and nearby info
        """
        try:
            game_state = self.data_store.get_game_state()
            
            # Get recent location events for additional context
            location_events = self.data_store.get_events_by_type("Location", limit=1)
            recent_jumps = self.data_store.get_events_by_type("FSDJump", limit=5)
            
            response = {
                "current_system": game_state.current_system or "Unknown",
                "current_station": game_state.current_station,
                "current_body": game_state.current_body,
                "coordinates": game_state.coordinates,
                "docked": game_state.docked,
                "landed": game_state.landed,
                "in_supercruise": game_state.supercruise,
                "recent_systems": []
            }
            
            # Add recent system visits
            for jump in recent_jumps:
                system_info = {
                    "system": jump.key_data.get("system"),
                    "timestamp": jump.timestamp.isoformat(),
                    "distance": jump.key_data.get("distance")
                }
                response["recent_systems"].append(system_info)
            
            # Add additional location context if available
            if location_events:
                latest = location_events[-1]
                response["location_timestamp"] = latest.timestamp.isoformat()
                response["population"] = latest.raw_event.get("Population", 0)
                response["allegiance"] = latest.raw_event.get("Allegiance")
                response["economy"] = latest.raw_event.get("Economy")
                response["government"] = latest.raw_event.get("Government")
                response["security"] = latest.raw_event.get("Security")
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting current location: {e}")
            return {"error": str(e)}
    
    async def get_ship_status(self) -> Dict[str, Any]:
        """
        Get comprehensive ship status and configuration.
        
        Returns:
            Dict containing ship type, name, modules, and condition
        """
        try:
            game_state = self.data_store.get_game_state()
            
            # Get recent ship-related events
            loadout_events = self.data_store.get_events_by_type("Loadout", limit=1)
            repair_events = self.data_store.get_events_by_type("Repair", limit=5)
            refuel_events = self.data_store.get_events_by_type("RefuelAll", limit=1)
            
            response = {
                "ship_type": game_state.current_ship or "Unknown",
                "ship_name": game_state.ship_name,
                "ship_id": game_state.ship_id,
                "modules": game_state.ship_modules,
                "status": {
                    "docked": game_state.docked,
                    "landed": game_state.landed,
                    "in_srv": game_state.in_srv,
                    "in_fighter": game_state.in_fighter,
                    "low_fuel": game_state.low_fuel,
                    "overheating": game_state.overheating,
                    "in_danger": game_state.is_in_danger,
                    "being_interdicted": game_state.being_interdicted
                },
                "recent_maintenance": []
            }
            
            # Add loadout details if available
            if loadout_events:
                latest = loadout_events[-1]
                response["hull_value"] = latest.raw_event.get("HullValue", 0)
                response["modules_value"] = latest.raw_event.get("ModulesValue", 0)
                response["rebuy"] = latest.raw_event.get("Rebuy", 0)
            
            # Add recent maintenance
            for repair in repair_events:
                response["recent_maintenance"].append({
                    "type": "repair",
                    "timestamp": repair.timestamp.isoformat(),
                    "cost": repair.raw_event.get("Cost", 0)
                })
            
            for refuel in refuel_events:
                response["recent_maintenance"].append({
                    "type": "refuel",
                    "timestamp": refuel.timestamp.isoformat(),
                    "amount": refuel.raw_event.get("Amount", 0),
                    "cost": refuel.raw_event.get("Cost", 0)
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting ship status: {e}")
            return {"error": str(e)}
    
    # ==================== Event Search and Filter Tools ====================
    
    async def search_events(
        self,
        event_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        time_range_minutes: Optional[int] = None,
        system_names: Optional[List[str]] = None,
        contains_text: Optional[str] = None,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Search for events with flexible filtering criteria.
        
        Args:
            event_types: List of event types to filter
            categories: List of event categories to filter
            time_range_minutes: Time range in minutes from now
            system_names: Filter by system names
            contains_text: Text search in event data
            max_results: Maximum number of results
            
        Returns:
            Dict containing matching events and metadata
        """
        try:
            # Build filter criteria
            filter_criteria = EventFilter(max_results=max_results)
            
            if event_types:
                filter_criteria.event_types = set(event_types)
            
            if categories:
                # Convert string categories to EventCategory enums
                category_enums = []
                for cat_str in categories:
                    try:
                        category_enums.append(EventCategory(cat_str.lower()))
                    except ValueError:
                        logger.warning(f"Invalid category: {cat_str}")
                if category_enums:
                    filter_criteria.categories = set(category_enums)
            
            if time_range_minutes:
                filter_criteria.start_time = datetime.now(timezone.utc) - timedelta(minutes=time_range_minutes)
            
            if system_names:
                filter_criteria.system_names = set(system_names)
            
            if contains_text:
                filter_criteria.contains_text = contains_text
            
            # Execute query
            events = self.data_store.query_events(
                filter_criteria=filter_criteria,
                sort_order=QuerySortOrder.NEWEST_FIRST
            )
            
            # Format response
            response = {
                "total_found": len(events),
                "search_criteria": {
                    "event_types": event_types,
                    "categories": categories,
                    "time_range_minutes": time_range_minutes,
                    "system_names": system_names,
                    "contains_text": contains_text
                },
                "events": []
            }
            
            for event in events:
                response["events"].append({
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "category": event.category.value,
                    "summary": event.summary,
                    "key_data": event.key_data,
                    "is_valid": event.is_valid
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return {"error": str(e)}
    
    # ==================== Activity Summary Tools ====================
    
    async def get_activity_summary(
        self,
        activity_type: str,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get comprehensive summary of specific activity type.
        
        Args:
            activity_type: Type of activity (exploration, trading, combat, etc.)
            time_range_hours: Time range to analyze
            
        Returns:
            Dict containing activity statistics and highlights
        """
        try:
            # Validate activity type
            try:
                activity = ActivityType(activity_type.lower())
            except ValueError:
                return {"error": f"Invalid activity type: {activity_type}"}
            
            # Get events for time range
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
            
            if activity == ActivityType.EXPLORATION:
                return await self._get_exploration_summary(cutoff_time)
            elif activity == ActivityType.TRADING:
                return await self._get_trading_summary(cutoff_time)
            elif activity == ActivityType.COMBAT:
                return await self._get_combat_summary(cutoff_time)
            elif activity == ActivityType.MINING:
                return await self._get_mining_summary(cutoff_time)
            elif activity == ActivityType.MISSIONS:
                return await self._get_mission_summary(cutoff_time)
            elif activity == ActivityType.ENGINEERING:
                return await self._get_engineering_summary(cutoff_time)
            else:
                return {"error": f"Activity type {activity_type} not yet implemented"}
                
        except Exception as e:
            logger.error(f"Error getting activity summary: {e}")
            return {"error": str(e)}
    
    async def _get_exploration_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Generate exploration activity summary."""
        filter_criteria = EventFilter(
            categories={EventCategory.EXPLORATION},
            start_time=cutoff_time
        )
        
        events = self.data_store.query_events(filter_criteria)
        
        summary = {
            "activity_type": "exploration",
            "total_events": len(events),
            "bodies_scanned": 0,
            "valuable_bodies": [],
            "systems_discovered": set(),
            "exploration_value": 0,
            "first_discoveries": 0,
            "terraformable_found": 0,
            "detailed_scans": []
        }
        
        for event in events:
            if event.event_type == "Scan":
                summary["bodies_scanned"] += 1
                
                # Check for valuable bodies
                if event.key_data.get("terraformable"):
                    summary["terraformable_found"] += 1
                    summary["valuable_bodies"].append({
                        "name": event.key_data.get("body_name"),
                        "type": event.key_data.get("body_type"),
                        "terraformable": True,
                        "timestamp": event.timestamp.isoformat()
                    })
                
                # Track systems
                system = event.raw_event.get("StarSystem")
                if system:
                    summary["systems_discovered"].add(system)
                
                # Add scan details
                summary["detailed_scans"].append({
                    "body": event.key_data.get("body_name"),
                    "type": event.key_data.get("body_type"),
                    "distance": event.key_data.get("distance"),
                    "landable": event.key_data.get("landable"),
                    "timestamp": event.timestamp.isoformat()
                })
                
            elif event.event_type in ["SellExplorationData", "MultiSellExplorationData"]:
                summary["exploration_value"] += event.key_data.get("value", 0)
                summary["first_discoveries"] += event.key_data.get("discovered", 0)
        
        # Convert set to list for JSON serialization
        summary["systems_discovered"] = list(summary["systems_discovered"])
        
        # Limit detailed scans to most recent 20
        summary["detailed_scans"] = summary["detailed_scans"][:20]
        
        return summary
    
    async def _get_trading_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Generate trading activity summary."""
        filter_criteria = EventFilter(
            categories={EventCategory.TRADING},
            start_time=cutoff_time
        )
        
        events = self.data_store.query_events(filter_criteria)
        
        summary = {
            "activity_type": "trading",
            "total_events": len(events),
            "total_profit": 0,
            "total_loss": 0,
            "commodities_traded": {},
            "stations_visited": set(),
            "best_trades": [],
            "recent_transactions": []
        }
        
        for event in events:
            if event.event_type == "MarketBuy":
                commodity = event.key_data.get("commodity", "Unknown")
                cost = event.key_data.get("total", 0)
                
                if commodity not in summary["commodities_traded"]:
                    summary["commodities_traded"][commodity] = {
                        "bought": 0,
                        "sold": 0,
                        "spent": 0,
                        "earned": 0
                    }
                
                summary["commodities_traded"][commodity]["bought"] += event.key_data.get("count", 0)
                summary["commodities_traded"][commodity]["spent"] += cost
                summary["total_loss"] += cost
                
            elif event.event_type == "MarketSell":
                commodity = event.key_data.get("commodity", "Unknown")
                revenue = event.key_data.get("total", 0)
                
                if commodity not in summary["commodities_traded"]:
                    summary["commodities_traded"][commodity] = {
                        "bought": 0,
                        "sold": 0,
                        "spent": 0,
                        "earned": 0
                    }
                
                summary["commodities_traded"][commodity]["sold"] += event.key_data.get("count", 0)
                summary["commodities_traded"][commodity]["earned"] += revenue
                summary["total_profit"] += revenue
                
                # Track best trades
                summary["best_trades"].append({
                    "commodity": commodity,
                    "amount": event.key_data.get("count", 0),
                    "revenue": revenue,
                    "timestamp": event.timestamp.isoformat()
                })
            
            # Track recent transactions
            summary["recent_transactions"].append({
                "type": event.event_type,
                "commodity": event.key_data.get("commodity"),
                "amount": event.key_data.get("count"),
                "value": event.key_data.get("total"),
                "timestamp": event.timestamp.isoformat()
            })
            
            # Track stations
            station = event.raw_event.get("StationName")
            if station:
                summary["stations_visited"].add(station)
        
        # Calculate net profit
        summary["net_profit"] = summary["total_profit"] - summary["total_loss"]
        
        # Sort and limit best trades
        summary["best_trades"].sort(key=lambda x: x["revenue"], reverse=True)
        summary["best_trades"] = summary["best_trades"][:10]
        
        # Limit recent transactions
        summary["recent_transactions"] = summary["recent_transactions"][:20]
        
        # Convert set to list
        summary["stations_visited"] = list(summary["stations_visited"])
        
        return summary
    
    async def _get_combat_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Generate combat activity summary."""
        filter_criteria = EventFilter(
            categories={EventCategory.COMBAT},
            start_time=cutoff_time
        )
        
        events = self.data_store.query_events(filter_criteria)
        
        summary = {
            "activity_type": "combat",
            "total_events": len(events),
            "bounties_collected": 0,
            "total_bounty_value": 0,
            "combat_bonds": 0,
            "total_bond_value": 0,
            "kills": [],
            "deaths": 0,
            "interdictions_escaped": 0,
            "interdictions_won": 0,
            "combat_zones": set(),
            "factions_fought": set()
        }
        
        for event in events:
            if event.event_type == "Bounty":
                summary["bounties_collected"] += 1
                summary["total_bounty_value"] += event.key_data.get("reward", 0)
                
                # Track kills
                summary["kills"].append({
                    "target": event.key_data.get("target"),
                    "faction": event.key_data.get("faction"),
                    "reward": event.key_data.get("reward"),
                    "timestamp": event.timestamp.isoformat()
                })
                
                # Track factions
                faction = event.key_data.get("faction")
                if faction:
                    summary["factions_fought"].add(faction)
                    
            elif event.event_type == "FactionKillBond":
                summary["combat_bonds"] += 1
                summary["total_bond_value"] += event.raw_event.get("Reward", 0)
                
            elif event.event_type == "Died":
                summary["deaths"] += 1
                
            elif event.event_type == "EscapeInterdiction":
                summary["interdictions_escaped"] += 1
                
            elif event.event_type == "Interdiction":
                if event.raw_event.get("Success"):
                    summary["interdictions_won"] += 1
        
        # Convert sets to lists
        summary["combat_zones"] = list(summary["combat_zones"])
        summary["factions_fought"] = list(summary["factions_fought"])
        
        # Limit kills list
        summary["kills"] = summary["kills"][:20]
        
        return summary
    
    async def _get_mining_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Generate mining activity summary."""
        # Get mining events
        mining_filter = EventFilter(
            categories={EventCategory.MINING},
            start_time=cutoff_time
        )
        mining_events = self.data_store.query_events(mining_filter)

        # Also get material collection events that might be mining-related
        material_filter = EventFilter(
            event_types={"MaterialCollected"},
            start_time=cutoff_time
        )
        material_events = self.data_store.query_events(material_filter)

        # Combine events for comprehensive analysis
        events = mining_events + material_events
        
        summary = {
            "activity_type": "mining",
            "total_events": len(events),
            # Separate commodities (sellable cargo from refinery) from materials (engineering resources)
            "commodities_refined": {},  # From MiningRefined events - what users want to see
            "raw_materials_collected": {},  # From MaterialCollected events - for engineering
            "materials_mined": {},  # Legacy field, now populated from Mined events only
            "asteroids_cracked": 0,
            "asteroids_prospected": 0,
            "refineries_used": set(),
            "mining_locations": set(),
            "recent_mining": []
        }
        
        for event in events:
            if event.event_type == "Mined":
                # Handle actual Elite Dangerous mining events
                material = event.raw_event.get("Type", "Unknown")
                count = event.raw_event.get("Count", 1)
                if material not in summary["materials_mined"]:
                    summary["materials_mined"][material] = 0
                summary["materials_mined"][material] += count

                summary["recent_mining"].append({
                    "type": "mined",
                    "material": material,
                    "count": count,
                    "timestamp": event.timestamp.isoformat()
                })

            elif event.event_type == "AsteroidCracked":
                summary["asteroids_cracked"] += 1

                # Track cracked asteroids in recent mining
                summary["recent_mining"].append({
                    "type": "cracked",
                    "body": event.raw_event.get("Body"),
                    "timestamp": event.timestamp.isoformat()
                })

            elif event.event_type == "ProspectedAsteroid":
                summary["asteroids_prospected"] += 1

                summary["recent_mining"].append({
                    "type": "prospected",
                    "content": event.raw_event.get("Content"),
                    "remaining": event.raw_event.get("Remaining"),
                    "timestamp": event.timestamp.isoformat()
                })

            elif event.event_type == "RefineryOpen":
                # Track refinery usage
                refinery = event.raw_event.get("Name", "Unknown Refinery")
                summary["refineries_used"].add(refinery)

            elif event.event_type == "MiningRefined":
                # Handle refined commodities - sellable cargo from refinery (what users want to see)
                commodity = event.raw_event.get("Type", "Unknown")
                # MiningRefined events in Elite Dangerous don't have Count field, they represent 1 unit
                count = 1

                if commodity not in summary["commodities_refined"]:
                    summary["commodities_refined"][commodity] = 0
                summary["commodities_refined"][commodity] += count

                summary["recent_mining"].append({
                    "type": "refined",
                    "commodity": commodity,
                    "count": count,
                    "timestamp": event.timestamp.isoformat()
                })

            elif event.event_type == "MaterialCollected":
                # Track raw materials collected (for engineering, not sellable)
                material = event.raw_event.get("Name", "Unknown")
                count = event.raw_event.get("Count", 1)
                category = event.raw_event.get("Category", "")

                # Store raw materials separately from commodities
                if material not in summary["raw_materials_collected"]:
                    summary["raw_materials_collected"][material] = 0
                summary["raw_materials_collected"][material] += count

                summary["recent_mining"].append({
                    "type": "material_collected",
                    "material": material,
                    "count": count,
                    "category": category,
                    "timestamp": event.timestamp.isoformat()
                })
        
        # Convert sets to lists
        summary["refineries_used"] = list(summary["refineries_used"])
        summary["mining_locations"] = list(summary["mining_locations"])
        
        # Limit recent mining
        summary["recent_mining"] = summary["recent_mining"][:20]
        
        return summary
    
    async def _get_mission_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Generate mission activity summary."""
        filter_criteria = EventFilter(
            categories={EventCategory.MISSION},
            start_time=cutoff_time
        )
        
        events = self.data_store.query_events(filter_criteria)
        
        summary = {
            "activity_type": "missions",
            "total_events": len(events),
            "missions_accepted": 0,
            "missions_completed": 0,
            "missions_failed": 0,
            "missions_abandoned": 0,
            "total_rewards": 0,
            "factions_worked_for": set(),
            "active_missions": [],
            "completed_missions": []
        }
        
        active_missions = {}
        
        for event in events:
            if event.event_type == "MissionAccepted":
                summary["missions_accepted"] += 1
                mission_id = event.raw_event.get("MissionID")
                
                if mission_id:
                    active_missions[mission_id] = {
                        "name": event.key_data.get("name"),
                        "faction": event.key_data.get("faction"),
                        "reward": event.key_data.get("reward"),
                        "expiry": event.key_data.get("expiry"),
                        "accepted_at": event.timestamp.isoformat()
                    }
                
                faction = event.key_data.get("faction")
                if faction:
                    summary["factions_worked_for"].add(faction)
                    
            elif event.event_type == "MissionCompleted":
                summary["missions_completed"] += 1
                summary["total_rewards"] += event.key_data.get("reward", 0)
                
                mission_id = event.raw_event.get("MissionID")
                if mission_id and mission_id in active_missions:
                    mission_info = active_missions.pop(mission_id)
                    mission_info["completed_at"] = event.timestamp.isoformat()
                    summary["completed_missions"].append(mission_info)
                else:
                    summary["completed_missions"].append({
                        "name": event.key_data.get("name"),
                        "faction": event.key_data.get("faction"),
                        "reward": event.key_data.get("reward"),
                        "completed_at": event.timestamp.isoformat()
                    })
                    
            elif event.event_type == "MissionFailed":
                summary["missions_failed"] += 1
                mission_id = event.raw_event.get("MissionID")
                if mission_id and mission_id in active_missions:
                    active_missions.pop(mission_id)
                    
            elif event.event_type == "MissionAbandoned":
                summary["missions_abandoned"] += 1
                mission_id = event.raw_event.get("MissionID")
                if mission_id and mission_id in active_missions:
                    active_missions.pop(mission_id)
        
        # Add remaining active missions
        summary["active_missions"] = list(active_missions.values())
        
        # Convert sets to lists
        summary["factions_worked_for"] = list(summary["factions_worked_for"])
        
        # Limit completed missions
        summary["completed_missions"] = summary["completed_missions"][:20]
        
        return summary
    
    async def _get_engineering_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Generate engineering activity summary."""
        filter_criteria = EventFilter(
            categories={EventCategory.ENGINEERING},
            start_time=cutoff_time
        )
        
        events = self.data_store.query_events(filter_criteria)
        
        summary = {
            "activity_type": "engineering",
            "total_events": len(events),
            "modifications_applied": 0,
            "engineers_visited": set(),
            "modules_modified": {},
            "materials_contributed": 0,
            "recent_modifications": []
        }
        
        for event in events:
            if event.event_type == "EngineerCraft":
                summary["modifications_applied"] += 1
                
                engineer = event.key_data.get("engineer")
                if engineer:
                    summary["engineers_visited"].add(engineer)
                
                module = event.key_data.get("module", "Unknown")
                if module not in summary["modules_modified"]:
                    summary["modules_modified"][module] = []
                
                summary["modules_modified"][module].append({
                    "blueprint": event.key_data.get("blueprint"),
                    "level": event.key_data.get("level"),
                    "engineer": engineer,
                    "timestamp": event.timestamp.isoformat()
                })
                
                summary["recent_modifications"].append({
                    "module": module,
                    "blueprint": event.key_data.get("blueprint"),
                    "level": event.key_data.get("level"),
                    "engineer": engineer,
                    "timestamp": event.timestamp.isoformat()
                })
                
            elif event.event_type == "EngineerContribution":
                summary["materials_contributed"] += 1
        
        # Convert sets to lists
        summary["engineers_visited"] = list(summary["engineers_visited"])
        
        # Limit recent modifications
        summary["recent_modifications"] = summary["recent_modifications"][:20]
        
        return summary
    
    # ==================== Journey and Navigation Tools ====================
    
    async def get_journey_summary(
        self,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get comprehensive journey and navigation summary.
        
        Args:
            time_range_hours: Time range to analyze
            
        Returns:
            Dict containing journey statistics and route information
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
            
            filter_criteria = EventFilter(
                categories={EventCategory.NAVIGATION},
                start_time=cutoff_time
            )
            
            events = self.data_store.query_events(filter_criteria)
            
            summary = {
                "total_jumps": 0,
                "total_distance": 0,
                "fuel_used": 0,
                "systems_visited": [],
                "stations_docked": [],
                "bodies_landed": [],
                "route_map": [],
                "current_location": None
            }
            
            # Get current location
            game_state = self.data_store.get_game_state()
            summary["current_location"] = {
                "system": game_state.current_system,
                "station": game_state.current_station,
                "body": game_state.current_body,
                "docked": game_state.docked,
                "landed": game_state.landed
            }
            
            visited_systems = set()
            
            for event in events:
                if event.event_type == "FSDJump":
                    summary["total_jumps"] += 1
                    distance = event.key_data.get("distance", 0)
                    summary["total_distance"] += distance
                    summary["fuel_used"] += event.key_data.get("fuel_used", 0)
                    
                    system = event.key_data.get("system")
                    if system and system not in visited_systems:
                        visited_systems.add(system)
                        summary["systems_visited"].append({
                            "system": system,
                            "timestamp": event.timestamp.isoformat(),
                            "distance": distance
                        })
                    
                    # Add to route map
                    summary["route_map"].append({
                        "type": "jump",
                        "system": system,
                        "timestamp": event.timestamp.isoformat(),
                        "distance": distance
                    })
                    
                elif event.event_type == "Docked":
                    station = event.key_data.get("station")
                    system = event.key_data.get("system")
                    
                    summary["stations_docked"].append({
                        "station": station,
                        "system": system,
                        "station_type": event.key_data.get("station_type"),
                        "timestamp": event.timestamp.isoformat()
                    })
                    
                    summary["route_map"].append({
                        "type": "dock",
                        "station": station,
                        "system": system,
                        "timestamp": event.timestamp.isoformat()
                    })
                    
                elif event.event_type == "Touchdown":
                    body = event.raw_event.get("Body")
                    summary["bodies_landed"].append({
                        "body": body,
                        "timestamp": event.timestamp.isoformat()
                    })
                    
                    summary["route_map"].append({
                        "type": "landing",
                        "body": body,
                        "timestamp": event.timestamp.isoformat()
                    })
            
            # Calculate statistics
            summary["unique_systems"] = len(visited_systems)
            summary["average_jump_distance"] = (
                summary["total_distance"] / summary["total_jumps"] 
                if summary["total_jumps"] > 0 else 0
            )
            
            # Limit route map to last 50 events
            summary["route_map"] = summary["route_map"][-50:]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting journey summary: {e}")
            return {"error": str(e)}
    
    # ==================== Performance and Statistics Tools ====================
    
    async def get_performance_metrics(
        self,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics across all activities.
        
        Args:
            time_range_hours: Time range to analyze
            
        Returns:
            Dict containing performance metrics and efficiency ratings
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
            
            # Get all events in time range
            filter_criteria = EventFilter(start_time=cutoff_time)
            events = self.data_store.query_events(filter_criteria)
            
            # Initialize metrics
            metrics = {
                "time_range_hours": time_range_hours,
                "total_events": len(events),
                "credits_earned": 0,
                "credits_spent": 0,
                "net_profit": 0,
                "efficiency_metrics": {},
                "activity_breakdown": {},
                "peak_activity_times": [],
                "achievements": []
            }
            
            # Track activity by hour
            hourly_activity = {}
            
            # Process events for metrics
            for event in events:
                hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
                if hour_key not in hourly_activity:
                    hourly_activity[hour_key] = 0
                hourly_activity[hour_key] += 1
                
                # Track credits
                if event.event_type in ["MarketSell", "Bounty", "MissionCompleted", "SellExplorationData"]:
                    credits = (
                        event.key_data.get("total", 0) or 
                        event.key_data.get("reward", 0) or 
                        event.key_data.get("value", 0)
                    )
                    metrics["credits_earned"] += credits
                    
                elif event.event_type in ["MarketBuy", "Repair", "RefuelAll"]:
                    cost = event.key_data.get("total", 0) or event.raw_event.get("Cost", 0)
                    metrics["credits_spent"] += cost
                
                # Track activity breakdown
                category = event.category.value
                if category not in metrics["activity_breakdown"]:
                    metrics["activity_breakdown"][category] = 0
                metrics["activity_breakdown"][category] += 1
            
            # Calculate net profit
            metrics["net_profit"] = metrics["credits_earned"] - metrics["credits_spent"]
            
            # Calculate efficiency metrics
            if metrics["total_events"] > 0:
                metrics["efficiency_metrics"]["credits_per_event"] = (
                    metrics["net_profit"] / metrics["total_events"]
                )
                metrics["efficiency_metrics"]["events_per_hour"] = (
                    metrics["total_events"] / time_range_hours
                )
            
            # Find peak activity times
            sorted_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)
            metrics["peak_activity_times"] = [
                {"hour": hour, "events": count} 
                for hour, count in sorted_hours[:5]
            ]
            
            # Identify achievements
            if metrics["credits_earned"] > 1000000:
                metrics["achievements"].append("Millionaire - Earned over 1M credits")
            
            if metrics["activity_breakdown"].get("exploration", 0) > 50:
                metrics["achievements"].append("Explorer - 50+ exploration events")
            
            if metrics["activity_breakdown"].get("combat", 0) > 30:
                metrics["achievements"].append("Combat Veteran - 30+ combat events")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    # ==================== Specialized Query Tools ====================
    
    async def get_faction_standings(self) -> Dict[str, Any]:
        """
        Get current faction standings and reputation changes.
        
        Returns:
            Dict containing faction relationships and recent changes
        """
        try:
            # Get reputation events
            rep_events = self.data_store.get_events_by_type("Reputation", limit=1)
            faction_events = []
            
            # Get mission completions for faction tracking
            mission_filter = EventFilter(
                event_types={"MissionCompleted", "MissionFailed"},
                start_time=datetime.now(timezone.utc) - timedelta(days=7)
            )
            mission_events = self.data_store.query_events(mission_filter)
            
            summary = {
                "current_reputation": {},
                "faction_interactions": {},
                "recent_changes": []
            }
            
            # Process reputation status
            if rep_events:
                latest_rep = rep_events[-1]
                if "Reputation" in latest_rep.raw_event:
                    for faction in latest_rep.raw_event["Reputation"]:
                        summary["current_reputation"][faction["Faction"]] = {
                            "reputation": faction.get("Reputation", 0),
                            "trend": faction.get("Trend", "Stable")
                        }
            
            # Track faction interactions from missions
            for event in mission_events:
                faction = event.key_data.get("faction")
                if faction:
                    if faction not in summary["faction_interactions"]:
                        summary["faction_interactions"][faction] = {
                            "missions_completed": 0,
                            "missions_failed": 0,
                            "total_rewards": 0
                        }
                    
                    if event.event_type == "MissionCompleted":
                        summary["faction_interactions"][faction]["missions_completed"] += 1
                        summary["faction_interactions"][faction]["total_rewards"] += event.key_data.get("reward", 0)
                    else:
                        summary["faction_interactions"][faction]["missions_failed"] += 1
                    
                    summary["recent_changes"].append({
                        "faction": faction,
                        "type": event.event_type,
                        "timestamp": event.timestamp.isoformat()
                    })
            
            # Limit recent changes
            summary["recent_changes"] = summary["recent_changes"][:20]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting faction standings: {e}")
            return {"error": str(e)}
    
    async def get_material_inventory(self) -> Dict[str, Any]:
        """
        Get current material and cargo inventory.
        
        Returns:
            Dict containing materials, cargo, and recent changes
        """
        try:
            # Get cargo and materials events
            cargo_events = self.data_store.get_events_by_type("Cargo", limit=1)
            materials_events = self.data_store.get_events_by_type("Materials", limit=1)
            
            summary = {
                "cargo": {},
                "materials": {
                    "raw": {},
                    "manufactured": {},
                    "encoded": {}
                },
                "recent_changes": []
            }
            
            # Process cargo inventory
            if cargo_events:
                latest_cargo = cargo_events[-1]
                if "Inventory" in latest_cargo.raw_event:
                    for item in latest_cargo.raw_event["Inventory"]:
                        summary["cargo"][item["Name"]] = {
                            "count": item["Count"],
                            "stolen": item.get("Stolen", 0)
                        }
            
            # Process materials inventory
            if materials_events:
                latest_materials = materials_events[-1]
                for category in ["Raw", "Manufactured", "Encoded"]:
                    if category in latest_materials.raw_event:
                        category_key = category.lower()
                        for material in latest_materials.raw_event[category]:
                            summary["materials"][category_key][material["Name"]] = material["Count"]
            
            # Track recent material collection
            material_filter = EventFilter(
                event_types={"MaterialCollected", "MaterialDiscarded", "MaterialTrade"},
                start_time=datetime.now(timezone.utc) - timedelta(hours=24)
            )
            material_events = self.data_store.query_events(material_filter)
            
            for event in material_events[:20]:
                summary["recent_changes"].append({
                    "type": event.event_type,
                    "material": event.raw_event.get("Name") or event.raw_event.get("Paid"),
                    "category": event.raw_event.get("Category"),
                    "count": event.raw_event.get("Count", 1),
                    "timestamp": event.timestamp.isoformat()
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting material inventory: {e}")
            return {"error": str(e)}

    def generate_edcopilot_chatter(self, chatter_type: str = "all") -> Dict[str, Any]:
        """
        Generate EDCoPilot custom chatter files based on current game state.

        Args:
            chatter_type: Type of chatter to generate ("space", "crew", "deepspace", or "all")

        Returns:
            Status of file generation with details
        """
        try:
            try:
                from ..edcopilot.generator import EDCoPilotContentGenerator
                from ..utils.config import EliteConfig
            except ImportError:
                from src.edcopilot.generator import EDCoPilotContentGenerator
                from src.utils.config import EliteConfig

            config = EliteConfig()
            generator = EDCoPilotContentGenerator(self.data_store, config.edcopilot_path)

            if chatter_type == "all":
                written_files = generator.write_files(backup_existing=True)
                return {
                    "status": "success",
                    "files_generated": list(written_files.keys()),
                    "output_directory": str(config.edcopilot_path),
                    "message": f"Generated {len(written_files)} EDCoPilot chatter files"
                }
            else:
                # Generate specific chatter type
                files = generator.generate_contextual_chatter()

                # Filter to requested type
                target_files = {}
                if chatter_type.lower() in ["space", "spacechatter"]:
                    target_files = {k: v for k, v in files.items() if "SpaceChatter" in k}
                elif chatter_type.lower() in ["crew", "crewchatter"]:
                    target_files = {k: v for k, v in files.items() if "CrewChatter" in k}
                elif chatter_type.lower() in ["deepspace", "deepspacechatter"]:
                    target_files = {k: v for k, v in files.items() if "DeepSpaceChatter" in k}
                else:
                    return {"error": f"Unknown chatter type: {chatter_type}"}

                # Write filtered files
                written_files = {}
                for filename, content in target_files.items():
                    file_path = config.edcopilot_path / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    written_files[filename] = file_path

                return {
                    "status": "success",
                    "files_generated": list(written_files.keys()),
                    "output_directory": str(config.edcopilot_path),
                    "message": f"Generated {chatter_type} chatter file(s)"
                }

        except ImportError as e:
            return {
                "error": "EDCoPilot integration not available",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Error generating EDCoPilot chatter: {e}")
            return {"error": str(e)}

    def get_edcopilot_status(self) -> Dict[str, Any]:
        """
        Get status of EDCoPilot integration and existing custom files.

        Returns:
            Status of EDCoPilot integration and file information
        """
        try:
            try:
                from ..edcopilot.generator import EDCoPilotFileManager
                from ..utils.config import EliteConfig
            except ImportError:
                from src.edcopilot.generator import EDCoPilotFileManager
                from src.utils.config import EliteConfig

            config = EliteConfig()
            file_manager = EDCoPilotFileManager(config.edcopilot_path)

            # Check if EDCoPilot directory exists
            if not config.edcopilot_path.exists():
                return {
                    "status": "not_configured",
                    "edcopilot_path": str(config.edcopilot_path),
                    "exists": False,
                    "message": "EDCoPilot directory not found. Set ELITE_EDCOPILOT_PATH environment variable."
                }

            # List existing custom files
            custom_files = file_manager.list_custom_files()
            file_info = {}

            for file_path in custom_files:
                file_info[file_path.name] = file_manager.get_file_info(file_path)

            # Get current game context for chatter generation
            try:
                from ..edcopilot.generator import EDCoPilotContextAnalyzer
            except ImportError:
                from src.edcopilot.generator import EDCoPilotContextAnalyzer
            context_analyzer = EDCoPilotContextAnalyzer(self.data_store)
            context = context_analyzer.analyze_current_context()

            return {
                "status": "available",
                "edcopilot_path": str(config.edcopilot_path),
                "exists": True,
                "custom_files": file_info,
                "total_files": len(custom_files),
                "current_context": {
                    "primary_activity": context["primary_activity"],
                    "current_system": context["current_system"],
                    "docked": context["docked"],
                    "fuel_low": context["fuel_low"],
                    "deep_space": context["is_deep_space"]
                },
                "message": f"EDCoPilot integration ready. Found {len(custom_files)} existing custom files."
            }

        except ImportError as e:
            return {
                "error": "EDCoPilot integration not available",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Error getting EDCoPilot status: {e}")
            return {"error": str(e)}

    def backup_edcopilot_files(self) -> Dict[str, Any]:
        """
        Create backups of all existing EDCoPilot custom files.

        Returns:
            Status of backup operation
        """
        try:
            try:
                from ..edcopilot.generator import EDCoPilotFileManager
                from ..utils.config import EliteConfig
            except ImportError:
                from src.edcopilot.generator import EDCoPilotFileManager
                from src.utils.config import EliteConfig

            config = EliteConfig()
            file_manager = EDCoPilotFileManager(config.edcopilot_path)

            if not config.edcopilot_path.exists():
                return {
                    "status": "error",
                    "message": "EDCoPilot directory not found"
                }

            backup_files = file_manager.backup_files()

            return {
                "status": "success",
                "backups_created": len(backup_files),
                "backup_files": {name: str(path) for name, path in backup_files.items()},
                "message": f"Created {len(backup_files)} backup files"
            }

        except ImportError as e:
            return {
                "error": "EDCoPilot integration not available",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Error backing up EDCoPilot files: {e}")
            return {"error": str(e)}

    def preview_edcopilot_chatter(self, chatter_type: str = "space") -> Dict[str, Any]:
        """
        Preview EDCoPilot chatter content without writing files.

        Args:
            chatter_type: Type of chatter to preview ("space", "crew", "deepspace")

        Returns:
            Preview of generated chatter content
        """
        try:
            try:
                from ..edcopilot.generator import EDCoPilotContentGenerator
                from ..utils.config import EliteConfig
            except ImportError:
                from src.edcopilot.generator import EDCoPilotContentGenerator
                from src.utils.config import EliteConfig

            config = EliteConfig()
            generator = EDCoPilotContentGenerator(self.data_store, config.edcopilot_path)

            # Generate content without writing files
            files = generator.generate_contextual_chatter()

            # Filter to requested type
            target_file = None
            if chatter_type.lower() in ["space", "spacechatter"]:
                target_file = next((k for k in files.keys() if "SpaceChatter" in k), None)
            elif chatter_type.lower() in ["crew", "crewchatter"]:
                target_file = next((k for k in files.keys() if "CrewChatter" in k), None)
            elif chatter_type.lower() in ["deepspace", "deepspacechatter"]:
                target_file = next((k for k in files.keys() if "DeepSpaceChatter" in k), None)
            else:
                return {"error": f"Unknown chatter type: {chatter_type}"}

            if not target_file:
                return {"error": f"Could not find {chatter_type} chatter template"}

            content = files[target_file]

            # Count entries (non-comment, non-empty lines)
            lines = content.split('\n')
            entry_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

            return {
                "status": "success",
                "chatter_type": chatter_type,
                "filename": target_file,
                "content_preview": content[:1000] + "..." if len(content) > 1000 else content,
                "total_lines": len(lines),
                "entry_count": len(entry_lines),
                "sample_entries": entry_lines[:5],
                "message": f"Generated {len(entry_lines)} {chatter_type} chatter entries"
            }

        except ImportError as e:
            return {
                "error": "EDCoPilot integration not available",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Error previewing EDCoPilot chatter: {e}")
            return {"error": str(e)}

    async def server_status(self) -> Dict[str, Any]:
        """
        Get server status information.

        Returns:
            Dict containing server status information
        """
        try:
            stats = self.data_store.get_statistics()
            game_state = self.data_store.get_game_state()

            return {
                "server_running": True,
                "journal_monitoring": True,  # Assume monitoring is active if we have stats
                "uptime_seconds": stats.get('uptime_seconds', 0),
                "total_events": stats.get('total_processed', 0),
                "memory_usage_events": stats.get('memory_usage_events', 0),
                "current_system": game_state.current_system,
                "current_station": game_state.current_station,
                "last_updated": game_state.last_updated.isoformat() if game_state.last_updated else None,
                "data_store_stats": {
                    "total_events": stats.get('total_processed', 0),
                    "events_by_type": stats.get('events_by_type', {}),
                    "events_by_category": stats.get('events_by_category', {}),
                    "uptime_seconds": stats.get('uptime_seconds', 0),
                    "memory_usage_events": stats.get('memory_usage_events', 0),
                    "max_events": stats.get('max_events', 0),
                    "storage_efficiency": stats.get('storage_efficiency', 0)
                }
            }
        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            return {
                "server_running": False,
                "error": str(e)
            }

    def get_recent_events(self, minutes: int = 60) -> Dict[str, Any]:
        """
        Get recent events from specified time range.

        Args:
            minutes: Number of minutes to look back

        Returns:
            Dict containing recent events information
        """
        try:
            from datetime import datetime, timezone, timedelta

            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            events = self.data_store.get_recent_events(minutes)

            return {
                "event_count": len(events),
                "time_range_minutes": minutes,
                "cutoff_time": cutoff_time.isoformat(),
                "events": [
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "event_type": event.event_type,
                        "category": event.category.value,
                        "summary": event.summary
                    }
                    for event in events
                ]
            }
        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
            return {
                "event_count": 0,
                "error": str(e)
            }
