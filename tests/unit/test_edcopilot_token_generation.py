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
        """Test that space chatter uses <starsystem> instead of hardcoded system names."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()

        # Check that generated content uses tokens, not hardcoded names
        content = template.to_file_content()

        # SHOULD contain dynamic tokens when referencing systems
        if "entering" in content.lower() or "welcome to" in content.lower():
            assert "<starsystem>" in content, "Should use <starsystem> token for system references"

        # SHOULD NOT contain hardcoded system names
        assert "Blae Drye" not in content, "Should not hardcode system names"
        assert "Sol" not in content or "<" in content, "Should use tokens for system references"

    def test_station_chatter_uses_dynamic_tokens(self):
        """Test that station references use <stationname> tokens."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()

        content = template.to_file_content()

        # Should use dynamic station token
        if "docking" in content.lower() or "docked at" in content.lower():
            assert "<stationname>" in content, "Should use <stationname> token for station references"

        # Should not hardcode specific stations
        assert "K1F-37B" not in content, "Should not hardcode station names"
        assert "Jameson Memorial" not in content, "Should not hardcode station names"

    def test_exploration_chatter_uses_dynamic_tokens(self):
        """Test that exploration chatter uses proper dynamic tokens."""
        template = SpaceChatterTemplate()
        template.generate_exploration_chatter()

        content = template.to_file_content()

        # Exploration chatter should not contain hardcoded specific data
        assert "Blae Drye" not in content, "Should not hardcode system names in exploration"
        # Check for lowercase token format (authoritative)
        # Tokens may or may not be present depending on content, but should be lowercase if present
        if "<" in content and ">" in content:
            # Extract tokens and verify they're lowercase
            import re
            tokens = re.findall(r'<([^>]+)>', content)
            for token in tokens:
                assert token.islower() or token == "DistanceFromSol" or token == "BodyName" or token == "CargoCount" or token == "CargoCapacity" or token == "Credits", \
                    f"Tokens should be lowercase (authoritative format): <{token}>"

    def test_generated_content_follows_token_patterns(self):
        """Test that all generated content follows proper token patterns."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()
        template.generate_exploration_chatter()
        template.generate_combat_chatter()

        content = template.to_file_content()

        # Check for common hardcoded patterns that should NOT be present
        hardcoded_patterns = [
            "Blae Drye", "K1F-37B", "EXCELSIOR", "Hadesfire",
            "25,962,345", "32%"  # Specific credits/fuel values
        ]

        for pattern in hardcoded_patterns:
            assert pattern not in content, f"Should not contain hardcoded data: {pattern}"

    def test_token_replacement_preserves_dynamic_nature(self):
        """Test that token replacement maintains dynamic nature of chatter."""
        template = SpaceChatterTemplate()
        template.generate_navigation_chatter()

        original_content = template.to_file_content()

        # Simulate token replacement (using lowercase authoritative format)
        replaced_content = original_content.replace("<starsystem>", "Test System")
        replaced_content = replaced_content.replace("<stationname>", "Test Station")

        # After replacement, should not contain the original hardcoded names
        assert "Blae Drye" not in replaced_content, "Token replacement should not leave hardcoded names"
        assert "K1F-37B" not in replaced_content, "Token replacement should not leave hardcoded names"

        # Should contain the test replacements if tokens were present
        if "<starsystem>" in original_content:
            assert "Test System" in replaced_content, "Token replacement should work correctly"