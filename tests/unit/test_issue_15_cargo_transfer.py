"""
Test for Issue #15: Fleet Carrier Cargo Inventory Not Tracked

GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/15

Problem: CargoTransfer events not extracting commodity data, fleet carrier cargo not tracked
Expected: CargoTransfer events should have commodity details in key_data
Actual (before fix): key_data is empty {}, carrier cargo inventory not available
"""

import pytest
from datetime import datetime, timezone
from src.journal.events import EventProcessor
from src.utils.data_store import DataStore


class TestIssue15CargoTransferEventData:
    """Test CargoTransfer event data extraction (Issue #15)."""

    def test_issue_15_cargo_transfer_key_data_extraction(self):
        """
        Test for Issue #15: CargoTransfer Event Data Extraction

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/15

        Problem: CargoTransfer events have empty key_data
        Expected: key_data should contain transfers list with commodity details
        Actual (before fix): key_data is {}
        """
        processor = EventProcessor()

        # Real CargoTransfer event from issue #15
        event = {
            "timestamp": "2025-10-04T23:10:17Z",
            "event": "CargoTransfer",
            "Transfers": [
                {
                    "Type": "platinum",
                    "Type_Localised": "Platinum",
                    "Count": 10,
                    "Direction": "tocarrier"
                },
                {
                    "Type": "painite",
                    "Type_Localised": "Painite",
                    "Count": 5,
                    "Direction": "tocarrier"
                }
            ]
        }

        processed = processor.process_event(event)

        # Should extract transfers data
        assert processed.key_data is not None
        assert "transfers" in processed.key_data, "key_data should contain 'transfers'"
        assert len(processed.key_data["transfers"]) == 2, "Should have 2 transfers"

        # Verify first transfer
        transfer1 = processed.key_data["transfers"][0]
        assert transfer1["commodity"] == "platinum"
        assert transfer1["commodity_localized"] == "Platinum"
        assert transfer1["count"] == 10
        assert transfer1["direction"] == "tocarrier"

        # Verify second transfer
        transfer2 = processed.key_data["transfers"][1]
        assert transfer2["commodity"] == "painite"
        assert transfer2["commodity_localized"] == "Painite"
        assert transfer2["count"] == 5
        assert transfer2["direction"] == "tocarrier"

    def test_issue_15_cargo_transfer_summary_generation(self):
        """
        Test for Issue #15: CargoTransfer Event Summary Generation

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/15

        Problem: CargoTransfer events have generic "CargoTransfer event occurred" summary
        Expected: Specific summary like "Transferred 10t Platinum to carrier"
        Actual (before fix): Generic summary
        """
        processor = EventProcessor()

        event = {
            "timestamp": "2025-10-04T23:10:17Z",
            "event": "CargoTransfer",
            "Transfers": [
                {
                    "Type": "platinum",
                    "Type_Localised": "Platinum",
                    "Count": 10,
                    "Direction": "tocarrier"
                }
            ]
        }

        processed = processor.process_event(event)

        # Should generate specific summary
        assert processed.summary != "CargoTransfer event occurred", \
            "Summary should be specific, not generic"
        assert "platinum" in processed.summary.lower() or "Platinum" in processed.summary, \
            "Summary should mention commodity name"
        assert "10" in processed.summary, "Summary should mention count"
        assert "carrier" in processed.summary.lower(), "Summary should mention carrier"

    def test_issue_15_cargo_transfer_multiple_commodities_summary(self):
        """Test CargoTransfer summary with multiple commodities."""
        processor = EventProcessor()

        event = {
            "timestamp": "2025-10-04T23:10:17Z",
            "event": "CargoTransfer",
            "Transfers": [
                {
                    "Type": "platinum",
                    "Type_Localised": "Platinum",
                    "Count": 10,
                    "Direction": "tocarrier"
                },
                {
                    "Type": "painite",
                    "Type_Localised": "Painite",
                    "Count": 5,
                    "Direction": "tocarrier"
                }
            ]
        }

        processed = processor.process_event(event)

        # Should indicate multiple items or total count
        assert processed.summary != "CargoTransfer event occurred"
        # Summary should be informative about the transfer
        assert len(processed.summary) > 20, "Summary should be descriptive"

    def test_issue_15_cargo_transfer_from_carrier(self):
        """Test CargoTransfer event with direction 'toship'."""
        processor = EventProcessor()

        event = {
            "timestamp": "2025-10-04T23:15:00Z",
            "event": "CargoTransfer",
            "Transfers": [
                {
                    "Type": "osmium",
                    "Type_Localised": "Osmium",
                    "Count": 2,
                    "Direction": "toship"
                }
            ]
        }

        processed = processor.process_event(event)

        # Should extract direction correctly
        assert processed.key_data["transfers"][0]["direction"] == "toship"
        # Summary should indicate transfer from carrier
        assert "osmium" in processed.summary.lower() or "Osmium" in processed.summary


