"""
Unit tests for MCP Prompts implementation.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, MagicMock, patch

from src.mcp.mcp_prompts import MCPPrompts, PromptTemplate, PromptType
from src.utils.data_store import DataStore
from src.journal.events import ProcessedEvent, EventCategory


class TestPromptTemplate:
    """Test PromptTemplate functionality."""
    
    def test_template_initialization(self):
        """Test template initialization with proper attributes."""
        template = PromptTemplate(
            name="Test Template",
            description="A test template",
            template="Hello {name}!",
            variables=["name"]
        )
        
        assert template.name == "Test Template"
        assert template.description == "A test template"
        assert template.template == "Hello {name}!"
        assert template.variables == ["name"]
    
    def test_template_render_success(self):
        """Test successful template rendering."""
        template = PromptTemplate(
            name="Test Template",
            description="A test template",
            template="Hello {name}, you have {credits} credits!",
            variables=["name", "credits"]
        )
        
        context = {"name": "Commander", "credits": 1000000}
        result = template.render(context)
        
        assert result == "Hello Commander, you have 1000000 credits!"
    
    def test_template_render_missing_variables(self):
        """Test template rendering with missing variables."""
        template = PromptTemplate(
            name="Test Template",
            description="A test template",
            template="Hello {name}, you have {credits} credits!",
            variables=["name", "credits"]
        )
        
        context = {"name": "Commander"}  # Missing credits
        result = template.render(context)
        
        assert "Commander" in result
        assert "[CREDITS_NOT_AVAILABLE]" in result
    
    def test_template_render_error_handling(self):
        """Test template rendering error handling."""
        template = PromptTemplate(
            name="Test Template",
            description="A test template",
            template="Hello {name!",  # Invalid template syntax
            variables=["name"]
        )
        
        context = {"name": "Commander"}
        result = template.render(context)
        
        assert "Error rendering prompt template" in result


class TestMCPPrompts:
    """Test MCPPrompts functionality."""
    
    @pytest.fixture
    def mock_data_store(self):
        """Create a mock data store with test data."""
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
        
        # Mock events
        mock_event1 = ProcessedEvent(
            timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
            event_type="FSDJump",
            category=EventCategory.NAVIGATION,
            raw_event={"StarSystem": "Alpha Centauri", "JumpDist": 4.37},
            summary="Jumped to Alpha Centauri"
        )

        mock_event2 = ProcessedEvent(
            timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
            event_type="Scan",
            category=EventCategory.EXPLORATION,
            raw_event={"BodyName": "Alpha Centauri A", "ScanType": "Detailed"},
            summary="Scanned Alpha Centauri A"
        )

        mock_event3 = ProcessedEvent(
            timestamp=datetime.now(timezone.utc) - timedelta(hours=3),
            event_type="MarketSell",
            category=EventCategory.TRADING,
            raw_event={"Type": "Gold", "Profit": 50000},
            summary="Sold Gold for 50,000 CR profit"
        )
        
        store.get_recent_events.return_value = [mock_event1, mock_event2, mock_event3]
        store.get_events_by_type.return_value = [mock_event1]
        store.get_events_by_category.return_value = [mock_event2]
        
        return store
    
    @pytest.fixture
    def prompts(self, mock_data_store):
        """Create MCPPrompts instance with mock data store."""
        return MCPPrompts(mock_data_store)
    
    def test_initialization(self, prompts):
        """Test MCPPrompts initialization."""
        assert prompts.data_store is not None
        assert isinstance(prompts.templates, dict)
        assert len(prompts.templates) > 0
        
        # Check specific templates exist
        expected_templates = [
            "exploration_analysis",
            "trading_strategy",
            "combat_assessment",
            "mining_optimization",
            "mission_guidance",
            "engineering_progress",
            "journey_review",
            "performance_review",
            "strategic_planning"
        ]
        
        for template_id in expected_templates:
            assert template_id in prompts.templates
    
    def test_list_available_prompts(self, prompts):
        """Test listing available prompts."""
        prompt_list = prompts.list_available_prompts()
        
        assert isinstance(prompt_list, list)
        assert len(prompt_list) > 0
        
        # Check structure of prompt definitions
        for prompt in prompt_list:
            assert "id" in prompt
            assert "name" in prompt
            assert "description" in prompt
            assert "variables" in prompt
            assert "type" in prompt
    
    def test_get_prompt_type(self, prompts):
        """Test prompt type classification."""
        assert prompts._get_prompt_type("exploration_analysis") == PromptType.EXPLORATION.value
        assert prompts._get_prompt_type("trading_strategy") == PromptType.TRADING.value
        assert prompts._get_prompt_type("combat_assessment") == PromptType.COMBAT.value
        assert prompts._get_prompt_type("mining_optimization") == PromptType.MINING.value
        assert prompts._get_prompt_type("mission_guidance") == PromptType.MISSIONS.value
        assert prompts._get_prompt_type("engineering_progress") == PromptType.ENGINEERING.value
        assert prompts._get_prompt_type("journey_review") == PromptType.JOURNEY.value
        assert prompts._get_prompt_type("performance_review") == PromptType.PERFORMANCE.value
        assert prompts._get_prompt_type("strategic_planning") == PromptType.STRATEGY.value
        assert prompts._get_prompt_type("unknown_template") == "general"
    
    @pytest.mark.asyncio
    async def test_generate_prompt_invalid_template(self, prompts):
        """Test prompt generation with invalid template ID."""
        result = await prompts.generate_prompt("invalid_template")
        
        assert "Invalid template ID" in result
        assert "invalid_template" in result
    
    @pytest.mark.asyncio
    async def test_generate_exploration_prompt(self, prompts, mock_data_store):
        """Test exploration prompt generation."""
        result = await prompts.generate_prompt("exploration_analysis", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "exploration" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
        assert "Pioneer" in result  # Exploration rank
    
    @pytest.mark.asyncio
    async def test_generate_trading_prompt(self, prompts, mock_data_store):
        """Test trading prompt generation."""
        result = await prompts.generate_prompt("trading_strategy", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "trading" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
        assert "Tycoon" in result  # Trade rank
    
    @pytest.mark.asyncio
    async def test_generate_combat_prompt(self, prompts, mock_data_store):
        """Test combat prompt generation."""
        result = await prompts.generate_prompt("combat_assessment", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "combat" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
        assert "Elite" in result  # Combat rank
    
    @pytest.mark.asyncio
    async def test_generate_mining_prompt(self, prompts, mock_data_store):
        """Test mining prompt generation."""
        result = await prompts.generate_prompt("mining_optimization", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "mining" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
    
    @pytest.mark.asyncio
    async def test_generate_mission_prompt(self, prompts, mock_data_store):
        """Test mission prompt generation."""
        result = await prompts.generate_prompt("mission_guidance", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "mission" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
    
    @pytest.mark.asyncio
    async def test_generate_engineering_prompt(self, prompts, mock_data_store):
        """Test engineering prompt generation."""
        result = await prompts.generate_prompt("engineering_progress", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "engineering" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
    
    @pytest.mark.asyncio
    async def test_generate_journey_prompt(self, prompts, mock_data_store):
        """Test journey prompt generation."""
        result = await prompts.generate_prompt("journey_review", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "journey" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
    
    @pytest.mark.asyncio
    async def test_generate_performance_prompt(self, prompts, mock_data_store):
        """Test performance prompt generation."""
        result = await prompts.generate_prompt("performance_review", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "performance" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
    
    @pytest.mark.asyncio
    async def test_generate_strategic_prompt(self, prompts, mock_data_store):
        """Test strategic prompt generation."""
        result = await prompts.generate_prompt("strategic_planning", 24)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "strategic" in result.lower() or "planning" in result.lower()
        assert "Sol" in result  # Current system
        assert "Python" in result  # Current ship
    
    @pytest.mark.asyncio
    async def test_build_context_basic(self, prompts, mock_data_store):
        """Test basic context building."""
        context = await prompts._build_context("exploration_analysis", 24)
        
        # Check basic game state context
        assert context["current_system"] == "Sol"
        assert context["current_ship"] == "Python"
        assert context["credits"] == 1000000
        assert context["hull_health"] == 100.0
        assert context["fuel_level"] == 32.0
        assert context["time_range"] == 24
        assert context["combat_rank"] == "Elite"
        assert context["trade_rank"] == "Tycoon"
        assert context["exploration_rank"] == "Pioneer"
    
    @pytest.mark.asyncio
    async def test_build_exploration_context(self, prompts, mock_data_store):
        """Test exploration-specific context building."""
        recent_events = [
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
                event_type="FSDJump",
                category=EventCategory.NAVIGATION,
                raw_event={"StarSystem": "Alpha Centauri", "JumpDist": 4.37},
                summary="Jumped to Alpha Centauri"
            ),
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
                event_type="Scan",
                category=EventCategory.EXPLORATION,
                raw_event={"BodyName": "Alpha Centauri A", "ScanType": "Detailed"},
                summary="Scanned Alpha Centauri A"
            )
        ]
        
        context = await prompts._build_exploration_context(recent_events, 24)
        
        assert "systems_visited" in context
        assert "bodies_scanned" in context
        assert "distance_ly" in context
        assert "exploration_earnings" in context
        assert "recent_systems" in context
        assert "scan_summary" in context
        
        assert context["systems_visited"] >= 1
        assert context["bodies_scanned"] >= 1
        assert context["distance_ly"] >= 0
    
    @pytest.mark.asyncio
    async def test_build_trading_context(self, prompts, mock_data_store):
        """Test trading-specific context building."""
        recent_events = [
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
                event_type="MarketSell",
                category=EventCategory.TRADING,
                raw_event={"Type": "Gold", "Profit": 50000},
                summary="Sold Gold for 50,000 CR profit"
            ),
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
                event_type="MarketBuy",
                category=EventCategory.TRADING,
                raw_event={"Type": "Gold", "Cost": 450000},
                summary="Bought Gold for 450,000 CR"
            )
        ]
        
        # Mock loadout events for cargo capacity
        mock_data_store.get_events_by_type.return_value = [
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc),
                event_type="Loadout",
                category=EventCategory.SHIP,
                raw_event={"CargoCapacity": 284},
                summary="Ship loadout"
            )
        ]
        
        context = await prompts._build_trading_context(recent_events, 24)
        
        assert "cargo_capacity" in context
        assert "total_profit" in context
        assert "trade_count" in context
        assert "avg_profit_per_trade" in context
        assert "profit_per_hour" in context
        assert "best_trades" in context
        assert "market_opportunities" in context
        
        assert context["cargo_capacity"] == 284
        assert context["total_profit"] >= 0
    
    @pytest.mark.asyncio
    async def test_build_combat_context(self, prompts, mock_data_store):
        """Test combat-specific context building."""
        recent_events = [
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
                event_type="Bounty",
                category=EventCategory.COMBAT,
                raw_event={"Reward": 100000, "Target": "Pirate"},
                summary="Bounty claimed: 100,000 CR"
            ),
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
                event_type="FactionKillBond",
                category=EventCategory.COMBAT,
                raw_event={"Reward": 75000, "AwardingFaction": "Federation"},
                summary="Combat bond: 75,000 CR"
            )
        ]
        
        context = await prompts._build_combat_context(recent_events, 24)
        
        assert "bounties_earned" in context
        assert "combat_bonds" in context
        assert "ships_destroyed" in context
        assert "deaths" in context
        assert "survival_rate" in context
        assert "combat_events" in context
        assert "ship_loadout" in context
        
        assert context["bounties_earned"] >= 0
        assert context["combat_bonds"] >= 0
        assert context["ships_destroyed"] >= 0
    
    @pytest.mark.asyncio
    async def test_build_mining_context(self, prompts, mock_data_store):
        """Test mining-specific context building."""
        recent_events = [
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
                event_type="MaterialCollected",
                category=EventCategory.MINING,
                raw_event={"Name": "Painite", "MarketValue": 50000},
                summary="Collected Painite"
            ),
            ProcessedEvent(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
                event_type="AsteroidCracked",
                category=EventCategory.MINING,
                raw_event={"Body": "Asteroid"},
                summary="Cracked asteroid"
            )
        ]
        
        # Mock cargo and loadout events
        mock_data_store.get_events_by_type.side_effect = lambda event_type, limit=None: {
            "Cargo": [ProcessedEvent(
                timestamp=datetime.now(timezone.utc),
                event_type="Cargo",
                category=EventCategory.SHIP,
                raw_event={"Inventory": [{"Name": "Painite", "Count": 5}]},
                summary="Cargo inventory"
            )],
            "Loadout": [ProcessedEvent(
                timestamp=datetime.now(timezone.utc),
                event_type="Loadout",
                category=EventCategory.SHIP,
                raw_event={"CargoCapacity": 284},
                summary="Ship loadout"
            )]
        }.get(event_type, [])
        
        context = await prompts._build_mining_context(recent_events, 24)
        
        assert "cargo_used" in context
        assert "cargo_capacity" in context
        assert "materials_collected" in context
        assert "asteroids_mined" in context
        assert "mining_earnings" in context
        assert "avg_value_per_ton" in context
        assert "materials_summary" in context
        assert "mining_equipment" in context
        
        assert context["cargo_capacity"] == 284
        assert context["materials_collected"] >= 0
    
    @pytest.mark.asyncio
    async def test_error_handling_build_context(self, prompts, mock_data_store):
        """Test error handling in context building."""
        # Make data store throw an exception
        mock_data_store.get_game_state.side_effect = Exception("Test error")
        
        context = await prompts._build_context("exploration_analysis", 24)
        
        assert "error" in context
        assert "Test error" in context["error"]
    
    @pytest.mark.asyncio
    async def test_error_handling_generate_prompt(self, prompts, mock_data_store):
        """Test error handling in prompt generation."""
        # Make context building fail
        with patch.object(prompts, '_build_context', side_effect=Exception("Context error")):
            result = await prompts.generate_prompt("exploration_analysis", 24)
            
            assert "Error generating prompt" in result
            assert "Context error" in result
    
    def test_template_content_completeness(self, prompts):
        """Test that all templates have reasonable content and required fields."""
        for template_id, template in prompts.templates.items():
            # Check template has required attributes
            assert hasattr(template, 'name')
            assert hasattr(template, 'description')
            assert hasattr(template, 'template')
            assert hasattr(template, 'variables')
            
            # Check content is not empty
            assert len(template.name) > 0
            assert len(template.description) > 0
            assert len(template.template) > 100  # Substantial content
            assert len(template.variables) > 0
            
            # Check template contains variable placeholders
            for variable in template.variables:
                assert f"{{{variable}}}" in template.template
    
    @pytest.mark.asyncio
    async def test_prompt_contains_game_context(self, prompts, mock_data_store):
        """Test that generated prompts contain relevant game context."""
        for template_id in prompts.templates.keys():
            result = await prompts.generate_prompt(template_id, 24)
            
            # Should contain basic game state info
            assert "Sol" in result  # Current system
            assert "Python" in result  # Current ship
            assert "1,000,000" in result or "1000000" in result  # Credits formatted
            
            # Should not contain error messages
            assert "Error" not in result
    
    @pytest.mark.asyncio
    async def test_different_time_ranges(self, prompts, mock_data_store):
        """Test prompt generation with different time ranges."""
        template_id = "exploration_analysis"
        
        result_24h = await prompts.generate_prompt(template_id, 24)
        result_12h = await prompts.generate_prompt(template_id, 12)
        result_48h = await prompts.generate_prompt(template_id, 48)
        
        # All should be valid prompts
        assert len(result_24h) > 0
        assert len(result_12h) > 0
        assert len(result_48h) > 0
        
        # Should contain time range information
        assert "24" in result_24h
        assert "12" in result_12h
        assert "48" in result_48h
    
    @pytest.mark.asyncio
    async def test_template_variable_coverage(self, prompts, mock_data_store):
        """Test that context building covers all template variables."""
        for template_id, template in prompts.templates.items():
            context = await prompts._build_context(template_id, 24)
            
            # Check that we have values for most variables (allowing for some placeholders)
            missing_count = 0
            for variable in template.variables:
                if variable not in context:
                    missing_count += 1
                elif isinstance(context[variable], str) and "NOT_AVAILABLE" in context[variable]:
                    missing_count += 1
            
            # Should have most variables available (allow some missing for complex scenarios)
            coverage_ratio = (len(template.variables) - missing_count) / len(template.variables)
            assert coverage_ratio >= 0.5, f"Template {template_id} has insufficient variable coverage"
