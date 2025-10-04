"""
Unit tests for Milestone 17: Comprehensive Event Coverage.

Tests that all 34 previously unmapped events are now properly categorized
and not falling into EventCategory.OTHER (unless intended).
"""

import pytest
from datetime import datetime, timezone

from src.journal.events import EventProcessor, EventCategory, ProcessedEvent


class TestMilestone17NavigationEvents:
    """Test newly mapped navigation events."""

    def test_book_taxi_categorized_correctly(self):
        """Test BookTaxi event is categorized as NAVIGATION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "BookTaxi",
            "Cost": 1000
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.NAVIGATION
        assert processed.event_type == "BookTaxi"
        assert processed.is_valid

    def test_fsd_target_categorized_correctly(self):
        """Test FSDTarget event is categorized as NAVIGATION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "FSDTarget",
            "Name": "Pleiades Sector AB-W b2-4",
            "SystemAddress": 84180519395914
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.NAVIGATION
        assert processed.event_type == "FSDTarget"
        assert processed.is_valid

    def test_supercruise_destination_drop_categorized_correctly(self):
        """Test SupercruiseDestinationDrop event is categorized as NAVIGATION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "SupercruiseDestinationDrop",
            "Type": "Station",
            "Threat": 0
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.NAVIGATION
        assert processed.event_type == "SupercruiseDestinationDrop"
        assert processed.is_valid

    def test_uss_drop_categorized_correctly(self):
        """Test USSDrop event is categorized as NAVIGATION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "USSDrop",
            "USSType": "$USS_Type_Salvage;",
            "USSThreat": 0
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.NAVIGATION
        assert processed.event_type == "USSDrop"
        assert processed.is_valid

    def test_fetch_remote_module_categorized_correctly(self):
        """Test FetchRemoteModule event is categorized as NAVIGATION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "FetchRemoteModule",
            "StorageSlot": 1,
            "StoredItem": "int_planetapproachsuite"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.NAVIGATION
        assert processed.event_type == "FetchRemoteModule"
        assert processed.is_valid


class TestMilestone17ExplorationEvents:
    """Test newly mapped exploration events."""

    def test_nav_beacon_scan_categorized_correctly(self):
        """Test NavBeaconScan event is categorized as EXPLORATION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "NavBeaconScan",
            "NumBodies": 12
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.EXPLORATION
        assert processed.event_type == "NavBeaconScan"
        assert processed.is_valid

    def test_scan_bary_centre_categorized_correctly(self):
        """Test ScanBaryCentre event is categorized as EXPLORATION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "ScanBaryCentre",
            "StarSystem": "Blae Drye SG-P b25-6",
            "BodyID": 1
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.EXPLORATION
        assert processed.event_type == "ScanBaryCentre"
        assert processed.is_valid

    def test_fss_signal_discovered_categorized_correctly(self):
        """Test FSSSignalDiscovered event is categorized as EXPLORATION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "FSSSignalDiscovered",
            "SignalName": "$MULTIPLAYER_SCENARIO42_TITLE;",
            "IsStation": False
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.EXPLORATION
        assert processed.event_type == "FSSSignalDiscovered"
        assert processed.is_valid


