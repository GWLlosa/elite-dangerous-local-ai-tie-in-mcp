"""
Unit tests for EDCoPilot templates system.
"""

import pytest
from datetime import datetime, timezone

from src.edcopilot.templates import (
    EDCoPilotTemplateManager, SpaceChatterTemplate, CrewChatterTemplate,
    DeepSpaceChatterTemplate, ChatterEntry, ChatterType, VoiceProvider,
    EDCoPilotTokens, EDCoPilotConditions
)


class TestChatterEntry:
    """Test ChatterEntry functionality."""

    def test_chatter_entry_creation(self):
        """Test creating a chatter entry."""
        entry = ChatterEntry(
            text="Test dialogue",
            conditions=["Docked"],
            voice_override="ARIA"
        )

        assert entry.text == "Test dialogue"
        assert entry.conditions == ["Docked"]
        assert entry.voice_override == "ARIA"
        assert entry.probability == 1.0

    def test_format_for_edcopilot_full(self):
        """Test formatting entry with all fields."""
        entry = ChatterEntry(
            text="Welcome to {SystemName}, Commander",
            conditions=["InSupercruise", "Exploring"],
            voice_override="MICROSOFT"
        )

        formatted = entry.format_for_edcopilot()
        expected = "condition:InSupercruise&Exploring|voice:MICROSOFT|Welcome to {SystemName}, Commander"
        assert formatted == expected

    def test_format_for_edcopilot_text_only(self):
        """Test formatting entry with text only."""
        entry = ChatterEntry(text="Simple dialogue")
        formatted = entry.format_for_edcopilot()
        assert formatted == "Simple dialogue"

    def test_format_for_edcopilot_conditions_only(self):
        """Test formatting entry with conditions but no voice."""
        entry = ChatterEntry(
            text="Docked successfully",
            conditions=["Docked"]
        )

        formatted = entry.format_for_edcopilot()
        assert formatted == "condition:Docked|Docked successfully"

    def test_format_for_edcopilot_voice_only(self):
        """Test formatting entry with voice but no conditions."""
        entry = ChatterEntry(
            text="Emergency alert!",
            voice_override="ARIA"
        )

        formatted = entry.format_for_edcopilot()
        assert formatted == "voice:ARIA|Emergency alert!"


class TestSpaceChatterTemplate:
    """Test SpaceChatterTemplate functionality."""

    @pytest.fixture
    def space_template(self):
        """Create a space chatter template for testing."""
        return SpaceChatterTemplate()

    def test_initialization(self, space_template):
        """Test template initialization."""
        assert space_template.entries == []
        assert space_template.filename == "EDCoPilot.SpaceChatter.Custom.txt"

    def test_add_entry(self, space_template):
        """Test adding entries to template."""
        space_template.add_entry("Test dialogue", ["Docked"], "ARIA")

        assert len(space_template.entries) == 1
        assert space_template.entries[0].text == "Test dialogue"
        assert space_template.entries[0].conditions == ["Docked"]
        assert space_template.entries[0].voice_override == "ARIA"

    def test_generate_navigation_chatter(self, space_template):
        """Test generating navigation chatter."""
        space_template.generate_navigation_chatter()

        assert len(space_template.entries) > 0

        # Check for expected navigation entries
        navigation_texts = [entry.text for entry in space_template.entries]
        assert any("Entering" in text for text in navigation_texts)
        assert any("docked" in text.lower() for text in navigation_texts)
        assert any("fuel" in text.lower() for text in navigation_texts)

    def test_generate_exploration_chatter(self, space_template):
        """Test generating exploration chatter."""
        space_template.generate_exploration_chatter()

        assert len(space_template.entries) > 0

        # Check for expected exploration entries
        exploration_texts = [entry.text.lower() for entry in space_template.entries]
        assert any("scan" in text or "exploration" in text for text in exploration_texts)

    def test_generate_combat_chatter(self, space_template):
        """Test generating combat chatter."""
        space_template.generate_combat_chatter()

        assert len(space_template.entries) > 0

        # Check for expected combat entries
        combat_texts = [entry.text for entry in space_template.entries]
        assert any("shield" in text.lower() for text in combat_texts)
        assert any("hostiles" in text.lower() or "attack" in text.lower() for text in combat_texts)

    def test_generate_trading_chatter(self, space_template):
        """Test generating trading chatter."""
        space_template.generate_trading_chatter()

        assert len(space_template.entries) > 0

        # Check for expected trading entries
        trading_texts = [entry.text for entry in space_template.entries]
        assert any("cargo" in text.lower() for text in trading_texts)
        assert any("credits" in text.lower() or "profit" in text.lower() for text in trading_texts)

    def test_generate_default_chatter(self, space_template):
        """Test generating all default chatter types."""
        space_template.generate_default_chatter()

        # Should have entries from all categories
        assert len(space_template.entries) > 15  # Minimum expected entries

        all_texts = [entry.text.lower() for entry in space_template.entries]
        assert any("navigation" in text or "jump" in text for text in all_texts)
        assert any("scan" in text or "discovery" in text for text in all_texts)
        assert any("shield" in text or "combat" in text for text in all_texts)
        assert any("cargo" in text or "trading" in text for text in all_texts)

    def test_to_file_content(self, space_template):
        """Test generating file content."""
        space_template.add_entry("Test dialogue", ["Docked"])
        content = space_template.to_file_content()

        assert "# EDCoPilot Space Chatter Custom File" in content
        assert "Generated by Elite Dangerous MCP Server" in content
        assert "condition:Docked|Test dialogue" in content
        assert len(content.split('\n')) > 8  # Header + entry


