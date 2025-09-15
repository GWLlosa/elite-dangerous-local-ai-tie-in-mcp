"""
EDCoPilot File Templates System

Provides template classes for generating EDCoPilot custom chatter files
with proper formatting, conditions, and token support.
"""

import logging
from typing import Dict, List, Any, Optional
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
        """Format for Space Chatter - single line with conditions."""
        parts = []

        # Add conditions if present
        if self.conditions:
            condition_str = "condition:" + "&".join(self.conditions)
            parts.append(condition_str)

        # Add voice override if present
        if self.voice_override:
            parts.append(f"voice:{self.voice_override}")

        # Add the dialogue text
        parts.append(self.text)

        return "|".join(parts)

    def _format_crew_chatter(self) -> str:
        """Format for Crew Chatter - simple line (conversations handled at template level)."""
        # For crew chatter, individual entries are just dialogue lines
        # The conversation structure is handled by the template manager
        return self.text


class EDCoPilotTokens:
    """Available tokens that EDCoPilot can replace in chatter."""

    # Commander and ship tokens
    COMMANDER_NAME = "{CommanderName}"
    COMMANDER_RANK = "{CommanderRank}"
    SHIP_NAME = "{ShipName}"
    SHIP_TYPE = "{ShipType}"

    # Location tokens
    SYSTEM_NAME = "{SystemName}"
    STATION_NAME = "{StationName}"
    BODY_NAME = "{BodyName}"

    # Status tokens
    FUEL_PERCENT = "{FuelPercent}"
    SHIELD_PERCENT = "{ShieldPercent}"
    HULL_PERCENT = "{HullPercent}"
    CREDITS = "{Credits}"

    # Navigation tokens
    JUMP_DISTANCE = "{JumpDistance}"
    DISTANCE_FROM_SOL = "{DistanceFromSol}"
    NEXT_SYSTEM = "{NextSystem}"

    # Activity tokens
    CARGO_COUNT = "{CargoCount}"
    CARGO_CAPACITY = "{CargoCapacity}"
    MISSION_COUNT = "{MissionCount}"


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

        lines.append("[\example]")
        return "\n".join(lines)