class TestMilestone17CombatEvents:
    """Test newly mapped combat events."""

    def test_data_scanned_categorized_correctly(self):
        """Test DataScanned event is categorized as COMBAT."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "DataScanned",
            "Type": "$Datascan_DataPointEncoded;"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.COMBAT
        assert processed.event_type == "DataScanned"
        assert processed.is_valid

    def test_heat_damage_categorized_correctly(self):
        """Test HeatDamage event is categorized as COMBAT."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "HeatDamage"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.COMBAT
        assert processed.event_type == "HeatDamage"
        assert processed.is_valid

    def test_heat_warning_categorized_correctly(self):
        """Test HeatWarning event is categorized as COMBAT."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "HeatWarning"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.COMBAT
        assert processed.event_type == "HeatWarning"
        assert processed.is_valid

    def test_launch_drone_categorized_correctly(self):
        """Test LaunchDrone event is categorized as COMBAT."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "LaunchDrone",
            "Type": "Hatchbreaker"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.COMBAT
        assert processed.event_type == "LaunchDrone"
        assert processed.is_valid

    def test_scanned_categorized_correctly(self):
        """Test Scanned event is categorized as COMBAT."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "Scanned",
            "ScanType": "Cargo"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.COMBAT
        assert processed.event_type == "Scanned"
        assert processed.is_valid


class TestMilestone17TradingEvents:
    """Test newly mapped trading events."""

    def test_refuel_all_categorized_correctly(self):
        """Test RefuelAll event is categorized as TRADING."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "RefuelAll",
            "Cost": 1000,
            "Amount": 32.0
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.TRADING
        assert processed.event_type == "RefuelAll"
        assert processed.is_valid

    def test_redeem_voucher_categorized_correctly(self):
        """Test RedeemVoucher event is categorized as TRADING."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "RedeemVoucher",
            "Type": "bounty",
            "Amount": 15000
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.TRADING
        assert processed.event_type == "RedeemVoucher"
        assert processed.is_valid

    def test_buy_drones_categorized_correctly(self):
        """Test BuyDrones event is categorized as TRADING."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "BuyDrones",
            "Type": "Drones",
            "Count": 20,
            "BuyPrice": 101,
            "TotalCost": 2020
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.TRADING
        assert processed.event_type == "BuyDrones"
        assert processed.is_valid

    def test_cargo_transfer_categorized_correctly(self):
        """Test CargoTransfer event is categorized as TRADING."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "CargoTransfer",
            "Transfers": [
                {"Type": "Gold", "Count": 10, "Direction": "tocarrier"}
            ]
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.TRADING
        assert processed.event_type == "CargoTransfer"
        assert processed.is_valid


class TestMilestone17ShipEvents:
    """Test newly mapped ship management events."""

    def test_fuel_scoop_categorized_correctly(self):
        """Test FuelScoop event is categorized as SHIP."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "FuelScoop",
            "Scooped": 1.0,
            "Total": 32.0
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SHIP
        assert processed.event_type == "FuelScoop"
        assert processed.is_valid

    def test_set_user_ship_name_categorized_correctly(self):
        """Test SetUserShipName event is categorized as SHIP."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "SetUserShipName",
            "Ship": "python",
            "ShipID": 1,
            "UserShipName": "Enterprise",
            "UserShipId": "NCC-1701"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SHIP
        assert processed.event_type == "SetUserShipName"
        assert processed.is_valid

    def test_ship_locker_categorized_correctly(self):
        """Test ShipLocker event is categorized as SHIP."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "ShipLocker",
            "Items": [],
            "Components": []
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SHIP
        assert processed.event_type == "ShipLocker"
        assert processed.is_valid

    def test_ship_redeemed_categorized_correctly(self):
        """Test ShipRedeemed event is categorized as SHIP."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "ShipRedeemed",
            "MarketID": 128666762,
            "Ship": "python"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SHIP
        assert processed.event_type == "ShipRedeemed"
        assert processed.is_valid

    def test_shipyard_redeem_categorized_correctly(self):
        """Test ShipyardRedeem event is categorized as SHIP."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "ShipyardRedeem",
            "MarketID": 128666762
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SHIP
        assert processed.event_type == "ShipyardRedeem"
        assert processed.is_valid

    def test_module_info_categorized_correctly(self):
        """Test ModuleInfo event is categorized as SHIP."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "ModuleInfo",
            "Modules": []
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SHIP
        assert processed.event_type == "ModuleInfo"
        assert processed.is_valid

    def test_stored_modules_categorized_correctly(self):
        """Test StoredModules event is categorized as SHIP."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "StoredModules",
            "MarketID": 128666762,
            "StationName": "Jameson Memorial",
            "StarSystem": "Shinrarta Dezhra",
            "Items": []
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SHIP
        assert processed.event_type == "StoredModules"
        assert processed.is_valid


class TestMilestone17MissionEvents:
    """Test newly mapped mission/community goal events."""

    def test_community_goal_categorized_correctly(self):
        """Test CommunityGoal event is categorized as MISSION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "CommunityGoal",
            "CurrentGoals": []
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.MISSION
        assert processed.event_type == "CommunityGoal"
        assert processed.is_valid

    def test_community_goal_join_categorized_correctly(self):
        """Test CommunityGoalJoin event is categorized as MISSION."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "CommunityGoalJoin",
            "CGID": 726,
            "Name": "Alliance Research Initiative"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.MISSION
        assert processed.event_type == "CommunityGoalJoin"
        assert processed.is_valid


