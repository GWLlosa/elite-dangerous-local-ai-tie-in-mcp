"""
MCP Resources for Elite Dangerous Data Access

Provides structured resource endpoints for accessing Elite Dangerous game data
through the Model Context Protocol (MCP). Resources support dynamic URIs with
parameters and caching for performance optimization.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse, parse_qs
from enum import Enum
import hashlib

try:
    from ..utils.data_store import DataStore
    from ..journal.events import EventCategory
except ImportError:
    from src.utils.data_store import DataStore
    from src.journal.events import EventCategory


logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of MCP resources available."""
    STATUS = "status"
    JOURNAL = "journal"
    EVENTS = "events"
    SUMMARY = "summary"
    STATE = "state"
    METRICS = "metrics"


class ResourceCache:
    """Simple cache implementation for resource responses."""
    
    def __init__(self, ttl_seconds: int = 30):
        """
        Initialize resource cache.
        
        Args:
            ttl_seconds: Time to live for cached entries in seconds
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        async with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if datetime.now(timezone.utc) - timestamp < timedelta(seconds=self.ttl_seconds):
                    logger.debug(f"Cache hit for key: {key}")
                    return value
                else:
                    # Expired, remove from cache
                    del self._cache[key]
                    logger.debug(f"Cache expired for key: {key}")
            return None
    
    async def set(self, key: str, value: Any):
        """Set cache value with current timestamp."""
        async with self._lock:
            self._cache[key] = (value, datetime.now(timezone.utc))
            logger.debug(f"Cache set for key: {key}")
    
    async def clear(self):
        """Clear all cached entries."""
        async with self._lock:
            self._cache.clear()
            logger.debug("Cache cleared")
    
    def make_key(self, resource_type: str, params: Dict[str, Any]) -> str:
        """Create cache key from resource type and parameters."""
        # Sort params for consistent key generation
        sorted_params = sorted(params.items())
        param_str = json.dumps(sorted_params, sort_keys=True)
        key_str = f"{resource_type}:{param_str}"
        # Use hash for shorter keys
        return hashlib.md5(key_str.encode()).hexdigest()


class MCPResources:
    """
    MCP Resources provider for Elite Dangerous data.
    
    Implements dynamic resource URIs with parameter support and caching
    for efficient data access through the MCP protocol.
    """
    
    def __init__(self, data_store: DataStore):
        """
        Initialize MCP resources provider.
        
        Args:
            data_store: DataStore instance for accessing game data
        """
        self.data_store = data_store
        self.cache = ResourceCache(ttl_seconds=30)  # 30 second cache TTL
        
        # Define available resources with metadata
        self.resources = {
            "elite://status/current": {
                "type": ResourceType.STATUS,
                "name": "Current Status",
                "description": "Current game status including location, ship, and state",
                "mimeType": "application/json"
            },
            "elite://status/location": {
                "type": ResourceType.STATUS,
                "name": "Current Location",
                "description": "Current system and station location",
                "mimeType": "application/json"
            },
            "elite://status/ship": {
                "type": ResourceType.STATUS,
                "name": "Ship Status",
                "description": "Current ship type and condition",
                "mimeType": "application/json"
            },
            "elite://journal/recent": {
                "type": ResourceType.JOURNAL,
                "name": "Recent Journal Entries",
                "description": "Recent journal events (supports ?minutes=N parameter)",
                "mimeType": "application/json",
                "parameters": ["minutes"]
            },
            "elite://journal/stats": {
                "type": ResourceType.JOURNAL,
                "name": "Journal Statistics",
                "description": "Statistics about stored journal events",
                "mimeType": "application/json"
            },
            "elite://events/by-category": {
                "type": ResourceType.EVENTS,
                "name": "Events by Category",
                "description": "Events filtered by category (supports ?category=NAME parameter)",
                "mimeType": "application/json",
                "parameters": ["category"]
            },
            "elite://events/by-type": {
                "type": ResourceType.EVENTS,
                "name": "Events by Type",
                "description": "Events filtered by type (supports ?type=NAME parameter)",
                "mimeType": "application/json",
                "parameters": ["type"]
            },
            "elite://events/search": {
                "type": ResourceType.EVENTS,
                "name": "Event Search",
                "description": "Search events with multiple filters (type, category, system, text)",
                "mimeType": "application/json",
                "parameters": ["type", "category", "system", "text", "minutes"]
            },
            "elite://summary/exploration": {
                "type": ResourceType.SUMMARY,
                "name": "Exploration Summary",
                "description": "Summary of exploration activities (supports ?hours=N parameter)",
                "mimeType": "application/json",
                "parameters": ["hours"]
            },
            "elite://summary/trading": {
                "type": ResourceType.SUMMARY,
                "name": "Trading Summary",
                "description": "Summary of trading activities (supports ?hours=N parameter)",
                "mimeType": "application/json",
                "parameters": ["hours"]
            },
            "elite://summary/combat": {
                "type": ResourceType.SUMMARY,
                "name": "Combat Summary",
                "description": "Summary of combat activities (supports ?hours=N parameter)",
                "mimeType": "application/json",
                "parameters": ["hours"]
            },
            "elite://summary/mining": {
                "type": ResourceType.SUMMARY,
                "name": "Mining Summary",
                "description": "Summary of mining activities (supports ?hours=N parameter)",
                "mimeType": "application/json",
                "parameters": ["hours"]
            },
            "elite://summary/journey": {
                "type": ResourceType.SUMMARY,
                "name": "Journey Summary",
                "description": "Summary of travel and navigation (supports ?hours=N parameter)",
                "mimeType": "application/json",
                "parameters": ["hours"]
            },
            "elite://state/materials": {
                "type": ResourceType.STATE,
                "name": "Material Inventory",
                "description": "Current material and cargo inventory",
                "mimeType": "application/json"
            },
            "elite://state/factions": {
                "type": ResourceType.STATE,
                "name": "Faction Standings",
                "description": "Current faction standings and reputation",
                "mimeType": "application/json"
            },
            "elite://metrics/performance": {
                "type": ResourceType.METRICS,
                "name": "Performance Metrics",
                "description": "Performance metrics and achievements (supports ?hours=N parameter)",
                "mimeType": "application/json",
                "parameters": ["hours"]
            },
            "elite://metrics/credits": {
                "type": ResourceType.METRICS,
                "name": "Credit Flow",
                "description": "Credit earnings and spending (supports ?hours=N parameter)",
                "mimeType": "application/json",
                "parameters": ["hours"]
            }
        }
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all available resources with metadata.
        
        Returns:
            List of resource definitions with URIs and metadata
        """
        resources_list = []
        for uri, metadata in self.resources.items():
            resource_def = {
                "uri": uri,
                "name": metadata["name"],
                "description": metadata["description"],
                "mimeType": metadata["mimeType"]
            }
            if "parameters" in metadata:
                resource_def["parameters"] = metadata["parameters"]
            resources_list.append(resource_def)
        
        return resources_list
    
    def parse_resource_uri(self, uri: str) -> Tuple[str, Dict[str, str]]:
        """
        Parse resource URI and extract parameters.
        
        Args:
            uri: Resource URI with optional query parameters
            
        Returns:
            Tuple of (base_uri, parameters_dict)
        """
        parsed = urlparse(uri)
        base_uri = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Parse query parameters
        params = {}
        if parsed.query:
            query_params = parse_qs(parsed.query)
            # Convert lists to single values (take first)
            for key, values in query_params.items():
                if values:
                    params[key] = values[0]
        
        return base_uri, params
    
    async def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """
        Get resource data for the specified URI.
        
        Args:
            uri: Resource URI with optional parameters
            
        Returns:
            Resource data or None if invalid URI
        """
        try:
            # Parse URI and parameters
            base_uri, params = self.parse_resource_uri(uri)
            
            # Check if resource exists
            if base_uri not in self.resources:
                logger.warning(f"Unknown resource URI: {base_uri}")
                if "summary/" in base_uri:
                    return {
                        "error": f"Unknown activity type: {base_uri.split('/')[-1]}",
                        "valid_activities": ["exploration", "trading", "combat", "mining", "journey"]
                    }
                return {
                    "error": f"Unknown resource URI: {base_uri}",
                    "available_resources": list(self.resources.keys())
                }
            
            metadata = self.resources[base_uri]
            
            # Check cache
            cache_key = self.cache.make_key(base_uri, params)
            cached_data = await self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Generate resource data based on type
            resource_data = None
            
            if base_uri == "elite://status/current":
                resource_data = await self._get_current_status()
            elif base_uri == "elite://status/location":
                resource_data = await self._get_location_status()
            elif base_uri == "elite://status/ship":
                resource_data = await self._get_ship_status()
            elif base_uri == "elite://journal/recent":
                minutes = int(params.get("minutes", "60"))
                resource_data = await self._get_recent_journal(minutes)
            elif base_uri == "elite://journal/stats":
                resource_data = await self._get_journal_stats()
            elif base_uri == "elite://events/by-category":
                category = params.get("category", "")
                resource_data = await self._get_events_by_category(category)
            elif base_uri == "elite://events/by-type":
                event_type = params.get("type", "")
                resource_data = await self._get_events_by_type(event_type)
            elif base_uri == "elite://events/search":
                resource_data = await self._search_events(params)
            elif base_uri.startswith("elite://summary/"):
                activity = base_uri.split("/")[-1]
                hours = int(params.get("hours", "24"))
                resource_data = await self._get_activity_summary(activity, hours)
            elif base_uri == "elite://state/materials":
                resource_data = await self._get_material_state()
            elif base_uri == "elite://state/factions":
                resource_data = await self._get_faction_state()
            elif base_uri == "elite://metrics/performance":
                hours = int(params.get("hours", "24"))
                resource_data = await self._get_performance_metrics(hours)
            elif base_uri == "elite://metrics/credits":
                hours = int(params.get("hours", "24"))
                resource_data = await self._get_credit_metrics(hours)
            
            # Cache the result
            if resource_data is not None:
                await self.cache.set(cache_key, resource_data)
            
            return resource_data
            
        except Exception as e:
            logger.error(f"Error getting resource {uri}: {e}")
            return {"error": str(e)}
    
    async def _get_current_status(self) -> Dict[str, Any]:
        """Get comprehensive current status."""
        try:
            game_state = self.data_store.get_game_state()
            stats = self.data_store.get_statistics()
            
            return {
                "location": {
                    "system": game_state.current_system,
                    "station": game_state.current_station,
                    "docked": game_state.docked,
                    "coordinates": game_state.coordinates
                },
                "ship": {
                    "type": game_state.current_ship,
                    "fuel_level": game_state.fuel_level,
                    "hull_health": game_state.hull_health
                },
                "commander": {
                    "credits": game_state.credits,
                    "combat_rank": game_state.ranks.get("Combat"),
                    "trade_rank": game_state.ranks.get("Trade"),
                    "exploration_rank": game_state.ranks.get("Explore")
                },
                "statistics": stats,
                "last_updated": game_state.last_updated.isoformat() if game_state.last_updated else None
            }
        except Exception as e:
            logger.error(f"Error getting current status: {e}")
            return {"error": str(e)}
    
    async def _get_location_status(self) -> Dict[str, Any]:
        """Get current location information."""
        try:
            game_state = self.data_store.get_game_state()
            
            # Get nearby systems from recent jumps
            recent_events = self.data_store.get_events_by_type("FSDJump", limit=10)
            visited_systems = list({e.raw_event.get("StarSystem") for e in recent_events if "StarSystem" in e.raw_event})
            
            return {
                "current_system": game_state.current_system,
                "current_station": game_state.current_station,
                "docked": game_state.docked,
                "coordinates": game_state.coordinates,
                "recently_visited": visited_systems[:5],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting location status: {e}")
            return {"error": str(e)}
    
    async def _get_ship_status(self) -> Dict[str, Any]:
        """Get current ship status."""
        try:
            game_state = self.data_store.get_game_state()
            
            # Get recent ship events for more details
            loadout_events = self.data_store.get_events_by_type("Loadout", limit=1)
            current_loadout = loadout_events[0].raw_event if loadout_events else {}
            
            return {
                "ship_type": game_state.current_ship,
                "fuel": {
                    "level": game_state.fuel_level,
                    "capacity": current_loadout.get("FuelCapacity", {}).get("Main", 0)
                },
                "health": {
                    "hull": game_state.hull_health,
                    "integrity": 100.0  # Default if not available
                },
                "modules": current_loadout.get("Modules", []) if current_loadout else [],
                "cargo_capacity": current_loadout.get("CargoCapacity", 0) if current_loadout else 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting ship status: {e}")
            return {"error": str(e)}
    
    async def _get_recent_journal(self, minutes: int) -> Dict[str, Any]:
        """Get recent journal entries."""
        try:
            events = self.data_store.get_recent_events(minutes=minutes)
            
            # Group events by category
            events_by_category = {}
            for event in events:
                category = event.category.value
                if category not in events_by_category:
                    events_by_category[category] = []
                events_by_category[category].append({
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "summary": event.summary
                })
            
            return {
                "time_range_minutes": minutes,
                "total_events": len(events),
                "events_by_category": events_by_category,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting recent journal: {e}")
            return {"error": str(e)}
    
    async def _get_journal_stats(self) -> Dict[str, Any]:
        """Get journal statistics."""
        try:
            stats = self.data_store.get_statistics()
            
            # Get event distribution
            all_events = self.data_store.get_recent_events(24 * 60)  # Get last 24 hours
            type_distribution = {}
            category_distribution = {}
            
            for event in all_events:
                # Count by type
                if event.event_type not in type_distribution:
                    type_distribution[event.event_type] = 0
                type_distribution[event.event_type] += 1
                
                # Count by category
                category = event.category.value
                if category not in category_distribution:
                    category_distribution[category] = 0
                category_distribution[category] += 1
            
            # Sort distributions
            top_types = sorted(type_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_events": stats["total_events"],
                "unique_event_types": stats["unique_event_types"],
                "events_in_last_hour": stats["events_in_last_hour"],
                "top_event_types": dict(top_types),
                "category_distribution": category_distribution,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting journal stats: {e}")
            return {"error": str(e)}
    
    async def _get_events_by_category(self, category: str) -> Dict[str, Any]:
        """Get events filtered by category."""
        try:
            # Validate category
            try:
                category_enum = EventCategory(category.lower())
            except ValueError:
                return {
                    "error": f"Invalid category: {category}",
                    "valid_categories": [c.value for c in EventCategory]
                }
            
            events = self.data_store.get_events_by_category(category_enum, limit=100)
            
            return {
                "category": category,
                "event_count": len(events),
                "events": [
                    {
                        "timestamp": e.timestamp.isoformat(),
                        "type": e.event_type,
                        "summary": e.summary,
                        "data": e.raw_event
                    }
                    for e in events
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting events by category: {e}")
            return {"error": str(e)}
    
    async def _get_events_by_type(self, event_type: str) -> Dict[str, Any]:
        """Get events filtered by type."""
        try:
            events = self.data_store.get_events_by_type(event_type, limit=100)
            
            return {
                "event_type": event_type,
                "event_count": len(events),
                "events": [
                    {
                        "timestamp": e.timestamp.isoformat(),
                        "category": e.category.value,
                        "summary": e.summary,
                        "data": e.raw_event
                    }
                    for e in events
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting events by type: {e}")
            return {"error": str(e)}
    
    async def _search_events(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Search events with multiple filters."""
        try:
            # Build filter criteria
            events = self.data_store.get_recent_events(24 * 60)  # Get last 24 hours
            
            # Apply filters
            if "type" in params:
                events = [e for e in events if e.event_type == params["type"]]
            
            if "category" in params:
                try:
                    category = EventCategory(params["category"].lower())
                    events = [e for e in events if e.category == category]
                except ValueError:
                    pass
            
            if "system" in params:
                system_name = params["system"]
                events = [e for e in events if e.raw_event.get("StarSystem") == system_name]
            
            if "text" in params:
                search_text = params["text"].lower()
                events = [e for e in events if search_text in e.summary.lower() or 
                         search_text in str(e.raw_event).lower()]
            
            if "minutes" in params:
                minutes = int(params["minutes"])
                cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
                events = [e for e in events if e.timestamp >= cutoff_time]
            
            # Limit results
            events = events[:100]
            
            return {
                "search_params": params,
                "result_count": len(events),
                "events": [
                    {
                        "timestamp": e.timestamp.isoformat(),
                        "type": e.event_type,
                        "category": e.category.value,
                        "summary": e.summary
                    }
                    for e in events
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return {"error": str(e)}
    
    async def _get_activity_summary(self, activity: str, hours: int) -> Dict[str, Any]:
        """Get activity summary for specified type."""
        try:
            # Get events from time range
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            all_events = self.data_store.get_recent_events(24 * 60)  # Get last 24 hours
            events = [e for e in all_events if e.timestamp >= cutoff_time]
            
            # Filter by activity type
            if activity == "exploration":
                relevant_categories = [EventCategory.EXPLORATION, EventCategory.SYSTEM]
                events = [e for e in events if e.category in relevant_categories]
                
                # Calculate exploration metrics
                systems_visited = len(set(e.raw_event.get("StarSystem") for e in events 
                                         if e.event_type == "FSDJump"))
                bodies_scanned = len([e for e in events if "Scan" in e.event_type])
                
                return {
                    "activity": "exploration",
                    "time_range_hours": hours,
                    "systems_visited": systems_visited,
                    "bodies_scanned": bodies_scanned,
                    "event_count": len(events),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            elif activity == "trading":
                relevant_categories = [EventCategory.TRADING]
                events = [e for e in events if e.category in relevant_categories]
                
                # Calculate trading metrics
                total_profit = sum(e.raw_event.get("Profit", 0) for e in events 
                                 if e.event_type == "MarketSell")
                trades_count = len([e for e in events if e.event_type in ["MarketBuy", "MarketSell"]])
                
                return {
                    "activity": "trading",
                    "time_range_hours": hours,
                    "total_profit": total_profit,
                    "trades_count": trades_count,
                    "event_count": len(events),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            elif activity == "combat":
                relevant_categories = [EventCategory.COMBAT]
                events = [e for e in events if e.category in relevant_categories]
                
                # Calculate combat metrics
                bounties_earned = sum(e.raw_event.get("Reward", 0) for e in events 
                                    if e.event_type == "Bounty")
                kills = len([e for e in events if e.event_type in ["PVPKill", "Died"]])
                
                return {
                    "activity": "combat",
                    "time_range_hours": hours,
                    "bounties_earned": bounties_earned,
                    "kills": kills,
                    "event_count": len(events),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            elif activity == "mining":
                relevant_categories = [EventCategory.MINING]
                events = [e for e in events if e.category in relevant_categories]
                
                # Calculate mining metrics
                materials_collected = len([e for e in events if e.event_type == "MaterialCollected"])
                asteroids_prospected = len([e for e in events if e.event_type == "ProspectedAsteroid"])
                
                return {
                    "activity": "mining",
                    "time_range_hours": hours,
                    "materials_collected": materials_collected,
                    "asteroids_prospected": asteroids_prospected,
                    "event_count": len(events),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            elif activity == "journey":
                jump_events = [e for e in events if e.event_type == "FSDJump"]
                total_distance = sum(e.raw_event.get("JumpDist", 0) for e in jump_events)
                
                return {
                    "activity": "journey",
                    "time_range_hours": hours,
                    "total_jumps": len(jump_events),
                    "total_distance_ly": round(total_distance, 2),
                    "systems_visited": len(set(e.raw_event.get("StarSystem") for e in jump_events)),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    "error": f"Unknown activity type: {activity}",
                    "valid_activities": ["exploration", "trading", "combat", "mining", "journey"]
                }
                
        except Exception as e:
            logger.error(f"Error getting activity summary: {e}")
            return {"error": str(e)}
    
    async def _get_material_state(self) -> Dict[str, Any]:
        """Get current material inventory."""
        try:
            # Get material events
            material_events = self.data_store.get_events_by_type("Materials", limit=1)
            cargo_events = self.data_store.get_events_by_type("Cargo", limit=1)
            
            materials = {}
            cargo = {}
            
            if material_events:
                materials = material_events[0].raw_event.get("Raw", {})
            
            if cargo_events:
                cargo = cargo_events[0].raw_event.get("Inventory", [])
            
            return {
                "materials": materials,
                "cargo": cargo,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting material state: {e}")
            return {"error": str(e)}
    
    async def _get_faction_state(self) -> Dict[str, Any]:
        """Get faction standings."""
        try:
            # Get faction-related events
            reputation_events = self.data_store.get_events_by_type("Reputation", limit=1)
            
            factions = {}
            if reputation_events:
                # Process reputation data
                rep_data = reputation_events[0].raw_event
                for faction in ["Empire", "Federation", "Alliance"]:
                    if faction in rep_data:
                        factions[faction] = rep_data[faction]
            
            return {
                "major_factions": factions,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting faction state: {e}")
            return {"error": str(e)}
    
    async def _get_performance_metrics(self, hours: int) -> Dict[str, Any]:
        """Get performance metrics."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            all_events = self.data_store.get_recent_events(24 * 60)  # Get last 24 hours
            events = [e for e in all_events if e.timestamp >= cutoff_time]
            
            # Calculate various metrics
            credits_earned = sum(e.raw_event.get("Reward", 0) for e in events if "Reward" in e.raw_event)
            credits_spent = sum(e.raw_event.get("Cost", 0) for e in events if "Cost" in e.raw_event)
            jumps_made = len([e for e in events if e.event_type == "FSDJump"])
            
            return {
                "time_range_hours": hours,
                "credits_earned": credits_earned,
                "credits_spent": credits_spent,
                "net_credits": credits_earned - credits_spent,
                "jumps_made": jumps_made,
                "events_processed": len(events),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def _get_credit_metrics(self, hours: int) -> Dict[str, Any]:
        """Get credit flow metrics."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            all_events = self.data_store.get_recent_events(24 * 60)  # Get last 24 hours
            events = [e for e in all_events if e.timestamp >= cutoff_time]
            
            # Track credit changes
            earnings = []
            expenses = []
            
            for event in events:
                if "Reward" in event.raw_event:
                    earnings.append({
                        "amount": event.raw_event["Reward"],
                        "source": event.event_type,
                        "timestamp": event.timestamp.isoformat()
                    })
                if "Cost" in event.raw_event:
                    expenses.append({
                        "amount": event.raw_event["Cost"],
                        "reason": event.event_type,
                        "timestamp": event.timestamp.isoformat()
                    })
            
            # Sort by amount
            earnings.sort(key=lambda x: x["amount"], reverse=True)
            expenses.sort(key=lambda x: x["amount"], reverse=True)
            
            return {
                "time_range_hours": hours,
                "total_earned": sum(e["amount"] for e in earnings),
                "total_spent": sum(e["amount"] for e in expenses),
                "top_earnings": earnings[:5],
                "top_expenses": expenses[:5],
                "transaction_count": len(earnings) + len(expenses),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting credit metrics: {e}")
            return {"error": str(e)}
    
    async def clear_cache(self):
        """Clear the resource cache."""
        await self.cache.clear()
        logger.info("Resource cache cleared")
