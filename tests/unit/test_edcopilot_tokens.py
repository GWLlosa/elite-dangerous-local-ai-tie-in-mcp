"""
Unit tests for EDCoPilot token definitions.

Tests validate that tokens match the authoritative EDCoPilot format:
- Lowercase format: <cmdrname>, <starsystem>, etc.
- All required tokens are defined
- Old token names are deprecated but still work for backwards compatibility
"""

import pytest
from src.edcopilot.templates import EDCoPilotTokens


class TestEDCoPilotTokens:
    """Test suite for EDCoPilot token format validation."""

    def test_commander_tokens_are_lowercase(self):
        """Commander-related tokens must use lowercase format."""
        assert EDCoPilotTokens.CMDR_NAME == "<cmdrname>"
        assert EDCoPilotTokens.CMDR_ADDRESS == "<cmdraddress>"

    def test_location_tokens_are_lowercase(self):
        """Location-related tokens must use lowercase format."""
        assert EDCoPilotTokens.STAR_SYSTEM == "<starsystem>"
        assert EDCoPilotTokens.STATION_NAME == "<stationname>"
        assert EDCoPilotTokens.LOCAL_DESTINATION == "<localdestination>"
        assert EDCoPilotTokens.RANDOM_STAR_SYSTEM == "<randomstarsystem>"

    def test_ship_tokens_are_lowercase(self):
        """Ship-related tokens must use lowercase format."""
        assert EDCoPilotTokens.MY_SHIP_NAME == "<myshipname>"
        assert EDCoPilotTokens.CALLSIGN == "<callsign>"
        assert EDCoPilotTokens.OTHER_CALLSIGN == "<othercallsign>"
        assert EDCoPilotTokens.SHIP_CORPORATION == "<shipCorporation>"

    def test_status_tokens_are_lowercase(self):
        """Status-related tokens must use lowercase format."""
        assert EDCoPilotTokens.FUEL_LEVELS == "<fuellevels>"

    def test_flight_tokens_are_lowercase(self):
        """Flight-related tokens must use lowercase format."""
        assert EDCoPilotTokens.FLIGHT_NUM == "<flightnum>"

    def test_all_authoritative_tokens_defined(self):
        """All tokens from authoritative EDCoPilot files must be defined."""
        required_tokens = [
            "<cmdrname>",
            "<cmdraddress>",
            "<myshipname>",
            "<stationname>",
            "<starsystem>",
            "<randomstarsystem>",
            "<callsign>",
            "<localdestination>",
            "<flightnum>",
            "<fuellevels>",
            "<shipCorporation>",
            "<othercallsign>",
        ]

        token_values = [
            getattr(EDCoPilotTokens, attr)
            for attr in dir(EDCoPilotTokens)
            if not attr.startswith('_') and isinstance(getattr(EDCoPilotTokens, attr), str)
        ]

        for token in required_tokens:
            assert token in token_values, f"Required token {token} not defined"

    def test_old_tokens_kept_for_backwards_compatibility(self):
        """Old token names should be kept but marked as deprecated."""
        # Old tokens should exist as class attributes for backwards compatibility
        assert hasattr(EDCoPilotTokens, 'COMMANDER_NAME')
        assert hasattr(EDCoPilotTokens, 'SYSTEM_NAME')
        assert hasattr(EDCoPilotTokens, 'SHIP_NAME')
        assert hasattr(EDCoPilotTokens, 'FUEL_PERCENT')

        # But they should have corresponding new names in the mapping
        mapping = EDCoPilotTokens.get_token_mapping()
        assert EDCoPilotTokens.COMMANDER_NAME in mapping
        assert EDCoPilotTokens.SYSTEM_NAME in mapping
        assert EDCoPilotTokens.SHIP_NAME in mapping
        assert EDCoPilotTokens.FUEL_PERCENT in mapping


class TestBackwardsCompatibility:
    """Test suite for backwards compatibility with old token names."""

    def test_token_mapping_exists(self):
        """Token mapping for old->new names should exist."""
        assert hasattr(EDCoPilotTokens, 'get_token_mapping')
        mapping = EDCoPilotTokens.get_token_mapping()
        assert isinstance(mapping, dict)

    def test_old_commander_name_maps_to_new(self):
        """<CommanderName> should map to <cmdrname>."""
        mapping = EDCoPilotTokens.get_token_mapping()
        assert "<CommanderName>" in mapping
        assert mapping["<CommanderName>"] == "<cmdrname>"

    def test_old_system_name_maps_to_new(self):
        """<SystemName> should map to <starsystem>."""
        mapping = EDCoPilotTokens.get_token_mapping()
        assert "<SystemName>" in mapping
        assert mapping["<SystemName>"] == "<starsystem>"

    def test_old_station_name_maps_to_new(self):
        """<StationName> should map to <stationname>."""
        mapping = EDCoPilotTokens.get_token_mapping()
        assert "<StationName>" in mapping
        assert mapping["<StationName>"] == "<stationname>"

    def test_old_ship_name_maps_to_new(self):
        """<ShipName> should map to <myshipname>."""
        mapping = EDCoPilotTokens.get_token_mapping()
        assert "<ShipName>" in mapping
        assert mapping["<ShipName>"] == "<myshipname>"

    def test_old_fuel_percent_maps_to_new(self):
        """<FuelPercent> should map to <fuellevels>."""
        mapping = EDCoPilotTokens.get_token_mapping()
        assert "<FuelPercent>" in mapping
        assert mapping["<FuelPercent>"] == "<fuellevels>"

    def test_all_old_tokens_have_mapping(self):
        """All old TitleCase tokens should have mappings."""
        mapping = EDCoPilotTokens.get_token_mapping()
        old_tokens = [
            "<CommanderName>",
            "<SystemName>",
            "<StationName>",
            "<ShipName>",
            "<FuelPercent>",
        ]

        for old_token in old_tokens:
            assert old_token in mapping, f"Old token {old_token} missing from mapping"
