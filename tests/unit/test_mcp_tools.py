"""
Comprehensive tests for MCP tools functionality.

Tests all core MCP tools including location queries, event searching,
activity summaries, and performance metrics.
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, MagicMock, patch

from src.mcp.mcp_tools import MCPTools, ActivityType
from src.journal.events import ProcessedEvent, EventCategory
from src.utils.data_store import DataStore, GameState, EventFilter


class TestMCPTools:
    """Test suite for MCP tools functionality."""
    
    @pytest.fixture
    def mock_data_store(self):
        """Create a mock data store with test data."""
        store = Mock(spec=DataStore)
        
        # Mock game state
        game_state = GameState(
            current_system="Sol",
            current_station="Abraham Lincoln",
            current_body=None,
            coordinates={"x": 0, "y": 0, "z": 0},
            current_ship="AspExplorer",
            ship_name="Wanderer",
            ship_id="ASP-01",
            docked=True,
            landed=False,
            in_srv=False,
            in_fighter=False,
            supercruise=False,
            low_fuel=False,
            overheating=False,
            is_in_danger=False,
            being_interdicted=False,
            credits=1000000,
            cargo_capacity=64,
            cargo_count=32,
            last_updated=datetime.now(timezone.utc)
        )
        store.get_game_state.return_value = game_state
        
        # Mock statistics
        store.get_statistics.return_value = {
            "total_events": 100,
            "total_processed": 100,
            "events_by_type": {"FSDJump": 10, "Scan": 20},
            "events_by_category": {"exploration": 30, "navigation": 20}
        }
        
        return store
    
    @pytest.fixture
    def mcp_tools(self, mock_data_store):
        """Create MCP tools instance with mock data store."""
        return MCPTools(mock_data_store)
    
    @pytest.fixture
    def sample_events(self):
        """Create sample processed events for testing."""
        now = datetime.now(timezone.utc)
        
        events = [
            ProcessedEvent(
                raw_event={"event": "FSDJump", "StarSystem": "Alpha Centauri", "JumpDist": 4.37},
                event_type="FSDJump",
                timestamp=now - timedelta(hours=1),
                category=EventCategory.NAVIGATION,
                summary="Jumped to Alpha Centauri (4.37ly)",
                key_data={"system": "Alpha Centauri", "distance": 4.37, "fuel_used": 0.5}
            ),
            ProcessedEvent(
                raw_event={"event": "Scan", "BodyName": "Earth-like World"},
                event_type="Scan",
                timestamp=now - timedelta(minutes=30),
                category=EventCategory.EXPLORATION,
                summary="Scanned Earth-like World",
                key_data={"body_name": "Earth-like World", "terraformable": True, "landable": False}
            ),
            ProcessedEvent(
                raw_event={"event": "MarketSell", "Type": "Gold", "Count": 10, "SellPrice": 50000},
                event_type="MarketSell",
                timestamp=now - timedelta(minutes=15),
                category=EventCategory.TRADING,
                summary="Sold 10t of Gold for 500,000 credits",
                key_data={"commodity": "Gold", "count": 10, "total": 500000}
            ),
            ProcessedEvent(
                raw_event={"event": "Bounty", "Target": "Pirate", "TotalReward": 100000},
                event_type="Bounty",
                timestamp=now - timedelta(minutes=5),
                category=EventCategory.COMBAT,
                summary="Collected bounty on Pirate for 100,000 credits",
                key_data={"target": "Pirate", "reward": 100000, "faction": "Federation"}
            )
        ]
        
        return events
    
    # ==================== Location and Status Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_current_location(self, mcp_tools, mock_data_store, sample_events):
        """Test getting current location information."""
        mock_data_store.get_events_by_type.return_value = [sample_events[0]]
        
        result = await mcp_tools.get_current_location()
        
        assert result["current_system"] == "Sol"
        assert result["current_station"] == "Abraham Lincoln"
        assert result["docked"] is True
        assert result["landed"] is False
        assert "coordinates" in result
        assert "recent_systems" in result
    
    @pytest.mark.asyncio
    async def test_get_current_location_error(self, mcp_tools, mock_data_store):
        """Test error handling in get_current_location."""
        mock_data_store.get_game_state.side_effect = Exception("Database error")
        
        result = await mcp_tools.get_current_location()
        
        assert "error" in result
        assert "Database error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_ship_status(self, mcp_tools, mock_data_store):
        """Test getting ship status information."""
        mock_data_store.get_events_by_type.return_value = []
        
        result = await mcp_tools.get_ship_status()
        
        assert result["ship_type"] == "AspExplorer"
        assert result["ship_name"] == "Wanderer"
        assert result["ship_id"] == "ASP-01"
        assert result["status"]["docked"] is True
        assert result["status"]["low_fuel"] is False
        assert "recent_maintenance" in result
    
    @pytest.mark.asyncio
    async def test_get_ship_status_with_loadout(self, mcp_tools, mock_data_store):
        """Test ship status with loadout information."""
        loadout_event = ProcessedEvent(
            raw_event={"event": "Loadout", "HullValue": 1000000, "ModulesValue": 500000, "Rebuy": 75000},
            event_type="Loadout",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.SHIP,
            summary="Loadout for AspExplorer",
            key_data={}
        )
        
        mock_data_store.get_events_by_type.return_value = [loadout_event]
        
        result = await mcp_tools.get_ship_status()
        
        assert result["hull_value"] == 1000000
        assert result["modules_value"] == 500000
        assert result["rebuy"] == 75000
    
    # ==================== Event Search Tests ====================
    
    @pytest.mark.asyncio
    async def test_search_events_basic(self, mcp_tools, mock_data_store, sample_events):
        """Test basic event searching."""
        mock_data_store.query_events.return_value = sample_events
        
        result = await mcp_tools.search_events(
            event_types=["FSDJump", "Scan"],
            max_results=10
        )
        
        assert result["total_found"] == 4
        assert len(result["events"]) == 4
        assert result["search_criteria"]["event_types"] == ["FSDJump", "Scan"]
        
        # Verify filter was called with correct parameters
        call_args = mock_data_store.query_events.call_args
        filter_criteria = call_args[1]["filter_criteria"]
        assert filter_criteria.max_results == 10
        assert "FSDJump" in filter_criteria.event_types
    
    @pytest.mark.asyncio
    async def test_search_events_by_category(self, mcp_tools, mock_data_store, sample_events):
        """Test searching events by category."""
        exploration_events = [e for e in sample_events if e.category == EventCategory.EXPLORATION]
        mock_data_store.query_events.return_value = exploration_events
        
        result = await mcp_tools.search_events(
            categories=["exploration"],
            time_range_minutes=60
        )
        
        assert result["total_found"] == 1
        assert result["events"][0]["category"] == "exploration"
    
    @pytest.mark.asyncio
    async def test_search_events_with_text(self, mcp_tools, mock_data_store, sample_events):
        """Test text search in events."""
        mock_data_store.query_events.return_value = [sample_events[2]]  # Gold trade
        
        result = await mcp_tools.search_events(
            contains_text="Gold",
            max_results=5
        )
        
        assert result["total_found"] == 1
        assert "Gold" in result["events"][0]["summary"]
    
    @pytest.mark.asyncio
    async def test_search_events_error(self, mcp_tools, mock_data_store):
        """Test error handling in event search."""
        mock_data_store.query_events.side_effect = Exception("Search failed")
        
        result = await mcp_tools.search_events()
        
        assert "error" in result
        assert "Search failed" in result["error"]
    
    # ==================== Activity Summary Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_exploration_summary(self, mcp_tools, mock_data_store, sample_events):
        """Test exploration activity summary."""
        exploration_events = [sample_events[1]]  # Scan event
        mock_data_store.query_events.return_value = exploration_events
        
        result = await mcp_tools.get_activity_summary("exploration", 24)
        
        assert result["activity_type"] == "exploration"
        assert result["bodies_scanned"] == 1
        assert result["terraformable_found"] == 1
        assert len(result["valuable_bodies"]) == 1
        assert result["valuable_bodies"][0]["terraformable"] is True
    
    @pytest.mark.asyncio
    async def test_get_trading_summary(self, mcp_tools, mock_data_store, sample_events):
        """Test trading activity summary."""
        trading_events = [sample_events[2]]  # MarketSell event
        mock_data_store.query_events.return_value = trading_events
        
        result = await mcp_tools.get_activity_summary("trading", 24)
        
        assert result["activity_type"] == "trading"
        assert result["total_profit"] == 500000
        assert "Gold" in result["commodities_traded"]
        assert result["commodities_traded"]["Gold"]["earned"] == 500000
        assert len(result["best_trades"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_combat_summary(self, mcp_tools, mock_data_store, sample_events):
        """Test combat activity summary."""
        combat_events = [sample_events[3]]  # Bounty event
        mock_data_store.query_events.return_value = combat_events
        
        result = await mcp_tools.get_activity_summary("combat", 24)
        
        assert result["activity_type"] == "combat"
        assert result["bounties_collected"] == 1
        assert result["total_bounty_value"] == 100000
        assert len(result["kills"]) == 1
        assert result["kills"][0]["target"] == "Pirate"
    
    @pytest.mark.asyncio
    async def test_get_mining_summary(self, mcp_tools, mock_data_store):
        """Test mining activity summary."""
        mining_event = ProcessedEvent(
            raw_event={"event": "MiningRefined", "Type": "Platinum"},
            event_type="MiningRefined",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.MINING,
            summary="Refined Platinum",
            key_data={}
        )
        
        mock_data_store.query_events.return_value = [mining_event]
        
        result = await mcp_tools.get_activity_summary("mining", 24)
        
        assert result["activity_type"] == "mining"
        assert "Platinum" in result["materials_mined"]
        assert result["materials_mined"]["Platinum"] == 1
    
    @pytest.mark.asyncio
    async def test_get_mission_summary(self, mcp_tools, mock_data_store):
        """Test mission activity summary."""
        mission_events = [
            ProcessedEvent(
                raw_event={"event": "MissionAccepted", "MissionID": 123},
                event_type="MissionAccepted",
                timestamp=datetime.now(timezone.utc),
                category=EventCategory.MISSION,
                summary="Accepted mission from Federation",
                key_data={"name": "Delivery", "faction": "Federation", "reward": 50000}
            ),
            ProcessedEvent(
                raw_event={"event": "MissionCompleted", "MissionID": 123},
                event_type="MissionCompleted",
                timestamp=datetime.now(timezone.utc),
                category=EventCategory.MISSION,
                summary="Completed mission for Federation",
                key_data={"faction": "Federation", "reward": 50000}
            )
        ]
        
        mock_data_store.query_events.return_value = mission_events
        
        result = await mcp_tools.get_activity_summary("missions", 24)
        
        assert result["activity_type"] == "missions"
        assert result["missions_accepted"] == 1
        assert result["missions_completed"] == 1
        assert result["total_rewards"] == 50000
        assert "Federation" in result["factions_worked_for"]
    
    @pytest.mark.asyncio
    async def test_get_engineering_summary(self, mcp_tools, mock_data_store):
        """Test engineering activity summary."""
        engineering_event = ProcessedEvent(
            raw_event={"event": "EngineerCraft"},
            event_type="EngineerCraft",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.ENGINEERING,
            summary="Applied modification",
            key_data={
                "engineer": "Felicity Farseer",
                "module": "Frame Shift Drive",
                "blueprint": "Increased Range",
                "level": 5
            }
        )
        
        mock_data_store.query_events.return_value = [engineering_event]
        
        result = await mcp_tools.get_activity_summary("engineering", 24)
        
        assert result["activity_type"] == "engineering"
        assert result["modifications_applied"] == 1
        assert "Felicity Farseer" in result["engineers_visited"]
        assert "Frame Shift Drive" in result["modules_modified"]
    
    @pytest.mark.asyncio
    async def test_invalid_activity_type(self, mcp_tools, mock_data_store):
        """Test error handling for invalid activity type."""
        result = await mcp_tools.get_activity_summary("invalid_type", 24)
        
        assert "error" in result
        assert "Invalid activity type" in result["error"]
    
    # ==================== Journey and Navigation Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_journey_summary(self, mcp_tools, mock_data_store, sample_events):
        """Test journey summary generation."""
        nav_events = [sample_events[0]]  # FSDJump event
        mock_data_store.query_events.return_value = nav_events
        
        result = await mcp_tools.get_journey_summary(24)
        
        assert result["total_jumps"] == 1
        assert result["total_distance"] == 4.37
        assert result["fuel_used"] == 0.5
        assert len(result["systems_visited"]) == 1
        assert result["unique_systems"] == 1
        assert result["average_jump_distance"] == 4.37
    
    @pytest.mark.asyncio
    async def test_get_journey_summary_with_docking(self, mcp_tools, mock_data_store):
        """Test journey summary with docking events."""
        docking_event = ProcessedEvent(
            raw_event={"event": "Docked", "StationName": "Columbus"},
            event_type="Docked",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.NAVIGATION,
            summary="Docked at Columbus",
            key_data={"station": "Columbus", "system": "Sol", "station_type": "Orbis"}
        )
        
        mock_data_store.query_events.return_value = [docking_event]
        
        result = await mcp_tools.get_journey_summary(24)
        
        assert len(result["stations_docked"]) == 1
        assert result["stations_docked"][0]["station"] == "Columbus"
        assert len(result["route_map"]) == 1
        assert result["route_map"][0]["type"] == "dock"
    
    # ==================== Performance Metrics Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, mcp_tools, mock_data_store, sample_events):
        """Test performance metrics calculation."""
        mock_data_store.query_events.return_value = sample_events
        
        result = await mcp_tools.get_performance_metrics(24)
        
        assert result["total_events"] == 4
        assert result["credits_earned"] == 600000  # 500k trade + 100k bounty
        assert result["net_profit"] == 600000  # No spending events
        assert "efficiency_metrics" in result
        assert "activity_breakdown" in result
        assert "achievements" in result
    
    @pytest.mark.asyncio
    async def test_performance_metrics_with_achievements(self, mcp_tools, mock_data_store):
        """Test achievement detection in performance metrics."""
        # Create events that trigger achievements
        events = []
        for i in range(51):  # 51 exploration events
            events.append(ProcessedEvent(
                raw_event={"event": "Scan"},
                event_type="Scan",
                timestamp=datetime.now(timezone.utc),
                category=EventCategory.EXPLORATION,
                summary="Scanned body",
                key_data={}
            ))
        
        # Add high-value trade
        events.append(ProcessedEvent(
            raw_event={"event": "MarketSell"},
            event_type="MarketSell",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.TRADING,
            summary="Big sale",
            key_data={"total": 2000000}
        ))
        
        mock_data_store.query_events.return_value = events
        
        result = await mcp_tools.get_performance_metrics(24)
        
        assert "Millionaire" in " ".join(result["achievements"])
        assert "Explorer" in " ".join(result["achievements"])
    
    # ==================== Specialized Query Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_faction_standings(self, mcp_tools, mock_data_store):
        """Test faction standings retrieval."""
        rep_event = ProcessedEvent(
            raw_event={
                "event": "Reputation",
                "Reputation": [
                    {"Faction": "Federation", "Reputation": 75, "Trend": "UpGood"},
                    {"Faction": "Empire", "Reputation": -10, "Trend": "DownBad"}
                ]
            },
            event_type="Reputation",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.SOCIAL,
            summary="Reputation update",
            key_data={}
        )
        
        mock_data_store.get_events_by_type.return_value = [rep_event]
        mock_data_store.query_events.return_value = []
        
        result = await mcp_tools.get_faction_standings()
        
        assert "Federation" in result["current_reputation"]
        assert result["current_reputation"]["Federation"]["reputation"] == 75
        assert result["current_reputation"]["Federation"]["trend"] == "UpGood"
        assert "Empire" in result["current_reputation"]
    
    @pytest.mark.asyncio
    async def test_get_material_inventory(self, mcp_tools, mock_data_store):
        """Test material inventory retrieval."""
        cargo_event = ProcessedEvent(
            raw_event={
                "event": "Cargo",
                "Inventory": [
                    {"Name": "Gold", "Count": 10, "Stolen": 0},
                    {"Name": "Silver", "Count": 20, "Stolen": 5}
                ]
            },
            event_type="Cargo",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.SHIP,
            summary="Cargo update",
            key_data={}
        )
        
        materials_event = ProcessedEvent(
            raw_event={
                "event": "Materials",
                "Raw": [{"Name": "Iron", "Count": 50}],
                "Manufactured": [{"Name": "Shield Emitters", "Count": 10}],
                "Encoded": [{"Name": "Shield Data", "Count": 20}]
            },
            event_type="Materials",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.SHIP,
            summary="Materials update",
            key_data={}
        )
        
        mock_data_store.get_events_by_type.side_effect = [
            [cargo_event],  # First call for Cargo
            [materials_event]  # Second call for Materials
        ]
        mock_data_store.query_events.return_value = []
        
        result = await mcp_tools.get_material_inventory()
        
        assert "Gold" in result["cargo"]
        assert result["cargo"]["Gold"]["count"] == 10
        assert "Iron" in result["materials"]["raw"]
        assert result["materials"]["raw"]["Iron"] == 50
        assert "Shield Emitters" in result["materials"]["manufactured"]
        assert "Shield Data" in result["materials"]["encoded"]
    
    # ==================== Error Handling Tests ====================
    
    @pytest.mark.asyncio
    async def test_activity_summary_error(self, mcp_tools, mock_data_store):
        """Test error handling in activity summary."""
        mock_data_store.query_events.side_effect = Exception("Query failed")
        
        result = await mcp_tools.get_activity_summary("exploration", 24)
        
        assert "error" in result
        assert "Query failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_journey_summary_error(self, mcp_tools, mock_data_store):
        """Test error handling in journey summary."""
        mock_data_store.get_game_state.side_effect = Exception("State error")
        
        result = await mcp_tools.get_journey_summary(24)
        
        assert "error" in result
        assert "State error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_performance_metrics_error(self, mcp_tools, mock_data_store):
        """Test error handling in performance metrics."""
        mock_data_store.query_events.side_effect = Exception("Metrics error")
        
        result = await mcp_tools.get_performance_metrics(24)
        
        assert "error" in result
        assert "Metrics error" in result["error"]


class TestActivityType:
    """Test ActivityType enum."""
    
    def test_activity_type_values(self):
        """Test ActivityType enum has all expected values."""
        assert ActivityType.EXPLORATION.value == "exploration"
        assert ActivityType.TRADING.value == "trading"
        assert ActivityType.COMBAT.value == "combat"
        assert ActivityType.MINING.value == "mining"
        assert ActivityType.MISSIONS.value == "missions"
        assert ActivityType.ENGINEERING.value == "engineering"
        assert ActivityType.PASSENGER.value == "passenger"
        assert ActivityType.FLEET_CARRIER.value == "fleet_carrier"
    
    def test_activity_type_from_string(self):
        """Test creating ActivityType from string."""
        activity = ActivityType("exploration")
        assert activity == ActivityType.EXPLORATION
        
        with pytest.raises(ValueError):
            ActivityType("invalid_activity")
