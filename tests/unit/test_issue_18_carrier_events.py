"""
Unit tests for Issue #18: CarrierStats and CarrierFinance Events Return Empty key_data

GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/18

Problem: Carrier events (CarrierStats, CarrierFinance, CarrierCrewServices, CarrierModulePack)
are being detected and categorized correctly but return empty key_data dictionaries instead of
extracting the relevant carrier information.

Expected: key_data should contain carrier information like CarrierID, Callsign, Finance data, etc.
Actual (before fix): key_data is an empty dictionary {}
"""

import pytest
from datetime import datetime, timezone

from src.journal.events import EventProcessor, EventCategory


class TestIssue18CarrierStats:
    """Test for Issue #18: CarrierStats event data extraction"""

    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()

    def test_issue_18_carrier_stats_key_data_extraction(self, processor):
        """
        Test for Issue #18: CarrierStats Event Returns Empty key_data

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/18

        Problem: CarrierStats events return empty key_data instead of carrier information
        Expected: key_data should contain CarrierID, Callsign, Name, Finance, Crew, etc.
        Actual (before fix): key_data is {}
        """
        carrier_stats_event = {
            "timestamp": "2025-10-09T04:01:48Z",
            "event": "CarrierStats",
            "CarrierID": 3700005632,
            "Callsign": "K1F-37B",
            "Name": "Test Carrier",
            "DockingAccess": "all",
            "AllowNotorious": False,
            "FuelLevel": 800,
            "JumpRangeCurr": 500.00,
            "JumpRangeMax": 500.00,
            "Finance": {
                "CarrierBalance": 1500000000,
                "ReserveBalance": 100000000,
                "AvailableBalance": 1400000000,
                "ReservePercent": 0,
                "TaxRate_rearm": 0,
                "TaxRate_refuel": 0,
                "TaxRate_repair": 0
            },
            "Crew": [
                {
                    "CrewRole": "BlackMarket",
                    "Activated": True,
                    "Enabled": True,
                    "CrewName": "Test Fence"
                }
            ],
            "ShipPacks": [
                {
                    "PackTheme": "ExplorationPack",
                    "PackTier": 1
                }
            ],
            "ModulePacks": [
                {
                    "PackTheme": "MiningUtilities",
                    "PackTier": 1
                }
            ]
        }

        processed = processor.process_event(carrier_stats_event)

        # Verify basic processing
        assert processed.event_type == "CarrierStats"
        assert processed.category == EventCategory.CARRIER
        assert processed.is_valid

        # Verify key_data is NOT empty (this test should FAIL before the fix)
        assert processed.key_data, "key_data should not be empty for CarrierStats events"

        # Verify essential carrier data is extracted
        assert "carrier_id" in processed.key_data
        assert processed.key_data["carrier_id"] == 3700005632

        assert "callsign" in processed.key_data
        assert processed.key_data["callsign"] == "K1F-37B"

        assert "name" in processed.key_data
        assert processed.key_data["name"] == "Test Carrier"

        # Verify fuel information
        assert "fuel_level" in processed.key_data
        assert processed.key_data["fuel_level"] == 800

        # Verify finance data is included
        assert "finance" in processed.key_data
        assert processed.key_data["finance"]["CarrierBalance"] == 1500000000
        assert processed.key_data["finance"]["AvailableBalance"] == 1400000000

        # Verify crew data is included
        assert "crew" in processed.key_data
        assert len(processed.key_data["crew"]) == 1
        assert processed.key_data["crew"][0]["CrewRole"] == "BlackMarket"

        # Verify ship packs are included
        assert "ship_packs" in processed.key_data
        assert len(processed.key_data["ship_packs"]) == 1

        # Verify module packs are included
        assert "module_packs" in processed.key_data
        assert len(processed.key_data["module_packs"]) == 1

    def test_issue_18_carrier_stats_summary_generation(self, processor):
        """
        Test that CarrierStats events generate meaningful summaries.

        Before fix: "CarrierStats event occurred"
        After fix: Should include carrier name and/or callsign
        """
        carrier_stats_event = {
            "timestamp": "2025-10-09T04:01:48Z",
            "event": "CarrierStats",
            "CarrierID": 3700005632,
            "Callsign": "K1F-37B",
            "Name": "Test Carrier"
        }

        processed = processor.process_event(carrier_stats_event)

        # Summary should be more descriptive than the generic default
        assert processed.summary != "CarrierStats event occurred"
        assert "K1F-37B" in processed.summary or "Test Carrier" in processed.summary


