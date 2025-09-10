"""
MCP Prompts for Elite Dangerous AI Assistant

Provides intelligent, context-aware prompts for common Elite Dangerous tasks.
Prompts adapt to current game state and recent player activities, generating
comprehensive instructions for AI analysis and assistance.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import json

from ..utils.data_store import DataStore
from ..journal.events import EventCategory


logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Types of prompts available."""
    EXPLORATION = "exploration"
    TRADING = "trading"
    COMBAT = "combat"
    MINING = "mining"
    NAVIGATION = "navigation"
    ENGINEERING = "engineering"
    MISSIONS = "missions"
    PERFORMANCE = "performance"
    STRATEGY = "strategy"
    ROLEPLAY = "roleplay"


class PromptTemplate:
    """Template for generating dynamic prompts."""
    
    def __init__(self, template: str, variables: List[str], description: str):
        """
        Initialize prompt template.
        
        Args:
            template: Template string with {variable} placeholders
            variables: List of required variables
            description: Description of the prompt
        """
        self.template = template
        self.variables = variables
        self.description = description
    
    def render(self, context: Dict[str, Any]) -> str:
        """
        Render the template with provided context.
        
        Args:
            context: Dictionary of variable values
            
        Returns:
            Rendered prompt string
        """
        try:
            # Check all required variables are present
            missing = [v for v in self.variables if v not in context]
            if missing:
                logger.warning(f"Missing template variables: {missing}")
                # Use defaults for missing variables
                for var in missing:
                    context[var] = "[Unknown]"
            
            return self.template.format(**context)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return self.template


