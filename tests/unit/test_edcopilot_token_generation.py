"""
Test EDCoPilot chatter generation for proper token usage.

These tests verify that generated chatter uses dynamic tokens instead of
hardcoded system/ship names, ensuring the chatter works across all contexts.
"""

import pytest
from src.edcopilot.templates import SpaceChatterTemplate, EDCoPilotTokens


class TestEDCoPilotTokenGeneration:
    """Test that EDCoPilot chatter uses proper dynamic tokens."""

    def test_space_chatter_uses_dynamic_tokens_not_hardcoded_names(self):
        """Test that space chatter uses {SystemName} instead of hardcoded system names."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()

        # Check that generated content uses tokens, not hardcoded names
        for entry in template.entries:
            content = entry.text

            # SHOULD contain dynamic tokens when referencing systems directly
            if ("entering" in content.lower() or "welcome to" in content.lower() or
                ("system" in content.lower() and "system" not in "systems secure")):
                assert "<SystemName>" in content, f"Entry should use <SystemName> token: {content}"

            # SHOULD NOT contain hardcoded system names
            assert "Blae Drye" not in content, f"Should not hardcode system names: {content}"
            assert "Sol" not in content or "{" in content, f"Should use tokens for system references: {content}"

    def test_station_chatter_uses_dynamic_tokens(self):
        """Test that station references use {StationName} tokens."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()

        for entry in template.entries:
            content = entry.text

            # Only check entries that explicitly mention specific stations
            if ("docking request" in content.lower() or "docked at" in content.lower()):
                # Should use dynamic station token
                assert "<StationName>" in content, f"Entry should use <StationName> token: {content}"

            # Should not hardcode specific stations
            assert "K1F-37B" not in content, f"Should not hardcode station names: {content}"
            assert "Jameson Memorial" not in content, f"Should not hardcode station names: {content}"

    def test_exploration_chatter_uses_dynamic_tokens(self):
        """Test that exploration chatter uses proper dynamic tokens."""
        template = SpaceChatterTemplate()
        template.generate_exploration_chatter()

        for entry in template.entries:
            content = entry.text

            # Only check entries that explicitly reference specific bodies
            if ("data from" in content.lower() and "body" in content.lower()):
                # Should use dynamic body token when referencing bodies
                assert "<BodyName>" in content, f"Entry should use <BodyName> token: {content}"

            if "light years" in content.lower() and "sol" in content.lower():
                # Should use distance token, not hardcoded distances
                assert "<DistanceFromSol>" in content, f"Entry should use <DistanceFromSol> token: {content}"

    def test_generated_content_follows_token_patterns(self):
        """Test that all generated content follows proper token patterns."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()
        template.generate_exploration_chatter()
        template.generate_combat_chatter()

        for entry in template.entries:
            content = entry.text

            # Check for common hardcoded patterns that should be tokens
            hardcoded_patterns = [
                "Blae Drye", "K1F-37B", "EXCELSIOR", "Hadesfire",
                "25,962,345", "32%"  # Specific credits/fuel values
            ]

            for pattern in hardcoded_patterns:
                if pattern in content:
                    # If it contains hardcoded data, it should be in a template context
                    assert "{" in content and "}" in content, f"Hardcoded data should be in token context: {content}"

    def test_token_replacement_preserves_dynamic_nature(self):
        """Test that token replacement maintains dynamic nature of chatter."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()

        # Simulate token replacement
        for entry in template.entries:
            original_content = entry.text

            # Replace tokens as the system would
            replaced_content = original_content.replace("{SystemName}", "Test System")
            replaced_content = replaced_content.replace("{StationName}", "Test Station")

            # After replacement, should not contain the original hardcoded names
            assert "Blae Drye" not in replaced_content, "Token replacement should not leave hardcoded names"
            assert "K1F-37B" not in replaced_content, "Token replacement should not leave hardcoded names"

            # Should contain the test replacements
            if "{SystemName}" in original_content:
                assert "Test System" in replaced_content, "Token replacement should work correctly"