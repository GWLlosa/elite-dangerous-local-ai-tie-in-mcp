"""
AI-Powered Theme Generation System

Generates themed EDCoPilot dialogue templates using Claude Desktop integration.
Provides prompt generation for AI-powered theme creation while maintaining
token syntax and EDCoPilot grammar compliance.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .templates import ChatterEntry, ChatterType, EDCoPilotTokens, EDCoPilotConditions
from .theme_storage import ThemeStorage, CrewMemberTheme, ShipCrewConfig

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when template validation fails."""
    pass


@dataclass
class ThemePromptContext:
    """Context information for theme prompt generation."""
    theme: str
    context: str
    crew_role: Optional[str] = None
    ship_name: Optional[str] = None
    current_templates: Optional[List[str]] = None
    game_state: Optional[Dict[str, Any]] = None


class TemplateValidator:
    """
    Validates generated templates for EDCoPilot compliance.

    Ensures generated content maintains proper token syntax,
    grammar compliance, and content appropriateness.
    """

    # Valid EDCoPilot tokens
    VALID_TOKENS = {
        '{SystemName}', '{StationName}', '{BodyName}', '{ShipName}',
        '{CommanderName}', '{Credits}', '{FuelPercent}', '{ShieldPercent}',
        '{DistanceFromSol}', '{CargoCount}', '{CargoCapacity}'
    }

    # Valid conditions
    VALID_CONDITIONS = {
        'InSupercruise', 'Supercruise', 'Docked', 'ApproachingStation', 'FuelLow', 'UnderAttack',
        'Scanning', 'Exploring', 'FirstDiscovery', 'DeepSpace', 'Trading',
        'InDanger', 'ShieldsDown', 'InNormalSpace'
    }

    @classmethod
    def validate_template(cls, template: str) -> Tuple[bool, List[str]]:
        """
        Validate a single template for EDCoPilot compliance.

        Args:
            template: Template string to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check basic format: condition:State|optional_voice|dialogue
        if not re.match(r'^condition:[A-Za-z&]+(\|voice:[A-Za-z_]+)?\|.+$', template):
            issues.append("Template doesn't match EDCoPilot format: condition:State|dialogue")

        # Extract components
        parts = template.split('|')
        if len(parts) < 2:
            issues.append("Template missing required components")
            return False, issues

        condition_part = parts[0]
        dialogue_part = parts[-1]  # Last part is always dialogue

        # Validate condition format
        if not condition_part.startswith('condition:'):
            issues.append("Template must start with 'condition:'")
        else:
            conditions_str = condition_part[10:]  # Remove 'condition:' prefix
            conditions = conditions_str.split('&')

            for condition in conditions:
                if condition not in cls.VALID_CONDITIONS:
                    issues.append(f"Unknown condition: {condition}")

        # Check for valid tokens
        found_tokens = re.findall(r'\{[^}]+\}', dialogue_part)
        for token in found_tokens:
            if token not in cls.VALID_TOKENS:
                issues.append(f"Invalid or unknown token: {token}")

        # Check for malformed tokens
        malformed_tokens = re.findall(r'\{[^}]*(?:\{|$)', dialogue_part)
        if malformed_tokens:
            issues.append("Malformed tokens found (missing closing braces)")

        # Check content appropriateness (basic checks)
        inappropriate_content = ['fuck', 'shit', 'damn', 'hell', 'ass', 'bitch']
        dialogue_lower = dialogue_part.lower()
        for word in inappropriate_content:
            if word in dialogue_lower:
                issues.append(f"Potentially inappropriate content: {word}")

        # Check dialogue isn't empty
        if not dialogue_part.strip():
            issues.append("Dialogue text is empty")

        # Check reasonable length
        if len(dialogue_part) > 200:
            issues.append("Dialogue text is too long (>200 characters)")

        return len(issues) == 0, issues

    @classmethod
    def validate_templates(cls, templates: List[str]) -> Tuple[List[str], List[Tuple[str, List[str]]]]:
        """
        Validate multiple templates.

        Args:
            templates: List of template strings

        Returns:
            Tuple of (valid_templates, failed_templates_with_issues)
        """
        valid_templates = []
        failed_templates = []

        for template in templates:
            is_valid, issues = cls.validate_template(template)
            if is_valid:
                valid_templates.append(template)
            else:
                failed_templates.append((template, issues))
                logger.warning(f"Template validation failed: {template} - Issues: {issues}")

        return valid_templates, failed_templates


class ThemePromptGenerator:
    """
    Generates AI prompts for Claude Desktop to create themed templates.

    Creates structured prompts that guide AI generation while ensuring
    compliance with EDCoPilot format and token requirements.
    """

    def __init__(self, theme_storage: ThemeStorage):
        self.theme_storage = theme_storage

    def generate_theme_prompt(self, context: ThemePromptContext) -> Dict[str, Any]:
        """
        Generate a comprehensive prompt for Claude Desktop theme generation.

        Args:
            context: Theme prompt context with theme, context, and templates

        Returns:
            Dictionary with prompt and supporting information for Claude Desktop
        """
        # Build the main prompt
        prompt_parts = [
            "# EDCoPilot Theme Generation Request",
            "",
            f"**Theme**: {context.theme}",
            f"**Context**: {context.context}",
        ]

        if context.crew_role:
            prompt_parts.extend([
                f"**Crew Role**: {context.crew_role}",
            ])

        if context.ship_name:
            prompt_parts.extend([
                f"**Ship**: {context.ship_name}",
            ])

        prompt_parts.extend([
            "",
            "## Requirements",
            "",
            "Generate EDCoPilot dialogue templates that match the specified theme and context.",
            "Each template must follow this exact format:",
            "",
            "```",
            "condition:ConditionName|Dialogue text with {Tokens}",
            "```",
            "",
            "### Critical Requirements:",
            "",
            "1. **Token Preservation**: Use exact token syntax: {SystemName}, {StationName}, {ShipName}, etc.",
            "2. **EDCoPilot Grammar**: Follow condition:State|dialogue format exactly",
            "3. **Theme Consistency**: All dialogue must reflect the specified theme and context",
            "4. **Appropriate Content**: Keep dialogue suitable for all audiences",
            "5. **Immersive Quality**: Dialogue should feel natural and enhance roleplay",
            "",
            "### Available Tokens:",
            "- {SystemName} - Current star system",
            "- {StationName} - Current station/port",
            "- {BodyName} - Current celestial body",
            "- {ShipName} - Player's ship name",
            "- {CommanderName} - Player's commander name",
            "- {Credits} - Current credit balance",
            "- {FuelPercent} - Current fuel percentage",
            "- {ShieldPercent} - Current shield percentage",
            "- {DistanceFromSol} - Distance from Sol in light years",
            "- {CargoCount} - Current cargo count",
            "- {CargoCapacity} - Maximum cargo capacity",
            "",
            "### Available Conditions:",
            "- InSupercruise - Traveling in supercruise",
            "- Docked - Docked at a station",
            "- ApproachingStation - Approaching a station",
            "- FuelLow - Low fuel warning",
            "- UnderAttack - Under hostile attack",
            "- Scanning - Performing scans",
            "- Exploring - Exploration activities",
            "- FirstDiscovery - First discovery of system/body",
            "- DeepSpace - >5000 LY from Sol/Colonia",
            "- Trading - Trading activities",
            "- InDanger - Ship in danger",
            "- ShieldsDown - Shields offline",
            "- InNormalSpace - In normal space (not supercruise)",
            "",
            "### Condition Combinations:",
            "You can combine conditions with & (e.g., condition:Scanning&Exploring)",
            "",
        ])

        # Add current templates for reference if available
        if context.current_templates:
            prompt_parts.extend([
                "## Current Templates (for reference):",
                "",
                "Here are the current templates that need to be transformed with your theme:",
                "",
            ])
            for i, template in enumerate(context.current_templates, 1):
                prompt_parts.append(f"{i}. {template}")
            prompt_parts.append("")

        # Add theme-specific guidance
        prompt_parts.extend(self._get_theme_guidance(context.theme, context.context))

        # Add crew role specific guidance if applicable
        if context.crew_role:
            prompt_parts.extend(self._get_crew_role_guidance(context.crew_role))

        # Add examples
        prompt_parts.extend(self._get_examples(context.theme, context.context))

        # Final instructions
        prompt_parts.extend([
            "",
            "## Generation Instructions:",
            "",
            "1. Generate 8-12 themed dialogue templates",
            "2. Cover different game situations (navigation, docking, combat, exploration, trading)",
            "3. Ensure variety in conditions and dialogue content",
            "4. Maintain consistent theme voice across all templates",
            "5. Return ONLY the templates in the correct format, one per line",
            "6. Do not include explanations or additional text",
            "",
            "## Expected Output Format:",
            "",
            "```",
            "condition:InSupercruise|[Themed dialogue with {SystemName}]",
            "condition:Docked|[Themed dialogue with {StationName}]",
            "condition:FuelLow|[Themed dialogue with {FuelPercent}]",
            "[...additional templates...]",
            "```",
        ])

        full_prompt = "\n".join(prompt_parts)

        return {
            "prompt": full_prompt,
            "theme": context.theme,
            "context": context.context,
            "crew_role": context.crew_role,
            "ship_name": context.ship_name,
            "validation_rules": self._get_validation_rules(),
            "processing_instructions": "Generate themed EDCoPilot dialogue templates"
        }

    def _get_theme_guidance(self, theme: str, context: str) -> List[str]:
        """Get theme-specific guidance for prompt generation."""
        guidance = [
            f"## Theme Guidance for '{theme}':",
            "",
            f"**Character Background**: {context}",
            "",
        ]

        # Theme-specific guidance
        theme_lower = theme.lower()

        if "pirate" in theme_lower:
            guidance.extend([
                "**Pirate Theme Guidelines**:",
                "- Use nautical terminology (matey, arrr, ship, crew, treasure)",
                "- Show interest in cargo and trading opportunities",
                "- Maintain a roguish but not evil personality",
                "- Reference ships as vessels, stations as ports",
                "- Use confident, slightly aggressive tone",
            ])

        elif "corporate" in theme_lower or "executive" in theme_lower:
            guidance.extend([
                "**Corporate Theme Guidelines**:",
                "- Use business terminology (profit, market, efficiency, ROI)",
                "- Focus on optimization and performance metrics",
                "- Maintain professional but ambitious tone",
                "- Reference opportunities and competitive advantages",
                "- Show interest in trade routes and market data",
            ])

        elif "military" in theme_lower or "veteran" in theme_lower:
            guidance.extend([
                "**Military Theme Guidelines**:",
                "- Use military terminology (officer, mission, tactical, operational)",
                "- Maintain disciplined, professional communication",
                "- Reference combat readiness and threat assessment",
                "- Show respect for chain of command and protocols",
                "- Use precise, efficient language",
            ])

        elif "explorer" in theme_lower or "scientist" in theme_lower:
            guidance.extend([
                "**Explorer/Scientist Theme Guidelines**:",
                "- Use scientific terminology (analysis, data, discovery, research)",
                "- Show curiosity about astronomical phenomena",
                "- Express excitement about discoveries and exploration",
                "- Reference stellar cartography and scientific methods",
                "- Maintain enthusiastic but professional tone",
            ])

        else:
            guidance.extend([
                "**General Theme Guidelines**:",
                "- Develop consistent personality traits based on the theme",
                "- Use vocabulary and speech patterns appropriate to the character",
                "- Maintain the character's perspective in all situations",
                "- Show appropriate emotional responses to game events",
                "- Keep dialogue authentic to the character concept",
            ])

        guidance.append("")
        return guidance

    def _get_crew_role_guidance(self, crew_role: str) -> List[str]:
        """Get crew role-specific guidance."""
        guidance = [
            f"## Crew Role Guidance for '{crew_role}':",
            "",
        ]

        role_lower = crew_role.lower()

        if "navigator" in role_lower:
            guidance.extend([
                "**Navigator Role**:",
                "- Focus on jump calculations, route planning, stellar cartography",
                "- Report on system status and navigation data",
                "- Use precise, technical language for navigation",
                "- Reference star charts, jump ranges, and system information",
            ])

        elif "science" in role_lower:
            guidance.extend([
                "**Science Officer Role**:",
                "- Focus on scanning, discoveries, and research",
                "- Report on astronomical data and exploration findings",
                "- Express scientific curiosity and analytical thinking",
                "- Reference stellar phenomena, scan results, and discoveries",
            ])

        elif "engineer" in role_lower:
            guidance.extend([
                "**Engineer Role**:",
                "- Focus on ship systems, fuel, repairs, and technical status",
                "- Report on engineering problems and solutions",
                "- Use technical language for ship operations",
                "- Reference power systems, fuel efficiency, and maintenance",
            ])

        elif "security" in role_lower:
            guidance.extend([
                "**Security Chief Role**:",
                "- Focus on threats, combat readiness, and defensive measures",
                "- Report on tactical situations and security status",
                "- Use military/security terminology",
                "- Reference threat assessment, weapons status, and defensive protocols",
            ])

        elif "comms" in role_lower:
            guidance.extend([
                "**Communications Officer Role**:",
                "- Focus on station contact, trading, and external communications",
                "- Report on market data and communication status",
                "- Use diplomatic and commercial language",
                "- Reference station services, trade opportunities, and communications",
            ])

        else:
            guidance.extend([
                f"**{crew_role.title()} Role**:",
                "- Maintain professional crew member communication style",
                "- Report information relevant to your role and responsibilities",
                "- Use appropriate terminology for your position",
                "- Support the overall crew dynamic and ship operations",
            ])

        guidance.append("")
        return guidance

    def _get_examples(self, theme: str, context: str) -> List[str]:
        """Get theme-specific examples."""
        examples = [
            "## Examples:",
            "",
        ]

        theme_lower = theme.lower()

        if "pirate" in theme_lower:
            examples.extend([
                "**Pirate Theme Examples**:",
                "",
                "```",
                "condition:InSupercruise|Entering {SystemName}. Raise the Jolly Roger, matey! Scanning for merchant vessels.",
                "condition:Docked|Anchored at {StationName}. Time to see what treasure this port holds, arrr!",
                "condition:FuelLow|Fuel reserves at {FuelPercent}%. We need to find a fuel depot before we're stranded, ye scurvy dog!",
                "condition:Trading|Cargo hold shows {CargoCount} tons of... acquired goods. Let's see what we can fence here.",
                "```",
            ])

        elif "corporate" in theme_lower:
            examples.extend([
                "**Corporate Executive Examples**:",
                "",
                "```",
                "condition:InSupercruise|Entering {SystemName}. Analyzing market opportunities and profit potential.",
                "condition:Docked|Docked at {StationName}. Reviewing station services for competitive advantages.",
                "condition:FuelLow|Fuel at {FuelPercent}%. Efficiency metrics indicate immediate refueling required.",
                "condition:Trading|Portfolio shows {CargoCount} units. Market analysis suggests optimal profit margins.",
                "```",
            ])

        else:
            examples.extend([
                "**General Theme Examples** (adapt to your specific theme):",
                "",
                "```",
                "condition:InSupercruise|[Theme-appropriate arrival dialogue with {SystemName}]",
                "condition:Docked|[Theme-appropriate docking dialogue with {StationName}]",
                "condition:FuelLow|[Theme-appropriate fuel warning with {FuelPercent}]",
                "condition:Exploring|[Theme-appropriate exploration dialogue]",
                "```",
            ])

        examples.append("")
        return examples

    def _get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for template checking."""
        return {
            "required_format": "condition:State|dialogue",
            "valid_tokens": list(TemplateValidator.VALID_TOKENS),
            "valid_conditions": list(TemplateValidator.VALID_CONDITIONS),
            "max_length": 200,
            "min_templates": 8,
            "max_templates": 15
        }

    def generate_crew_theme_prompt(self, ship_name: str, crew_roles: List[str],
                                  overall_theme: str, overall_context: str) -> Dict[str, Any]:
        """
        Generate prompt for setting up entire crew with individual personalities.

        Args:
            ship_name: Name of the ship
            crew_roles: List of crew roles to configure
            overall_theme: Overall theme for the crew
            overall_context: Overall context for the crew

        Returns:
            Dictionary with prompt for crew setup
        """
        prompt_parts = [
            "# Multi-Crew Theme Configuration",
            "",
            f"**Ship**: {ship_name}",
            f"**Overall Theme**: {overall_theme}",
            f"**Overall Context**: {overall_context}",
            f"**Crew Roles**: {', '.join(crew_roles)}",
            "",
            "## Task",
            "",
            f"Create individual personality themes for each crew member that complement the overall '{overall_theme}' theme.",
            "Each crew member should have their own distinct personality while fitting the overall theme.",
            "",
            "## Crew Role Descriptions:",
            "",
        ]

        # Add role descriptions
        role_descriptions = {
            "commander": "Player character - ship's commanding officer",
            "navigator": "Navigation officer - handles jump calculations and route planning",
            "science": "Science officer - manages scanning, exploration, and research",
            "engineer": "Chief engineer - maintains ship systems and handles technical issues",
            "security": "Security chief - handles combat situations and threat assessment",
            "comms": "Communications officer - manages station contact and trading",
            "medical": "Medical officer - handles crew health and life support",
            "quartermaster": "Quartermaster - manages cargo and supplies"
        }

        for role in crew_roles:
            description = role_descriptions.get(role, f"{role.title()} - specialized crew member")
            prompt_parts.append(f"- **{role.title()}**: {description}")

        prompt_parts.extend([
            "",
            "## Instructions",
            "",
            "For each crew role, provide:",
            "1. **Individual Theme**: Specific personality archetype for this crew member",
            "2. **Individual Context**: Background story that fits the overall context",
            "3. **Personality Traits**: 2-3 key traits that define this character",
            "",
            "## Example Response Format:",
            "",
            "```json",
            "{",
            '  "navigator": {',
            '    "theme": "by-the-book military officer",',
            '    "context": "30-year navy veteran who reluctantly joined this crew",',
            '    "personality_traits": ["precise", "disciplined", "slightly disapproving"]',
            "  },",
            '  "science": {',
            '    "theme": "excited treasure hunter",',
            '    "context": "young researcher fascinated by the hunt for valuable discoveries",',
            '    "personality_traits": ["enthusiastic", "curious", "opportunistic"]',
            "  }",
            "}",
            "```",
            "",
            "Ensure each character feels distinct while maintaining the overall theme consistency.",
        ])

        return {
            "prompt": "\n".join(prompt_parts),
            "ship_name": ship_name,
            "crew_roles": crew_roles,
            "overall_theme": overall_theme,
            "overall_context": overall_context,
            "processing_instructions": "Configure individual crew member personalities"
        }


