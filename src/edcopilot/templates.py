"""
EDCoPilot File Templates System

Provides template classes for generating EDCoPilot custom chatter files
with proper formatting, conditions, and token support.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ChatterType(Enum):
    """Types of EDCoPilot chatter files."""
    SPACE_CHATTER = "SpaceChatter"
    CREW_CHATTER = "CrewChatter"
    DEEP_SPACE_CHATTER = "DeepSpaceChatter"


class VoiceProvider(Enum):
    """Supported voice providers for EDCoPilot."""
    ARIA = "ARIA"
    MICROSOFT = "MICROSOFT"
    AZURE = "AZURE"
    CEREPROC = "CEREPROC"
    IVONA = "IVONA"


@dataclass
class ChatterEntry:
    """Single chatter entry with conditions, voice, and text."""
    text: str
    conditions: Optional[List[str]] = None
    voice_override: Optional[str] = None
    probability: float = 1.0
    chatter_type: ChatterType = ChatterType.SPACE_CHATTER

    def format_for_edcopilot(self) -> str:
        """Format entry for EDCoPilot file format based on chatter type."""
        if self.chatter_type == ChatterType.SPACE_CHATTER:
            return self._format_space_chatter()
        elif self.chatter_type in [ChatterType.CREW_CHATTER, ChatterType.DEEP_SPACE_CHATTER]:
            return self._format_crew_chatter()
        else:
            return self._format_space_chatter()  # Default fallback

    def _format_space_chatter(self) -> str:
        """Format for Space Chatter - proper EDCoPilot format."""
        # For space chatter, EDCoPilot uses either:
        # 1. Simple format: "Dialogue text"
        # 2. Conditional format: "(Condition) Dialogue text"

        if self.conditions:
            # Use parentheses format for conditions
            condition_str = "(" + "&".join(self.conditions) + ")"
            return f"{condition_str} {self.text}"
        else:
            # Simple dialogue without conditions
            return self.text

    def _format_crew_chatter(self) -> str:
        """Format for Crew Chatter - simple line (conversations handled at template level)."""
        # For crew chatter, individual entries are just dialogue lines
        # The conversation structure is handled by the template manager
        return self.text


class EDCoPilotTokens:
    """
    Available tokens that EDCoPilot can replace in chatter.

    Token names match authoritative EDCoPilot format (lowercase).
    Based on tokens found in EDCoPilot default files.
    """

    # Commander tokens (authoritative)
    CMDR_NAME = "<cmdrname>"              # Commander's name
    CMDR_ADDRESS = "<cmdraddress>"        # Sir/Ma'am/Commander

    # Ship tokens (authoritative)
    MY_SHIP_NAME = "<myshipname>"         # Player's ship name
    CALLSIGN = "<callsign>"               # Ship callsign
    OTHER_CALLSIGN = "<othercallsign>"    # Another ship's callsign
    SHIP_CORPORATION = "<shipCorporation>" # Ship manufacturer (note: CamelCase in original)

    # Location tokens (authoritative)
    STAR_SYSTEM = "<starsystem>"          # Current star system
    RANDOM_STAR_SYSTEM = "<randomstarsystem>" # Random system for variety
    STATION_NAME = "<stationname>"        # Station/port name
    LOCAL_DESTINATION = "<localdestination>" # Local destination

    # Flight tokens (authoritative)
    FLIGHT_NUM = "<flightnum>"            # Flight number for Apex/etc

    # Status tokens (authoritative)
    FUEL_LEVELS = "<fuellevels>"          # Fuel level percentage

    # Old token names (deprecated - kept for backwards compatibility)
    # These will be mapped to new names in get_token_mapping()
    COMMANDER_NAME = "<CommanderName>"    # DEPRECATED: Use CMDR_NAME
    SYSTEM_NAME = "<SystemName>"          # DEPRECATED: Use STAR_SYSTEM
    STATION_NAME_OLD = "<StationName>"    # DEPRECATED: Use STATION_NAME
    SHIP_NAME = "<ShipName>"              # DEPRECATED: Use MY_SHIP_NAME
    FUEL_PERCENT = "<FuelPercent>"        # DEPRECATED: Use FUEL_LEVELS

    # Extended tokens (not in authoritative files, but useful)
    COMMANDER_RANK = "<CommanderRank>"
    SHIP_TYPE = "<ShipType>"
    BODY_NAME = "<BodyName>"
    SHIELD_PERCENT = "<ShieldPercent>"
    HULL_PERCENT = "<HullPercent>"
    CREDITS = "<Credits>"
    JUMP_DISTANCE = "<JumpDistance>"
    DISTANCE_FROM_SOL = "<DistanceFromSol>"
    NEXT_SYSTEM = "<NextSystem>"
    CARGO_COUNT = "<CargoCount>"
    CARGO_CAPACITY = "<CargoCapacity>"
    MISSION_COUNT = "<MissionCount>"

    @classmethod
    def get_token_mapping(cls) -> Dict[str, str]:
        """
        Get mapping from old TitleCase token names to new lowercase names.

        Used for backwards compatibility when processing existing templates
        or user-provided text with old token format.

        Returns:
            Dictionary mapping old token names to new authoritative names
        """
        return {
            "<CommanderName>": "<cmdrname>",
            "<SystemName>": "<starsystem>",
            "<StationName>": "<stationname>",
            "<ShipName>": "<myshipname>",
            "<FuelPercent>": "<fuellevels>",
        }


class EDCoPilotConditions:
    """Available conditions that EDCoPilot recognizes."""

    # Basic states
    DOCKED = "Docked"
    IN_SUPERCRUISE = "InSupercruise"
    IN_NORMAL_SPACE = "InNormalSpace"
    LANDED = "Landed"

    # Combat states
    UNDER_ATTACK = "UnderAttack"
    IN_DANGER = "InDanger"
    SHIELDS_DOWN = "ShieldsDown"

    # Navigation states
    JUMPING = "Jumping"
    APPROACHING_STATION = "ApproachingStation"
    FUEL_LOW = "FuelLow"

    # Activity states
    SCANNING = "Scanning"
    MINING = "Mining"
    TRADING = "Trading"
    EXPLORING = "Exploring"

    # Special conditions
    DEEP_SPACE = "DeepSpace"  # >5000 LY from Sol and Colonia
    FIRST_DISCOVERY = "FirstDiscovery"
    HIGH_VALUE_TARGET = "HighValueTarget"


class SpaceRole(Enum):
    """Speaker roles for space chatter conversations."""
    SHIP1 = "[<ship1>]"               # Player's ship
    SHIP2 = "[<ship2>]"               # Another ship
    STATIONNAME = "[<stationname>]"   # Station control


@dataclass
class SpaceConversation:
    """
    Multi-speaker space conversation for space chatter files.

    Space chatter uses conversation blocks with [example]...[\\example] markers
    and speaker roles like [<ship1>], [<stationname>].

    Based on authoritative EDCoPilot.SpaceChatter.txt format.
    """
    dialogue_lines: List[Tuple[SpaceRole, str]]  # (speaker, text) pairs
    conditions: Optional[List[str]] = None
    probability: float = 1.0

    def __post_init__(self):
        """Validate conversation structure."""
        if not self.dialogue_lines:
            raise ValueError("Space conversation must have at least one dialogue line")

    def format_for_edcopilot(self) -> str:
        """
        Format conversation for EDCoPilot space chatter format.

        Returns conversation block with [example]...[\\example] markers.
        Conditions are placed inline with [example] tag if present.
        """
        # Build condition string if present
        condition_str = ""
        if self.conditions:
            condition_str = " (" + "&".join(self.conditions) + ")"

        # Start with [example] tag (with optional conditions)
        lines = [f"[example]{condition_str}"]

        # Add each dialogue line with speaker role
        for speaker, text in self.dialogue_lines:
            lines.append(f"{speaker.value} {text}")

        # End with [\example] tag (backslash, not forward slash)
        lines.append("[\\example]")

        return "\n".join(lines)


class CrewRole(Enum):
    """Standard crew roles for crew chatter conversations."""
    EDCOPILOT = "[<EDCoPilot>]"        # Ship's computer
    OPERATIONS = "[<Operations>]"       # Operations officer
    HELM = "[<Helm>]"                  # Helm officer
    ENGINEERING = "[<Engineering>]"    # Chief engineer
    COMMS = "[<Comms>]"               # Communications officer
    NUMBER1 = "[<Number1>]"           # First officer
    SCIENCE = "[<Science>]"           # Science officer
    SECURITY = "[<Security>]"         # Security chief


@dataclass
class CrewConversation:
    """Multi-speaker crew conversation for crew chatter files."""
    dialogue_lines: List[Tuple[CrewRole, str]]  # (speaker, text) pairs
    conditions: Optional[List[str]] = None
    probability: float = 1.0

    def format_for_edcopilot(self) -> str:
        """Format conversation for EDCoPilot crew chatter format."""
        lines = ["[example]"]

        for speaker, text in self.dialogue_lines:
            lines.append(f"{speaker.value} {text}")

        lines.append("[\\example]")
        return "\n".join(lines)


class SpaceChatterTemplate:
    """
    Template for generating EDCoPilot Space Chatter files.

    Space Chatter uses conversation blocks with [example]...[\\example] markers
    and speaker roles, not single-line conditional format.

    Based on authoritative EDCoPilot.SpaceChatter.txt format.
    """

    def __init__(self):
        self.conversations: List[SpaceConversation] = []
        self.filename = "EDCoPilot.SpaceChatter.Custom.txt"

    def add_conversation(self, conversation: SpaceConversation) -> None:
        """Add a space conversation block."""
        self.conversations.append(conversation)

    def add_entry(self, text: str, conditions: Optional[List[str]] = None,
                  voice_override: Optional[str] = None) -> None:
        """
        DEPRECATED: Add a chatter entry (old API).

        For backwards compatibility, converts single-line entries to conversation blocks.
        New code should use add_conversation() instead.
        """
        # Convert old single-line entry to conversation format
        conversation = SpaceConversation(
            dialogue_lines=[(SpaceRole.SHIP1, text)],
            conditions=conditions
        )
        self.conversations.append(conversation)

    def generate_navigation_chatter(self) -> None:
        """Generate navigation-related chatter conversations."""
        # System entry conversation
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, f"Entering {EDCoPilotTokens.STAR_SYSTEM}. Scanning for points of interest."),
            ],
            conditions=[EDCoPilotConditions.IN_SUPERCRUISE]
        ))

        # Docking clearance conversation
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, f"{EDCoPilotTokens.STATION_NAME} control, requesting docking clearance."),
                (SpaceRole.STATIONNAME, f"{EDCoPilotTokens.CALLSIGN}, this is {EDCoPilotTokens.STATION_NAME} control. Sending landing pad assignment now."),
                (SpaceRole.SHIP1, "Copy that, proceeding to pad."),
            ],
            conditions=[EDCoPilotConditions.APPROACHING_STATION]
        ))

        # Docked conversation
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, f"Successfully docked at {EDCoPilotTokens.STATION_NAME}."),
                (SpaceRole.STATIONNAME, "Welcome, Commander. Station services are available."),
            ],
            conditions=[EDCoPilotConditions.DOCKED]
        ))

        # Departure conversation
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Control, requesting departure clearance."),
                (SpaceRole.STATIONNAME, "Clearance granted. Safe travels, Commander."),
            ],
            conditions=[EDCoPilotConditions.DOCKED]
        ))

        # Fuel warning conversation
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, f"Fuel reserves at {EDCoPilotTokens.FUEL_LEVELS} percent. Need to refuel soon."),
            ],
            conditions=[EDCoPilotConditions.FUEL_LOW]
        ))

    def generate_exploration_chatter(self) -> None:
        """Generate exploration-related chatter conversations."""
        # Scanning discovery
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Detailed surface scan complete. Fascinating astronomical data."),
            ],
            conditions=[EDCoPilotConditions.SCANNING]
        ))

        # First discovery
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "We appear to be the first to discover this system!"),
            ],
            conditions=[EDCoPilotConditions.FIRST_DISCOVERY]
        ))

        # Deep space exploration
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "The void between stars is vast, but every system tells a story."),
            ],
            conditions=[EDCoPilotConditions.DEEP_SPACE, EDCoPilotConditions.EXPLORING]
        ))

    def generate_combat_chatter(self) -> None:
        """Generate combat-related chatter conversations."""
        # Under attack
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Multiple hostiles on scanner! Engaging defensive systems!"),
            ],
            conditions=[EDCoPilotConditions.UNDER_ATTACK]
        ))

        # Shields down
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Shield generators offline! Hull integrity critical!"),
            ],
            conditions=[EDCoPilotConditions.SHIELDS_DOWN, EDCoPilotConditions.IN_DANGER]
        ))

        # Post-combat
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Target eliminated. Scanning for additional threats."),
            ],
            conditions=[EDCoPilotConditions.IN_NORMAL_SPACE]
        ))

    def generate_trading_chatter(self) -> None:
        """Generate trading-related chatter conversations."""
        # Cargo status
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, f"Cargo manifest shows {EDCoPilotTokens.CARGO_COUNT} of {EDCoPilotTokens.CARGO_CAPACITY} tons loaded."),
            ],
            conditions=[EDCoPilotConditions.TRADING, EDCoPilotConditions.DOCKED]
        ))

        # Profitable trade
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, f"Credits updated: {EDCoPilotTokens.CREDITS}. Profitable trading run."),
            ],
            conditions=[EDCoPilotConditions.TRADING, EDCoPilotConditions.DOCKED]
        ))

        # Market analysis
        self.conversations.append(SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, "Market data suggests excellent profit margins on our current cargo."),
            ],
            conditions=[EDCoPilotConditions.TRADING]
        ))

    def generate_default_chatter(self) -> None:
        """Generate all default chatter categories."""
        logger.info("Generating default Space Chatter entries")
        self.generate_navigation_chatter()
        self.generate_exploration_chatter()
        self.generate_combat_chatter()
        self.generate_trading_chatter()

    def to_file_content(self) -> str:
        """
        Generate the complete file content for EDCoPilot.

        NO COMMENTS - EDCoPilot parser rejects comment lines.
        Uses conversation blocks with [example]...[\\example] markers.
        """
        lines = []

        # Add all conversations
        for conversation in self.conversations:
            lines.append(conversation.format_for_edcopilot())
            lines.append("")  # Blank line between conversations

        return "\n".join(lines)


class CrewChatterTemplate:
    """Template for generating EDCoPilot Crew Chatter files."""

    def __init__(self):
        self.entries: List[ChatterEntry] = []
        self.filename = "EDCoPilot.CrewChatter.Custom.txt"

    def add_entry(self, text: str, conditions: Optional[List[str]] = None,
                  voice_override: Optional[str] = None) -> None:
        """Add a crew chatter entry."""
        entry = ChatterEntry(text=text, conditions=conditions, voice_override=voice_override)
        self.entries.append(entry)

    def generate_crew_responses(self) -> None:
        """Generate crew response chatter using proper conversation block format."""
        # Crew chatter uses conversation blocks instead of individual entries
        # Use lowercase tokens matching authoritative format
        self.conversation_blocks = [
            # Navigation conversation
            {
                "condition": EDCoPilotConditions.IN_SUPERCRUISE,
                "conversation": [
                    f"{CrewRole.OPERATIONS.value} Navigation officer reports jump calculations complete, {EDCoPilotTokens.CMDR_ADDRESS}",
                    f"{CrewRole.EDCOPILOT.value} Acknowledged, {EDCoPilotTokens.CMDR_NAME}. Course set and locked"
                ]
            },
            # Docking conversation
            {
                "condition": EDCoPilotConditions.APPROACHING_STATION,
                "conversation": [
                    f"{CrewRole.HELM.value} Helm responding. Setting course for optimal approach vector",
                    f"{CrewRole.OPERATIONS.value} Station traffic control has granted docking clearance",
                    f"{CrewRole.EDCOPILOT.value} Docking procedure initiated. Approach velocity nominal"
                ]
            },
            # Engineering conversation
            {
                "condition": EDCoPilotConditions.DOCKED,
                "conversation": [
                    f"{CrewRole.ENGINEERING.value} Engineering reports all systems nominal. Power distribution at peak efficiency",
                    f"{CrewRole.OPERATIONS.value} Station services are available, {EDCoPilotTokens.CMDR_ADDRESS}",
                    f"{CrewRole.EDCOPILOT.value} Ship maintenance and refuel options displayed on your console"
                ]
            },
            # Fuel warning conversation
            {
                "condition": EDCoPilotConditions.FUEL_LOW,
                "conversation": [
                    f"{CrewRole.ENGINEERING.value} Chief Engineer here. Fuel reserves at {EDCoPilotTokens.FUEL_LEVELS} percent. Recommend topping off",
                    f"{CrewRole.EDCOPILOT.value} Fuel warning acknowledged. Plotting course to nearest fuel source"
                ]
            },
            # Combat conversation
            {
                "condition": EDCoPilotConditions.UNDER_ATTACK,
                "conversation": [
                    f"{CrewRole.SECURITY.value} All hands, red alert! Hostile contacts on approach vector!",
                    f"{CrewRole.HELM.value} Evasive maneuvers engaged. All weapons systems online",
                    f"{CrewRole.EDCOPILOT.value} Combat protocols activated. Fight or flight options available"
                ]
            },
            # Science/exploration conversation
            {
                "condition": f"{EDCoPilotConditions.SCANNING}&{EDCoPilotConditions.EXPLORING}",
                "conversation": [
                    f"{CrewRole.SCIENCE.value} Science officer reporting. Stellar cartography data has been updated",
                    f"{CrewRole.OPERATIONS.value} Long-range sensors detect additional points of interest",
                    f"{CrewRole.EDCOPILOT.value} Exploration data logged. Universal Cartographics will pay well for this"
                ]
            }
        ]

    def generate_default_chatter(self) -> None:
        """Generate all default crew chatter."""
        logger.info("Generating default Crew Chatter entries")
        self.generate_crew_responses()

    def to_file_content(self) -> str:
        """
        Generate the complete file content for EDCoPilot.

        NO COMMENTS - EDCoPilot parser rejects comment lines.
        Uses conversation blocks with [example]...[\\example] markers.
        """
        lines = []

        # Generate conversation blocks if they exist
        if hasattr(self, 'conversation_blocks'):
            for block in self.conversation_blocks:
                lines.append("[example]")
                for dialogue_line in block["conversation"]:
                    lines.append(dialogue_line)
                lines.append("[\\example]")
                lines.append("")  # Empty line between conversations
        else:
            # Fallback to old format if conversation_blocks don't exist
            for entry in self.entries:
                lines.append(entry.format_for_edcopilot())

        return "\n".join(lines)


class DeepSpaceChatterTemplate:
    """Template for generating EDCoPilot Deep Space Chatter files."""

    def __init__(self):
        self.entries: List[ChatterEntry] = []
        self.filename = "EDCoPilot.DeepSpaceChatter.Custom.txt"

    def add_entry(self, text: str, conditions: Optional[List[str]] = None,
                  voice_override: Optional[str] = None) -> None:
        """Add a deep space chatter entry."""
        entry = ChatterEntry(text=text, conditions=conditions, voice_override=voice_override)
        self.entries.append(entry)

    def generate_deep_space_chatter(self) -> None:
        """Generate atmospheric deep space dialogue."""
        deep_space_entries = [
            # Isolation and wonder
            ChatterEntry(
                text=f"We're {EDCoPilotTokens.DISTANCE_FROM_SOL} light years from home. The isolation is profound.",
                conditions=[EDCoPilotConditions.DEEP_SPACE]
            ),
            ChatterEntry(
                text="Out here in the void, every star is a beacon of hope in the cosmic darkness.",
                conditions=[EDCoPilotConditions.DEEP_SPACE]
            ),
            ChatterEntry(
                text="The silence between the stars is deafening, yet somehow comforting.",
                conditions=[EDCoPilotConditions.DEEP_SPACE, EDCoPilotConditions.EXPLORING]
            ),

            # Discovery and exploration
            ChatterEntry(
                text="Commander, we may be among the first humans to witness this stellar phenomena.",
                conditions=[EDCoPilotConditions.DEEP_SPACE, EDCoPilotConditions.FIRST_DISCOVERY]
            ),
            ChatterEntry(
                text="The galaxy is vast beyond comprehension. We're just tiny explorers in infinity.",
                conditions=[EDCoPilotConditions.DEEP_SPACE]
            ),
            ChatterEntry(
                text="Each system we discover adds another verse to humanity's cosmic story.",
                conditions=[EDCoPilotConditions.DEEP_SPACE, EDCoPilotConditions.EXPLORING]
            ),

            # Philosophical musings
            ChatterEntry(
                text="In deep space, you realize how connected yet alone we all are.",
                conditions=[EDCoPilotConditions.DEEP_SPACE]
            ),
            ChatterEntry(
                text="The ancient light of distant stars carries stories from eons past.",
                conditions=[EDCoPilotConditions.DEEP_SPACE, EDCoPilotConditions.SCANNING]
            ),
        ]

        self.entries.extend(deep_space_entries)

    def generate_default_chatter(self) -> None:
        """Generate all default deep space chatter."""
        logger.info("Generating default Deep Space Chatter entries")
        self.generate_deep_space_chatter()

    def to_file_content(self) -> str:
        """
        Generate the complete file content for EDCoPilot.

        NO COMMENTS - EDCoPilot parser rejects comment lines.
        Deep Space Chatter uses conversation blocks like Crew Chatter.
        """
        lines = []

        for entry in self.entries:
            lines.append(entry.format_for_edcopilot())

        return "\n".join(lines)


class EDCoPilotTemplateManager:
    """Manager for all EDCoPilot template types."""

    def __init__(self):
        self.space_chatter = SpaceChatterTemplate()
        self.crew_chatter = CrewChatterTemplate()
        self.deep_space_chatter = DeepSpaceChatterTemplate()

    def generate_all_templates(self) -> Dict[str, str]:
        """Generate all template files and return their content."""
        logger.info("Generating all EDCoPilot template files")

        # Generate default content for all templates
        self.space_chatter.generate_default_chatter()
        self.crew_chatter.generate_default_chatter()
        self.deep_space_chatter.generate_default_chatter()

        return {
            self.space_chatter.filename: self.space_chatter.to_file_content(),
            self.crew_chatter.filename: self.crew_chatter.to_file_content(),
            self.deep_space_chatter.filename: self.deep_space_chatter.to_file_content()
        }

    def get_template_by_type(self, chatter_type: ChatterType):
        """Get template instance by chatter type."""
        if chatter_type == ChatterType.SPACE_CHATTER:
            return self.space_chatter
        elif chatter_type == ChatterType.CREW_CHATTER:
            return self.crew_chatter
        elif chatter_type == ChatterType.DEEP_SPACE_CHATTER:
            return self.deep_space_chatter
        else:
            raise ValueError(f"Unknown chatter type: {chatter_type}")