"""
Elite Dangerous MCP Server - Data Storage and Retrieval System

This module provides in-memory event storage with current state tracking,
time-based filtering, and efficient querying for Elite Dangerous journal events.
"""

import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable, Union
from dataclasses import dataclass, field

from ..journal.events import ProcessedEvent, EventCategory


class EventStorageError(Exception):
    """Custom exception for event storage related errors."""
    pass


class QuerySortOrder(Enum):
    """Sorting options for event queries."""
    NEWEST_FIRST = "newest_first"
    OLDEST_FIRST = "oldest_first"
    RELEVANCE = "relevance"


@dataclass
class EventFilter:
    """Filter criteria for event queries."""
    event_types: Optional[Set[str]] = None
    categories: Optional[Set[EventCategory]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    system_names: Optional[Set[str]] = None
    ship_types: Optional[Set[str]] = None
    contains_text: Optional[str] = None
    min_importance: Optional[int] = None
    max_results: Optional[int] = None


@dataclass 
class GameState:
    """Current game state tracking."""
    # Location information
    current_system: Optional[str] = None
    current_station: Optional[str] = None
    current_body: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    
    # Ship information
    current_ship: Optional[str] = None
    ship_name: Optional[str] = None
    ship_id: Optional[str] = None
    ship_modules: Dict[str, Any] = field(default_factory=dict)
    
    # Status information
    docked: bool = False
    landed: bool = False
    in_srv: bool = False
    in_fighter: bool = False
    supercruise: bool = False
    fsd_charging: bool = False
    fsd_cooldown: bool = False
    low_fuel: bool = False
    overheating: bool = False
    has_lat_long: bool = False
    is_in_danger: bool = False
    being_interdicted: bool = False
    in_main_ship: bool = True
    in_fighter: bool = False
    in_srv: bool = False
    analysis_mode: bool = False
    night_vision: bool = False
    altitude_from_average_radius: bool = False
    
    # Game mode
    game_mode: Optional[str] = None
    group: Optional[str] = None
    
    # Commander information
    commander_name: Optional[str] = None

    # Credits and cargo
    credits: int = 0
    loan: int = 0
    cargo_capacity: int = 0
    cargo_count: int = 0

    # Fuel information
    fuel_level: float = 100.0
    fuel_capacity: float = 32.0

    # Last update timestamp
    last_updated: Optional[datetime] = None


class DataStore:
    """
    In-memory data store for Elite Dangerous journal events with current state tracking.
    
    Features:
    - Efficient event storage with automatic cleanup
    - Current game state tracking
    - Time-based event filtering
    - Fast querying and aggregation
    - Thread-safe operations
    """
    
    def __init__(self, max_events: int = 10000, cleanup_interval: int = 300):
        """
        Initialize the data store.
        
        Args:
            max_events: Maximum number of events to store
            cleanup_interval: Cleanup interval in seconds
        """
        self.max_events = max_events
        self.cleanup_interval = cleanup_interval
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Event storage
        self._events: deque[ProcessedEvent] = deque(maxlen=max_events)
        self._events_by_type: Dict[str, List[ProcessedEvent]] = defaultdict(list)
        self._events_by_category: Dict[EventCategory, List[ProcessedEvent]] = defaultdict(list)
        
        # Current game state
        self._game_state = GameState()
        
        # Statistics and performance tracking
        self._stats = {
            'total_events_processed': 0,
            'events_by_type_count': defaultdict(int),
            'events_by_category_count': defaultdict(int),
            'last_cleanup': time.time(),
            'store_start_time': time.time()
        }
        
        # Cleanup tracking
        self._last_cleanup = time.time()
        
        # State update handlers
        self._state_handlers: Dict[str, Callable[[ProcessedEvent], None]] = {
            'FSDJump': self._handle_fsd_jump,
            'SupercruiseEntry': self._handle_supercruise_entry,
            'SupercruiseExit': self._handle_supercruise_exit,
            'Docked': self._handle_docked,
            'Undocked': self._handle_undocked,
            'Touchdown': self._handle_touchdown,
            'Liftoff': self._handle_liftoff,
            'LoadGame': self._handle_load_game,
            'Loadout': self._handle_loadout,
            'ShipyardBuy': self._handle_ship_purchase,
            'ShipyardSell': self._handle_ship_sale,
            'ShipyardSwap': self._handle_ship_swap,
            'Status': self._handle_status_update,
            'Location': self._handle_location_update,
            'Statistics': self._handle_statistics_update,
        }
    
    def store_event(self, event: ProcessedEvent) -> None:
        """
        Store a processed event and update game state.

        Args:
            event: The processed event to store
            
        Raises:
            EventStorageError: If there's an error storing the event
        """
        try:
            with self._lock:
                # Add to main storage
                self._events.append(event)
                
                # Add to type-specific storage
                self._events_by_type[event.event_type].append(event)
                
                # Add to category-specific storage
                self._events_by_category[event.category].append(event)
                
                # Update statistics
                self._stats['total_events_processed'] += 1
                self._stats['events_by_type_count'][event.event_type] += 1
                self._stats['events_by_category_count'][event.category] += 1
                
                # Update game state
                self._update_game_state(event)
                
                # Perform cleanup if needed
                self._cleanup_if_needed()
                
        except Exception as e:
            raise EventStorageError(f"Failed to store event: {e}") from e
    
    def query_events(self, 
                    filter_criteria: Optional[EventFilter] = None,
                    sort_order: QuerySortOrder = QuerySortOrder.NEWEST_FIRST) -> List[ProcessedEvent]:
        """
        Query events based on filter criteria.
        
        Args:
            filter_criteria: Filter to apply to events
            sort_order: How to sort the results
            
        Returns:
            List of events matching the criteria
        """
        with self._lock:
            events = list(self._events)
            
            # Apply filters
            if filter_criteria:
                events = self._apply_filters(events, filter_criteria)
            
            # Sort events
            events = self._sort_events(events, sort_order)
            
            # Limit results
            if filter_criteria and filter_criteria.max_results:
                events = events[:filter_criteria.max_results]
            
            return events
    
    def get_events_by_type(self, event_type: str, limit: Optional[int] = None) -> List[ProcessedEvent]:
        """Get events of a specific type."""
        with self._lock:
            events = self._events_by_type.get(event_type, [])
            if limit:
                events = events[-limit:]  # Get most recent
            return list(events)
    
    def get_events_by_category(self, category: EventCategory, limit: Optional[int] = None) -> List[ProcessedEvent]:
        """Get events of a specific category."""
        with self._lock:
            events = self._events_by_category.get(category, [])
            if limit:
                events = events[-limit:]  # Get most recent
            return list(events)
    
    def get_recent_events(self, minutes: int = 60) -> List[ProcessedEvent]:
        """Get events from the last N minutes."""
        # Fixed: Use timezone-aware datetime to match event timestamps
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        filter_criteria = EventFilter(start_time=cutoff_time)
        return self.query_events(filter_criteria)
    
    def get_game_state(self) -> GameState:
        """Get the current game state."""
        with self._lock:
            # Return a copy to prevent external modification
            return GameState(
                current_system=self._game_state.current_system,
                current_station=self._game_state.current_station,
                current_body=self._game_state.current_body,
                coordinates=self._game_state.coordinates.copy() if self._game_state.coordinates else None,
                current_ship=self._game_state.current_ship,
                ship_name=self._game_state.ship_name,
                ship_id=self._game_state.ship_id,
                ship_modules=self._game_state.ship_modules.copy(),
                docked=self._game_state.docked,
                landed=self._game_state.landed,
                in_srv=self._game_state.in_srv,
                in_fighter=self._game_state.in_fighter,
                supercruise=self._game_state.supercruise,
                fsd_charging=self._game_state.fsd_charging,
                fsd_cooldown=self._game_state.fsd_cooldown,
                low_fuel=self._game_state.low_fuel,
                overheating=self._game_state.overheating,
                has_lat_long=self._game_state.has_lat_long,
                is_in_danger=self._game_state.is_in_danger,
                being_interdicted=self._game_state.being_interdicted,
                in_main_ship=self._game_state.in_main_ship,
                analysis_mode=self._game_state.analysis_mode,
                night_vision=self._game_state.night_vision,
                altitude_from_average_radius=self._game_state.altitude_from_average_radius,
                game_mode=self._game_state.game_mode,
                group=self._game_state.group,
                commander_name=self._game_state.commander_name,
                credits=self._game_state.credits,
                loan=self._game_state.loan,
                cargo_capacity=self._game_state.cargo_capacity,
                cargo_count=self._game_state.cargo_count,
                fuel_level=self._game_state.fuel_level,
                fuel_capacity=self._game_state.fuel_capacity,
                last_updated=self._game_state.last_updated
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        with self._lock:
            uptime = time.time() - self._stats['store_start_time']
            return {
                'total_events': len(self._events),
                'total_processed': self._stats['total_events_processed'],
                'events_by_type': dict(self._stats['events_by_type_count']),
                'events_by_category': {cat.value: count for cat, count in self._stats['events_by_category_count'].items()},
                'uptime_seconds': uptime,
                'last_cleanup': self._stats['last_cleanup'],
                'memory_usage_events': len(self._events),
                'max_events': self.max_events,
                'storage_efficiency': len(self._events) / self.max_events * 100 if self.max_events > 0 else 0
            }
    
    def cleanup_old_events(self, max_age_hours: int = 24) -> int:
        """
        Clean up events older than specified age.
        
        Args:
            max_age_hours: Maximum age of events to keep
            
        Returns:
            Number of events removed
        """
        # Fixed: Use timezone-aware datetime for consistency
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        with self._lock:
            initial_count = len(self._events)
            
            # Filter events by age
            self._events = deque(
                [event for event in self._events if event.timestamp >= cutoff_time],
                maxlen=self.max_events
            )
            
            # Rebuild type and category indexes
            self._rebuild_indexes()
            
            # Update statistics
            removed_count = initial_count - len(self._events)
            self._stats['last_cleanup'] = time.time()
            
            return removed_count
    
    def clear(self) -> None:
        """Clear all stored events and reset game state."""
        with self._lock:
            self._events.clear()
            self._events_by_type.clear()
            self._events_by_category.clear()
            self._game_state = GameState()
            
            # Reset statistics except for totals
            self._stats['events_by_type_count'].clear()
            self._stats['events_by_category_count'].clear()
            self._stats['last_cleanup'] = time.time()
    
    # Private methods
    
    def _apply_filters(self, events: List[ProcessedEvent], filter_criteria: EventFilter) -> List[ProcessedEvent]:
        """Apply filter criteria to events."""
        filtered_events = events
        
        # Filter by event types
        if filter_criteria.event_types:
            filtered_events = [e for e in filtered_events if e.event_type in filter_criteria.event_types]
        
        # Filter by categories
        if filter_criteria.categories:
            filtered_events = [e for e in filtered_events if e.category in filter_criteria.categories]
        
        # Filter by time range
        if filter_criteria.start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= filter_criteria.start_time]
        
        if filter_criteria.end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= filter_criteria.end_time]
        
        # Filter by system names - FIXED: use key_data instead of extracted_data
        if filter_criteria.system_names:
            filtered_events = [
                e for e in filtered_events 
                if hasattr(e, 'key_data') and e.key_data.get('system_name') in filter_criteria.system_names
            ]
        
        # Filter by ship types - FIXED: use key_data instead of extracted_data
        if filter_criteria.ship_types:
            filtered_events = [
                e for e in filtered_events 
                if hasattr(e, 'key_data') and e.key_data.get('ship_type') in filter_criteria.ship_types
            ]
        
        # Filter by text content - FIXED: use raw_event instead of raw_data
        if filter_criteria.contains_text:
            text_lower = filter_criteria.contains_text.lower()
            filtered_events = [
                e for e in filtered_events 
                if text_lower in e.summary.lower() or text_lower in str(e.raw_event).lower()
            ]
        
        # Filter by importance
        if filter_criteria.min_importance is not None:
            filtered_events = [
                e for e in filtered_events 
                if getattr(e, 'importance', 0) >= filter_criteria.min_importance
            ]
        
        return filtered_events
    
    def _sort_events(self, events: List[ProcessedEvent], sort_order: QuerySortOrder) -> List[ProcessedEvent]:
        """Sort events according to specified order."""
        if sort_order == QuerySortOrder.NEWEST_FIRST:
            return sorted(events, key=lambda e: e.timestamp, reverse=True)
        elif sort_order == QuerySortOrder.OLDEST_FIRST:
            return sorted(events, key=lambda e: e.timestamp)
        elif sort_order == QuerySortOrder.RELEVANCE:
            # Sort by importance (if available) then by timestamp
            return sorted(events, key=lambda e: (getattr(e, 'importance', 0), e.timestamp), reverse=True)
        else:
            return events
    
    def _update_game_state(self, event: ProcessedEvent) -> None:
        """Update game state based on event."""
        # Update last updated timestamp
        self._game_state.last_updated = event.timestamp
        
        # Call specific handler if available
        handler = self._state_handlers.get(event.event_type)
        if handler:
            handler(event)
    
    def _handle_fsd_jump(self, event: ProcessedEvent) -> None:
        """Handle FSD jump events."""
        # Use both key_data and raw_event to extract system information
        data = event.key_data or {}
        raw_data = event.raw_event or {}

        # Try multiple field names to extract system name
        system_name = (
            data.get('system_name') or  # From key_data
            data.get('system') or       # Alternative key_data field
            raw_data.get('StarSystem')  # From raw_event
        )

        self._game_state.current_system = system_name
        self._game_state.coordinates = {
            'x': data.get('star_pos_x') or raw_data.get('StarPosX'),
            'y': data.get('star_pos_y') or raw_data.get('StarPosY'),
            'z': data.get('star_pos_z') or raw_data.get('StarPosZ')
        }
        self._game_state.current_station = None
        self._game_state.current_body = None
        self._game_state.docked = False
        self._game_state.supercruise = True
    
    def _handle_supercruise_entry(self, event: ProcessedEvent) -> None:
        """Handle supercruise entry."""
        self._game_state.supercruise = True
        self._game_state.docked = False
        self._game_state.landed = False
    
    def _handle_supercruise_exit(self, event: ProcessedEvent) -> None:
        """Handle supercruise exit."""
        self._game_state.supercruise = False
        # FIXED: use key_data instead of extracted_data and correct field names
        data = event.key_data
        self._game_state.current_body = data.get('body')  # Changed from 'body_name'
    
    def _handle_docked(self, event: ProcessedEvent) -> None:
        """Handle docking events."""
        self._game_state.docked = True
        self._game_state.landed = False
        self._game_state.supercruise = False
        # Use both key_data and raw_event to extract station information
        data = event.key_data or {}
        raw_data = event.raw_event or {}

        # Try multiple field names to extract station name
        station_name = (
            data.get('station_name') or  # From key_data
            data.get('station') or       # Alternative key_data field
            raw_data.get('StationName')  # From raw_event
        )

        self._game_state.current_station = station_name
    
    def _handle_undocked(self, event: ProcessedEvent) -> None:
        """Handle undocking events."""
        self._game_state.docked = False
        self._game_state.current_station = None
    
    def _handle_touchdown(self, event: ProcessedEvent) -> None:
        """Handle landing events."""
        self._game_state.landed = True
        self._game_state.docked = False
        self._game_state.supercruise = False
    
    def _handle_liftoff(self, event: ProcessedEvent) -> None:
        """Handle takeoff events."""
        self._game_state.landed = False
    
    def _handle_load_game(self, event: ProcessedEvent) -> None:
        """Handle game load events."""
        # Use both key_data and raw_event to extract LoadGame information
        data = event.key_data or {}
        raw_data = event.raw_event or {}

        # Extract commander name from multiple possible sources
        commander_name = (
            data.get('commander') or
            data.get('commander_name') or
            raw_data.get('Commander')
        )

        # Extract ship information from multiple sources
        ship_type = (
            data.get('ship_type') or
            data.get('ship') or
            raw_data.get('Ship')
        )

        ship_name = (
            data.get('ship_name') or
            raw_data.get('ShipName')
        )

        self._game_state.commander_name = commander_name
        self._game_state.current_ship = ship_type
        self._game_state.ship_name = ship_name
        self._game_state.ship_id = data.get('ship_id') or raw_data.get('ShipID')
        self._game_state.game_mode = data.get('game_mode') or raw_data.get('GameMode')
        self._game_state.group = data.get('group') or raw_data.get('Group')
        self._game_state.credits = data.get('credits') or raw_data.get('Credits', 0)
        self._game_state.loan = data.get('loan') or raw_data.get('Loan', 0)

        # Store fuel info for contextual generation
        self._game_state.fuel_level = (
            data.get('fuel_level') or
            raw_data.get('FuelLevel', 100.0)
        )
        self._game_state.fuel_capacity = (
            data.get('fuel_capacity') or
            raw_data.get('FuelCapacity', 32.0)
        )
    
    def _handle_loadout(self, event: ProcessedEvent) -> None:
        """Handle ship loadout events."""
        # FIXED: use key_data instead of extracted_data and correct field names
        data = event.key_data
        self._game_state.current_ship = data.get('ship')  # Changed from 'ship_type' to 'ship'
        self._game_state.ship_name = data.get('ship_name')
        self._game_state.ship_id = data.get('ship_id')
        if 'modules' in data:
            self._game_state.ship_modules = data['modules']
    
    def _handle_ship_purchase(self, event: ProcessedEvent) -> None:
        """Handle ship purchase events."""
        # FIXED: use key_data instead of extracted_data
        data = event.key_data
        self._game_state.current_ship = data.get('ship_type')
        self._game_state.ship_name = data.get('ship_name')
        self._game_state.ship_id = data.get('ship_id')
    
    def _handle_ship_sale(self, event: ProcessedEvent) -> None:
        """Handle ship sale events."""
        # Ship sale doesn't change current ship unless it was the active one
        pass
    
    def _handle_ship_swap(self, event: ProcessedEvent) -> None:
        """Handle ship swap events."""
        # FIXED: use key_data instead of extracted_data
        data = event.key_data
        self._game_state.current_ship = data.get('ship_type')
        self._game_state.ship_name = data.get('ship_name')
        self._game_state.ship_id = data.get('ship_id')
    
    def _handle_status_update(self, event: ProcessedEvent) -> None:
        """Handle status file updates."""
        # FIXED: use key_data instead of extracted_data
        data = event.key_data
        
        # Update various status flags
        flags = data.get('flags', 0)
        self._game_state.docked = bool(flags & 0x01)
        self._game_state.landed = bool(flags & 0x02)
        self._game_state.supercruise = bool(flags & 0x10)
        self._game_state.fsd_charging = bool(flags & 0x20)
        self._game_state.fsd_cooldown = bool(flags & 0x40)
        self._game_state.low_fuel = bool(flags & 0x80)
        self._game_state.overheating = bool(flags & 0x100)
        self._game_state.has_lat_long = bool(flags & 0x200)
        self._game_state.is_in_danger = bool(flags & 0x400)
        self._game_state.being_interdicted = bool(flags & 0x800)
        self._game_state.in_main_ship = bool(flags & 0x1000)
        self._game_state.in_fighter = bool(flags & 0x2000)
        self._game_state.in_srv = bool(flags & 0x4000)
        self._game_state.analysis_mode = bool(flags & 0x8000)
        self._game_state.night_vision = bool(flags & 0x10000)
        self._game_state.altitude_from_average_radius = bool(flags & 0x20000)
    
    def _handle_location_update(self, event: ProcessedEvent) -> None:
        """Handle location updates."""
        # Extract data from both key_data and raw_event with multiple field name variants
        data = event.key_data or {}
        raw_data = event.raw_event or {}

        # Try multiple field names for system
        system_name = (
            data.get('system') or
            data.get('system_name') or
            raw_data.get('StarSystem')
        )
        if system_name:
            self._game_state.current_system = system_name

        # Try multiple field names for station
        station_name = (
            data.get('station') or
            data.get('station_name') or
            raw_data.get('StationName')
        )
        if station_name:
            self._game_state.current_station = station_name

        # Try multiple field names for body
        body_name = (
            data.get('body') or
            data.get('body_name') or
            raw_data.get('Body')
        )
        if body_name:
            self._game_state.current_body = body_name

        # Update docked status from Location event
        docked = data.get('docked') or raw_data.get('Docked')
        if docked is not None:
            self._game_state.docked = docked

        if 'star_pos' in data:
            self._game_state.coordinates = data['star_pos']
    
    def _handle_statistics_update(self, event: ProcessedEvent) -> None:
        """Handle statistics updates."""
        # FIXED: use key_data instead of extracted_data
        data = event.key_data
        self._game_state.credits = data.get('credits', self._game_state.credits)
    
    def _cleanup_if_needed(self) -> None:
        """Perform cleanup if enough time has passed."""
        current_time = time.time()
        if current_time - self._last_cleanup >= self.cleanup_interval:
            self._last_cleanup = current_time
            # Just update the timestamp - the deque handles size automatically
            self._stats['last_cleanup'] = current_time
    
    def _rebuild_indexes(self) -> None:
        """Rebuild type and category indexes after cleanup."""
        self._events_by_type.clear()
        self._events_by_category.clear()
        
        for event in self._events:
            self._events_by_type[event.event_type].append(event)
            self._events_by_category[event.category].append(event)


# Global data store instance
_data_store: Optional[DataStore] = None


def get_data_store() -> DataStore:
    """Get the global data store instance."""
    global _data_store
    if _data_store is None:
        _data_store = DataStore()
    return _data_store


def reset_data_store() -> None:
    """Reset the global data store instance."""
    global _data_store
    _data_store = None