class TestIssue18CarrierFinance:
    """Test for Issue #18: CarrierFinance event data extraction"""

    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()

    def test_issue_18_carrier_finance_key_data_extraction(self, processor):
        """
        Test for Issue #18: CarrierFinance Event Returns Empty key_data

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/18

        Problem: CarrierFinance events return empty key_data instead of financial information
        Expected: key_data should contain CarrierID, balances, tax rates, etc.
        Actual (before fix): key_data is {}
        """
        carrier_finance_event = {
            "timestamp": "2025-10-09T04:00:55Z",
            "event": "CarrierFinance",
            "CarrierID": 3700005632,
            "TaxRate_pioneersupplies": 0,
            "TaxRate_shipyard": 0,
            "TaxRate_rearm": 0,
            "TaxRate_outfitting": 0,
            "TaxRate_refuel": 0,
            "TaxRate_repair": 0,
            "CarrierBalance": 1500000000,
            "ReserveBalance": 100000000,
            "AvailableBalance": 1400000000,
            "ReservePercent": 0
        }

        processed = processor.process_event(carrier_finance_event)

        # Verify basic processing
        assert processed.event_type == "CarrierFinance"
        assert processed.category == EventCategory.CARRIER
        assert processed.is_valid

        # Verify key_data is NOT empty (this test should FAIL before the fix)
        assert processed.key_data, "key_data should not be empty for CarrierFinance events"

        # Verify carrier ID is extracted
        assert "carrier_id" in processed.key_data
        assert processed.key_data["carrier_id"] == 3700005632

        # Verify balance information is extracted
        assert "carrier_balance" in processed.key_data
        assert processed.key_data["carrier_balance"] == 1500000000

        assert "reserve_balance" in processed.key_data
        assert processed.key_data["reserve_balance"] == 100000000

        assert "available_balance" in processed.key_data
        assert processed.key_data["available_balance"] == 1400000000

        # Verify tax rates are extracted
        assert "tax_rates" in processed.key_data
        tax_rates = processed.key_data["tax_rates"]
        assert tax_rates["rearm"] == 0
        assert tax_rates["refuel"] == 0
        assert tax_rates["repair"] == 0

    def test_issue_18_carrier_finance_summary_generation(self, processor):
        """
        Test that CarrierFinance events generate meaningful summaries.

        Before fix: "CarrierFinance event occurred"
        After fix: Should include balance information
        """
        carrier_finance_event = {
            "timestamp": "2025-10-09T04:00:55Z",
            "event": "CarrierFinance",
            "CarrierID": 3700005632,
            "CarrierBalance": 1500000000,
            "AvailableBalance": 1400000000
        }

        processed = processor.process_event(carrier_finance_event)

        # Summary should be more descriptive than the generic default
        assert processed.summary != "CarrierFinance event occurred"


