"""
EDCoPilot Content Generation Engine

Dynamically generates EDCoPilot custom chatter files based on current Elite Dangerous
game state, recent activities, and contextual information.
"""

import logging
import os
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from .templates import (
    EDCoPilotTemplateManager, ChatterType, ChatterEntry,
    EDCoPilotTokens, EDCoPilotConditions
)
try:
    from ..utils.data_store import DataStore
    from ..journal.events import EventCategory, ProcessedEvent
except ImportError:
    from src.utils.data_store import DataStore
    from src.journal.events import EventCategory, ProcessedEvent

logger = logging.getLogger(__name__)


class EDCoPilotContextAnalyzer:
    """Analyzes Elite Dangerous game state to determine appropriate chatter context."""

    def __init__(self, data_store: DataStore):
        self.data_store = data_store

    def analyze_current_context(self) -> Dict[str, Any]:
        """Analyze current game state to determine chatter context."""
        game_state = self.data_store.get_game_state()
        recent_events = self.data_store.get_recent_events(minutes=30)

        # Debug logging to see what data we're actually getting
        logger.info(f"DEBUG: Game state - system: {game_state.current_system}, ship: {game_state.current_ship}, credits: {game_state.credits}")
        logger.info(f"DEBUG: Found {len(recent_events)} recent events")

        context = {
            # Basic game state
            'commander_name': game_state.commander_name or 'Commander',
            'current_system': game_state.current_system or 'Unknown System',
            'current_station': game_state.current_station,
            'current_body': game_state.current_body,
            'ship_type': game_state.current_ship or 'Unknown Ship',
            'credits': game_state.credits,
            'fuel_level': game_state.fuel_level or 100.0,
            'hull_health': 100.0,  # Default value, would be from Status events
            'docked': game_state.docked,

            # Activity analysis
            'primary_activity': self._determine_primary_activity(recent_events),
            'recent_discoveries': self._count_discoveries(recent_events),
            'combat_events': self._count_combat_events(recent_events),
            'trading_events': self._count_trading_events(recent_events),
            'exploration_events': self._count_exploration_events(recent_events),

            # Contextual flags
            'is_deep_space': self._is_deep_space(recent_events),
            'fuel_low': game_state.low_fuel,  # Use boolean flag from GameState
            'recently_under_attack': self._recently_under_attack(recent_events),
            'first_discoveries': self._has_first_discoveries(recent_events),
            'high_value_cargo': self._has_high_value_cargo(recent_events)
        }

        return context

    def _determine_primary_activity(self, recent_events: List[ProcessedEvent]) -> str:
        """Determine the commander's primary recent activity."""
        activity_counts = {}
        for event in recent_events:
            category = event.category.value
            activity_counts[category] = activity_counts.get(category, 0) + 1

        if not activity_counts:
            return 'general'

        primary_activity = max(activity_counts, key=activity_counts.get)
        return primary_activity.lower()

    def _count_discoveries(self, recent_events: List[ProcessedEvent]) -> int:
        """Count recent discovery events."""
        return len([e for e in recent_events if 'Scan' in e.event_type or 'Discovery' in e.event_type])

    def _count_combat_events(self, recent_events: List[ProcessedEvent]) -> int:
        """Count recent combat events."""
        return len([e for e in recent_events if e.category == EventCategory.COMBAT])

    def _count_trading_events(self, recent_events: List[ProcessedEvent]) -> int:
        """Count recent trading events."""
        return len([e for e in recent_events if e.category == EventCategory.TRADING])

    def _count_exploration_events(self, recent_events: List[ProcessedEvent]) -> int:
        """Count recent exploration events."""
        return len([e for e in recent_events if e.category == EventCategory.EXPLORATION])

    def _is_deep_space(self, recent_events: List[ProcessedEvent]) -> bool:
        """Check if currently in deep space (>5000 LY from Sol/Colonia)."""
        # This would need actual distance calculation from coordinates
        # For now, use heuristic based on recent jump distances
        jump_events = [e for e in recent_events if e.event_type == 'FSDJump']
        if jump_events:
            avg_jump_distance = sum(e.raw_event.get('JumpDist', 0) for e in jump_events) / len(jump_events)
            return avg_jump_distance > 40  # High jump distances suggest deep space
        return False

    def _recently_under_attack(self, recent_events: List[ProcessedEvent]) -> bool:
        """Check if recently under attack."""
        combat_events = [e for e in recent_events if e.category == EventCategory.COMBAT]
        return len(combat_events) > 0

    def _has_first_discoveries(self, recent_events: List[ProcessedEvent]) -> bool:
        """Check if recent first discoveries occurred."""
        return any('first to map' in e.summary.lower() or 'first discovery' in e.summary.lower()
                  for e in recent_events if e.summary)

    def _has_high_value_cargo(self, recent_events: List[ProcessedEvent]) -> bool:
        """Check if carrying high-value cargo."""
        # Look for recent market buy events with high values
        market_events = [e for e in recent_events if e.event_type in ['MarketBuy', 'MarketSell']]
        for event in market_events:
            if event.raw_event.get('TotalCost', 0) > 1000000:  # > 1M credits
                return True
        return False


