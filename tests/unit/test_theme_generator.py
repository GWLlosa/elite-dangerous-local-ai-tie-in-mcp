"""
Unit tests for Theme Generator System

Tests the AI-powered theme generation and validation functionality
for the Dynamic Multi-Crew Theme System.
"""

import pytest
from unittest.mock import Mock, patch

from src.edcopilot.theme_generator import (
    ThemeGenerator, ThemePromptGenerator, TemplateValidator,
    ThemePromptContext, ValidationError
)
from src.edcopilot.theme_storage import ThemeStorage, CrewMemberTheme
from src.edcopilot.templates import ChatterType


class TestTemplateValidator:
    """Test template validation functionality."""

    def test_validate_valid_template(self):
        """Test validation of valid templates."""
        valid_templates = [
            "condition:InSupercruise|Entering {SystemName}, Commander.",
            "condition:Docked|Successfully docked at {StationName}.",
            "condition:FuelLow|Fuel at {FuelPercent}%. Recommend refueling.",
            "condition:Scanning&Exploring|Scanning {BodyName} for data.",
            "condition:UnderAttack|voice:ARIA|Red alert! Shields at {ShieldPercent}%!"
        ]

        for template in valid_templates:
            is_valid, issues = TemplateValidator.validate_template(template)
            assert is_valid, f"Template should be valid: {template} - Issues: {issues}"
            assert len(issues) == 0

    def test_validate_invalid_templates(self):
        """Test validation of invalid templates."""
        invalid_templates = [
            # Missing condition prefix
            "InSupercruise|Invalid template",
            # Invalid token
            "condition:Docked|Invalid {BadToken} usage",
            # Missing dialogue
            "condition:InSupercruise|",
            # Invalid condition
            "condition:InvalidCondition|Some dialogue",
            # Malformed token
            "condition:Docked|Missing closing brace {SystemName",
            # Empty dialogue
            "condition:Docked|",
            # Too long dialogue
            "condition:Docked|" + "A" * 250,
        ]

        for template in invalid_templates:
            is_valid, issues = TemplateValidator.validate_template(template)
            assert not is_valid, f"Template should be invalid: {template}"
            assert len(issues) > 0

    def test_validate_templates_batch(self):
        """Test batch validation of multiple templates."""
        templates = [
            "condition:InSupercruise|Valid template with {SystemName}",
            "condition:Docked|Another valid template",
            "invalid|Missing condition prefix",
            "condition:BadCondition|Invalid condition",
            "condition:FuelLow|Valid fuel warning at {FuelPercent}%"
        ]

        valid_templates, failed_templates = TemplateValidator.validate_templates(templates)

        assert len(valid_templates) == 3
        assert len(failed_templates) == 2

        # Check valid templates
        assert "condition:InSupercruise|Valid template with {SystemName}" in valid_templates
        assert "condition:Docked|Another valid template" in valid_templates
        assert "condition:FuelLow|Valid fuel warning at {FuelPercent}%" in valid_templates

        # Check failed templates
        failed_template_texts = [template for template, issues in failed_templates]
        assert "invalid|Missing condition prefix" in failed_template_texts
        assert "condition:BadCondition|Invalid condition" in failed_template_texts

    def test_validate_token_syntax(self):
        """Test token syntax validation."""
        # Valid tokens
        valid_token_templates = [
            "condition:Docked|System: {SystemName}",
            "condition:Trading|Credits: {Credits}",
            "condition:FuelLow|Fuel: {FuelPercent}%",
            "condition:Exploring|Distance: {DistanceFromSol} LY"
        ]

        for template in valid_token_templates:
            is_valid, issues = TemplateValidator.validate_template(template)
            assert is_valid, f"Valid token template failed: {template}"

        # Invalid tokens
        invalid_token_templates = [
            "condition:Docked|Invalid {BadToken}",
            "condition:Docked|Malformed {SystemName without closing",
            "condition:Docked|Multiple {InvalidToken} {AnotherBadToken}"
        ]

        for template in invalid_token_templates:
            is_valid, issues = TemplateValidator.validate_template(template)
            assert not is_valid, f"Invalid token template should fail: {template}"

    def test_validate_condition_combinations(self):
        """Test validation of condition combinations."""
        valid_combinations = [
            "condition:Scanning&Exploring|Combined conditions work",
            "condition:DeepSpace&FirstDiscovery|Deep space discovery",
            "condition:Trading&Docked|Trading while docked"
        ]

        for template in valid_combinations:
            is_valid, issues = TemplateValidator.validate_template(template)
            assert is_valid, f"Valid combination failed: {template}"

        invalid_combinations = [
            "condition:ValidCondition&InvalidCondition|Bad combination",
            "condition:&EmptyCondition|Empty condition part"
        ]

        for template in invalid_combinations:
            is_valid, issues = TemplateValidator.validate_template(template)
            assert not is_valid, f"Invalid combination should fail: {template}"


