"""
Unit tests for MCP Resources implementation.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock

from src.elite_mcp.mcp_resources import MCPResources, ResourceCache, ResourceType
from src.utils.data_store import DataStore
from src.journal.events import ProcessedEvent, EventCategory


class TestResourceCache:
    """Test ResourceCache functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """Test setting and getting cached values."""
        cache = ResourceCache(ttl_seconds=30)
        
        # Set a value
        await cache.set("test_key", {"data": "test_value"})
        
        # Get the value
        result = await cache.get("test_key")
        assert result == {"data": "test_value"}
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """Test cache expiration."""
        cache = ResourceCache(ttl_seconds=0)  # Immediate expiration
        
        # Set a value
        await cache.set("test_key", {"data": "test_value"})
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Value should be expired
        result = await cache.get("test_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_clear(self):
        """Test clearing the cache."""
        cache = ResourceCache(ttl_seconds=30)
        
        # Set multiple values
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        
        # Clear cache
        await cache.clear()
        
        # All values should be gone
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
    
    def test_make_key(self):
        """Test cache key generation."""
        cache = ResourceCache()
        
        # Test consistent key generation
        key1 = cache.make_key("resource_type", {"param1": "value1", "param2": "value2"})
        key2 = cache.make_key("resource_type", {"param2": "value2", "param1": "value1"})
        
        # Keys should be identical regardless of parameter order
        assert key1 == key2
        
        # Different parameters should produce different keys
        key3 = cache.make_key("resource_type", {"param1": "different"})
        assert key1 != key3


class TestMCPResources:
    """Test MCPResources functionality."""
    
    @pytest.fixture
    def mock_data_store(self):
        """Create a mock data store."""
        store = Mock(spec=DataStore)
        
        # Mock game state
        game_state = Mock()
        game_state.current_system = "Sol"
        game_state.current_station = "Earth Station"
        game_state.current_ship = "Python"
        game_state.docked = True
        game_state.fuel_level = 32.0
        game_state.hull_health = 100.0
        game_state.credits = 1000000
        game_state.current_coordinates = [0, 0, 0]
        game_state.ranks = {"Combat": "Elite", "Trade": "Tycoon", "Explore": "Pioneer"}
        game_state.last_updated = datetime.now(timezone.utc)
        store.get_game_state.return_value = game_state
        
        # Mock statistics
        store.get_statistics.return_value = {
            "total_events": 1000,
            "unique_event_types": 50,
            "events_in_last_hour": 100
        }
        
        # Mock events
        mock_event = ProcessedEvent(
            raw_event={"event": "FSDJump", "timestamp": datetime.now(timezone.utc).isoformat(), "StarSystem": "Alpha Centauri", "JumpDist": 4.37},
            event_type="FSDJump",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.NAVIGATION,
            summary="Jumped to Alpha Centauri",
            key_data={"StarSystem": "Alpha Centauri", "JumpDist": 4.37}
        )
        store.query_events.return_value = [mock_event]
        store.get_recent_events.return_value = [mock_event]
        store.get_events_by_type.return_value = [mock_event]
        store.get_events_by_category.return_value = [mock_event]
        
        return store
    
    @pytest.fixture
    def resources(self, mock_data_store):
        """Create MCPResources instance with mock data store."""
        return MCPResources(mock_data_store)
    
    def test_list_resources(self, resources):
        """Test listing available resources."""
        resource_list = resources.list_resources()
        
        # Check we have resources
        assert len(resource_list) > 0
        
        # Check resource structure
        for resource in resource_list:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource
        
        # Check specific resources exist
        uris = [r["uri"] for r in resource_list]
        assert "elite://status/current" in uris
        assert "elite://journal/recent" in uris
        assert "elite://events/search" in uris
        assert "elite://summary/exploration" in uris
    
    def test_parse_resource_uri(self, resources):
        """Test URI parsing."""
        # Test simple URI
        base_uri, params = resources.parse_resource_uri("elite://status/current")
        assert base_uri == "elite://status/current"
        assert params == {}
        
        # Test URI with parameters
        base_uri, params = resources.parse_resource_uri("elite://journal/recent?minutes=30")
        assert base_uri == "elite://journal/recent"
        assert params == {"minutes": "30"}
        
        # Test URI with multiple parameters
        base_uri, params = resources.parse_resource_uri(
            "elite://events/search?type=FSDJump&category=navigation&minutes=60"
        )
        assert base_uri == "elite://events/search"
        assert params == {"type": "FSDJump", "category": "navigation", "minutes": "60"}
    
    @pytest.mark.asyncio
    async def test_get_current_status(self, resources, mock_data_store):
        """Test getting current status resource."""
        result = await resources.get_resource("elite://status/current")
        
        assert result is not None
        assert "location" in result
        assert result["location"]["system"] == "Sol"
        assert result["location"]["station"] == "Earth Station"
        assert "ship" in result
        assert result["ship"]["type"] == "Python"
        assert "commander" in result
        assert result["commander"]["credits"] == 1000000
    
    @pytest.mark.asyncio
    async def test_get_location_status(self, resources, mock_data_store):
        """Test getting location status resource."""
        result = await resources.get_resource("elite://status/location")
        
        assert result is not None
        assert result["current_system"] == "Sol"
        assert result["current_station"] == "Earth Station"
        assert result["docked"] is True
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_get_ship_status(self, resources, mock_data_store):
        """Test getting ship status resource."""
        result = await resources.get_resource("elite://status/ship")
        
        assert result is not None
        assert result["ship_type"] == "Python"
        assert "fuel" in result
        assert result["fuel"]["level"] == 32.0
        assert "health" in result
        assert result["health"]["hull"] == 100.0
    
    @pytest.mark.asyncio
    async def test_get_recent_journal(self, resources, mock_data_store):
        """Test getting recent journal entries."""
        result = await resources.get_resource("elite://journal/recent?minutes=60")
        
        assert result is not None
        assert result["time_range_minutes"] == 60
        assert result["total_events"] == 1
        assert "events_by_category" in result
        mock_data_store.get_recent_events.assert_called_once_with(minutes=60)
    
    @pytest.mark.asyncio
    async def test_get_journal_stats(self, resources, mock_data_store):
        """Test getting journal statistics."""
        result = await resources.get_resource("elite://journal/stats")
        
        assert result is not None
        assert result["total_events"] == 1000
        assert result["unique_event_types"] == 50
        assert result["events_in_last_hour"] == 100
        assert "category_distribution" in result
    
    @pytest.mark.asyncio
    async def test_get_events_by_category(self, resources, mock_data_store):
        """Test getting events by category."""
        result = await resources.get_resource("elite://events/by-category?category=navigation")
        
        assert result is not None
        assert result["category"] == "navigation"
        assert result["event_count"] == 1
        assert "events" in result
    
    @pytest.mark.asyncio
    async def test_get_events_by_category_invalid(self, resources, mock_data_store):
        """Test getting events with invalid category."""
        result = await resources.get_resource("elite://events/by-category?category=invalid")
        
        assert result is not None
        assert "error" in result
        assert "valid_categories" in result
    
    @pytest.mark.asyncio
    async def test_get_events_by_type(self, resources, mock_data_store):
        """Test getting events by type."""
        result = await resources.get_resource("elite://events/by-type?type=FSDJump")
        
        assert result is not None
        assert result["event_type"] == "FSDJump"
        assert result["event_count"] == 1
        assert "events" in result
    
    @pytest.mark.asyncio
    async def test_search_events(self, resources, mock_data_store):
        """Test searching events with multiple filters."""
        result = await resources.get_resource(
            "elite://events/search?type=FSDJump&category=navigation&minutes=60"
        )
        
        assert result is not None
        assert "search_params" in result
        assert result["search_params"]["type"] == "FSDJump"
        assert result["search_params"]["category"] == "navigation"
        assert result["result_count"] >= 0
        assert "events" in result
    
    @pytest.mark.asyncio
    async def test_get_exploration_summary(self, resources, mock_data_store):
        """Test getting exploration summary."""
        result = await resources.get_resource("elite://summary/exploration?hours=24")
        
        assert result is not None
        assert result["activity"] == "exploration"
        assert result["time_range_hours"] == 24
        assert "systems_visited" in result
        assert "bodies_scanned" in result
    
    @pytest.mark.asyncio
    async def test_get_trading_summary(self, resources, mock_data_store):
        """Test getting trading summary."""
        result = await resources.get_resource("elite://summary/trading?hours=12")
        
        assert result is not None
        assert result["activity"] == "trading"
        assert result["time_range_hours"] == 12
        assert "total_profit" in result
        assert "trades_count" in result
    
    @pytest.mark.asyncio
    async def test_get_combat_summary(self, resources, mock_data_store):
        """Test getting combat summary."""
        result = await resources.get_resource("elite://summary/combat")
        
        assert result is not None
        assert result["activity"] == "combat"
        assert "bounties_earned" in result
        assert "kills" in result
    
    @pytest.mark.asyncio
    async def test_get_mining_summary(self, resources, mock_data_store):
        """Test getting mining summary."""
        result = await resources.get_resource("elite://summary/mining")
        
        assert result is not None
        assert result["activity"] == "mining"
        assert "materials_collected" in result
        assert "asteroids_prospected" in result
    
    @pytest.mark.asyncio
    async def test_get_journey_summary(self, resources, mock_data_store):
        """Test getting journey summary."""
        result = await resources.get_resource("elite://summary/journey?hours=48")
        
        assert result is not None
        assert result["activity"] == "journey"
        assert result["time_range_hours"] == 48
        assert "total_jumps" in result
        assert "total_distance_ly" in result
        assert "systems_visited" in result
    
    @pytest.mark.asyncio
    async def test_get_material_state(self, resources, mock_data_store):
        """Test getting material inventory."""
        result = await resources.get_resource("elite://state/materials")
        
        assert result is not None
        assert "materials" in result
        assert "cargo" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_get_faction_state(self, resources, mock_data_store):
        """Test getting faction standings."""
        result = await resources.get_resource("elite://state/factions")
        
        assert result is not None
        assert "major_factions" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, resources, mock_data_store):
        """Test getting performance metrics."""
        result = await resources.get_resource("elite://metrics/performance?hours=24")
        
        assert result is not None
        assert result["time_range_hours"] == 24
        assert "credits_earned" in result
        assert "credits_spent" in result
        assert "net_credits" in result
        assert "jumps_made" in result
    
    @pytest.mark.asyncio
    async def test_get_credit_metrics(self, resources, mock_data_store):
        """Test getting credit flow metrics."""
        result = await resources.get_resource("elite://metrics/credits?hours=12")
        
        assert result is not None
        assert result["time_range_hours"] == 12
        assert "total_earned" in result
        assert "total_spent" in result
        assert "top_earnings" in result
        assert "top_expenses" in result
    
    @pytest.mark.asyncio
    async def test_invalid_resource_uri(self, resources):
        """Test handling of invalid resource URI."""
        result = await resources.get_resource("elite://invalid/resource")

        assert result is not None
        assert "error" in result
        assert "available_resources" in result
    
    @pytest.mark.asyncio
    async def test_caching_behavior(self, resources, mock_data_store):
        """Test that caching works correctly."""
        # First call should hit the data store
        result1 = await resources.get_resource("elite://status/current")
        assert mock_data_store.get_game_state.call_count == 1
        
        # Second call should use cache
        result2 = await resources.get_resource("elite://status/current")
        assert mock_data_store.get_game_state.call_count == 1  # No additional call
        
        # Results should be identical
        assert result1 == result2
        
        # Clear cache and call again
        await resources.clear_cache()
        result3 = await resources.get_resource("elite://status/current")
        assert mock_data_store.get_game_state.call_count == 2  # New call made
    
    @pytest.mark.asyncio
    async def test_error_handling(self, resources, mock_data_store):
        """Test error handling in resource retrieval."""
        # Make data store throw an exception
        mock_data_store.get_game_state.side_effect = Exception("Test error")
        
        result = await resources.get_resource("elite://status/current")
        
        assert result is not None
        assert "error" in result
        assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_activity_summary_unknown_type(self, resources, mock_data_store):
        """Test activity summary with unknown activity type."""
        result = await resources.get_resource("elite://summary/unknown")
        
        assert result is not None
        assert "error" in result
        assert "valid_activities" in result
    
    @pytest.mark.asyncio
    async def test_default_parameter_values(self, resources, mock_data_store):
        """Test resources use default parameter values when not specified."""
        # Journal recent should default to 60 minutes
        result = await resources.get_resource("elite://journal/recent")
        assert result["time_range_minutes"] == 60
        
        # Activity summaries should default to 24 hours
        result = await resources.get_resource("elite://summary/exploration")
        assert result["time_range_hours"] == 24
    
    @pytest.mark.asyncio
    async def test_resource_metadata(self, resources):
        """Test that all resources have proper metadata."""
        resource_list = resources.list_resources()
        
        for resource in resource_list:
            # Check required fields
            assert resource["uri"]
            assert resource["name"]
            assert resource["description"]
            assert resource["mimeType"] == "application/json"
            
            # Check that parameterized resources have parameters listed
            if "?" in resource["description"] or "supports" in resource["description"]:
                if "summary" in resource["uri"] or "journal/recent" in resource["uri"]:
                    assert "parameters" in resource