class EDCoPilotContentGenerator:
    """Generates contextual EDCoPilot chatter content based on game state."""

    def __init__(self, data_store: DataStore, edcopilot_path: Path):
        self.data_store = data_store
        self.edcopilot_path = edcopilot_path
        self.template_manager = EDCoPilotTemplateManager()
        self.context_analyzer = EDCoPilotContextAnalyzer(data_store)

    def generate_contextual_chatter(self) -> Dict[str, str]:
        """Generate contextual chatter based on current game state."""
        logger.info("Generating contextual EDCoPilot chatter")

        # Analyze current context
        context = self.context_analyzer.analyze_current_context()

        # Generate base templates
        files = self.template_manager.generate_all_templates()

        # Enhance with contextual content
        files = self._enhance_with_context(files, context)

        return files

    def _enhance_with_context(self, files: Dict[str, str], context: Dict[str, Any]) -> Dict[str, str]:
        """Enhance template files with contextual entries."""
        logger.info(f"Enhancing chatter with context: primary_activity={context['primary_activity']}")

        # Add contextual entries to space chatter
        space_template = self.template_manager.space_chatter

        # Add activity-specific entries
        if context['primary_activity'] == 'exploration':
            self._add_exploration_context(space_template, context)
        elif context['primary_activity'] == 'trading':
            self._add_trading_context(space_template, context)
        elif context['primary_activity'] == 'combat':
            self._add_combat_context(space_template, context)

        # Add situational entries
        if context['fuel_low']:
            self._add_fuel_warning_context(space_template, context)

        if context['first_discoveries']:
            self._add_discovery_context(space_template, context)

        if context['is_deep_space']:
            self._add_deep_space_context(space_template, context)

        # Generate files with enhanced content (don't regenerate from scratch)
        enhanced_files = self.template_manager.generate_all_templates()

        # Replace tokens with actual contextual values for generated content
        # Tests and headless workflows expect concrete values rather than placeholders
        enhanced_files = self._replace_tokens_in_files(enhanced_files, context)
        return enhanced_files

    def _add_exploration_context(self, template, context: Dict[str, Any]) -> None:
        """Add exploration-specific contextual chatter."""
        from .templates import EDCoPilotTokens, ChatterType, ChatterEntry

        exploration_entries = [
            ChatterEntry(
                text=f"We've made {context['recent_discoveries']} discoveries in the past hour. Excellent work!",
                conditions=[EDCoPilotConditions.EXPLORING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"Current system: {EDCoPilotTokens.SYSTEM_NAME}. Scanning for valuable astronomical data.",
                conditions=[EDCoPilotConditions.IN_SUPERCRUISE, EDCoPilotConditions.EXPLORING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"{EDCoPilotTokens.SHIP_NAME}'s sensors are detecting fascinating stellar phenomena in {EDCoPilotTokens.SYSTEM_NAME}.",
                conditions=[EDCoPilotConditions.EXPLORING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
        ]
        template.entries.extend(exploration_entries)

    def _add_trading_context(self, template, context: Dict[str, Any]) -> None:
        """Add trading-specific contextual chatter."""
        from .templates import EDCoPilotTokens, ChatterType, ChatterEntry

        trading_entries = [
            ChatterEntry(
                text=f"Market analysis complete for {EDCoPilotTokens.SYSTEM_NAME}. Profit margins look promising.",
                conditions=[EDCoPilotConditions.TRADING, EDCoPilotConditions.DOCKED],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"Credits: {EDCoPilotTokens.CREDITS}. Our trading run is proving quite profitable.",
                conditions=[EDCoPilotConditions.TRADING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"{EDCoPilotTokens.SHIP_NAME}'s cargo manifest updated. Trading algorithms suggest optimal routes from {EDCoPilotTokens.SYSTEM_NAME}.",
                conditions=[EDCoPilotConditions.TRADING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
        ]

        if context['high_value_cargo']:
            trading_entries.append(ChatterEntry(
                text="High-value cargo detected. Recommend caution in inhabited systems.",
                conditions=[EDCoPilotConditions.TRADING],
                chatter_type=ChatterType.SPACE_CHATTER
            ))

        template.entries.extend(trading_entries)

    def _add_combat_context(self, template, context: Dict[str, Any]) -> None:
        """Add combat-specific contextual chatter."""
        from .templates import EDCoPilotTokens, ChatterType, ChatterEntry

        combat_entries = [
            ChatterEntry(
                text=f"Combat log shows {context['combat_events']} engagements recently. Stay sharp, Commander.",
                conditions=[EDCoPilotConditions.IN_NORMAL_SPACE],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text=f"{EDCoPilotTokens.SHIP_NAME}'s combat systems are primed and ready for engagement in {EDCoPilotTokens.SYSTEM_NAME}.",
                conditions=[EDCoPilotConditions.IN_NORMAL_SPACE],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
        ]

        if context['recently_under_attack']:
            combat_entries.append(ChatterEntry(
                text="Threat assessment: elevated. Multiple hostiles in recent encounters.",
                conditions=[EDCoPilotConditions.IN_NORMAL_SPACE],
                chatter_type=ChatterType.SPACE_CHATTER
            ))

        template.entries.extend(combat_entries)

    def _add_fuel_warning_context(self, template, context: Dict[str, Any]) -> None:
        """Add fuel-specific contextual chatter."""
        from .templates import EDCoPilotTokens, ChatterType, ChatterEntry

        fuel_entries = [
            ChatterEntry(
                text=f"Fuel at {EDCoPilotTokens.FUEL_PERCENT}%. Nearest fuel source should be prioritized.",
                conditions=[EDCoPilotConditions.FUEL_LOW],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text="Engineering recommends fuel conservation protocols until refuel.",
                conditions=[EDCoPilotConditions.FUEL_LOW],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
        ]
        template.entries.extend(fuel_entries)

    def _add_discovery_context(self, template, context: Dict[str, Any]) -> None:
        """Add first discovery contextual chatter."""
        from .templates import ChatterType, ChatterEntry

        discovery_entries = [
            ChatterEntry(
                text="Cartographics will pay handsomely for our recent first discovery data!",
                conditions=[EDCoPilotConditions.FIRST_DISCOVERY],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
            ChatterEntry(
                text="Commander, we're making history with these uncharted discoveries.",
                conditions=[EDCoPilotConditions.FIRST_DISCOVERY, EDCoPilotConditions.EXPLORING],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
        ]
        template.entries.extend(discovery_entries)

    def _add_deep_space_context(self, template, context: Dict[str, Any]) -> None:
        """Add deep space contextual chatter."""
        from .templates import ChatterType, ChatterEntry

        deep_space_entries = [
            ChatterEntry(
                text=f"We're deep in unexplored territory. The nearest inhabited system feels like a distant memory.",
                conditions=[EDCoPilotConditions.DEEP_SPACE],
                chatter_type=ChatterType.SPACE_CHATTER
            ),
        ]
        template.entries.extend(deep_space_entries)

    def _replace_tokens_in_files(self, files: Dict[str, str], context: Dict[str, Any]) -> Dict[str, str]:
        """Replace placeholder tokens with actual contextual values."""
        enhanced_files = {}

        for filename, content in files.items():
            enhanced_content = self._replace_tokens_in_content(content, context)
            enhanced_files[filename] = enhanced_content

        return enhanced_files

    def _replace_tokens_in_content(self, content: str, context: Dict[str, Any]) -> str:
        """Replace tokens in content with actual values from context."""
        # Create token replacement mapping with null-safe values
        replacements = {
            '{SystemName}': context.get('current_system') or 'Unknown System',
            '{ShipName}': self._extract_ship_name(context.get('ship_type') or 'Unknown Ship'),
            '{ShipType}': context.get('ship_type') or 'Unknown Ship',
            '{CommanderName}': context.get('commander_name') or 'Commander',
            '{Credits}': f"{context.get('credits', 0):,}",
            '{FuelPercent}': f"{context.get('fuel_level', 100):.0f}",
            '{StationName}': context.get('current_station') or 'Station',
            '{BodyName}': context.get('current_body') or 'Body',
        }

        # Apply replacements (ensure all values are strings)
        enhanced_content = content
        for token, value in replacements.items():
            if value is not None:
                enhanced_content = enhanced_content.replace(token, str(value))

        return enhanced_content

    def _extract_ship_name(self, ship_type: str) -> str:
        """Extract ship name from ship type string."""
        if not ship_type:
            return 'Unknown Ship'

        # Handle formats like "Mandalay EXCELSIOR" -> "EXCELSIOR"
        if ' ' in ship_type:
            parts = ship_type.split(' ', 1)
            if len(parts) > 1:
                return parts[1]  # Return the name part
        return ship_type

    def write_files(self, backup_existing: bool = True) -> Dict[str, Path]:
        """Write generated files to EDCoPilot directory."""
        if not self.edcopilot_path.exists():
            logger.warning(f"EDCoPilot path does not exist: {self.edcopilot_path}")
            try:
                self.edcopilot_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created EDCoPilot directory: {self.edcopilot_path}")
            except Exception as e:
                logger.error(f"Failed to create EDCoPilot directory: {e}")
                raise

        # Generate contextual content
        files = self.generate_contextual_chatter()
        written_files = {}

        for filename, content in files.items():
            file_path = self.edcopilot_path / filename

            # Backup existing file if requested
            if backup_existing and file_path.exists():
                backup_path = file_path.with_suffix(f'.backup.{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.txt')
                shutil.copy2(file_path, backup_path)
                logger.info(f"Backed up existing file: {backup_path}")

            # Write new content
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                written_files[filename] = file_path
                logger.info(f"Generated EDCoPilot file: {file_path}")

            except Exception as e:
                logger.error(f"Failed to write file {file_path}: {e}")
                raise

        return written_files


class EDCoPilotFileManager:
    """Manages EDCoPilot custom file operations."""

    def __init__(self, edcopilot_path: Path):
        self.edcopilot_path = edcopilot_path

    def list_custom_files(self) -> List[Path]:
        """List all existing EDCoPilot custom files."""
        if not self.edcopilot_path.exists():
            return []

        custom_files = []
        patterns = ["*.Custom.txt", "*.custom.txt"]

        for pattern in patterns:
            custom_files.extend(self.edcopilot_path.glob(pattern))

        return sorted(custom_files)

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get information about an EDCoPilot custom file."""
        if not file_path.exists():
            return {"exists": False}

        stat = file_path.stat()

        # Count entries (non-comment, non-empty lines)
        entry_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        entry_count += 1
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")

        return {
            "exists": True,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            "entry_count": entry_count,
            "is_generated": "Generated by Elite Dangerous MCP Server" in self._read_file_header(file_path)
        }

    def _read_file_header(self, file_path: Path, lines: int = 5) -> str:
        """Read the first few lines of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                header_lines = []
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    header_lines.append(line.strip())
                return "\n".join(header_lines)
        except Exception:
            return ""

    def backup_files(self) -> Dict[str, Path]:
        """Create backups of all existing custom files."""
        custom_files = self.list_custom_files()
        backup_files = {}

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        for file_path in custom_files:
            backup_name = f"{file_path.stem}.backup.{timestamp}{file_path.suffix}"
            backup_path = file_path.parent / backup_name

            try:
                shutil.copy2(file_path, backup_path)
                backup_files[file_path.name] = backup_path
                logger.info(f"Backed up {file_path.name} to {backup_path.name}")
            except Exception as e:
                logger.error(f"Failed to backup {file_path}: {e}")

        return backup_files

    def clean_old_backups(self, keep_days: int = 7) -> int:
        """Clean up old backup files."""
        if not self.edcopilot_path.exists():
            return 0

        backup_files = list(self.edcopilot_path.glob("*.backup.*.txt"))
        removed_count = 0
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=keep_days)

        for backup_file in backup_files:
            try:
                # Use timezone-aware comparison (UTC)
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime, tz=timezone.utc)
                if file_mtime < cutoff_time:
                    backup_file.unlink()
                    removed_count += 1
                    logger.debug(f"Removed old backup: {backup_file.name}")
            except Exception as e:
                logger.error(f"Error removing backup {backup_file}: {e}")

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old backup files")

        return removed_count
