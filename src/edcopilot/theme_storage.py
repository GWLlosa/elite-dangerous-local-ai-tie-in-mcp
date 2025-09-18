"""
Theme Storage and Persistence System

Manages storage and persistence of EDCoPilot themes, crew configurations,
and ship-specific settings for the Dynamic Multi-Crew Theme System.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class CrewRole(Enum):
    """Available crew roles for ship-specific configurations."""
    COMMANDER = "commander"
    NAVIGATOR = "navigator"
    SCIENCE_OFFICER = "science"
    ENGINEER = "engineer"
    SECURITY_CHIEF = "security"
    COMMS_OFFICER = "comms"
    MEDICAL_OFFICER = "medical"
    QUARTERMASTER = "quartermaster"


@dataclass
class CrewMemberTheme:
    """Theme configuration for individual crew member."""
    role: str
    theme: str
    context: str
    voice_preference: Optional[str] = None
    personality_traits: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrewMemberTheme':
        """Create from dictionary for JSON deserialization."""
        return cls(**data)


@dataclass
class ShipCrewConfig:
    """Complete crew configuration for a specific ship."""
    ship_name: str
    crew_roles: List[str]
    crew_themes: Dict[str, CrewMemberTheme]
    overall_theme: Optional[str] = None
    overall_context: Optional[str] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime to ISO string
        if self.last_updated:
            data['last_updated'] = self.last_updated.isoformat()
        # Convert CrewMemberTheme objects to dicts
        data['crew_themes'] = {
            role: theme.to_dict() for role, theme in self.crew_themes.items()
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShipCrewConfig':
        """Create from dictionary for JSON deserialization."""
        # Convert ISO string back to datetime
        if 'last_updated' in data and data['last_updated']:
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])

        # Convert crew_themes dicts back to CrewMemberTheme objects
        if 'crew_themes' in data:
            data['crew_themes'] = {
                role: CrewMemberTheme.from_dict(theme_data)
                for role, theme_data in data['crew_themes'].items()
            }

        return cls(**data)


class ThemeStorage:
    """
    Manages storage and persistence of theme configurations.

    Stores themes in JSON files for persistence across sessions and provides
    efficient access to current themes and ship configurations.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize theme storage with optional custom path.

        Args:
            storage_path: Custom path for theme storage. If None, uses default.
        """
        if storage_path is None:
            # Default to subdirectory in current working directory
            self.storage_path = Path.cwd() / "edcopilot_themes"
        else:
            sp = Path(storage_path)
            # If a file path is provided (exists as file), use its parent as storage directory
            if sp.exists() and sp.is_file():
                self.storage_path = sp.parent
            else:
                self.storage_path = sp

        self.storage_path.mkdir(exist_ok=True)

        # Storage files
        self.current_theme_file = self.storage_path / "current_theme.json"
        self.ship_configs_file = self.storage_path / "ship_configurations.json"
        self.theme_history_file = self.storage_path / "theme_history.json"
        self.presets_file = self.storage_path / "theme_presets.json"

        # In-memory cache
        self._current_theme: Optional[Dict[str, Any]] = None
        self._ship_configs: Dict[str, ShipCrewConfig] = {}
        self._theme_history: List[Dict[str, Any]] = []
        self._presets: Dict[str, Dict[str, Any]] = {}

        # Load existing data
        self._load_all_data()

    def _load_all_data(self) -> None:
        """Load all theme data from storage files."""
        try:
            self._load_current_theme()
            self._load_ship_configs()
            self._load_theme_history()
            self._load_presets()
            logger.info("Theme storage data loaded successfully")
        except Exception as e:
            logger.warning(f"Error loading theme data: {e}")
            # Initialize with empty data if loading fails
            self._current_theme = None
            self._ship_configs = {}
            self._theme_history = []
            self._presets = {}

    def _load_current_theme(self) -> None:
        """Load current theme from storage."""
        if self.current_theme_file.exists():
            with open(self.current_theme_file, 'r', encoding='utf-8') as f:
                self._current_theme = json.load(f)

    def _load_ship_configs(self) -> None:
        """Load ship configurations from storage."""
        if self.ship_configs_file.exists():
            with open(self.ship_configs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._ship_configs = {
                    ship_name: ShipCrewConfig.from_dict(config_data)
                    for ship_name, config_data in data.items()
                }

    def _load_theme_history(self) -> None:
        """Load theme history from storage."""
        if self.theme_history_file.exists():
            with open(self.theme_history_file, 'r', encoding='utf-8') as f:
                self._theme_history = json.load(f)

    def _load_presets(self) -> None:
        """Load theme presets from storage."""
        if self.presets_file.exists():
            with open(self.presets_file, 'r', encoding='utf-8') as f:
                self._presets = json.load(f)

    def _save_current_theme(self) -> None:
        """Save current theme to storage."""
        with open(self.current_theme_file, 'w', encoding='utf-8') as f:
            json.dump(self._current_theme, f, indent=2, ensure_ascii=False)

    def _save_ship_configs(self) -> None:
        """Save ship configurations to storage."""
        data = {
            ship_name: config.to_dict()
            for ship_name, config in self._ship_configs.items()
        }
        with open(self.ship_configs_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_theme_history(self) -> None:
        """Save theme history to storage."""
        with open(self.theme_history_file, 'w', encoding='utf-8') as f:
            json.dump(self._theme_history, f, indent=2, ensure_ascii=False)

    def _save_presets(self) -> None:
        """Save theme presets to storage."""
        with open(self.presets_file, 'w', encoding='utf-8') as f:
            json.dump(self._presets, f, indent=2, ensure_ascii=False)

    # Current Theme Management

    def set_current_theme(self, theme: str, context: str) -> None:
        """
        Set the current overall theme.

        Args:
            theme: Theme identifier (e.g., "space pirate")
            context: Theme context (e.g., "owes debt to Space Mafia")
        """
        # Validate inputs
        if theme is None or context is None:
            raise TypeError("theme and context must not be None")

        self._current_theme = {
            "theme": theme,
            "context": context,
            "set_time": datetime.now(timezone.utc).isoformat(),
            "theme_id": f"{theme.replace(' ', '_')}_{int(datetime.now(timezone.utc).timestamp())}"
        }
        self._save_current_theme()
        self._add_to_history("theme_set", {"theme": theme, "context": context})
        logger.info(f"Current theme set to: {theme} - {context}")

    def get_current_theme(self) -> Optional[Dict[str, Any]]:
        """Get the current theme configuration."""
        return self._current_theme

    def clear_current_theme(self) -> None:
        """Clear the current theme configuration."""
        if self._current_theme:
            self._add_to_history("theme_cleared", self._current_theme)
        self._current_theme = None
        self._save_current_theme()
        logger.info("Current theme cleared")

    # Ship Configuration Management

    def set_ship_config(self, ship_config: ShipCrewConfig) -> None:
        """
        Set crew configuration for a specific ship.

        Args:
            ship_config: Complete ship crew configuration
        """
        ship_config.last_updated = datetime.now(timezone.utc)
        self._ship_configs[ship_config.ship_name] = ship_config
        self._save_ship_configs()
        self._add_to_history("ship_config_set", {
            "ship_name": ship_config.ship_name,
            "crew_roles": ship_config.crew_roles,
            "crew_count": len(ship_config.crew_themes)
        })
        logger.info(f"Ship configuration set for {ship_config.ship_name}")

    def get_ship_config(self, ship_name: str) -> Optional[ShipCrewConfig]:
        """Get crew configuration for a specific ship."""
        return self._ship_configs.get(ship_name)

    def get_all_ship_configs(self) -> Dict[str, ShipCrewConfig]:
        """Get all ship configurations."""
        return self._ship_configs.copy()

    def remove_ship_config(self, ship_name: str) -> bool:
        """Remove crew configuration for a ship."""
        if ship_name in self._ship_configs:
            removed_config = self._ship_configs.pop(ship_name)
            self._save_ship_configs()
            self._add_to_history("ship_config_removed", {
                "ship_name": ship_name,
                "crew_roles": removed_config.crew_roles
            })
            logger.info(f"Ship configuration removed for {ship_name}")
            return True
        return False

    # Crew Member Theme Management

    def set_crew_member_theme(self, ship_name: str, crew_role: str,
                             theme: str, context: str,
                             voice_preference: Optional[str] = None,
                             personality_traits: Optional[List[str]] = None) -> None:
        """
        Set theme for individual crew member.

        Args:
            ship_name: Name of the ship
            crew_role: Role of the crew member
            theme: Theme for this crew member
            context: Context for this crew member
            voice_preference: Optional voice preference
            personality_traits: Optional personality traits
        """
        # Get or create ship config
        ship_config = self.get_ship_config(ship_name)
        if ship_config is None:
            # Create new ship config with this crew member
            ship_config = ShipCrewConfig(
                ship_name=ship_name,
                crew_roles=[crew_role],
                crew_themes={}
            )

        # Add crew role if not present
        if crew_role not in ship_config.crew_roles:
            ship_config.crew_roles.append(crew_role)

        # Set crew member theme
        crew_theme = CrewMemberTheme(
            role=crew_role,
            theme=theme,
            context=context,
            voice_preference=voice_preference,
            personality_traits=personality_traits
        )
        ship_config.crew_themes[crew_role] = crew_theme

        # Save updated config
        self.set_ship_config(ship_config)
        logger.info(f"Crew theme set for {ship_name}/{crew_role}: {theme}")

    def get_crew_member_theme(self, ship_name: str, crew_role: str) -> Optional[CrewMemberTheme]:
        """Get theme for specific crew member."""
        ship_config = self.get_ship_config(ship_name)
        if ship_config:
            return ship_config.crew_themes.get(crew_role)
        return None

    # History Management

    def _add_to_history(self, action: str, data: Dict[str, Any]) -> None:
        """Add entry to theme history."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "data": data
        }
        self._theme_history.append(entry)

        # Keep only last 100 entries
        if len(self._theme_history) > 100:
            self._theme_history = self._theme_history[-100:]

        self._save_theme_history()

    def get_theme_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent theme history."""
        return self._theme_history[-limit:] if limit else self._theme_history

    # Preset Management

    def save_preset(self, name: str, theme: str, context: str,
                   ship_configs: Optional[Dict[str, ShipCrewConfig]] = None) -> None:
        """Save current configuration as a preset."""
        preset = {
            "name": name,
            "theme": theme,
            "context": context,
            "created_time": datetime.now(timezone.utc).isoformat(),
            "ship_configs": {}
        }

        if ship_configs:
            preset["ship_configs"] = {
                ship_name: config.to_dict()
                for ship_name, config in ship_configs.items()
            }

        self._presets[name] = preset
        self._save_presets()
        logger.info(f"Theme preset saved: {name}")

    def load_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a theme preset."""
        return self._presets.get(name)

    def get_all_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get all available presets."""
        return self._presets.copy()

    def remove_preset(self, name: str) -> bool:
        """Remove a theme preset."""
        if name in self._presets:
            del self._presets[name]
            self._save_presets()
            logger.info(f"Theme preset removed: {name}")
            return True
        return False

    # Default Ship Configurations

    @staticmethod
    def get_default_crew_for_ship(ship_name: str) -> List[str]:
        """Get default crew composition for a ship type."""
        ship_name_lower = ship_name.lower()

        # Small ships (1-2 crew)
        small_ships = {
            'sidewinder', 'eagle', 'hauler', 'adder', 'imperial_eagle',
            'viper', 'viper_mkiv', 'cobra_mkiii', 'type_6', 'dolphin'
        }

        # Medium ships (3-4 crew)
        medium_ships = {
            'asp_explorer', 'vulture', 'alliance_chieftain', 'alliance_challenger',
            'alliance_crusader', 'fer_de_lance', 'mamba', 'python', 'krait_mkii',
            'krait_phantom', 'type_7'
        }

        # Large ships (5+ crew)
        large_ships = {
            'anaconda', 'type_9', 'type_10', 'imperial_cutter', 'federal_corvette',
            'federal_gunship', 'federal_assault_ship', 'imperial_clipper',
            'orca', 'beluga'
        }

        # Normalize ship name for matching
        normalized_name = ship_name_lower.replace(' ', '_').replace('-', '_')

        if any(ship in normalized_name for ship in small_ships):
            if 'sidewinder' in normalized_name or 'eagle' in normalized_name:
                return [CrewRole.COMMANDER.value]  # Solo pilot
            else:
                return [CrewRole.COMMANDER.value, CrewRole.ENGINEER.value]

        elif any(ship in normalized_name for ship in medium_ships):
            return [
                CrewRole.COMMANDER.value,
                CrewRole.NAVIGATOR.value,
                CrewRole.ENGINEER.value,
                CrewRole.SCIENCE_OFFICER.value
            ]

        elif any(ship in normalized_name for ship in large_ships):
            return [
                CrewRole.COMMANDER.value,
                CrewRole.NAVIGATOR.value,
                CrewRole.SCIENCE_OFFICER.value,
                CrewRole.ENGINEER.value,
                CrewRole.SECURITY_CHIEF.value,
                CrewRole.COMMS_OFFICER.value
            ]

        else:
            # Default to medium ship configuration for unknown ships
            return [
                CrewRole.COMMANDER.value,
                CrewRole.NAVIGATOR.value,
                CrewRole.ENGINEER.value
            ]

    def create_default_ship_config(self, ship_name: str) -> ShipCrewConfig:
        """Create a default ship configuration based on ship type."""
        crew_roles = self.get_default_crew_for_ship(ship_name)

        return ShipCrewConfig(
            ship_name=ship_name,
            crew_roles=crew_roles,
            crew_themes={},  # No themes by default
            overall_theme=None,
            overall_context=None
        )

    # Utility Methods

    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about theme storage."""
        return {
            "storage_path": str(self.storage_path),
            "current_theme": self._current_theme is not None,
            "ship_configs_count": len(self._ship_configs),
            "history_entries": len(self._theme_history),
            "presets_count": len(self._presets),
            "storage_files": {
                "current_theme": self.current_theme_file.exists(),
                "ship_configs": self.ship_configs_file.exists(),
                "theme_history": self.theme_history_file.exists(),
                "presets": self.presets_file.exists()
            }
        }

    def clear_all_data(self) -> None:
        """Clear all theme data (use with caution)."""
        self._current_theme = None
        self._ship_configs = {}
        self._theme_history = []
        self._presets = {}

        # Remove storage files
        for file_path in [self.current_theme_file, self.ship_configs_file,
                         self.theme_history_file, self.presets_file]:
            if file_path.exists():
                file_path.unlink()

        logger.info("All theme data cleared")
