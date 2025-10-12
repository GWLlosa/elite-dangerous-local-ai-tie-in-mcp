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
        expected = "(InSupercruise&Exploring) Welcome to {SystemName}, Commander"
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
        assert formatted == "(Docked) Docked successfully"

    def test_format_for_edcopilot_voice_only(self):
        """Test formatting entry with voice but no conditions."""
        entry = ChatterEntry(
            text="Emergency alert!",
            voice_override="ARIA"
        )

        formatted = entry.format_for_edcopilot()
        assert formatted == "Emergency alert!"


class TestSpaceChatterTemplate:
    """Test SpaceChatterTemplate functionality."""

    @pytest.fixture
    def space_template(self):
        """Create a space chatter template for testing."""
        return SpaceChatterTemplate()

    def test_initialization(self, space_template):
        """Test template initialization."""
        assert space_template.conversations == []
        assert space_template.filename == "EDCoPilot.SpaceChatter.Custom.txt"

    def test_add_entry(self, space_template):
        """Test adding entries to template (backwards compatibility)."""
        space_template.add_entry("Test dialogue", ["Docked"], "ARIA")

        assert len(space_template.conversations) == 1
        # add_entry converts to conversation format
        assert "Test dialogue" in space_template.to_file_content()

    def test_generate_navigation_chatter(self, space_template):
        """Test generating navigation chatter."""
        space_template.generate_navigation_chatter()

        assert len(space_template.conversations) > 0

        # Check for expected navigation content
        content = space_template.to_file_content()
        assert "Entering" in content or "entering" in content
        assert "docked" in content.lower()
        assert "fuel" in content.lower()

    def test_generate_exploration_chatter(self, space_template):
        """Test generating exploration chatter."""
        space_template.generate_exploration_chatter()

        assert len(space_template.conversations) > 0

        # Check for expected exploration content
        content = space_template.to_file_content().lower()
        assert "scan" in content or "exploration" in content or "discover" in content

    def test_generate_combat_chatter(self, space_template):
        """Test generating combat chatter."""
        space_template.generate_combat_chatter()

        assert len(space_template.conversations) > 0

        # Check for expected combat content
        content = space_template.to_file_content().lower()
        assert "shield" in content
        assert "hostiles" in content or "attack" in content or "target" in content

    def test_generate_trading_chatter(self, space_template):
        """Test generating trading chatter."""
        space_template.generate_trading_chatter()

        assert len(space_template.conversations) > 0

        # Check for expected trading content
        content = space_template.to_file_content().lower()
        assert "cargo" in content
        assert "credits" in content or "profit" in content or "market" in content

    def test_generate_default_chatter(self, space_template):
        """Test generating all default chatter types."""
        space_template.generate_default_chatter()

        # Should have conversations from all categories
        assert len(space_template.conversations) > 10  # Minimum expected conversations

        content = space_template.to_file_content().lower()
        assert "docked" in content or "entering" in content
        assert "scan" in content or "discovery" in content or "discover" in content
        assert "shield" in content or "hostile" in content
        assert "cargo" in content or "profit" in content or "market" in content

    def test_to_file_content(self, space_template):
        """Test generating file content."""
        space_template.add_entry("Test dialogue", ["Docked"])
        content = space_template.to_file_content()

        # NO COMMENTS - EDCoPilot doesn't support them
        assert "#" not in content
        # Should use conversation block format
        assert "[example]" in content
        assert "[\\example]" in content
        assert "Test dialogue" in content


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
        # Test with the new template manager approach
        from src.edcopilot.templates import EDCoPilotTemplateManager
        manager = EDCoPilotTemplateManager()
        templates = manager.generate_all_templates()
        crew_content = templates.get('EDCoPilot.CrewChatter.Custom.txt', '')

        # Should contain conversation blocks
        assert '[example]' in crew_content
        assert '[\\example]' in crew_content

        # Check for expected crew roles
        assert '[<Operations>]' in crew_content
        assert '[<Engineering>]' in crew_content
        assert '[<Security>]' in crew_content or '[<Helm>]' in crew_content
        assert '[<Science>]' in crew_content or '[<EDCoPilot>]' in crew_content

    def test_to_file_content(self, crew_template):
        """Test generating crew file content."""
        crew_template.generate_default_chatter()
        content = crew_template.to_file_content()

        # NO COMMENTS - EDCoPilot doesn't support them
        assert not content.startswith("#")
        # Should use conversation block format
        assert "[example]" in content
        assert "[\\example]" in content


class TestDeepSpaceChatterTemplate:
    """Test DeepSpaceChatterTemplate functionality."""

    @pytest.fixture
    def deep_space_template(self):
        """Create a deep space chatter template for testing."""
        return DeepSpaceChatterTemplate()

    def test_initialization(self, deep_space_template):
        """Test template initialization."""
        assert deep_space_template.conversations == []
        assert deep_space_template.filename == "EDCoPilot.DeepSpaceChatter.Custom.txt"

    def test_generate_deep_space_chatter(self, deep_space_template):
        """Test generating deep space chatter."""
        deep_space_template.generate_deep_space_chatter()

        assert len(deep_space_template.conversations) > 0

        # Check for expected deep space content
        content = deep_space_template.to_file_content().lower()
        assert "void" in content or "isolation" in content or "nebula" in content
        assert "stars" in content or "stellar" in content or "star" in content
        assert "galaxy" in content or "cosmic" in content or "space" in content

    def test_to_file_content(self, deep_space_template):
        """Test generating deep space file content."""
        deep_space_template.generate_default_chatter()
        content = deep_space_template.to_file_content()

        # NO COMMENTS - EDCoPilot doesn't support them
        assert not content.startswith("#")
        # Should have deep space themed content
        assert "void" in content.lower() or "isolation" in content.lower() or "stars" in content.lower()


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
            # NO COMMENTS - EDCoPilot doesn't support them
            assert not content.startswith("#")

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
        assert EDCoPilotTokens.COMMANDER_NAME == "<CommanderName>"
        assert EDCoPilotTokens.SYSTEM_NAME == "<SystemName>"
        assert EDCoPilotTokens.SHIP_TYPE == "<ShipType>"
        assert EDCoPilotTokens.FUEL_PERCENT == "<FuelPercent>"

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

        # Should contain some common tokens (lowercase authoritative format)
        assert "<starsystem>" in all_content or "<cmdrname>" in all_content
        # Old TitleCase tokens should NOT be present
        assert "<SystemName>" not in all_content
        assert "<CommanderName>" not in all_content

    def test_conditions_in_templates(self):
        """Test that templates use proper condition format."""
        manager = EDCoPilotTemplateManager()
        files = manager.generate_all_templates()

        all_content = "\n".join(files.values())

        # Should contain condition formatting
        assert "(" in all_content and ")" in all_content  # Check for (Condition) format
        assert EDCoPilotConditions.DOCKED in all_content
        assert EDCoPilotConditions.IN_SUPERCRUISE in all_content