class TestIssue15CarrierCargoTracking:
    """Test fleet carrier cargo state tracking (Issue #15)."""

    def test_issue_15_carrier_cargo_state_tracking(self):
        """
        Test for Issue #15: Fleet Carrier Cargo State Tracking

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/15

        Problem: DataStore doesn't track carrier cargo inventory
        Expected: Carrier cargo levels maintained and updated on CargoTransfer events
        Actual (before fix): No carrier cargo tracking
        """
        data_store = DataStore()
        processor = EventProcessor()

        # Process CargoTransfer to carrier
        cargo_transfer_event = {
            "timestamp": "2025-10-04T23:10:17Z",
            "event": "CargoTransfer",
            "Transfers": [
                {
                    "Type": "platinum",
                    "Type_Localised": "Platinum",
                    "Count": 10,
                    "Direction": "tocarrier"
                },
                {
                    "Type": "painite",
                    "Type_Localised": "Painite",
                    "Count": 5,
                    "Direction": "tocarrier"
                }
            ]
        }

        processed = processor.process_event(cargo_transfer_event)
        data_store.store_event(processed)

        # Get game state
        game_state = data_store.get_game_state()

        # Should track carrier cargo
        assert hasattr(game_state, 'carrier_cargo'), \
            "GameState should have carrier_cargo attribute"
        assert game_state.carrier_cargo is not None, \
            "carrier_cargo should not be None"
        assert isinstance(game_state.carrier_cargo, dict), \
            "carrier_cargo should be a dictionary"
        assert "platinum" in game_state.carrier_cargo, \
            "Should track platinum in carrier cargo"
        assert game_state.carrier_cargo["platinum"] == 10, \
            "Should have 10 platinum"
        assert game_state.carrier_cargo["painite"] == 5, \
            "Should have 5 painite"

    def test_issue_15_carrier_cargo_accumulation(self):
        """Test that carrier cargo accumulates correctly."""
        data_store = DataStore()
        processor = EventProcessor()

        # First transfer
        event1 = {
            "timestamp": "2025-10-04T23:10:17Z",
            "event": "CargoTransfer",
            "Transfers": [
                {"Type": "platinum", "Type_Localised": "Platinum", "Count": 10, "Direction": "tocarrier"}
            ]
        }
        data_store.store_event(processor.process_event(event1))

        # Second transfer
        event2 = {
            "timestamp": "2025-10-04T23:15:00Z",
            "event": "CargoTransfer",
            "Transfers": [
                {"Type": "platinum", "Type_Localised": "Platinum", "Count": 13, "Direction": "tocarrier"}
            ]
        }
        data_store.store_event(processor.process_event(event2))

        game_state = data_store.get_game_state()

        # Should accumulate: 10 + 13 = 23
        assert game_state.carrier_cargo["platinum"] == 23, \
            "Carrier cargo should accumulate (10 + 13 = 23)"

    def test_issue_15_carrier_cargo_removal(self):
        """Test that carrier cargo decreases when transferred to ship."""
        data_store = DataStore()
        processor = EventProcessor()

        # Transfer to carrier
        event1 = {
            "timestamp": "2025-10-04T23:10:17Z",
            "event": "CargoTransfer",
            "Transfers": [
                {"Type": "osmium", "Type_Localised": "Osmium", "Count": 10, "Direction": "tocarrier"}
            ]
        }
        data_store.store_event(processor.process_event(event1))

        # Transfer from carrier to ship
        event2 = {
            "timestamp": "2025-10-04T23:15:00Z",
            "event": "CargoTransfer",
            "Transfers": [
                {"Type": "osmium", "Type_Localised": "Osmium", "Count": 2, "Direction": "toship"}
            ]
        }
        data_store.store_event(processor.process_event(event2))

        game_state = data_store.get_game_state()

        # Should have 10 - 2 = 8 osmium
        assert game_state.carrier_cargo["osmium"] == 8, \
            "Carrier cargo should decrease when transferred to ship (10 - 2 = 8)"

    def test_issue_15_get_material_inventory_includes_carrier_cargo(self):
        """
        Test for Issue #15: get_material_inventory Should Include Carrier Cargo

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/15

        Problem: get_material_inventory() only shows ship cargo, not carrier cargo
        Expected: Response should include carrier_cargo field with fleet carrier inventory
        Actual (before fix): No carrier cargo in response
        """
        from src.elite_mcp.mcp_tools import MCPTools

        data_store = DataStore()
        processor = EventProcessor()
        mcp_tools = MCPTools(data_store)

        # Store CargoTransfer event
        event = {
            "timestamp": "2025-10-04T23:10:17Z",
            "event": "CargoTransfer",
            "Transfers": [
                {"Type": "platinum", "Type_Localised": "Platinum", "Count": 23, "Direction": "tocarrier"},
                {"Type": "painite", "Type_Localised": "Painite", "Count": 68, "Direction": "tocarrier"},
                {"Type": "osmium", "Type_Localised": "Osmium", "Count": 2, "Direction": "tocarrier"}
            ]
        }
        data_store.store_event(processor.process_event(event))

        # Get inventory (sync call for test)
        import asyncio
        inventory = asyncio.run(mcp_tools.get_material_inventory())

        # Should include carrier_cargo field
        assert "carrier_cargo" in inventory, \
            "get_material_inventory should include carrier_cargo field"
        assert inventory["carrier_cargo"] is not None, \
            "carrier_cargo should not be None"
        assert len(inventory["carrier_cargo"]) > 0, \
            "carrier_cargo should not be empty"
        assert "platinum" in inventory["carrier_cargo"], \
            "Should include platinum in carrier_cargo"
        assert inventory["carrier_cargo"]["platinum"] == 23, \
            "Should have correct platinum count"
        assert inventory["carrier_cargo"]["painite"] == 68, \
            "Should have correct painite count"
        assert inventory["carrier_cargo"]["osmium"] == 2, \
            "Should have correct osmium count"