class TestIssue18CarrierCrewServices:
    """Test for Issue #18: CarrierCrewServices event data extraction"""

    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()

    def test_issue_18_carrier_crew_services_key_data_extraction(self, processor):
        """
        Test for Issue #18: CarrierCrewServices Event Returns Empty key_data

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/18

        Problem: CarrierCrewServices events return empty key_data
        Expected: key_data should contain CarrierID, CrewName, Operation
        Actual (before fix): key_data is {}
        """
        carrier_crew_event = {
            "timestamp": "2025-10-09T04:02:15Z",
            "event": "CarrierCrewServices",
            "CarrierID": 3700005632,
            "CrewName": "Bartender",
            "Operation": "ActivateCrew"
        }

        processed = processor.process_event(carrier_crew_event)

        # Verify basic processing
        assert processed.event_type == "CarrierCrewServices"
        assert processed.category == EventCategory.CARRIER
        assert processed.is_valid

        # Verify key_data is NOT empty (this test should FAIL before the fix)
        assert processed.key_data, "key_data should not be empty for CarrierCrewServices events"

        # Verify crew service data is extracted
        assert "carrier_id" in processed.key_data
        assert processed.key_data["carrier_id"] == 3700005632

        assert "crew_name" in processed.key_data
        assert processed.key_data["crew_name"] == "Bartender"

        assert "operation" in processed.key_data
        assert processed.key_data["operation"] == "ActivateCrew"

    def test_issue_18_carrier_crew_services_summary_generation(self, processor):
        """Test that CarrierCrewServices events generate meaningful summaries."""
        carrier_crew_event = {
            "timestamp": "2025-10-09T04:02:15Z",
            "event": "CarrierCrewServices",
            "CarrierID": 3700005632,
            "CrewName": "Bartender",
            "Operation": "ActivateCrew"
        }

        processed = processor.process_event(carrier_crew_event)

        # Summary should include crew name and operation
        assert processed.summary != "CarrierCrewServices event occurred"
        assert "Bartender" in processed.summary or "ActivateCrew" in processed.summary


class TestIssue18CarrierModulePack:
    """Test for Issue #18: CarrierModulePack event data extraction"""

    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()

    def test_issue_18_carrier_module_pack_key_data_extraction(self, processor):
        """
        Test for Issue #18: CarrierModulePack Event Returns Empty key_data

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/18

        Problem: CarrierModulePack events return empty key_data
        Expected: key_data should contain CarrierID, PackTheme, Operation, Cost
        Actual (before fix): key_data is {}
        """
        carrier_module_event = {
            "timestamp": "2025-10-09T04:03:20Z",
            "event": "CarrierModulePack",
            "CarrierID": 3700005632,
            "Operation": "buypack",
            "PackTheme": "MiningUtilities",
            "PackTier": 1,
            "Cost": 500000
        }

        processed = processor.process_event(carrier_module_event)

        # Verify basic processing
        assert processed.event_type == "CarrierModulePack"
        assert processed.category == EventCategory.CARRIER
        assert processed.is_valid

        # Verify key_data is NOT empty (this test should FAIL before the fix)
        assert processed.key_data, "key_data should not be empty for CarrierModulePack events"

        # Verify module pack data is extracted
        assert "carrier_id" in processed.key_data
        assert processed.key_data["carrier_id"] == 3700005632

        assert "operation" in processed.key_data
        assert processed.key_data["operation"] == "buypack"

        assert "pack_theme" in processed.key_data
        assert processed.key_data["pack_theme"] == "MiningUtilities"

        assert "pack_tier" in processed.key_data
        assert processed.key_data["pack_tier"] == 1

        assert "cost" in processed.key_data
        assert processed.key_data["cost"] == 500000

    def test_issue_18_carrier_module_pack_summary_generation(self, processor):
        """Test that CarrierModulePack events generate meaningful summaries."""
        carrier_module_event = {
            "timestamp": "2025-10-09T04:03:20Z",
            "event": "CarrierModulePack",
            "CarrierID": 3700005632,
            "Operation": "buypack",
            "PackTheme": "MiningUtilities",
            "Cost": 500000
        }

        processed = processor.process_event(carrier_module_event)

        # Summary should include pack theme and operation
        assert processed.summary != "CarrierModulePack event occurred"
        assert "MiningUtilities" in processed.summary or "buypack" in processed.summary