class TestThemePromptGenerator:
    """Test theme prompt generation for Claude Desktop."""

    @pytest.fixture
    def mock_theme_storage(self):
        """Create mock theme storage."""
        return Mock(spec=ThemeStorage)

    @pytest.fixture
    def prompt_generator(self, mock_theme_storage):
        """Create prompt generator with mock storage."""
        return ThemePromptGenerator(mock_theme_storage)

    def test_generate_basic_theme_prompt(self, prompt_generator):
        """Test basic theme prompt generation."""
        context = ThemePromptContext(
            theme="space pirate",
            context="owes debt to Space Mafia"
        )

        result = prompt_generator.generate_theme_prompt(context)

        assert "prompt" in result
        assert "theme" in result
        assert "context" in result
        assert "validation_rules" in result

        prompt = result["prompt"]
        assert "space pirate" in prompt
        assert "Space Mafia" in prompt
        assert "EDCoPilot" in prompt
        assert "{SystemName}" in prompt
        assert "condition:" in prompt

    def test_generate_crew_role_prompt(self, prompt_generator):
        """Test prompt generation with crew role."""
        context = ThemePromptContext(
            theme="military veteran",
            context="retired officer",
            crew_role="navigator",
            ship_name="Anaconda"
        )

        result = prompt_generator.generate_theme_prompt(context)

        prompt = result["prompt"]
        assert "navigator" in prompt
        assert "Anaconda" in prompt
        assert "military veteran" in prompt
        assert "navigation" in prompt.lower()

    def test_generate_with_current_templates(self, prompt_generator):
        """Test prompt generation with current templates."""
        current_templates = [
            "condition:InSupercruise|Entering {SystemName}, Commander.",
            "condition:Docked|Docked at {StationName}."
        ]

        context = ThemePromptContext(
            theme="corporate executive",
            context="ambitious trader",
            current_templates=current_templates
        )

        result = prompt_generator.generate_theme_prompt(context)

        prompt = result["prompt"]
        assert "Current Templates" in prompt
        assert "Entering {SystemName}" in prompt
        assert "Docked at {StationName}" in prompt

    def test_theme_specific_guidance(self, prompt_generator):
        """Test theme-specific guidance generation."""
        # Test pirate theme
        pirate_context = ThemePromptContext(
            theme="space pirate",
            context="treasure hunter"
        )
        pirate_result = prompt_generator.generate_theme_prompt(pirate_context)
        pirate_prompt = pirate_result["prompt"]
        assert "nautical terminology" in pirate_prompt.lower()
        assert "matey" in pirate_prompt.lower()

        # Test corporate theme
        corporate_context = ThemePromptContext(
            theme="corporate executive",
            context="profit-focused"
        )
        corporate_result = prompt_generator.generate_theme_prompt(corporate_context)
        corporate_prompt = corporate_result["prompt"]
        assert "business terminology" in corporate_prompt.lower()
        assert "profit" in corporate_prompt.lower()

        # Test military theme
        military_context = ThemePromptContext(
            theme="military veteran",
            context="retired officer"
        )
        military_result = prompt_generator.generate_theme_prompt(military_context)
        military_prompt = military_result["prompt"]
        assert "military terminology" in military_prompt.lower()
        assert "tactical" in military_prompt.lower()

    def test_crew_role_specific_guidance(self, prompt_generator):
        """Test crew role-specific guidance."""
        roles_to_test = [
            ("navigator", "navigation"),
            ("science", "research"),
            ("engineer", "systems"),
            ("security", "threats")
        ]

        for role, expected_keyword in roles_to_test:
            context = ThemePromptContext(
                theme="professional crew",
                context="experienced team",
                crew_role=role
            )

            result = prompt_generator.generate_theme_prompt(context)
            prompt = result["prompt"]
            assert expected_keyword.lower() in prompt.lower(), f"Role {role} should mention {expected_keyword}"

    def test_generate_crew_theme_prompt(self, prompt_generator):
        """Test multi-crew theme prompt generation."""
        result = prompt_generator.generate_crew_theme_prompt(
            ship_name="Anaconda",
            crew_roles=["commander", "navigator", "engineer"],
            overall_theme="space pirates",
            overall_context="rebel crew"
        )

        assert "prompt" in result
        assert "ship_name" in result
        assert "crew_roles" in result

        prompt = result["prompt"]
        assert "Anaconda" in prompt
        assert "space pirates" in prompt
        assert "commander" in prompt
        assert "navigator" in prompt
        assert "engineer" in prompt
        assert "json" in prompt.lower()  # Should include expected response format

    def test_validation_rules_generation(self, prompt_generator):
        """Test validation rules generation."""
        context = ThemePromptContext(
            theme="test theme",
            context="test context"
        )

        result = prompt_generator.generate_theme_prompt(context)
        validation_rules = result["validation_rules"]

        assert "required_format" in validation_rules
        assert "valid_tokens" in validation_rules
        assert "valid_conditions" in validation_rules
        assert "max_length" in validation_rules

        # Check that valid tokens include expected tokens
        valid_tokens = validation_rules["valid_tokens"]
        assert "{SystemName}" in valid_tokens
        assert "{StationName}" in valid_tokens
        assert "{FuelPercent}" in valid_tokens