class TestIssue15SearchCargoTransferEvents:
    """Test searching CargoTransfer events returns commodity data (Issue #15)."""

    def test_issue_15_search_cargo_transfer_events_returns_data(self):
        """
        Test for Issue #15: search_events for CargoTransfer Should Return Commodity Data

        GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/15

        Problem: Searching CargoTransfer events returns empty key_data
        Expected: key_data should contain commodity, count, direction
        Actual (before fix): key_data is {}
        """
        from src.elite_mcp.mcp_tools import MCPTools

        data_store = DataStore()
        processor = EventProcessor()
        mcp_tools = MCPTools(data_store)

        # Store multiple CargoTransfer events
        events = [
            {
                "timestamp": "2025-10-04T20:51:00Z",
                "event": "CargoTransfer",
                "Transfers": [
                    {"Type": "platinum", "Type_Localised": "Platinum", "Count": 5, "Direction": "tocarrier"}
                ]
            },
            {
                "timestamp": "2025-10-04T23:10:17Z",
                "event": "CargoTransfer",
                "Transfers": [
                    {"Type": "platinum", "Type_Localised": "Platinum", "Count": 10, "Direction": "tocarrier"},
                    {"Type": "painite", "Type_Localised": "Painite", "Count": 5, "Direction": "tocarrier"}
                ]
            }
        ]

        for event in events:
            data_store.store_event(processor.process_event(event))

        # Search for CargoTransfer events
        import asyncio
        results = asyncio.run(mcp_tools.search_events(
            event_types=["CargoTransfer"],
            max_results=10
        ))

        # Should find events with data
        assert len(results["events"]) > 0, "Should find CargoTransfer events"

        for event_data in results["events"]:
            if event_data["event_type"] == "CargoTransfer":
                # key_data should NOT be empty
                assert event_data["key_data"] != {}, \
                    f"CargoTransfer key_data should not be empty, got: {event_data['key_data']}"
                assert "transfers" in event_data["key_data"], \
                    "key_data should contain 'transfers'"

                # Verify transfers data
                for transfer in event_data["key_data"]["transfers"]:
                    assert "commodity" in transfer, "Transfer should have commodity"
                    assert "count" in transfer, "Transfer should have count"
                    assert "direction" in transfer, "Transfer should have direction"