class TestCrewChatterTemplate:
    """Test CrewChatterTemplate functionality."""

    @pytest.fixture
    def crew_template(self):
        """Create a crew chatter template for testing."""
        return CrewChatterTemplate()

    def test_initialization(self, crew_template):
        """Test template initialization."""
        assert crew_template.entries == []
        assert crew_template.filename == "EDCoPilot.CrewChatter.Custom.txt"

    def test_generate_crew_responses(self, crew_template):
        """Test generating crew response chatter."""
        crew_template.generate_crew_responses()

        assert len(crew_template.entries) > 0

        # Check for expected crew entries
        crew_texts = [entry.text for entry in crew_template.entries]
        assert any("navigation" in text.lower() for text in crew_texts)
        assert any("engineering" in text.lower() for text in crew_texts)
        assert any("security" in text.lower() for text in crew_texts)
        assert any("science" in text.lower() for text in crew_texts)

    def test_to_file_content(self, crew_template):
        """Test generating crew file content."""
        crew_template.generate_default_chatter()
        content = crew_template.to_file_content()

        assert "# EDCoPilot Crew Chatter Custom File" in content
        assert "Generated by Elite Dangerous MCP Server" in content


class TestDeepSpaceChatterTemplate:
    """Test DeepSpaceChatterTemplate functionality."""

    @pytest.fixture
    def deep_space_template(self):
        """Create a deep space chatter template for testing."""
        return DeepSpaceChatterTemplate()

    def test_initialization(self, deep_space_template):
        """Test template initialization."""
        assert deep_space_template.entries == []
        assert deep_space_template.filename == "EDCoPilot.DeepSpaceChatter.Custom.txt"

    def test_generate_deep_space_chatter(self, deep_space_template):
        """Test generating deep space chatter."""
        deep_space_template.generate_deep_space_chatter()

        assert len(deep_space_template.entries) > 0

        # Check for expected deep space entries
        deep_space_texts = [entry.text.lower() for entry in deep_space_template.entries]
        assert any("void" in text or "isolation" in text for text in deep_space_texts)
        assert any("stars" in text or "stellar" in text for text in deep_space_texts)
        assert any("galaxy" in text or "cosmic" in text for text in deep_space_texts)

    def test_to_file_content(self, deep_space_template):
        """Test generating deep space file content."""
        deep_space_template.generate_default_chatter()
        content = deep_space_template.to_file_content()

        assert "# EDCoPilot Deep Space Chatter Custom File" in content
        assert "Generated by Elite Dangerous MCP Server" in content
        assert ">5000 LY from both Sol and Colonia" in content