class ThemeGenerator:
    """
    Main theme generation coordinator.

    Coordinates between theme storage, prompt generation, and template validation
    to provide a complete theme generation system.
    """

    def __init__(self, theme_storage: ThemeStorage):
        self.theme_storage = theme_storage
        self.prompt_generator = ThemePromptGenerator(theme_storage)
        self.validator = TemplateValidator()

    def generate_theme_prompt_for_claude(self, theme: str, context: str,
                                       crew_role: Optional[str] = None,
                                       ship_name: Optional[str] = None,
                                       current_templates: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a prompt for Claude Desktop to create themed templates.

        This method creates a structured prompt that Claude Desktop can use
        to generate themed dialogue while maintaining EDCoPilot compliance.

        Args:
            theme: Theme identifier (e.g., "space pirate")
            context: Theme context (e.g., "owes debt to Space Mafia")
            crew_role: Optional specific crew role
            ship_name: Optional ship name for context
            current_templates: Optional current templates to transform

        Returns:
            Dictionary with prompt and metadata for Claude Desktop
        """
        prompt_context = ThemePromptContext(
            theme=theme,
            context=context,
            crew_role=crew_role,
            ship_name=ship_name,
            current_templates=current_templates
        )

        return self.prompt_generator.generate_theme_prompt(prompt_context)

    def validate_generated_templates(self, templates: List[str]) -> Dict[str, Any]:
        """
        Validate templates generated by Claude Desktop.

        Args:
            templates: List of template strings from Claude Desktop

        Returns:
            Dictionary with validation results and processed templates
        """
        # Clean up templates (remove empty lines, trim whitespace)
        cleaned_templates = []
        for template in templates:
            template = template.strip()
            if template and not template.startswith('#') and '|' in template:
                cleaned_templates.append(template)

        if not cleaned_templates:
            return {
                "success": False,
                "error": "No valid templates found in generated content",
                "valid_templates": [],
                "failed_templates": [],
                "validation_summary": {
                    "total": 0,
                    "valid": 0,
                    "failed": 0
                }
            }

        # Validate templates
        valid_templates, failed_templates = self.validator.validate_templates(cleaned_templates)

        validation_summary = {
            "total": len(cleaned_templates),
            "valid": len(valid_templates),
            "failed": len(failed_templates),
            "success_rate": len(valid_templates) / len(cleaned_templates) if cleaned_templates else 0
        }

        success = len(valid_templates) > 0 and (len(failed_templates) / len(cleaned_templates)) < 0.3

        result = {
            "success": success,
            "valid_templates": valid_templates,
            "failed_templates": failed_templates,
            "validation_summary": validation_summary
        }

        if not success:
            if len(valid_templates) == 0:
                result["error"] = "No valid templates generated"
            else:
                result["error"] = f"Too many validation failures: {len(failed_templates)} of {len(cleaned_templates)} templates failed"

        return result

    def create_chatter_entries_from_templates(self, templates: List[str],
                                            chatter_type: ChatterType = ChatterType.SPACE_CHATTER) -> List[ChatterEntry]:
        """
        Convert validated template strings to ChatterEntry objects.

        Args:
            templates: List of validated template strings
            chatter_type: Type of chatter for the entries

        Returns:
            List of ChatterEntry objects
        """
        entries = []

        for template in templates:
            # Parse template: condition:State|optional_voice|dialogue
            parts = template.split('|')
            if len(parts) < 2:
                continue

            condition_part = parts[0]
            dialogue_part = parts[-1]

            # Extract conditions
            if condition_part.startswith('condition:'):
                conditions_str = condition_part[10:]
                conditions = conditions_str.split('&')
            else:
                conditions = []

            # Check for voice override
            voice_override = None
            if len(parts) == 3 and parts[1].startswith('voice:'):
                voice_override = parts[1][6:]  # Remove 'voice:' prefix

            # Create ChatterEntry
            entry = ChatterEntry(
                text=dialogue_part,
                conditions=conditions,
                voice_override=voice_override,
                chatter_type=chatter_type
            )
            entries.append(entry)

        return entries

    def generate_crew_setup_prompt(self, ship_name: str, crew_roles: List[str],
                                  overall_theme: str, overall_context: str) -> Dict[str, Any]:
        """
        Generate prompt for setting up multi-crew themes.

        Args:
            ship_name: Name of the ship
            crew_roles: List of crew roles to configure
            overall_theme: Overall theme for the crew
            overall_context: Overall context for the crew

        Returns:
            Prompt for Claude Desktop to configure crew personalities
        """
        return self.prompt_generator.generate_crew_theme_prompt(
            ship_name, crew_roles, overall_theme, overall_context
        )

    def get_theme_status(self) -> Dict[str, Any]:
        """Get current theme generation system status."""
        current_theme = self.theme_storage.get_current_theme()
        ship_configs = self.theme_storage.get_all_ship_configs()
        storage_info = self.theme_storage.get_storage_info()

        return {
            "current_theme": current_theme,
            "ship_configurations": {
                name: {
                    "crew_roles": config.crew_roles,
                    "crew_count": len(config.crew_themes),
                    "overall_theme": config.overall_theme,
                    "last_updated": config.last_updated.isoformat() if config.last_updated else None
                }
                for name, config in ship_configs.items()
            },
            "storage_info": storage_info,
            "system_status": "operational"
        }