class TestThemeGenerator:
    """Test main theme generator coordination."""

    @pytest.fixture
    def mock_theme_storage(self):
        """Create mock theme storage."""
        storage = Mock(spec=ThemeStorage)
        storage.get_current_theme.return_value = {
            "theme": "test theme",
            "context": "test context"
        }
        return storage

    @pytest.fixture
    def theme_generator(self, mock_theme_storage):
        """Create theme generator with mock storage."""
        return ThemeGenerator(mock_theme_storage)

    def test_generate_theme_prompt_for_claude(self, theme_generator):
        """Test generating prompt for Claude Desktop."""
        result = theme_generator.generate_theme_prompt_for_claude(
            theme="space pirate",
            context="treasure hunter"
        )

        assert "prompt" in result
        assert "theme" in result
        assert "context" in result
        assert result["theme"] == "space pirate"
        assert result["context"] == "treasure hunter"

    def test_generate_theme_prompt_with_options(self, theme_generator):
        """Test prompt generation with all options."""
        result = theme_generator.generate_theme_prompt_for_claude(
            theme="corporate",
            context="ambitious",
            crew_role="navigator",
            ship_name="Python",
            current_templates=["condition:Docked|Test template"]
        )

        assert result["crew_role"] == "navigator"
        assert result["ship_name"] == "Python"
        assert "Test template" in result["prompt"]

    def test_validate_generated_templates(self, theme_generator):
        """Test validation of generated templates."""
        # Valid templates
        valid_templates = [
            "condition:InSupercruise|Pirate dialogue with {SystemName}",
            "condition:Docked|More pirate dialogue at {StationName}",
            "condition:FuelLow|Fuel warning at {FuelPercent}%"
        ]

        result = theme_generator.validate_generated_templates(valid_templates)

        assert result["success"] is True
        assert len(result["valid_templates"]) == 3
        assert len(result["failed_templates"]) == 0
        assert result["validation_summary"]["success_rate"] == 1.0

        # Mixed valid/invalid templates
        mixed_templates = [
            "condition:InSupercruise|Valid template",
            "invalid|Bad template",
            "condition:Docked|Another valid template"
        ]

        result = theme_generator.validate_generated_templates(mixed_templates)

        assert len(result["valid_templates"]) == 2
        assert len(result["failed_templates"]) == 1

        # Empty/no valid templates
        empty_result = theme_generator.validate_generated_templates([])
        assert empty_result["success"] is False
        assert "No valid templates found" in empty_result["error"]

    def test_create_chatter_entries_from_templates(self, theme_generator):
        """Test creating ChatterEntry objects from templates."""
        templates = [
            "condition:InSupercruise|Space dialogue",
            "condition:Docked|voice:ARIA|Docked dialogue",
            "condition:Scanning&Exploring|Exploration dialogue"
        ]

        entries = theme_generator.create_chatter_entries_from_templates(
            templates, ChatterType.SPACE_CHATTER
        )

        assert len(entries) == 3

        # Check first entry
        entry1 = entries[0]
        assert entry1.text == "Space dialogue"
        assert entry1.conditions == ["InSupercruise"]
        assert entry1.voice_override is None
        assert entry1.chatter_type == ChatterType.SPACE_CHATTER

        # Check second entry (with voice)
        entry2 = entries[1]
        assert entry2.text == "Docked dialogue"
        assert entry2.voice_override == "ARIA"

        # Check third entry (combined conditions)
        entry3 = entries[2]
        assert entry3.conditions == ["Scanning", "Exploring"]

    def test_generate_crew_setup_prompt(self, theme_generator):
        """Test crew setup prompt generation."""
        result = theme_generator.generate_crew_setup_prompt(
            ship_name="Anaconda",
            crew_roles=["commander", "navigator", "engineer"],
            overall_theme="military unit",
            overall_context="elite squadron"
        )

        assert "prompt" in result
        assert "ship_name" in result
        assert "crew_roles" in result
        assert result["ship_name"] == "Anaconda"
        assert result["overall_theme"] == "military unit"

        prompt = result["prompt"]
        assert "Anaconda" in prompt
        assert "military unit" in prompt
        assert "commander" in prompt
        assert "navigator" in prompt

    def test_get_theme_status(self, theme_generator, mock_theme_storage):
        """Test theme status retrieval."""
        # Mock storage responses
        mock_theme_storage.get_current_theme.return_value = {
            "theme": "test theme",
            "context": "test context"
        }
        mock_theme_storage.get_all_ship_configs.return_value = {}
        mock_theme_storage.get_storage_info.return_value = {
            "storage_path": "/test/path",
            "current_theme": True
        }

        status = theme_generator.get_theme_status()

        assert "current_theme" in status
        assert "ship_configurations" in status
        assert "storage_info" in status
        assert "system_status" in status
        assert status["system_status"] == "operational"

    def test_validation_error_handling(self, theme_generator):
        """Test handling of validation errors."""
        # Test with templates that have high failure rate
        bad_templates = [
            "badcondition:InvalidState|invalid template 1",
            "invalidcondition:BadState|invalid template 2",
            "wrongformat:IncorrectCondition|invalid template 3",
            "condition:Docked|One valid template"  # Only 1 valid out of 4
        ]

        result = theme_generator.validate_generated_templates(bad_templates)

        # Should fail due to high failure rate (>30%)
        assert result["success"] is False
        assert "Too many validation failures" in result["error"]

    def test_template_cleaning(self, theme_generator):
        """Test template cleaning during validation."""
        messy_templates = [
            "",  # Empty line
            "# Comment line",  # Comment
            "  condition:Docked|Valid template with whitespace  ",  # Whitespace
            "condition:InSupercruise|Another valid template",
            "not a template line"  # Invalid line without |
        ]

        result = theme_generator.validate_generated_templates(messy_templates)

        # Should only process the valid template lines
        assert len(result["valid_templates"]) == 2
        assert "Valid template with whitespace" in result["valid_templates"][0]