class TestEDCoPilotTemplateManager:
    """Test EDCoPilotTemplateManager functionality."""

    @pytest.fixture
    def template_manager(self):
        """Create a template manager for testing."""
        return EDCoPilotTemplateManager()

    def test_initialization(self, template_manager):
        """Test template manager initialization."""
        assert isinstance(template_manager.space_chatter, SpaceChatterTemplate)
        assert isinstance(template_manager.crew_chatter, CrewChatterTemplate)
        assert isinstance(template_manager.deep_space_chatter, DeepSpaceChatterTemplate)

    def test_generate_all_templates(self, template_manager):
        """Test generating all template files."""
        files = template_manager.generate_all_templates()

        assert len(files) == 3
        assert "EDCoPilot.SpaceChatter.Custom.txt" in files
        assert "EDCoPilot.CrewChatter.Custom.txt" in files
        assert "EDCoPilot.DeepSpaceChatter.Custom.txt" in files

        # Verify content exists for all files
        for filename, content in files.items():
            assert len(content) > 100  # Substantial content
            assert "Generated by Elite Dangerous MCP Server" in content

    def test_get_template_by_type(self, template_manager):
        """Test getting templates by type."""
        space_template = template_manager.get_template_by_type(ChatterType.SPACE_CHATTER)
        crew_template = template_manager.get_template_by_type(ChatterType.CREW_CHATTER)
        deep_space_template = template_manager.get_template_by_type(ChatterType.DEEP_SPACE_CHATTER)

        assert isinstance(space_template, SpaceChatterTemplate)
        assert isinstance(crew_template, CrewChatterTemplate)
        assert isinstance(deep_space_template, DeepSpaceChatterTemplate)

    def test_get_template_by_type_invalid(self, template_manager):
        """Test getting template with invalid type."""
        with pytest.raises(ValueError):
            template_manager.get_template_by_type("invalid_type")


class TestEDCoPilotConstants:
    """Test EDCoPilot constants and enums."""

    def test_chatter_type_enum(self):
        """Test ChatterType enum values."""
        assert ChatterType.SPACE_CHATTER.value == "SpaceChatter"
        assert ChatterType.CREW_CHATTER.value == "CrewChatter"
        assert ChatterType.DEEP_SPACE_CHATTER.value == "DeepSpaceChatter"

    def test_voice_provider_enum(self):
        """Test VoiceProvider enum values."""
        assert VoiceProvider.ARIA.value == "ARIA"
        assert VoiceProvider.MICROSOFT.value == "MICROSOFT"
        assert VoiceProvider.AZURE.value == "AZURE"

    def test_edcopilot_tokens(self):
        """Test EDCoPilot token constants."""
        assert EDCoPilotTokens.COMMANDER_NAME == "{CommanderName}"
        assert EDCoPilotTokens.SYSTEM_NAME == "{SystemName}"
        assert EDCoPilotTokens.SHIP_TYPE == "{ShipType}"
        assert EDCoPilotTokens.FUEL_PERCENT == "{FuelPercent}"

    def test_edcopilot_conditions(self):
        """Test EDCoPilot condition constants."""
        assert EDCoPilotConditions.DOCKED == "Docked"
        assert EDCoPilotConditions.IN_SUPERCRUISE == "InSupercruise"
        assert EDCoPilotConditions.UNDER_ATTACK == "UnderAttack"
        assert EDCoPilotConditions.DEEP_SPACE == "DeepSpace"

    def test_tokens_in_templates(self):
        """Test that templates use proper token format."""
        manager = EDCoPilotTemplateManager()
        files = manager.generate_all_templates()

        all_content = "\n".join(files.values())

        # Should contain some common tokens
        assert EDCoPilotTokens.SYSTEM_NAME in all_content
        assert EDCoPilotTokens.COMMANDER_NAME in all_content or "{CommanderName}" in all_content

    def test_conditions_in_templates(self):
        """Test that templates use proper condition format."""
        manager = EDCoPilotTemplateManager()
        files = manager.generate_all_templates()

        all_content = "\n".join(files.values())

        # Should contain condition formatting
        assert "condition:" in all_content
        assert EDCoPilotConditions.DOCKED in all_content
        assert EDCoPilotConditions.IN_SUPERCRUISE in all_content