class TestMilestone17CrewEvents:
    """Test newly mapped crew events."""

    def test_npc_crew_paid_wage_categorized_correctly(self):
        """Test NpcCrewPaidWage event is categorized as CREW."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "NpcCrewPaidWage",
            "NpcCrewName": "Margaret Parrish",
            "NpcCrewId": 236064708,
            "Amount": 12345
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.CREW
        assert processed.event_type == "NpcCrewPaidWage"
        assert processed.is_valid


class TestMilestone17PowerplayEvents:
    """Test newly mapped powerplay events."""

    def test_powerplay_categorized_correctly(self):
        """Test Powerplay event is categorized as POWERPLAY."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "Powerplay",
            "Power": "Edmund Mahon",
            "Rank": 2,
            "Merits": 100,
            "Votes": 0,
            "TimePledged": 1234567
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.POWERPLAY
        assert processed.event_type == "Powerplay"
        assert processed.is_valid


class TestMilestone17CarrierEvents:
    """Test newly mapped carrier events."""

    def test_carrier_location_categorized_correctly(self):
        """Test CarrierLocation event is categorized as CARRIER."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "CarrierLocation",
            "StarSystem": "Shinrarta Dezhra",
            "SystemAddress": 3932277478106,
            "Body": "Jameson Memorial"
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.CARRIER
        assert processed.event_type == "CarrierLocation"
        assert processed.is_valid


class TestMilestone17OdysseyEvents:
    """Test newly mapped Odyssey/on-foot events."""

    def test_backpack_categorized_correctly(self):
        """Test Backpack event is categorized as SUIT."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "Backpack",
            "Items": [],
            "Components": []
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SUIT
        assert processed.event_type == "Backpack"
        assert processed.is_valid

    def test_reservoir_replenished_categorized_correctly(self):
        """Test ReservoirReplenished event is categorized as SUIT."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "ReservoirReplenished",
            "FuelMain": 1.0,
            "FuelReservoir": 0.42
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.SUIT
        assert processed.event_type == "ReservoirReplenished"
        assert processed.is_valid


class TestMilestone17OtherEvents:
    """Test newly mapped OTHER category events."""

    def test_commit_crime_categorized_correctly(self):
        """Test CommitCrime event is categorized as OTHER."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "CommitCrime",
            "CrimeType": "assault",
            "Faction": "The Dark Wheel",
            "Fine": 200
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.OTHER
        assert processed.event_type == "CommitCrime"
        assert processed.is_valid

    def test_crime_victim_categorized_correctly(self):
        """Test CrimeVictim event is categorized as OTHER."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "CrimeVictim",
            "Offender": "John Doe",
            "CrimeType": "assault",
            "Fine": 200
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.OTHER
        assert processed.event_type == "CrimeVictim"
        assert processed.is_valid

    def test_materials_categorized_correctly(self):
        """Test Materials event is categorized as OTHER."""
        processor = EventProcessor()
        event = {
            "timestamp": "2025-10-04T14:00:00Z",
            "event": "Materials",
            "Raw": [],
            "Manufactured": [],
            "Encoded": []
        }
        processed = processor.process_event(event)

        assert processed.category == EventCategory.OTHER
        assert processed.event_type == "Materials"
        assert processed.is_valid


class TestMilestone17ComprehensiveCoverage:
    """Test comprehensive coverage of all newly mapped events."""

    def test_all_34_events_are_mapped(self):
        """Verify all 34 unmapped events are now in EVENT_CATEGORIES."""
        processor = EventProcessor()

        # List of all 34 events from gap analysis
        newly_mapped_events = [
            # Navigation (6)
            "BookTaxi", "FSDTarget", "SupercruiseDestinationDrop", "USSDrop",
            "FetchRemoteModule",
            # Exploration (3)
            "NavBeaconScan", "ScanBaryCentre", "FSSSignalDiscovered",
            # Combat (5)
            "DataScanned", "HeatDamage", "HeatWarning", "LaunchDrone", "Scanned",
            # Trading (4)
            "RefuelAll", "RedeemVoucher", "BuyDrones", "CargoTransfer",
            # Ship (7)
            "FuelScoop", "SetUserShipName", "ShipLocker", "ShipRedeemed",
            "ShipyardRedeem", "ModuleInfo", "StoredModules",
            # Mission (2)
            "CommunityGoal", "CommunityGoalJoin",
            # Crew (1)
            "NpcCrewPaidWage",
            # Powerplay (1)
            "Powerplay",
            # Carrier (1)
            "CarrierLocation",
            # Odyssey/Suit (2)
            "Backpack", "ReservoirReplenished",
            # Other (3)
            "CommitCrime", "CrimeVictim", "Materials"
        ]

        # Verify all are in EVENT_CATEGORIES
        for event_type in newly_mapped_events:
            assert event_type in processor.EVENT_CATEGORIES, \
                f"{event_type} should be in EVENT_CATEGORIES"

    def test_properly_categorized_events_not_in_unknown_list(self):
        """Verify properly categorized events don't appear in unknown events list.

        Note: Events categorized as OTHER will still appear in unknown list by design.
        This test verifies events with specific categories are not listed as unknown.
        """
        processor = EventProcessor()

        # Events that should have specific categories (not OTHER)
        properly_categorized_events = [
            "BookTaxi", "FSDTarget", "SupercruiseDestinationDrop", "USSDrop",
            "FetchRemoteModule", "NavBeaconScan", "ScanBaryCentre",
            "FSSSignalDiscovered", "DataScanned", "HeatDamage", "HeatWarning",
            "LaunchDrone", "Scanned", "RefuelAll", "RedeemVoucher", "BuyDrones",
            "CargoTransfer", "FuelScoop", "SetUserShipName", "ShipLocker",
            "ShipRedeemed", "ShipyardRedeem", "ModuleInfo", "StoredModules",
            "CommunityGoal", "CommunityGoalJoin", "NpcCrewPaidWage", "Powerplay",
            "CarrierLocation", "Backpack", "ReservoirReplenished"
        ]

        # Process one event of each type
        for event_type in properly_categorized_events:
            event = {
                "timestamp": "2025-10-04T14:00:00Z",
                "event": event_type
            }
            processor.process_event(event)

        # None should be in unknown events list
        unknown = processor.get_unknown_events()
        for event_type in properly_categorized_events:
            assert event_type not in unknown, \
                f"{event_type} should not be in unknown events list"

        # Note: CommitCrime, CrimeVictim, and Materials are in EventCategory.OTHER
        # and will appear in unknown list by design - this is expected behavior

    def test_event_count_by_category(self):
        """Test that events are distributed across the expected categories."""
        processor = EventProcessor()

        # Expected distribution
        expected_categories = {
            EventCategory.NAVIGATION: ["BookTaxi", "FSDTarget", "SupercruiseDestinationDrop", "USSDrop", "FetchRemoteModule"],
            EventCategory.EXPLORATION: ["NavBeaconScan", "ScanBaryCentre", "FSSSignalDiscovered"],
            EventCategory.COMBAT: ["DataScanned", "HeatDamage", "HeatWarning", "LaunchDrone", "Scanned"],
            EventCategory.TRADING: ["RefuelAll", "RedeemVoucher", "BuyDrones", "CargoTransfer"],
            EventCategory.SHIP: ["FuelScoop", "SetUserShipName", "ShipLocker", "ShipRedeemed", "ShipyardRedeem", "ModuleInfo", "StoredModules"],
            EventCategory.MISSION: ["CommunityGoal", "CommunityGoalJoin"],
            EventCategory.CREW: ["NpcCrewPaidWage"],
            EventCategory.POWERPLAY: ["Powerplay"],
            EventCategory.CARRIER: ["CarrierLocation"],
            EventCategory.SUIT: ["Backpack", "ReservoirReplenished"],
            EventCategory.OTHER: ["CommitCrime", "CrimeVictim", "Materials"]
        }

        # Verify each event is in the expected category
        for expected_category, event_types in expected_categories.items():
            for event_type in event_types:
                actual_category = processor.EVENT_CATEGORIES.get(event_type)
                assert actual_category == expected_category, \
                    f"{event_type} should be in {expected_category}, but is in {actual_category}"
