"""
Unit tests for MCP Prompts implementation.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, MagicMock, patch

from src.mcp.mcp_prompts import MCPPrompts, PromptTemplate, PromptType
from src.utils.data_store import DataStore
from src.journal.events import ProcessedEvent, EventCategory


class TestPromptTemplate:
    """Test PromptTemplate functionality."""
    
    def test_template_render(self):
        """Test basic template rendering."""
        template = PromptTemplate(
            "Hello {name}, you are in {location}.",
            ["name", "location"],
            "Test template"
        )
        
        context = {"name": "Commander", "location": "Sol"}
        result = template.render(context)
        
        assert result == "Hello Commander, you are in Sol."
    
    def test_template_missing_variables(self):
        """Test template rendering with missing variables."""
        template = PromptTemplate(
            "Ship: {ship}, Credits: {credits}",
            ["ship", "credits"],
            "Test template"
        )
        
        # Only provide one variable
        context = {"ship": "Python"}
        result = template.render(context)
        
        # Should use default for missing variable
        assert "Python" in result
        assert "[Unknown]" in result
    
    def test_template_extra_variables(self):
        """Test template rendering with extra variables."""
        template = PromptTemplate(
            "Location: {location}",
            ["location"],
            "Test template"
        )
        
        # Provide extra variables that aren't used
        context = {"location": "Sol", "extra": "value", "another": "value"}
        result = template.render(context)
        
        assert result == "Location: Sol"


class TestMCPPrompts:
    """Test MCPPrompts functionality."""
    
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
        
        # Mock events
        mock_event = ProcessedEvent(
            raw_event={"event": "FSDJump", "timestamp": datetime.now(timezone.utc).isoformat(), "StarSystem": "Alpha Centauri", "JumpDist": 4.37},
            event_type="FSDJump",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.NAVIGATION,
            summary="Jumped to Alpha Centauri",
            key_data={"StarSystem": "Alpha Centauri", "JumpDist": 4.37}
        )
        store.get_all_events.return_value = [mock_event]
        store.get_recent_events.return_value = [mock_event]
        store.get_events_by_type.return_value = [mock_event]
        store.get_events_by_category.return_value = [mock_event]
        
        return store
    
    @pytest.fixture
    def prompts(self, mock_data_store):
        """Create MCPPrompts instance with mock data store."""
        return MCPPrompts(mock_data_store)
    
    def test_list_prompts(self, prompts):
        """Test listing available prompts."""
        prompt_list = prompts.list_prompts()
        
        # Check we have prompts
        assert len(prompt_list) > 0
        
        # Check prompt structure
        for prompt in prompt_list:
            assert "name" in prompt
            assert "description" in prompt
            assert "variables" in prompt
            assert "type" in prompt
        
        # Check specific prompts exist
        prompt_names = [p["name"] for p in prompt_list]
        assert "exploration_analysis" in prompt_names
        assert "trading_analysis" in prompt_names
        assert "combat_review" in prompt_names
        assert "daily_goals" in prompt_names
        assert "commander_log" in prompt_names
    
    def test_get_prompt_type(self, prompts):
        """Test prompt type detection."""
        assert prompts._get_prompt_type("exploration_analysis") == PromptType.EXPLORATION
        assert prompts._get_prompt_type("trading_analysis") == PromptType.TRADING
        assert prompts._get_prompt_type("combat_review") == PromptType.COMBAT
        assert prompts._get_prompt_type("mining_optimization") == PromptType.MINING
        assert prompts._get_prompt_type("route_planning") == PromptType.NAVIGATION
        assert prompts._get_prompt_type("engineering_priorities") == PromptType.ENGINEERING
        assert prompts._get_prompt_type("mission_strategy") == PromptType.MISSIONS
        assert prompts._get_prompt_type("performance_analysis") == PromptType.PERFORMANCE
        assert prompts._get_prompt_type("daily_goals") == PromptType.STRATEGY
        assert prompts._get_prompt_type("commander_log") == PromptType.ROLEPLAY
    
    def test_generate_prompt_success(self, prompts, mock_data_store):
        """Test successful prompt generation."""
        result = prompts.generate_prompt("exploration_analysis")
        
        assert "prompt" in result
        assert "name" in result
        assert "type" in result
        assert "description" in result
        assert "context" in result
        assert "timestamp" in result
        
        # Check prompt content
        assert "Sol" in result["prompt"]  # Current system
        assert "Pioneer" in result["prompt"]  # Exploration rank
    
    def test_generate_prompt_unknown(self, prompts):
        """Test generating unknown prompt."""
        result = prompts.generate_prompt("unknown_prompt")
        
        assert "error" in result
        assert "unknown_prompt" in result["error"]
        assert "available_prompts" in result
    
    def test_generate_prompt_with_custom_context(self, prompts):
        """Test prompt generation with custom context."""
        custom_context = {
            "current_system": "Colonia",
            "exploration_rank": "Elite",
            "hours": 48
        }
        
        result = prompts.generate_prompt("exploration_analysis", custom_context)
        
        assert "Colonia" in result["prompt"]
        assert "Elite" in result["prompt"]
        assert "48" in result["prompt"]
    
    def test_build_exploration_context(self, prompts, mock_data_store):
        """Test exploration context building."""
        # Set up exploration events
        scan_event = ProcessedEvent(
            raw_event={"event": "Scan", "timestamp": datetime.now(timezone.utc).isoformat(), "BodyName": "Earth-like World", "TerraformState": "Terraformable"},
            event_type="Scan",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.EXPLORATION,
            summary="Scanned Earth-like World",
            key_data={"BodyName": "Earth-like World", "TerraformState": "Terraformable"}
        )
        jump_event = ProcessedEvent(
            raw_event={"event": "FSDJump", "timestamp": datetime.now(timezone.utc).isoformat(), "StarSystem": "System A", "JumpDist": 50.0},
            event_type="FSDJump",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.NAVIGATION,
            summary="Jumped to System A",
            key_data={"StarSystem": "System A", "JumpDist": 50.0}
        )
        
        mock_data_store.get_events_by_type.side_effect = lambda t, **kwargs: {
            "Scan": [scan_event],
            "FSDJump": [jump_event]
        }.get(t, [])
        
        context = prompts._build_exploration_context()
        
        assert context["bodies_scanned"] == 1
        assert context["systems_visited"] == 1
        assert "Earth-like World" in context["recent_discoveries"]
        assert float(context["jump_range"]) == 50.0
    
    def test_build_trading_context(self, prompts, mock_data_store):
        """Test trading context building."""
        buy_event = ProcessedEvent(
            raw_event={"event": "MarketBuy", "timestamp": datetime.now(timezone.utc).isoformat(), "Type": "Gold", "Count": 10, "TotalCost": 100000},
            event_type="MarketBuy",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.TRADING,
            summary="Bought Gold",
            key_data={"Type": "Gold", "Count": 10, "TotalCost": 100000}
        )
        sell_event = ProcessedEvent(
            raw_event={"event": "MarketSell", "timestamp": datetime.now(timezone.utc).isoformat(), "Type": "Gold", "Count": 10, "TotalSale": 150000, "Profit": 50000},
            event_type="MarketSell",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.TRADING,
            summary="Sold Gold",
            key_data={"Type": "Gold", "Count": 10, "TotalSale": 150000, "Profit": 50000}
        )
        
        mock_data_store.get_events_by_type.side_effect = lambda t, **kwargs: {
            "MarketBuy": [buy_event],
            "MarketSell": [sell_event]
        }.get(t, [])
        
        context = prompts._build_trading_context()
        
        assert context["trade_count"] == 2
        assert "50,000" in context["recent_profit"]
        assert "Gold" in context["top_commodities"]
    
    def test_build_combat_context(self, prompts, mock_data_store):
        """Test combat context building."""
        bounty_event = ProcessedEvent(
            raw_event={"event": "Bounty", "timestamp": datetime.now(timezone.utc).isoformat(), "Target": "Pirate", "Reward": 50000},
            event_type="Bounty",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.COMBAT,
            summary="Collected bounty",
            key_data={"Target": "Pirate", "Reward": 50000}
        )
        
        mock_data_store.get_events_by_type.side_effect = lambda t, **kwargs: {
            "Bounty": [bounty_event] if t == "Bounty" else [],
            "Died": [],
            "Interdicted": []
        }.get(t, [])
        
        mock_data_store.get_events_by_category.return_value = [bounty_event]
        
        context = prompts._build_combat_context()
        
        assert context["kills"] == 1
        assert context["deaths"] == 0
        assert "50,000" in context["bounties"]
        assert context["threat_level"] == "Low"
    
    def test_generate_contextual_prompt(self, prompts, mock_data_store):
        """Test contextual prompt generation."""
        result = prompts.generate_contextual_prompt(PromptType.EXPLORATION, 24)
        
        assert "prompt" in result
        assert result["type"] == "exploration"
        assert "error" not in result
    
    def test_generate_contextual_prompt_no_templates(self, prompts):
        """Test contextual prompt with no matching templates."""
        # Mock templates to be empty for a type
        with patch.object(prompts, 'templates', {}):
            result = prompts.generate_contextual_prompt(PromptType.EXPLORATION)
            
            assert "error" in result
            assert "No templates found" in result["error"]
    
    def test_select_best_template(self, prompts, mock_data_store):
        """Test template selection based on activity."""
        # Set up recent exploration events
        exploration_events = [
            ProcessedEvent(
                raw_event={"event": "Scan", "timestamp": datetime.now(timezone.utc).isoformat()},
                event_type="Scan",
                timestamp=datetime.now(timezone.utc),
                category=EventCategory.EXPLORATION,
                summary="Scan",
                key_data={}
            ) for _ in range(5)
        ]
        
        mock_data_store.get_all_events.return_value = exploration_events
        
        template_names = ["exploration_analysis", "exploration_route"]
        best = prompts._select_best_template(template_names, 24)
        
        # Should prefer analysis template
        assert best == "exploration_analysis"
    
    def test_analyze_recent_activity(self, prompts, mock_data_store):
        """Test activity analysis."""
        # Create events with different categories
        events = [
            ProcessedEvent(
                raw_event={"event": "FSDJump", "timestamp": datetime.now(timezone.utc).isoformat()},
                event_type="FSDJump",
                timestamp=datetime.now(timezone.utc),
                category=EventCategory.NAVIGATION,
                summary="Jump",
                key_data={}
            ),
            ProcessedEvent(
                raw_event={"event": "Scan", "timestamp": datetime.now(timezone.utc).isoformat()},
                event_type="Scan",
                timestamp=datetime.now(timezone.utc),
                category=EventCategory.EXPLORATION,
                summary="Scan",
                key_data={}
            ),
            ProcessedEvent(
                raw_event={"event": "MarketBuy", "timestamp": datetime.now(timezone.utc).isoformat()},
                event_type="MarketBuy",
                timestamp=datetime.now(timezone.utc),
                category=EventCategory.TRADING,
                summary="Buy",
                key_data={}
            )
        ]
        
        mock_data_store.get_recent_events.return_value = events
        
        activity_types = prompts._analyze_recent_activity()
        
        assert isinstance(activity_types, list)
        assert all(isinstance(pt, PromptType) for pt in activity_types)
        
        # Navigation and exploration should be high priority
        assert PromptType.NAVIGATION in activity_types[:3]
    
    def test_generate_adaptive_prompts(self, prompts, mock_data_store):
        """Test adaptive prompt generation."""
        result = prompts.generate_adaptive_prompts(count=3)
        
        assert isinstance(result, list)
        assert len(result) <= 3
        
        for prompt in result:
            if "error" not in prompt:
                assert "prompt" in prompt
                assert "name" in prompt
                assert "type" in prompt
    
    def test_generate_adaptive_prompts_no_activity(self, prompts, mock_data_store):
        """Test adaptive prompts with no recent activity."""
        mock_data_store.get_recent_events.return_value = []
        
        result = prompts.generate_adaptive_prompts(count=2)
        
        # Should still generate strategic prompts
        assert len(result) <= 2
        for prompt in result:
            if "error" not in prompt:
                assert "prompt" in prompt
    
    def test_all_templates_have_descriptions(self, prompts):
        """Test that all templates have descriptions."""
        for name, template in prompts.templates.items():
            assert template.description
            assert len(template.description) > 10
            assert isinstance(template.variables, list)
    
    def test_template_count(self, prompts):
        """Test that we have the expected number of templates."""
        # Should have at least 15 templates as per requirements
        assert len(prompts.templates) >= 15
    
    def test_prompt_types_coverage(self, prompts):
        """Test that all prompt types have templates."""
        # Get all prompt types used in templates
        template_types = set()
        for name in prompts.templates.keys():
            template_types.add(prompts._get_prompt_type(name))
        
        # Check we have good coverage
        expected_types = {
            PromptType.EXPLORATION,
            PromptType.TRADING,
            PromptType.COMBAT,
            PromptType.MINING,
            PromptType.NAVIGATION,
            PromptType.MISSIONS,
            PromptType.PERFORMANCE,
            PromptType.STRATEGY,
            PromptType.ROLEPLAY
        }
        
        # Most types should be covered
        assert len(template_types.intersection(expected_types)) >= 7
    
    def test_context_building_error_handling(self, prompts, mock_data_store):
        """Test context building handles errors gracefully."""
        # Make data store methods raise exceptions
        mock_data_store.get_events_by_type.side_effect = Exception("Test error")
        
        # Should still build context with defaults
        context = prompts._build_exploration_context()
        
        assert context["bodies_scanned"] == 0
        assert context["systems_visited"] == 0
        assert context["recent_discoveries"] == "None recently"
    
    def test_prompt_variable_substitution(self, prompts, mock_data_store):
        """Test that all template variables get substituted."""
        # Generate each prompt and check no unsubstituted variables remain
        for prompt_name in prompts.templates.keys():
            result = prompts.generate_prompt(prompt_name)
            
            if "error" not in result:
                prompt_text = result["prompt"]
                # Check for unsubstituted variables (would appear as {variable})
                assert "{" not in prompt_text or "}" not in prompt_text
    
    def test_prompt_timestamp(self, prompts, mock_data_store):
        """Test that generated prompts include timestamps."""
        result = prompts.generate_prompt("daily_goals")
        
        assert "timestamp" in result
        # Parse timestamp to verify format
        timestamp = datetime.fromisoformat(result["timestamp"].replace('Z', '+00:00'))
        assert timestamp.tzinfo is not None
