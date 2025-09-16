"""
Theme Generation MCP Tools

Provides MCP tools for the Dynamic Multi-Crew Theme System, enabling
AI-powered theme generation and crew configuration through Claude Desktop.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from .theme_storage import ThemeStorage, CrewMemberTheme, ShipCrewConfig
from .theme_generator import ThemeGenerator, TemplateValidator
from .templates import ChatterType
from .generator import EDCoPilotContentGenerator as EDCoPilotGenerator

try:
    from ..utils.data_store import DataStore
    from ..utils.config import load_config
except ImportError:
    from src.utils.data_store import DataStore
    from src.utils.config import load_config

logger = logging.getLogger(__name__)


class ThemeMCPTools:
    """
    MCP tools for Dynamic Multi-Crew Theme System.

    Provides comprehensive tools for:
    - Theme setting and management
    - Ship-specific crew configuration
    - AI prompt generation for Claude Desktop
    - Template validation and application
    - Theme history and presets
    """

    def __init__(self, data_store: DataStore):
        """
        Initialize theme MCP tools.

        Args:
            data_store: Data store for game state access
        """
        self.data_store = data_store

        # Initialize theme system components
        self.theme_storage = ThemeStorage()
        self.theme_generator = ThemeGenerator(self.theme_storage)

        # Load config to get edcopilot_path
        config = load_config()
        self.edcopilot_generator = EDCoPilotGenerator(data_store, config.edcopilot_path)

        logger.info("Theme MCP tools initialized")

    # ==================== Core Theme Management ====================

    async def set_edcopilot_theme(
        self,
        theme: str,
        context: str,
        apply_immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Set overall EDCoPilot theme with context.

        Sets the global theme that will influence all generated dialogue.
        Optionally applies the theme immediately to current ship.

        Args:
            theme: Theme identifier (e.g., "space pirate", "corporate executive")
            context: Theme context (e.g., "owes debt to Space Mafia")
            apply_immediately: Whether to apply theme to current ship immediately

        Returns:
            Dict with theme setting status and next steps
        """
        try:
            # Validate theme parameters
            if not theme or not theme.strip():
                return {"success": False, "error": "Theme cannot be empty"}

            if not context or not context.strip():
                return {"success": False, "error": "Context cannot be empty"}

            # Set the theme
            self.theme_storage.set_current_theme(theme.strip(), context.strip())

            result = {
                "success": True,
                "theme": theme.strip(),
                "context": context.strip(),
                "message": f"Theme set to '{theme}' with context '{context}'"
            }

            # Apply to current ship if requested
            if apply_immediately:
                game_state = self.data_store.get_game_state()
                current_ship = game_state.current_ship

                if current_ship:
                    apply_result = await self._apply_theme_to_ship(
                        current_ship, theme.strip(), context.strip()
                    )
                    result["immediate_application"] = apply_result
                else:
                    result["warning"] = "No current ship detected for immediate application"

            # Provide next steps guidance
            result["next_steps"] = [
                "Use 'generate_themed_templates_prompt' to get AI generation prompt",
                "Use 'configure_ship_crew' to set up crew for specific ships",
                "Use 'apply_generated_templates' after Claude generates themed content"
            ]

            return result

        except Exception as e:
            logger.error(f"Error setting theme: {e}")
            return {"success": False, "error": str(e)}

    async def get_theme_status(self) -> Dict[str, Any]:
        """
        Get current theme system status and configuration.

        Returns comprehensive information about current themes,
        ship configurations, and system state.

        Returns:
            Dict with complete theme system status
        """
        try:
            return self.theme_generator.get_theme_status()

        except Exception as e:
            logger.error(f"Error getting theme status: {e}")
            return {"success": False, "error": str(e)}

    async def reset_theme(self, clear_ship_configs: bool = False) -> Dict[str, Any]:
        """
        Reset theme configuration to defaults.

        Clears current theme and optionally ship-specific configurations.

        Args:
            clear_ship_configs: Whether to clear all ship configurations

        Returns:
            Dict with reset operation status
        """
        try:
            # Clear current theme
            self.theme_storage.clear_current_theme()

            result = {
                "success": True,
                "message": "Theme reset to defaults"
            }

            # Clear ship configs if requested
            if clear_ship_configs:
                ship_configs = self.theme_storage.get_all_ship_configs()
                for ship_name in list(ship_configs.keys()):
                    self.theme_storage.remove_ship_config(ship_name)

                result["message"] += " and all ship configurations cleared"
                result["ship_configs_cleared"] = len(ship_configs)

            return result

        except Exception as e:
            logger.error(f"Error resetting theme: {e}")
            return {"success": False, "error": str(e)}

    # ==================== AI Prompt Generation ====================

    async def generate_themed_templates_prompt(
        self,
        theme: Optional[str] = None,
        context: Optional[str] = None,
        crew_role: Optional[str] = None,
        ship_name: Optional[str] = None,
        chatter_type: str = "space"
    ) -> Dict[str, Any]:
        """
        Generate AI prompt for Claude Desktop to create themed templates.

        Creates a structured prompt that guides Claude Desktop to generate
        EDCoPilot dialogue templates matching the specified theme.

        Args:
            theme: Theme override (uses current theme if None)
            context: Context override (uses current context if None)
            crew_role: Specific crew role for targeted generation
            ship_name: Ship name for context
            chatter_type: Type of chatter ("space", "crew", "deepspace")

        Returns:
            Dict with AI prompt and generation instructions
        """
        try:
            # Use current theme if not specified
            current_theme = self.theme_storage.get_current_theme()

            if not theme and current_theme:
                theme = current_theme["theme"]
                context = current_theme["context"]

            if not theme:
                return {
                    "success": False,
                    "error": "No theme specified and no current theme set. Use 'set_edcopilot_theme' first."
                }

            # Get current ship if not specified
            if not ship_name:
                game_state = self.data_store.get_game_state()
                ship_name = game_state.current_ship

            # Get current templates for reference
            current_templates = None
            try:
                # Get some example templates from current generator
                from .templates import SpaceChatterTemplate
                template_gen = SpaceChatterTemplate()
                template_gen.generate_navigation_chatter()
                current_templates = [entry.format_for_edcopilot() for entry in template_gen.entries[:5]]
            except Exception as e:
                logger.warning(f"Could not get current templates: {e}")

            # Generate prompt
            prompt_result = self.theme_generator.generate_theme_prompt_for_claude(
                theme=theme,
                context=context or "",
                crew_role=crew_role,
                ship_name=ship_name,
                current_templates=current_templates
            )

            result = {
                "success": True,
                "prompt": prompt_result["prompt"],
                "theme": theme,
                "context": context,
                "crew_role": crew_role,
                "ship_name": ship_name,
                "chatter_type": chatter_type,
                "instructions": "Copy the prompt above and ask Claude Desktop to generate themed templates"
            }

            return result

        except Exception as e:
            logger.error(f"Error generating themed templates prompt: {e}")
            return {"success": False, "error": str(e)}

    async def apply_generated_templates(
        self,
        generated_templates: List[str],
        chatter_type: str = "space",
        ship_name: Optional[str] = None,
        crew_role: Optional[str] = None,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Validate and apply templates generated by Claude Desktop.

        Takes templates generated by Claude Desktop, validates them for
        EDCoPilot compliance, and applies them to the appropriate files.

        Args:
            generated_templates: List of template strings from Claude Desktop
            chatter_type: Type of chatter ("space", "crew", "deepspace")
            ship_name: Ship name for ship-specific application
            crew_role: Crew role for role-specific application
            create_backup: Whether to create backup before applying

        Returns:
            Dict with validation results and application status
        """
        try:
            # Validate templates
            validation_result = self.theme_generator.validate_generated_templates(generated_templates)

            if not validation_result["success"]:
                return {
                    "success": False,
                    "error": validation_result.get("error", "Template validation failed"),
                    "validation_details": validation_result
                }

            valid_templates = validation_result["valid_templates"]

            if not valid_templates:
                return {
                    "success": False,
                    "error": "No valid templates after validation",
                    "validation_details": validation_result
                }

            # Determine chatter type
            chatter_type_enum = ChatterType.SPACE_CHATTER
            if chatter_type.lower() == "crew":
                chatter_type_enum = ChatterType.CREW_CHATTER
            elif chatter_type.lower() in ["deepspace", "deep_space"]:
                chatter_type_enum = ChatterType.DEEP_SPACE_CHATTER

            # Convert to ChatterEntry objects
            chatter_entries = self.theme_generator.create_chatter_entries_from_templates(
                valid_templates, chatter_type_enum
            )

            # Create backup if requested
            backup_info = None
            if create_backup:
                try:
                    backup_result = await self.backup_edcopilot_files()
                    if backup_result.get("success"):
                        backup_info = backup_result
                except Exception as e:
                    logger.warning(f"Backup creation failed: {e}")

            # Apply templates using existing EDCoPilot generator
            # For now, we'll update the templates in the generator and regenerate files
            try:
                # Get current game context
                context = self.edcopilot_generator.context_analyzer.analyze_current_context()

                # Generate files with new themed templates
                # This is a simplified approach - in practice, we'd want to integrate
                # the themed templates into the generation process more seamlessly
                files = {
                    "space": chatter_entries if chatter_type_enum == ChatterType.SPACE_CHATTER else [],
                    "crew": chatter_entries if chatter_type_enum == ChatterType.CREW_CHATTER else [],
                    "deepspace": chatter_entries if chatter_type_enum == ChatterType.DEEP_SPACE_CHATTER else []
                }

                # Write files
                config = load_config()
                edcopilot_path = Path(config.edcopilot_path)

                written_files = []
                for file_type, entries in files.items():
                    if entries:
                        filename_map = {
                            "space": "EDCoPilot.SpaceChatter.Custom.txt",
                            "crew": "EDCoPilot.CrewChatter.Custom.txt",
                            "deepspace": "EDCoPilot.DeepSpaceChatter.Custom.txt"
                        }

                        filename = filename_map[file_type]
                        file_path = edcopilot_path / filename

                        # Create content
                        content_lines = [
                            f"# EDCoPilot {file_type.title()} Chatter Custom File",
                            "# Generated by Elite Dangerous MCP Server - Dynamic Theme System",
                            f"# Theme: {self.theme_storage.get_current_theme()}",
                            "#",
                            ""
                        ]

                        for entry in entries:
                            content_lines.append(entry.format_for_edcopilot())

                        content = "\n".join(content_lines)

                        # Write file
                        file_path.write_text(content, encoding='utf-8')
                        written_files.append(str(file_path))
                        logger.info(f"Applied themed templates to {filename}")

                return {
                    "success": True,
                    "templates_applied": len(valid_templates),
                    "chatter_type": chatter_type,
                    "files_written": written_files,
                    "validation_summary": validation_result["validation_summary"],
                    "backup_info": backup_info,
                    "message": f"Successfully applied {len(valid_templates)} themed templates"
                }

            except Exception as e:
                logger.error(f"Error applying templates: {e}")
                return {
                    "success": False,
                    "error": f"Template validation succeeded but application failed: {str(e)}",
                    "validation_details": validation_result
                }

        except Exception as e:
            logger.error(f"Error in apply_generated_templates: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Ship and Crew Management ====================

    async def configure_ship_crew(
        self,
        ship_name: str,
        crew_roles: Optional[List[str]] = None,
        auto_configure: bool = True
    ) -> Dict[str, Any]:
        """
        Configure crew composition for a specific ship.

        Sets up the crew roles for a ship, either automatically based on
        ship type or with custom role specification.

        Args:
            ship_name: Name of the ship to configure
            crew_roles: List of crew roles (auto-detected if None)
            auto_configure: Whether to auto-configure based on ship type

        Returns:
            Dict with crew configuration status
        """
        try:
            if not ship_name or not ship_name.strip():
                return {"success": False, "error": "Ship name cannot be empty"}

            ship_name = ship_name.strip()

            # Auto-configure crew roles if not specified
            if crew_roles is None or auto_configure:
                crew_roles = self.theme_storage.get_default_crew_for_ship(ship_name)

            if not crew_roles:
                return {"success": False, "error": "No crew roles specified or detected"}

            # Create ship configuration
            ship_config = ShipCrewConfig(
                ship_name=ship_name,
                crew_roles=crew_roles,
                crew_themes={}
            )

            # Apply current theme if available
            current_theme = self.theme_storage.get_current_theme()
            if current_theme:
                ship_config.overall_theme = current_theme["theme"]
                ship_config.overall_context = current_theme["context"]

            # Save configuration
            self.theme_storage.set_ship_config(ship_config)

            return {
                "success": True,
                "ship_name": ship_name,
                "crew_roles": crew_roles,
                "crew_count": len(crew_roles),
                "overall_theme": ship_config.overall_theme,
                "overall_context": ship_config.overall_context,
                "message": f"Crew configured for {ship_name} with {len(crew_roles)} roles"
            }

        except Exception as e:
            logger.error(f"Error configuring ship crew: {e}")
            return {"success": False, "error": str(e)}

    async def set_crew_member_theme(
        self,
        ship_name: str,
        crew_role: str,
        theme: str,
        context: str,
        voice_preference: Optional[str] = None,
        personality_traits: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Set theme for individual crew member.

        Configures personality theme for a specific crew member on a ship.

        Args:
            ship_name: Name of the ship
            crew_role: Role of the crew member
            theme: Theme for this crew member
            context: Context for this crew member
            voice_preference: Optional voice preference
            personality_traits: Optional personality traits

        Returns:
            Dict with crew member theme setting status
        """
        try:
            # Validate parameters
            if not all([ship_name, crew_role, theme, context]):
                return {"success": False, "error": "Ship name, crew role, theme, and context are required"}

            # Set crew member theme
            self.theme_storage.set_crew_member_theme(
                ship_name=ship_name.strip(),
                crew_role=crew_role.strip(),
                theme=theme.strip(),
                context=context.strip(),
                voice_preference=voice_preference,
                personality_traits=personality_traits
            )

            return {
                "success": True,
                "ship_name": ship_name.strip(),
                "crew_role": crew_role.strip(),
                "theme": theme.strip(),
                "context": context.strip(),
                "voice_preference": voice_preference,
                "personality_traits": personality_traits,
                "message": f"Theme set for {crew_role} on {ship_name}"
            }

        except Exception as e:
            logger.error(f"Error setting crew member theme: {e}")
            return {"success": False, "error": str(e)}

    async def generate_crew_setup_prompt(
        self,
        ship_name: str,
        overall_theme: str,
        overall_context: str,
        crew_roles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate prompt for Claude Desktop to set up multi-crew themes.

        Creates a prompt for configuring individual personalities for
        all crew members on a ship within an overall theme.

        Args:
            ship_name: Name of the ship
            overall_theme: Overall theme for the crew
            overall_context: Overall context for the crew
            crew_roles: List of crew roles (auto-detected if None)

        Returns:
            Dict with crew setup prompt for Claude Desktop
        """
        try:
            # Auto-configure crew roles if not specified
            if crew_roles is None:
                crew_roles = self.theme_storage.get_default_crew_for_ship(ship_name)

            if not crew_roles:
                return {"success": False, "error": "No crew roles specified or detected"}

            # Generate prompt
            prompt_result = self.theme_generator.generate_crew_setup_prompt(
                ship_name=ship_name.strip(),
                crew_roles=crew_roles,
                overall_theme=overall_theme.strip(),
                overall_context=overall_context.strip()
            )

            return {
                "success": True,
                "prompt": prompt_result["prompt"],
                "ship_name": ship_name,
                "crew_roles": crew_roles,
                "overall_theme": overall_theme,
                "overall_context": overall_context,
                "instructions": "Copy the prompt above and ask Claude Desktop to configure crew personalities"
            }

        except Exception as e:
            logger.error(f"Error generating crew setup prompt: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Preview and Validation ====================

    async def preview_themed_content(
        self,
        theme: Optional[str] = None,
        context: Optional[str] = None,
        crew_role: Optional[str] = None,
        ship_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview what themed content would look like without applying.

        Shows example of what themed templates would look like based on
        current or specified theme configuration.

        Args:
            theme: Theme override (uses current theme if None)
            context: Context override (uses current context if None)
            crew_role: Specific crew role for preview
            ship_name: Ship name for context

        Returns:
            Dict with preview content and examples
        """
        try:
            # Use current theme if not specified
            current_theme = self.theme_storage.get_current_theme()

            if not theme and current_theme:
                theme = current_theme["theme"]
                context = current_theme["context"]

            if not theme:
                return {
                    "success": False,
                    "error": "No theme specified and no current theme set"
                }

            # Get current ship if not specified
            if not ship_name:
                game_state = self.data_store.get_game_state()
                ship_name = game_state.current_ship

            # Generate example templates based on theme
            examples = self._generate_theme_examples(theme, context, crew_role)

            return {
                "success": True,
                "theme": theme,
                "context": context,
                "crew_role": crew_role,
                "ship_name": ship_name,
                "example_templates": examples,
                "preview_note": "These are examples. Use 'generate_themed_templates_prompt' for AI generation."
            }

        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Utility and Management ====================

    async def backup_current_themes(self) -> Dict[str, Any]:
        """
        Create backup of current theme configuration.

        Saves current theme and ship configurations as a preset
        with timestamp for later restoration.

        Returns:
            Dict with backup operation status
        """
        try:
            current_theme = self.theme_storage.get_current_theme()
            ship_configs = self.theme_storage.get_all_ship_configs()

            if not current_theme and not ship_configs:
                return {
                    "success": False,
                    "error": "No current theme or ship configurations to backup"
                }

            # Create backup name with timestamp
            from datetime import datetime, timezone
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"

            # Save as preset
            theme = current_theme["theme"] if current_theme else "no_theme"
            context = current_theme["context"] if current_theme else "no_context"

            self.theme_storage.save_preset(
                name=backup_name,
                theme=theme,
                context=context,
                ship_configs=ship_configs
            )

            return {
                "success": True,
                "backup_name": backup_name,
                "current_theme": current_theme,
                "ship_configs_count": len(ship_configs),
                "message": f"Theme configuration backed up as '{backup_name}'"
            }

        except Exception as e:
            logger.error(f"Error backing up themes: {e}")
            return {"success": False, "error": str(e)}

    async def backup_edcopilot_files(self) -> Dict[str, Any]:
        """
        Create backup of existing EDCoPilot custom files.

        Creates timestamped backups of existing custom files before
        applying new themed content.

        Returns:
            Dict with backup operation status
        """
        try:
            # This delegates to the existing EDCoPilot backup functionality
            return await self.edcopilot_generator.backup_files()

        except Exception as e:
            logger.error(f"Error backing up EDCoPilot files: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Private Helper Methods ====================

    async def _apply_theme_to_ship(self, ship_name: str, theme: str, context: str) -> Dict[str, Any]:
        """Apply theme immediately to specified ship."""
        try:
            # Configure ship with current theme
            crew_config_result = await self.configure_ship_crew(ship_name, auto_configure=True)

            if not crew_config_result["success"]:
                return crew_config_result

            return {
                "success": True,
                "ship_name": ship_name,
                "theme_applied": True,
                "crew_configured": True
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_theme_examples(self, theme: str, context: str, crew_role: Optional[str] = None) -> List[str]:
        """Generate example templates for preview based on theme."""
        examples = []

        theme_lower = theme.lower()

        if "pirate" in theme_lower:
            examples = [
                "condition:InSupercruise|Entering {SystemName}. Raise the Jolly Roger, matey! Scanning for merchant vessels.",
                "condition:Docked|Anchored at {StationName}. Time to see what treasure this port holds, arrr!",
                "condition:FuelLow|Fuel reserves at {FuelPercent}%. Need to find a fuel depot before we're stranded, ye scurvy dog!",
                "condition:Trading|Cargo hold shows {CargoCount} tons of... acquired goods. Let's fence these at market."
            ]
        elif "corporate" in theme_lower:
            examples = [
                "condition:InSupercruise|Entering {SystemName}. Analyzing market opportunities and profit potential.",
                "condition:Docked|Docked at {StationName}. Reviewing station services for competitive advantages.",
                "condition:FuelLow|Fuel at {FuelPercent}%. Efficiency metrics indicate immediate refueling required.",
                "condition:Trading|Portfolio shows {CargoCount} units. Market analysis suggests optimal profit margins."
            ]
        elif "military" in theme_lower:
            examples = [
                "condition:InSupercruise|Jump complete to {SystemName}. All stations, report status.",
                "condition:Docked|Secured at {StationName}. Requesting permission for shore leave and resupply.",
                "condition:FuelLow|Fuel at {FuelPercent}%. Recommend immediate refueling to maintain operational readiness.",
                "condition:UnderAttack|Red alert! All hands to battle stations! Engaging hostile targets!"
            ]
        else:
            examples = [
                f"condition:InSupercruise|[{theme}-themed arrival dialogue with {{SystemName}}]",
                f"condition:Docked|[{theme}-themed docking dialogue with {{StationName}}]",
                f"condition:FuelLow|[{theme}-themed fuel warning with {{FuelPercent}}]",
                f"condition:Exploring|[{theme}-themed exploration dialogue]"
            ]

        # Add crew role context if specified
        if crew_role:
            role_examples = []
            for example in examples:
                if crew_role.lower() == "navigator":
                    role_examples.append(example.replace("dialogue", "navigation report"))
                elif crew_role.lower() == "engineer":
                    role_examples.append(example.replace("dialogue", "engineering status"))
                elif crew_role.lower() == "security":
                    role_examples.append(example.replace("dialogue", "security report"))
                else:
                    role_examples.append(example)
            examples = role_examples

        return examples