class MCPPrompts:
    """
    MCP Prompts provider for Elite Dangerous AI assistance.
    
    Generates context-aware prompts that adapt to current game state
    and recent player activities for comprehensive AI analysis.
    """
    
    def __init__(self, data_store: DataStore):
        """
        Initialize MCP prompts provider.
        
        Args:
            data_store: DataStore instance for accessing game data
        """
        self.data_store = data_store
        
        # Define prompt templates
        self._init_templates()
    
    def _init_templates(self):
        """Initialize prompt templates."""
        self.templates = {
            # Exploration prompts
            "exploration_analysis": PromptTemplate(
                "Analyze my exploration progress in {current_system}. "
                "I've scanned {bodies_scanned} bodies in the last {hours} hours "
                "and visited {systems_visited} systems. My exploration rank is {exploration_rank}. "
                "What valuable discoveries should I prioritize? "
                "Consider stellar phenomena, terraformable worlds, and undiscovered systems.",
                ["current_system", "bodies_scanned", "hours", "systems_visited", "exploration_rank"],
                "Comprehensive exploration analysis with recommendations"
            ),
            
            "exploration_route": PromptTemplate(
                "Plan an exploration route from {current_system} considering: "
                "- My ship's jump range: {jump_range} LY\n"
                "- Fuel capacity: {fuel_capacity} tons\n"
                "- Recent discoveries: {recent_discoveries}\n"
                "Suggest unexplored regions with high value targets and neutron star highways.",
                ["current_system", "jump_range", "fuel_capacity", "recent_discoveries"],
                "Exploration route planning with efficiency optimization"
            ),
            
            # Trading prompts
            "trading_analysis": PromptTemplate(
                "Analyze my trading performance. Current location: {current_station} in {current_system}. "
                "Credits: {credits}. Recent profits: {recent_profit} CR from {trade_count} trades. "
                "Top commodities traded: {top_commodities}. "
                "Suggest profitable trade routes and commodity opportunities based on my trading history.",
                ["current_station", "current_system", "credits", "recent_profit", "trade_count", "top_commodities"],
                "Trading performance analysis with route suggestions"
            ),
            
            "market_opportunity": PromptTemplate(
                "Identify market opportunities near {current_system} within {jump_range} LY. "
                "I have {cargo_capacity} tons cargo capacity and {credits} credits available. "
                "Recent market activity: {market_events}. "
                "Find high-profit trade loops considering supply/demand fluctuations.",
                ["current_system", "jump_range", "cargo_capacity", "credits", "market_events"],
                "Market opportunity identification for immediate profit"
            ),
            
            # Combat prompts
            "combat_review": PromptTemplate(
                "Review my combat performance. Ship: {ship_type} with {ship_modules}. "
                "Combat rank: {combat_rank}. Recent combat: {kills} kills, {deaths} deaths. "
                "Bounties earned: {bounties} CR. Combat zones visited: {combat_zones}. "
                "Analyze my combat effectiveness and suggest improvements to loadout and tactics.",
                ["ship_type", "ship_modules", "combat_rank", "kills", "deaths", "bounties", "combat_zones"],
                "Combat performance review with tactical recommendations"
            ),
            
            "threat_assessment": PromptTemplate(
                "Assess threats in {current_system}. Security level: {security_level}. "
                "Recent hostile encounters: {hostile_events}. "
                "My combat rating: {combat_rank}, Ship: {ship_type}. "
                "Evaluate system danger level and recommend defensive strategies.",
                ["current_system", "security_level", "hostile_events", "combat_rank", "ship_type"],
                "System threat assessment for safety planning"
            ),
            
            # Mining prompts
            "mining_optimization": PromptTemplate(
                "Optimize my mining operations. Current location: {current_system}. "
                "Mining equipment: {mining_modules}. Materials collected: {materials_collected}. "
                "Asteroids prospected: {asteroids_prospected}. Time spent: {mining_time} hours. "
                "Suggest optimal mining locations and techniques for rare materials.",
                ["current_system", "mining_modules", "materials_collected", "asteroids_prospected", "mining_time"],
                "Mining operation optimization for maximum yield"
            ),
            
            # Navigation prompts
            "route_planning": PromptTemplate(
                "Plan optimal route from {current_system} to {destination_system}. "
                "Ship jump range: {jump_range} LY. Fuel: {fuel_level}/{fuel_capacity} tons. "
                "Cargo: {cargo_weight} tons. Preferences: {route_preferences}. "
                "Calculate fastest/most efficient route considering fuel stops and neutron boosts.",
                ["current_system", "destination_system", "jump_range", "fuel_level", "fuel_capacity", "cargo_weight", "route_preferences"],
                "Advanced route planning with optimization"
            ),
            
            "journey_review": PromptTemplate(
                "Review my journey over the last {hours} hours. "
                "Systems visited: {systems_visited}. Total distance: {total_distance} LY. "
                "Jumps made: {jump_count}. Fuel used: {fuel_used} tons. "
                "Notable discoveries: {discoveries}. "
                "Analyze travel efficiency and highlight interesting findings.",
                ["hours", "systems_visited", "total_distance", "jump_count", "fuel_used", "discoveries"],
                "Journey review with efficiency analysis"
            ),
            
            # Engineering prompts
            "engineering_priorities": PromptTemplate(
                "Analyze engineering priorities for {ship_type}. "
                "Current modifications: {current_mods}. "
                "Available materials: {engineering_materials}. "
                "Engineers unlocked: {engineers_unlocked}. "
                "Recommend modification priority order for {primary_activity} activities.",
                ["ship_type", "current_mods", "engineering_materials", "engineers_unlocked", "primary_activity"],
                "Engineering priority analysis for ship optimization"
            ),
            
            # Mission prompts
            "mission_strategy": PromptTemplate(
                "Develop mission strategy. Active missions: {active_missions}. "
                "Mission types: {mission_types}. Time remaining: {time_remaining}. "
                "Current location: {current_system}. Reputation goals: {reputation_goals}. "
                "Prioritize mission completion for maximum reputation and credit gain.",
                ["active_missions", "mission_types", "time_remaining", "current_system", "reputation_goals"],
                "Mission prioritization and completion strategy"
            ),
            
            # Performance prompts
            "performance_analysis": PromptTemplate(
                "Comprehensive performance analysis for the last {days} days. "
                "Credits earned: {credits_earned}. Credits spent: {credits_spent}. "
                "Activities: {activity_breakdown}. Ranks gained: {rank_progress}. "
                "Ships acquired: {new_ships}. Major achievements: {achievements}. "
                "Evaluate overall progress and suggest focus areas for improvement.",
                ["days", "credits_earned", "credits_spent", "activity_breakdown", "rank_progress", "new_ships", "achievements"],
                "Comprehensive performance analysis with recommendations"
            ),
            
            # Strategy prompts
            "daily_goals": PromptTemplate(
                "Set daily goals based on current status. Location: {current_system}. "
                "Ship: {ship_type}. Credits: {credits}. "
                "Recent activities: {recent_activities}. "
                "Active goals: {active_goals}. "
                "Suggest achievable daily objectives for progression.",
                ["current_system", "ship_type", "credits", "recent_activities", "active_goals"],
                "Daily goal setting based on current progress"
            ),
            
            "career_advice": PromptTemplate(
                "Provide career advice. Current ranks: Combat {combat_rank}, Trade {trade_rank}, Exploration {exploration_rank}. "
                "Credits: {credits}. Ships owned: {ships_owned}. "
                "Preferred activities: {preferred_activities}. "
                "Time available: {play_time} hours per week. "
                "Recommend career path and long-term goals.",
                ["combat_rank", "trade_rank", "exploration_rank", "credits", "ships_owned", "preferred_activities", "play_time"],
                "Career path advice for long-term progression"
            ),
            
            # Roleplay prompts
            "commander_log": PromptTemplate(
                "Create commander's log entry. Stardate: {stardate}. "
                "Location: {current_system}, {current_station}. "
                "Recent events: {recent_events}. "
                "Ship status: {ship_status}. "
                "Mission: {current_mission}. "
                "Write immersive log entry from commander's perspective.",
                ["stardate", "current_system", "current_station", "recent_events", "ship_status", "current_mission"],
                "Immersive commander's log generation"
            ),
            
            "situation_report": PromptTemplate(
                "Generate situation report. System: {current_system}. "
                "Threat level: {threat_level}. Faction states: {faction_states}. "
                "Economic status: {economic_status}. "
                "Notable events: {system_events}. "
                "Create detailed sitrep for tactical planning.",
                ["current_system", "threat_level", "faction_states", "economic_status", "system_events"],
                "Tactical situation report for system analysis"
            )
        }
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List all available prompts with metadata.
        
        Returns:
            List of prompt definitions with names and descriptions
        """
        prompts_list = []
        for name, template in self.templates.items():
            prompts_list.append({
                "name": name,
                "description": template.description,
                "variables": template.variables,
                "type": self._get_prompt_type(name).value
            })
        
        return prompts_list
    
    def _get_prompt_type(self, prompt_name: str) -> PromptType:
        """Get prompt type from prompt name."""
        if "exploration" in prompt_name:
            return PromptType.EXPLORATION
        elif "trading" in prompt_name or "market" in prompt_name:
            return PromptType.TRADING
        elif "combat" in prompt_name or "threat" in prompt_name:
            return PromptType.COMBAT
        elif "mining" in prompt_name:
            return PromptType.MINING
        elif "route" in prompt_name or "journey" in prompt_name or "navigation" in prompt_name:
            return PromptType.NAVIGATION
        elif "engineering" in prompt_name:
            return PromptType.ENGINEERING
        elif "mission" in prompt_name:
            return PromptType.MISSIONS
        elif "performance" in prompt_name:
            return PromptType.PERFORMANCE
        elif "strategy" in prompt_name or "goals" in prompt_name or "career" in prompt_name:
            return PromptType.STRATEGY
        elif "roleplay" in prompt_name or "log" in prompt_name or "report" in prompt_name:
            return PromptType.ROLEPLAY
        else:
            return PromptType.STRATEGY
    
    def generate_prompt(self, prompt_name: str, custom_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a specific prompt with current game context.
        
        Args:
            prompt_name: Name of the prompt template
            custom_context: Optional custom context values
            
        Returns:
            Generated prompt with metadata
        """
        try:
            if prompt_name not in self.templates:
                return {
                    "error": f"Unknown prompt: {prompt_name}",
                    "available_prompts": list(self.templates.keys())
                }
            
            template = self.templates[prompt_name]
            
            # Build context from game state
            context = self._build_context(prompt_name)
            
            # Override with custom context if provided
            if custom_context:
                context.update(custom_context)
            
            # Render the prompt
            rendered_prompt = template.render(context)
            
            return {
                "prompt": rendered_prompt,
                "name": prompt_name,
                "type": self._get_prompt_type(prompt_name).value,
                "description": template.description,
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating prompt {prompt_name}: {e}")
            return {"error": str(e)}
    
    def _build_context(self, prompt_name: str) -> Dict[str, Any]:
        """
        Build context for prompt generation from game state.
        
        Args:
            prompt_name: Name of the prompt being generated
            
        Returns:
            Context dictionary with game state values
        """
        context = {}
        game_state = self.data_store.get_game_state()
        
        # Basic game state
        context["current_system"] = game_state.current_system or "Unknown"
        context["current_station"] = game_state.current_station or "Deep Space"
        context["ship_type"] = game_state.current_ship or "Unknown"
        context["credits"] = f"{game_state.credits:,}" if game_state.credits else "0"
        context["fuel_level"] = game_state.fuel_level or 0
        context["fuel_capacity"] = 32  # Default, should be from ship data
        
        # Ranks
        context["combat_rank"] = game_state.ranks.get("Combat", "Harmless")
        context["trade_rank"] = game_state.ranks.get("Trade", "Penniless")
        context["exploration_rank"] = game_state.ranks.get("Explore", "Aimless")
        
        # Time-based context
        context["hours"] = 24  # Default time range
        context["days"] = 7
        context["stardate"] = datetime.now(timezone.utc).strftime("%Y.%m.%d %H:%M")
        
        # Activity-specific context based on prompt type
        prompt_type = self._get_prompt_type(prompt_name)
        
        if prompt_type == PromptType.EXPLORATION:
            context.update(self._build_exploration_context())
        elif prompt_type == PromptType.TRADING:
            context.update(self._build_trading_context())
        elif prompt_type == PromptType.COMBAT:
            context.update(self._build_combat_context())
        elif prompt_type == PromptType.MINING:
            context.update(self._build_mining_context())
        elif prompt_type == PromptType.NAVIGATION:
            context.update(self._build_navigation_context())
        elif prompt_type == PromptType.MISSIONS:
            context.update(self._build_mission_context())
        elif prompt_type == PromptType.PERFORMANCE:
            context.update(self._build_performance_context())
        
        # Add recent events summary
        recent_events = self.data_store.get_recent_events(minutes=60)
        if recent_events:
            event_summaries = [e.summary for e in recent_events[:5]]
            context["recent_events"] = "; ".join(event_summaries)
        else:
            context["recent_events"] = "No recent activity"
        
        return context
    
    def _build_exploration_context(self) -> Dict[str, Any]:
        """Build exploration-specific context."""
        context = {}
        
        # Get exploration events
        scan_events = self.data_store.get_events_by_type("Scan", limit=100)
        jump_events = self.data_store.get_events_by_type("FSDJump", limit=100)
        
        context["bodies_scanned"] = len(scan_events)
        context["systems_visited"] = len(set(e.data.get("StarSystem") for e in jump_events if "StarSystem" in e.data))
        
        # Recent discoveries
        valuable_scans = [e for e in scan_events if e.data.get("TerraformState") or e.data.get("WasDiscovered") == False]
        if valuable_scans:
            discoveries = [f"{e.data.get('BodyName', 'Unknown')}" for e in valuable_scans[:3]]
            context["recent_discoveries"] = ", ".join(discoveries)
        else:
            context["recent_discoveries"] = "None recently"
        
        # Jump range (estimate from recent jumps)
        if jump_events:
            max_jump = max([e.data.get("JumpDist", 0) for e in jump_events])
            context["jump_range"] = f"{max_jump:.2f}"
        else:
            context["jump_range"] = "30"  # Default
        
        return context
    
    def _build_trading_context(self) -> Dict[str, Any]:
        """Build trading-specific context."""
        context = {}
        
        # Get trading events
        buy_events = self.data_store.get_events_by_type("MarketBuy", limit=50)
        sell_events = self.data_store.get_events_by_type("MarketSell", limit=50)
        
        context["trade_count"] = len(buy_events) + len(sell_events)
        
        # Calculate profits
        total_profit = sum(e.data.get("Profit", 0) for e in sell_events)
        context["recent_profit"] = f"{total_profit:,}"
        
        # Top commodities
        commodities = {}
        for event in buy_events + sell_events:
            commodity = event.data.get("Type", "Unknown")
            commodities[commodity] = commodities.get(commodity, 0) + 1
        
        if commodities:
            top_3 = sorted(commodities.items(), key=lambda x: x[1], reverse=True)[:3]
            context["top_commodities"] = ", ".join([c[0] for c in top_3])
        else:
            context["top_commodities"] = "None recently"
        
        # Market events
        market_events = buy_events + sell_events
        if market_events:
            recent_markets = [f"{e.event_type} {e.data.get('Type', '')}" for e in market_events[:3]]
            context["market_events"] = "; ".join(recent_markets)
        else:
            context["market_events"] = "No recent market activity"
        
        # Cargo capacity (estimate)
        context["cargo_capacity"] = 100  # Default, should be from ship data
        
        return context
    
    def _build_combat_context(self) -> Dict[str, Any]:
        """Build combat-specific context."""
        context = {}
        
        # Get combat events
        bounty_events = self.data_store.get_events_by_type("Bounty", limit=50)
        death_events = self.data_store.get_events_by_type("Died", limit=10)
        interdiction_events = self.data_store.get_events_by_type("Interdicted", limit=20)
        
        context["kills"] = len(bounty_events)
        context["deaths"] = len(death_events)
        
        # Calculate bounties
        total_bounties = sum(e.data.get("Reward", 0) for e in bounty_events)
        context["bounties"] = f"{total_bounties:,}"
        
        # Combat zones
        combat_zone_events = self.data_store.get_events_by_category(EventCategory.COMBAT, limit=100)
        unique_systems = set(e.data.get("StarSystem") for e in combat_zone_events if "StarSystem" in e.data)
        context["combat_zones"] = len(unique_systems)
        
        # Hostile events
        hostile_events = bounty_events + death_events + interdiction_events
        if hostile_events:
            recent_hostiles = [e.summary for e in hostile_events[:3]]
            context["hostile_events"] = "; ".join(recent_hostiles)
        else:
            context["hostile_events"] = "No recent hostile encounters"
        
        # Ship modules (placeholder)
        context["ship_modules"] = "Multi-cannons, Shield boosters, Hull reinforcement"
        
        # Security level (estimate from current system)
        context["security_level"] = "Medium"  # Should be from system data
        
        # Threat level
        if len(death_events) > 2:
            context["threat_level"] = "High"
        elif len(interdiction_events) > 5:
            context["threat_level"] = "Medium"
        else:
            context["threat_level"] = "Low"
        
        return context
    
    def _build_mining_context(self) -> Dict[str, Any]:
        """Build mining-specific context."""
        context = {}
        
        # Get mining events
        mining_events = self.data_store.get_events_by_category(EventCategory.MINING, limit=100)
        material_events = self.data_store.get_events_by_type("MaterialCollected", limit=50)
        prospect_events = self.data_store.get_events_by_type("ProspectedAsteroid", limit=50)
        
        context["materials_collected"] = len(material_events)
        context["asteroids_prospected"] = len(prospect_events)
        
        # Mining time (estimate)
        if mining_events:
            first_event = min(mining_events, key=lambda e: e.timestamp)
            last_event = max(mining_events, key=lambda e: e.timestamp)
            time_diff = last_event.timestamp - first_event.timestamp
            context["mining_time"] = f"{time_diff.total_seconds() / 3600:.1f}"
        else:
            context["mining_time"] = "0"
        
        # Mining modules (placeholder)
        context["mining_modules"] = "Mining lasers, Refinery, Collector limpets"
        
        return context
    
    def _build_navigation_context(self) -> Dict[str, Any]:
        """Build navigation-specific context."""
        context = {}
        
        # Get navigation events
        jump_events = self.data_store.get_events_by_type("FSDJump", limit=100)
        
        if jump_events:
            # Calculate journey stats
            context["jump_count"] = len(jump_events)
            total_distance = sum(e.data.get("JumpDist", 0) for e in jump_events)
            context["total_distance"] = f"{total_distance:.2f}"
            
            # Systems visited
            systems = list(set(e.data.get("StarSystem") for e in jump_events if "StarSystem" in e.data))
            context["systems_visited"] = ", ".join(systems[:5]) if systems else "None"
            
            # Fuel usage (estimate)
            context["fuel_used"] = f"{len(jump_events) * 2.5:.1f}"  # Rough estimate
            
            # Jump range
            if jump_events:
                max_jump = max([e.data.get("JumpDist", 0) for e in jump_events])
                context["jump_range"] = f"{max_jump:.2f}"
            else:
                context["jump_range"] = "30"
        else:
            context["jump_count"] = 0
            context["total_distance"] = "0"
            context["systems_visited"] = "None"
            context["fuel_used"] = "0"
            context["jump_range"] = "30"
        
        # Navigation preferences
        context["route_preferences"] = "Fastest route, avoid hostile systems"
        context["destination_system"] = "Colonia"  # Example destination
        context["cargo_weight"] = "50"  # Example cargo
        
        # Discoveries
        scan_events = self.data_store.get_events_by_type("Scan", limit=20)
        if scan_events:
            discoveries = [e.data.get("BodyName", "Unknown") for e in scan_events[:3]]
            context["discoveries"] = ", ".join(discoveries)
        else:
            context["discoveries"] = "None recently"
        
        return context
    
    def _build_mission_context(self) -> Dict[str, Any]:
        """Build mission-specific context."""
        context = {}
        
        # Get mission events
        mission_accepted = self.data_store.get_events_by_type("MissionAccepted", limit=20)
        mission_completed = self.data_store.get_events_by_type("MissionCompleted", limit=20)
        
        # Active missions (accepted but not completed)
        active_count = len(mission_accepted) - len(mission_completed)
        context["active_missions"] = str(max(0, active_count))
        
        # Mission types
        if mission_accepted:
            types = set(e.data.get("Name", "Unknown") for e in mission_accepted)
            context["mission_types"] = ", ".join(list(types)[:3])
        else:
            context["mission_types"] = "None active"
        
        # Time remaining (placeholder)
        context["time_remaining"] = "Various deadlines"
        
        # Reputation goals
        context["reputation_goals"] = "Federation rank increase, Local faction support"
        
        return context
    
    def _build_performance_context(self) -> Dict[str, Any]:
        """Build performance-specific context."""
        context = {}
        
        # Get all events for performance analysis
        all_events = self.data_store.get_all_events()
        
        # Calculate credits flow
        credits_earned = sum(e.data.get("Reward", 0) for e in all_events if "Reward" in e.data)
        credits_spent = sum(e.data.get("Cost", 0) for e in all_events if "Cost" in e.data)
        
        context["credits_earned"] = f"{credits_earned:,}"
        context["credits_spent"] = f"{credits_spent:,}"
        
        # Activity breakdown
        categories = {}
        for event in all_events:
            cat = event.category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            top_activities = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
            context["activity_breakdown"] = ", ".join([f"{c[0]} ({c[1]})" for c in top_activities])
        else:
            context["activity_breakdown"] = "No recent activities"
        
        # Placeholder values for other metrics
        context["rank_progress"] = "Combat +1, Trade +0, Exploration +2"
        context["new_ships"] = "None"
        context["achievements"] = "First discovery bonus x3"
        
        # Strategy context
        context["recent_activities"] = context["activity_breakdown"]
        context["active_goals"] = "Elite exploration rank, Colonia journey"
        context["ships_owned"] = "Python, AspX, Vulture"
        context["preferred_activities"] = "Exploration, Trading"
        context["play_time"] = "10"
        
        # Additional roleplay context
        context["ship_status"] = "All systems operational"
        context["current_mission"] = "Deep space exploration"
        context["faction_states"] = "Federation: Friendly, Empire: Neutral"
        context["economic_status"] = "Boom"
        context["system_events"] = "None reported"
        
        return context
    
    def generate_contextual_prompt(
        self,
        prompt_type: PromptType,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate the most relevant prompt for the specified type based on current context.
        
        Args:
            prompt_type: Type of prompt to generate
            time_range_hours: Time range for analysis
            
        Returns:
            Generated prompt with context
        """
        try:
            # Find templates matching the prompt type
            matching_templates = [
                name for name in self.templates.keys()
                if self._get_prompt_type(name) == prompt_type
            ]
            
            if not matching_templates:
                return {
                    "error": f"No templates found for type: {prompt_type.value}",
                    "available_types": [t.value for t in PromptType]
                }
            
            # Select the most relevant template based on recent activity
            selected_template = self._select_best_template(matching_templates, time_range_hours)
            
            # Generate the prompt
            return self.generate_prompt(selected_template, {"hours": time_range_hours})
            
        except Exception as e:
            logger.error(f"Error generating contextual prompt: {e}")
            return {"error": str(e)}
    
    def _select_best_template(self, template_names: List[str], time_range_hours: int) -> str:
        """
        Select the best template based on recent activity.
        
        Args:
            template_names: List of template names to choose from
            time_range_hours: Time range for activity analysis
            
        Returns:
            Name of the best template
        """
        # Get recent events to determine activity
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
        all_events = self.data_store.get_all_events()
        recent_events = [e for e in all_events if e.timestamp >= cutoff_time]
        
        if not recent_events:
            # No recent activity, return first template
            return template_names[0]
        
        # Count events by category
        category_counts = {}
        for event in recent_events:
            cat = event.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Score templates based on relevance to recent activity
        template_scores = {}
        for name in template_names:
            score = 0
            
            # Higher score for templates matching recent activity
            if "exploration" in name and EventCategory.EXPLORATION in category_counts:
                score += category_counts[EventCategory.EXPLORATION]
            if "trading" in name and EventCategory.TRADING in category_counts:
                score += category_counts[EventCategory.TRADING]
            if "combat" in name and EventCategory.COMBAT in category_counts:
                score += category_counts[EventCategory.COMBAT]
            if "mining" in name and EventCategory.MINING in category_counts:
                score += category_counts[EventCategory.MINING]
            
            # Prefer analysis templates over specific action templates
            if "analysis" in name or "review" in name:
                score += 10
            
            template_scores[name] = score
        
        # Return template with highest score
        best_template = max(template_scores.items(), key=lambda x: x[1])
        return best_template[0]
    
    def generate_adaptive_prompts(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate multiple adaptive prompts based on current game state and recent activity.
        
        Args:
            count: Number of prompts to generate
            
        Returns:
            List of generated prompts
        """
        try:
            prompts = []
            
            # Analyze recent activity to determine relevant prompt types
            activity_types = self._analyze_recent_activity()
            
            # Generate prompts for top activity types
            for activity_type in activity_types[:count]:
                prompt = self.generate_contextual_prompt(activity_type)
                if "error" not in prompt:
                    prompts.append(prompt)
            
            # Fill remaining slots with strategic prompts if needed
            while len(prompts) < count:
                strategic_prompts = ["daily_goals", "performance_analysis", "career_advice"]
                for prompt_name in strategic_prompts:
                    if len(prompts) >= count:
                        break
                    prompt = self.generate_prompt(prompt_name)
                    if "error" not in prompt:
                        prompts.append(prompt)
            
            return prompts
            
        except Exception as e:
            logger.error(f"Error generating adaptive prompts: {e}")
            return [{"error": str(e)}]
    
    def _analyze_recent_activity(self) -> List[PromptType]:
        """
        Analyze recent activity to determine relevant prompt types.
        
        Returns:
            List of prompt types ordered by relevance
        """
        # Get recent events
        recent_events = self.data_store.get_recent_events(minutes=120)
        
        if not recent_events:
            # Default order when no recent activity
            return [PromptType.STRATEGY, PromptType.PERFORMANCE, PromptType.EXPLORATION]
        
        # Count events by category
        category_counts = {}
        for event in recent_events:
            cat = event.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Map categories to prompt types
        prompt_type_scores = {
            PromptType.EXPLORATION: category_counts.get(EventCategory.EXPLORATION, 0) + 
                                   category_counts.get(EventCategory.SYSTEM, 0),
            PromptType.TRADING: category_counts.get(EventCategory.TRADING, 0),
            PromptType.COMBAT: category_counts.get(EventCategory.COMBAT, 0),
            PromptType.MINING: category_counts.get(EventCategory.MINING, 0),
            PromptType.NAVIGATION: category_counts.get(EventCategory.NAVIGATION, 0),
            PromptType.ENGINEERING: category_counts.get(EventCategory.ENGINEERING, 0),
            PromptType.MISSIONS: category_counts.get(EventCategory.MISSION, 0),
            PromptType.PERFORMANCE: 5,  # Base score for performance
            PromptType.STRATEGY: 5,  # Base score for strategy
            PromptType.ROLEPLAY: 3   # Base score for roleplay
        }
        
        # Sort by score
        sorted_types = sorted(prompt_type_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [pt[0] for pt in sorted_types]