class SpaceChatterTemplate:
    """Template for generating EDCoPilot Space Chatter files."""

    def __init__(self):
        self.entries: List[ChatterEntry] = []
        self.filename = "EDCoPilot.SpaceChatter.Custom.txt"

    def add_entry(self, text: str, conditions: Optional[List[str]] = None,
                  voice_override: Optional[str] = None) -> None:
        """Add a chatter entry."""
        entry = ChatterEntry(text=text, conditions=conditions, voice_override=voice_override,
                           chatter_type=ChatterType.SPACE_CHATTER)
        self.entries.append(entry)

    def generate_navigation_chatter(self) -> None:
        """Generate navigation-related chatter entries."""
        nav_entries = [
            # System entry chatter
            ChatterEntry(
                text=f"Entering {EDCoPilotTokens.SYSTEM_NAME}, Commander. Scanning for points of interest.",
                conditions=[EDCoPilotConditions.IN_SUPERCRUISE],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"Welcome to {EDCoPilotTokens.SYSTEM_NAME}. Population centers detected on sensors.",
                conditions=[EDCoPilotConditions.IN_SUPERCRUISE],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"Jump complete. We're now in the {EDCoPilotTokens.SYSTEM_NAME} system.",
                conditions=[EDCoPilotConditions.IN_SUPERCRUISE],
                chatter_type=ChatterType.SPACE_CHATTER
            ),

            # Docking chatter
            ChatterEntry(
                text=f"Docking request acknowledged by {EDCoPilotTokens.STATION_NAME}. Bringing us in smoothly.",
                conditions=[EDCoPilotConditions.APPROACHING_STATION],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"Successfully docked at {EDCoPilotTokens.STATION_NAME}. All systems secure.",
                conditions=[EDCoPilotConditions.DOCKED],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text="Permission to disembark granted. Station services are now available.",
                conditions=[EDCoPilotConditions.DOCKED],
                chatter_type=ChatterType.SPACE_CHATTER
            ),

            # Fuel warnings
            ChatterEntry(
                text=f"Fuel reserves at {EDCoPilotTokens.FUEL_PERCENT}%. Recommend refueling soon, Commander.",
                conditions=[EDCoPilotConditions.FUEL_LOW],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text="We should consider fuel management for our next jump sequence.",
                conditions=[EDCoPilotConditions.FUEL_LOW],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
        ]

        self.entries.extend(nav_entries)

    def generate_exploration_chatter(self) -> None:
        """Generate exploration-related chatter entries."""
        exploration_entries = [
            ChatterEntry(
                text=f"Fascinating astronomical data from {EDCoPilotTokens.BODY_NAME}. This should sell well.",
                conditions=[EDCoPilotConditions.SCANNING, EDCoPilotConditions.EXPLORING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text="Detailed surface scan complete. Adding to our exploration database.",
                conditions=[EDCoPilotConditions.SCANNING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text="Commander, we appear to be the first to discover this. Excellent work!",
                conditions=[EDCoPilotConditions.FIRST_DISCOVERY],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"We're {EDCoPilotTokens.DISTANCE_FROM_SOL} light years from Sol. True exploration territory.",
                conditions=[EDCoPilotConditions.EXPLORING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text="The void between stars is vast, but every system tells a story.",
                conditions=[EDCoPilotConditions.DEEP_SPACE, EDCoPilotConditions.EXPLORING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
        ]

        self.entries.extend(exploration_entries)

    def generate_combat_chatter(self) -> None:
        """Generate combat-related chatter entries."""
        combat_entries = [
            ChatterEntry(
                text=f"Shields at {EDCoPilotTokens.SHIELD_PERCENT}%! Evasive maneuvers recommended!",
                conditions=[EDCoPilotConditions.UNDER_ATTACK],
                voice_override="ARIA"  # More dramatic voice for combat
            ),
            ChatterEntry(
                text="Multiple hostiles on scanner. All hands to battle stations!",
                conditions=[EDCoPilotConditions.UNDER_ATTACK]
            ),
            ChatterEntry(
                text="Shield generators are offline! Hull integrity critical!",
                conditions=[EDCoPilotConditions.SHIELDS_DOWN, EDCoPilotConditions.IN_DANGER]
            ),
            ChatterEntry(
                text="Target eliminated. Scanning for additional threats.",
                conditions=[EDCoPilotConditions.IN_NORMAL_SPACE]  # After combat
            ),
        ]

        self.entries.extend(combat_entries)

    def generate_trading_chatter(self) -> None:
        """Generate trading-related chatter entries."""
        trading_entries = [
            ChatterEntry(
                text=f"Cargo manifest shows {EDCoPilotTokens.CARGO_COUNT} of {EDCoPilotTokens.CARGO_CAPACITY} tons loaded.",
                conditions=[EDCoPilotConditions.TRADING, EDCoPilotConditions.DOCKED]
            ),
            ChatterEntry(
                text="Market data suggests excellent profit margins on our current cargo.",
                conditions=[EDCoPilotConditions.TRADING]
            ),
            ChatterEntry(
                text=f"Credits updated: {EDCoPilotTokens.CREDITS}. Profitable trading run, Commander.",
                conditions=[EDCoPilotConditions.TRADING, EDCoPilotConditions.DOCKED]
            ),
            ChatterEntry(
                text="Supply and demand fluctuations detected. Adjusting trade calculations.",
                conditions=[EDCoPilotConditions.TRADING]
            ),
        ]

        self.entries.extend(trading_entries)

    def generate_default_chatter(self) -> None:
        """Generate all default chatter categories."""
        logger.info("Generating default Space Chatter entries")
        self.generate_navigation_chatter()
        self.generate_exploration_chatter()
        self.generate_combat_chatter()
        self.generate_trading_chatter()

    def to_file_content(self) -> str:
        """Generate the complete file content for EDCoPilot."""
        lines = [
            "# EDCoPilot Space Chatter Custom File",
            "# Generated by Elite Dangerous MCP Server",
            "# Format: [condition:ConditionName&AnotherCondition]|[voice:VoiceName]|Dialogue text with {Tokens}",
            "#",
            "# Available Tokens: {CommanderName}, {SystemName}, {ShipName}, {FuelPercent}, etc.",
            "# Available Conditions: Docked, InSupercruise, UnderAttack, Scanning, etc.",
            "# Available Voices: ARIA, MICROSOFT, AZURE, CEREPROC, IVONA",
            "#",
            ""
        ]

        # Add all entries
        for entry in self.entries:
            lines.append(entry.format_for_edcopilot())

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
        """Generate crew response chatter."""
        crew_entries = [
            # Navigation crew
            ChatterEntry(
                text="Navigation officer reports jump calculations complete, Commander.",
                conditions=[EDCoPilotConditions.IN_SUPERCRUISE]
            ),
            ChatterEntry(
                text="Helm responding. Setting course for optimal approach vector.",
                conditions=[EDCoPilotConditions.APPROACHING_STATION]
            ),

            # Engineering crew
            ChatterEntry(
                text=f"Engineering reports all systems nominal. Power distribution at peak efficiency.",
                conditions=[EDCoPilotConditions.DOCKED]
            ),
            ChatterEntry(
                text=f"Chief Engineer here. Fuel reserves at {EDCoPilotTokens.FUEL_PERCENT}%. Recommend topping off.",
                conditions=[EDCoPilotConditions.FUEL_LOW]
            ),

            # Security crew
            ChatterEntry(
                text="Security officer reports perimeter is secure. No immediate threats detected.",
                conditions=[EDCoPilotConditions.DOCKED]
            ),
            ChatterEntry(
                text="All hands, red alert! Hostile contacts on approach vector!",
                conditions=[EDCoPilotConditions.UNDER_ATTACK],
                voice_override="ARIA"
            ),

            # Science crew
            ChatterEntry(
                text="Science officer reporting. Stellar cartography data has been updated.",
                conditions=[EDCoPilotConditions.SCANNING, EDCoPilotConditions.EXPLORING]
            ),
            ChatterEntry(
                text="Fascinating stellar composition detected. Updating astronomical records.",
                conditions=[EDCoPilotConditions.FIRST_DISCOVERY]
            ),
        ]

        self.entries.extend(crew_entries)

    def generate_default_chatter(self) -> None:
        """Generate all default crew chatter."""
        logger.info("Generating default Crew Chatter entries")
        self.generate_crew_responses()

    def to_file_content(self) -> str:
        """Generate the complete file content for EDCoPilot."""
        lines = [
            "# EDCoPilot Crew Chatter Custom File",
            "# Generated by Elite Dangerous MCP Server",
            "# Format: [condition:ConditionName]|[voice:VoiceName]|Crew member dialogue",
            "#",
            ""
        ]

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
        """Generate the complete file content for EDCoPilot."""
        lines = [
            "# EDCoPilot Deep Space Chatter Custom File",
            "# Generated by Elite Dangerous MCP Server",
            "# Triggers only when >5000 LY from both Sol and Colonia",
            "# Format: [condition:ConditionName]|[voice:VoiceName]|Deep space dialogue",
            "#",
            ""
        ]

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