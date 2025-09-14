"""
MCP Prompts for Elite Dangerous Context-Aware AI Assistance

Provides intelligent prompts for common Elite Dangerous tasks with context-aware
content generation based on current game state and recent activities.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

try:
    from ..utils.data_store import DataStore
    from ..journal.events import EventCategory
except ImportError:
    from src.utils.data_store import DataStore
    from src.journal.events import EventCategory

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Types of MCP prompts available."""
    EXPLORATION = "exploration"
    TRADING = "trading"
    COMBAT = "combat"
    MINING = "mining"
    MISSIONS = "missions"
    ENGINEERING = "engineering"
    JOURNEY = "journey"
    PERFORMANCE = "performance"
    STRATEGY = "strategy"


class PromptTemplate:
    """Template for dynamic prompt generation."""
    
    def __init__(self, name: str, description: str, template: str, variables: List[str]):
        """
        Initialize prompt template.
        
        Args:
            name: Template name
            description: Template description
            template: Template string with {variable} placeholders
            variables: List of required variable names
        """
        self.name = name
        self.description = description
        self.template = template
        self.variables = variables
    
    def render(self, context: Dict[str, Any]) -> str:
        """
        Render template with provided context variables.
        
        Args:
            context: Dictionary containing variable values
            
        Returns:
            Rendered prompt string
        """
        try:
            # Ensure all required variables are present
            missing_vars = [var for var in self.variables if var not in context]
            if missing_vars:
                logger.warning(f"Missing variables for template {self.name}: {missing_vars}")
                # Fill missing variables with placeholders
                for var in missing_vars:
                    context[var] = f"[{var.upper()}_NOT_AVAILABLE]"
            
            return self.template.format(**context)
        except Exception as e:
            logger.error(f"Error rendering template {self.name}: {e}")
            return f"Error rendering prompt template: {e}"


class MCPPrompts:
    """
    MCP Prompts provider for Elite Dangerous context-aware assistance.
    
    Generates intelligent prompts based on current game state, recent activities,
    and player context to provide relevant AI assistance.
    """
    
    def __init__(self, data_store: DataStore):
        """
        Initialize MCP prompts provider.
        
        Args:
            data_store: DataStore instance for accessing game data
        """
        self.data_store = data_store
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize prompt templates for different activities."""
        
        self.templates = {
            "exploration_analysis": PromptTemplate(
                name="Exploration Analysis",
                description="Analyze recent exploration activities and suggest next steps",
                template="""Analyze my recent Elite Dangerous exploration activities:

Current Status:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}
- Exploration Rank: {exploration_rank}

Recent Exploration (Last {time_range} hours):
- Systems Visited: {systems_visited}
- Bodies Scanned: {bodies_scanned}
- Distance Traveled: {distance_ly:.1f} LY
- Exploration Earnings: {exploration_earnings:,} CR

Recent Systems:
{recent_systems}

Scan Summary:
{scan_summary}

Please provide:
1. Analysis of my exploration efficiency and patterns
2. Recommendations for valuable scanning targets
3. Suggestions for profitable exploration routes
4. Tips for optimizing my exploration strategy
5. Assessment of my current exploration equipment and ship loadout""",
                variables=["current_system", "current_ship", "credits", "exploration_rank", 
                          "time_range", "systems_visited", "bodies_scanned", "distance_ly",
                          "exploration_earnings", "recent_systems", "scan_summary"]
            ),
            
            "trading_strategy": PromptTemplate(
                name="Trading Strategy",
                description="Analyze trading performance and suggest profitable opportunities",
                template="""Analyze my Elite Dangerous trading activities and suggest improvements:

Current Status:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}
- Trade Rank: {trade_rank}
- Cargo Capacity: {cargo_capacity}

Recent Trading (Last {time_range} hours):
- Total Profit: {total_profit:,} CR
- Number of Trades: {trade_count}
- Average Profit per Trade: {avg_profit_per_trade:,} CR
- Profit per Hour: {profit_per_hour:,} CR/hr

Best Recent Trades:
{best_trades}

Current Market Opportunities:
{market_opportunities}

Please provide:
1. Analysis of my trading efficiency and profit margins
2. Recommendations for improving trade routes
3. Suggestions for high-value commodities to focus on
4. Tips for optimizing cargo space and trade timing
5. Assessment of my trading ship setup and potential upgrades""",
                variables=["current_system", "current_ship", "credits", "trade_rank", "cargo_capacity",
                          "time_range", "total_profit", "trade_count", "avg_profit_per_trade",
                          "profit_per_hour", "best_trades", "market_opportunities"]
            ),
            
            "combat_assessment": PromptTemplate(
                name="Combat Assessment",
                description="Analyze combat performance and suggest tactical improvements",
                template="""Analyze my Elite Dangerous combat performance:

Current Status:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}
- Combat Rank: {combat_rank}
- Hull Health: {hull_health}%

Recent Combat (Last {time_range} hours):
- Bounties Earned: {bounties_earned:,} CR
- Combat Bonds: {combat_bonds:,} CR
- Ships Destroyed: {ships_destroyed}
- Deaths: {deaths}
- Survival Rate: {survival_rate:.1f}%

Combat Summary:
{combat_events}

Current Loadout:
{ship_loadout}

Please provide:
1. Analysis of my combat effectiveness and tactics
2. Recommendations for ship loadout improvements
3. Suggestions for profitable combat activities
4. Tips for improving survival and kill rates
5. Assessment of optimal combat zones and targets""",
                variables=["current_system", "current_ship", "credits", "combat_rank", "hull_health",
                          "time_range", "bounties_earned", "combat_bonds", "ships_destroyed",
                          "deaths", "survival_rate", "combat_events", "ship_loadout"]
            ),
            
            "mining_optimization": PromptTemplate(
                name="Mining Optimization",
                description="Analyze mining activities and suggest efficiency improvements",
                template="""Analyze my Elite Dangerous mining operations:

Current Status:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}
- Cargo Hold: {cargo_used}/{cargo_capacity}

Recent Mining (Last {time_range} hours):
- Materials Collected: {materials_collected}
- Asteroids Mined: {asteroids_mined}
- Mining Earnings: {mining_earnings:,} CR
- Average Value per Ton: {avg_value_per_ton:,} CR

Materials Summary:
{materials_summary}

Mining Equipment:
{mining_equipment}

Please provide:
1. Analysis of my mining efficiency and profitability
2. Recommendations for valuable mining targets
3. Suggestions for optimal mining locations
4. Tips for improving mining equipment and techniques
5. Assessment of market opportunities for mined materials""",
                variables=["current_system", "current_ship", "credits", "cargo_used", "cargo_capacity",
                          "time_range", "materials_collected", "asteroids_mined", "mining_earnings",
                          "avg_value_per_ton", "materials_summary", "mining_equipment"]
            ),
            
            "mission_guidance": PromptTemplate(
                name="Mission Guidance",
                description="Analyze mission performance and suggest strategic choices",
                template="""Analyze my Elite Dangerous mission activities:

Current Status:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}
- Reputation: {faction_reputation}

Active Missions:
{active_missions}

Recent Mission Performance (Last {time_range} hours):
- Missions Completed: {missions_completed}
- Missions Failed: {missions_failed}
- Success Rate: {success_rate:.1f}%
- Total Rewards: {total_rewards:,} CR

Mission Types:
{mission_types_summary}

Faction Standing:
{faction_standings}

Please provide:
1. Analysis of my mission performance and strategy
2. Recommendations for profitable mission types
3. Suggestions for improving success rates
4. Tips for building faction reputation efficiently
5. Assessment of risk vs reward for different mission categories""",
                variables=["current_system", "current_ship", "credits", "faction_reputation",
                          "active_missions", "time_range", "missions_completed", "missions_failed",
                          "success_rate", "total_rewards", "mission_types_summary", "faction_standings"]
            ),
            
            "engineering_progress": PromptTemplate(
                name="Engineering Progress",
                description="Analyze engineering activities and suggest upgrade priorities",
                template="""Analyze my Elite Dangerous engineering progress:

Current Status:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}

Engineering Status:
{engineer_standings}

Recent Engineering (Last {time_range} hours):
- Engineers Visited: {engineers_visited}
- Modifications Applied: {modifications_applied}
- Materials Used: {materials_used}

Current Ship Modifications:
{ship_modifications}

Material Inventory:
{material_inventory}

Blueprint Progress:
{blueprint_progress}

Please provide:
1. Analysis of my engineering progress and priorities
2. Recommendations for next engineering upgrades
3. Suggestions for efficient material gathering
4. Tips for unlocking and progressing with engineers
5. Assessment of optimal upgrade paths for my ship and playstyle""",
                variables=["current_system", "current_ship", "credits", "engineer_standings",
                          "time_range", "engineers_visited", "modifications_applied", "materials_used",
                          "ship_modifications", "material_inventory", "blueprint_progress"]
            ),
            
            "journey_review": PromptTemplate(
                name="Journey Review",
                description="Comprehensive review of recent journey and travel patterns",
                template="""Review my recent Elite Dangerous journey:

Current Status:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}
- Jump Range: {jump_range:.1f} LY
- Fuel: {fuel_level}%

Journey Summary (Last {time_range} hours):
- Total Jumps: {total_jumps}
- Distance Traveled: {total_distance:.1f} LY
- Systems Visited: {systems_visited}
- Stations Visited: {stations_visited}

Route Analysis:
{route_analysis}

Notable Events:
{notable_events}

Navigation Efficiency:
- Average Jump Distance: {avg_jump_distance:.1f} LY
- Fuel Efficiency: {fuel_efficiency}
- Navigation Time: {navigation_time}

Please provide:
1. Analysis of my travel patterns and route efficiency
2. Recommendations for optimizing jump range and fuel usage
3. Suggestions for discovering interesting locations
4. Tips for planning efficient long-distance routes
5. Assessment of exploration opportunities along my journey""",
                variables=["current_system", "current_ship", "credits", "jump_range", "fuel_level",
                          "time_range", "total_jumps", "total_distance", "systems_visited",
                          "stations_visited", "route_analysis", "notable_events", "avg_jump_distance",
                          "fuel_efficiency", "navigation_time"]
            ),
            
            "performance_review": PromptTemplate(
                name="Performance Review",
                description="Comprehensive performance analysis across all activities",
                template="""Comprehensive Elite Dangerous performance review:

Current Status:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}
- Total Assets: {total_assets:,} CR

Overall Performance (Last {time_range} hours):
- Total Credits Earned: {credits_earned:,} CR
- Total Credits Spent: {credits_spent:,} CR
- Net Profit: {net_profit:,} CR
- Credits per Hour: {credits_per_hour:,} CR/hr

Activity Breakdown:
{activity_breakdown}

Efficiency Metrics:
{efficiency_metrics}

Progress Indicators:
{progress_indicators}

Goals and Achievements:
{achievements}

Please provide:
1. Analysis of my overall performance and progress
2. Recommendations for improving credit earning efficiency
3. Suggestions for balancing different activities
4. Tips for achieving specific goals and milestones
5. Assessment of my Elite Dangerous career trajectory""",
                variables=["current_system", "current_ship", "credits", "total_assets",
                          "time_range", "credits_earned", "credits_spent", "net_profit",
                          "credits_per_hour", "activity_breakdown", "efficiency_metrics",
                          "progress_indicators", "achievements"]
            ),
            
            "strategic_planning": PromptTemplate(
                name="Strategic Planning",
                description="Strategic planning based on current state and goals",
                template="""Strategic planning for my Elite Dangerous career:

Current State Assessment:
- Location: {current_system}
- Ship: {current_ship}
- Credits: {credits:,}
- Combat Rank: {combat_rank}
- Trade Rank: {trade_rank}
- Exploration Rank: {exploration_rank}

Recent Activity Focus:
{activity_focus}

Current Objectives:
{current_objectives}

Available Opportunities:
{opportunities}

Resource Assessment:
{resource_assessment}

Market Conditions:
{market_conditions}

Risk Factors:
{risk_factors}

Please provide:
1. Strategic recommendations for my next steps
2. Suggestions for short-term and long-term goals
3. Analysis of optimal activities for my current situation
4. Tips for resource allocation and time management
5. Assessment of market opportunities and timing""",
                variables=["current_system", "current_ship", "credits", "combat_rank", "trade_rank",
                          "exploration_rank", "activity_focus", "current_objectives", "opportunities",
                          "resource_assessment", "market_conditions", "risk_factors"]
            )
        }
    
    def list_available_prompts(self) -> List[Dict[str, Any]]:
        """
        List all available prompt templates.
        
        Returns:
            List of prompt templates with metadata
        """
        prompts = []
        for template_id, template in self.templates.items():
            prompts.append({
                "id": template_id,
                "name": template.name,
                "description": template.description,
                "variables": template.variables,
                "type": self._get_prompt_type(template_id)
            })
        return prompts
    
    def _get_prompt_type(self, template_id: str) -> str:
        """Get prompt type from template ID."""
        if "exploration" in template_id:
            return PromptType.EXPLORATION.value
        elif "trading" in template_id:
            return PromptType.TRADING.value
        elif "combat" in template_id:
            return PromptType.COMBAT.value
        elif "mining" in template_id:
            return PromptType.MINING.value
        elif "mission" in template_id:
            return PromptType.MISSIONS.value
        elif "engineering" in template_id:
            return PromptType.ENGINEERING.value
        elif "journey" in template_id:
            return PromptType.JOURNEY.value
        elif "performance" in template_id:
            return PromptType.PERFORMANCE.value
        elif "strategic" in template_id:
            return PromptType.STRATEGY.value
        else:
            return "general"
    
    async def generate_prompt(self, template_id: str, time_range_hours: int = 24) -> str:
        """
        Generate a context-aware prompt based on current game state.
        
        Args:
            template_id: ID of the template to use
            time_range_hours: Time range for analyzing recent activities
            
        Returns:
            Generated prompt string
        """
        try:
            if template_id not in self.templates:
                available = ", ".join(self.templates.keys())
                return f"Invalid template ID: {template_id}. Available templates: {available}"
            
            template = self.templates[template_id]
            context = await self._build_context(template_id, time_range_hours)
            
            return template.render(context)
            
        except Exception as e:
            logger.error(f"Error generating prompt {template_id}: {e}")
            return f"Error generating prompt: {e}"
    
    async def _build_context(self, template_id: str, time_range_hours: int) -> Dict[str, Any]:
        """Build context variables for prompt generation."""
        try:
            # Get basic game state
            game_state = self.data_store.get_game_state()
            
            # Get recent events for analysis
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
            recent_events = self.data_store.get_recent_events(time_range_hours * 60)  # Convert hours to minutes
            
            # Build base context
            context = {
                "current_system": game_state.current_system or "Unknown",
                "current_ship": game_state.current_ship or "Unknown",
                "credits": game_state.credits,
                "hull_health": game_state.hull_health,
                "fuel_level": game_state.fuel_level,
                "time_range": time_range_hours,
                "combat_rank": game_state.ranks.get("Combat", "Unknown"),
                "trade_rank": game_state.ranks.get("Trade", "Unknown"),
                "exploration_rank": game_state.ranks.get("Explore", "Unknown")
            }
            
            # Add template-specific context
            if template_id == "exploration_analysis":
                context.update(await self._build_exploration_context(recent_events, time_range_hours))
            elif template_id == "trading_strategy":
                context.update(await self._build_trading_context(recent_events, time_range_hours))
            elif template_id == "combat_assessment":
                context.update(await self._build_combat_context(recent_events, time_range_hours))
            elif template_id == "mining_optimization":
                context.update(await self._build_mining_context(recent_events, time_range_hours))
            elif template_id == "mission_guidance":
                context.update(await self._build_mission_context(recent_events, time_range_hours))
            elif template_id == "engineering_progress":
                context.update(await self._build_engineering_context(recent_events, time_range_hours))
            elif template_id == "journey_review":
                context.update(await self._build_journey_context(recent_events, time_range_hours))
            elif template_id == "performance_review":
                context.update(await self._build_performance_context(recent_events, time_range_hours))
            elif template_id == "strategic_planning":
                context.update(await self._build_strategic_context(recent_events, time_range_hours))
            
            return context
            
        except Exception as e:
            logger.error(f"Error building context for {template_id}: {e}")
            return {"error": str(e)}
    
    async def _build_exploration_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for exploration analysis."""
        exploration_events = [e for e in recent_events if e.category == EventCategory.EXPLORATION]
        jump_events = [e for e in recent_events if e.event_type == "FSDJump"]
        scan_events = [e for e in recent_events if "Scan" in e.event_type]
        
        # Calculate exploration metrics
        systems_visited = len(set(e.raw_event.get("StarSystem") for e in jump_events if "StarSystem" in e.raw_event))
        bodies_scanned = len(scan_events)
        distance_ly = sum(e.raw_event.get("JumpDist", 0) for e in jump_events)
        exploration_earnings = sum(e.raw_event.get("Reward", 0) for e in exploration_events)
        
        # Recent systems list
        recent_systems_list = list({e.raw_event.get("StarSystem") for e in jump_events if "StarSystem" in e.raw_event})[-10:]
        recent_systems = "\n".join(f"- {system}" for system in recent_systems_list) or "No recent jumps"
        
        # Scan summary
        scan_types = {}
        for event in scan_events:
            scan_type = event.raw_event.get("ScanType", "Unknown")
            scan_types[scan_type] = scan_types.get(scan_type, 0) + 1
        
        scan_summary = "\n".join(f"- {scan_type}: {count}" for scan_type, count in scan_types.items()) or "No scans performed"
        
        return {
            "systems_visited": systems_visited,
            "bodies_scanned": bodies_scanned,
            "distance_ly": distance_ly,
            "exploration_earnings": exploration_earnings,
            "recent_systems": recent_systems,
            "scan_summary": scan_summary
        }
    
    async def _build_trading_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for trading strategy."""
        trading_events = [e for e in recent_events if e.category == EventCategory.TRADING]
        buy_events = [e for e in trading_events if e.event_type == "MarketBuy"]
        sell_events = [e for e in trading_events if e.event_type == "MarketSell"]
        
        # Calculate trading metrics
        total_profit = sum(e.raw_event.get("Profit", 0) for e in sell_events)
        trade_count = len(buy_events) + len(sell_events)
        avg_profit_per_trade = total_profit / max(len(sell_events), 1)
        profit_per_hour = total_profit / max(time_range_hours, 1)
        
        # Get ship cargo capacity
        loadout_events = self.data_store.get_events_by_type("Loadout", limit=1)
        cargo_capacity = loadout_events[0].raw_event.get("CargoCapacity", 0) if loadout_events else 0
        
        # Best trades
        best_trades_list = sorted(sell_events, key=lambda x: x.raw_event.get("Profit", 0), reverse=True)[:5]
        best_trades = "\n".join(
            f"- {e.raw_event.get('Type', 'Unknown')}: {e.raw_event.get('Profit', 0):,} CR profit"
            for e in best_trades_list
        ) or "No profitable trades found"
        
        # Market opportunities (placeholder)
        market_opportunities = "Check local market data for current opportunities"
        
        return {
            "cargo_capacity": cargo_capacity,
            "total_profit": total_profit,
            "trade_count": trade_count,
            "avg_profit_per_trade": avg_profit_per_trade,
            "profit_per_hour": profit_per_hour,
            "best_trades": best_trades,
            "market_opportunities": market_opportunities
        }
    
    async def _build_combat_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for combat assessment."""
        combat_events = [e for e in recent_events if e.category == EventCategory.COMBAT]
        bounty_events = [e for e in combat_events if e.event_type == "Bounty"]
        bond_events = [e for e in combat_events if e.event_type == "FactionKillBond"]
        death_events = [e for e in combat_events if e.event_type == "Died"]
        
        # Calculate combat metrics
        bounties_earned = sum(e.raw_event.get("Reward", 0) for e in bounty_events)
        combat_bonds = sum(e.raw_event.get("Reward", 0) for e in bond_events)
        ships_destroyed = len(bounty_events) + len(bond_events)
        deaths = len(death_events)
        survival_rate = ((ships_destroyed - deaths) / max(ships_destroyed, 1)) * 100
        
        # Combat events summary
        combat_events_summary = f"Bounties: {len(bounty_events)}, Bonds: {len(bond_events)}, Deaths: {deaths}"
        
        # Ship loadout (placeholder)
        ship_loadout = "Check current ship loadout for detailed analysis"
        
        return {
            "bounties_earned": bounties_earned,
            "combat_bonds": combat_bonds,
            "ships_destroyed": ships_destroyed,
            "deaths": deaths,
            "survival_rate": survival_rate,
            "combat_events": combat_events_summary,
            "ship_loadout": ship_loadout
        }
    
    async def _build_mining_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for mining optimization."""
        mining_events = [e for e in recent_events if e.category == EventCategory.MINING]
        collection_events = [e for e in mining_events if e.event_type == "MaterialCollected"]
        
        # Calculate mining metrics
        materials_collected = len(collection_events)
        asteroids_mined = len([e for e in mining_events if e.event_type == "AsteroidCracked"])
        mining_earnings = sum(e.raw_event.get("MarketValue", 0) for e in collection_events)
        avg_value_per_ton = mining_earnings / max(materials_collected, 1)
        
        # Get cargo info
        cargo_events = self.data_store.get_events_by_type("Cargo", limit=1)
        cargo_data = cargo_events[0].raw_event if cargo_events else {}
        inventory = cargo_data.get("Inventory", [])
        cargo_used = sum(item.get("Count", 0) for item in inventory)
        
        # Get ship cargo capacity
        loadout_events = self.data_store.get_events_by_type("Loadout", limit=1)
        cargo_capacity = loadout_events[0].raw_event.get("CargoCapacity", 0) if loadout_events else 0
        
        # Materials summary
        material_types = {}
        for event in collection_events:
            material = event.raw_event.get("Name", "Unknown")
            material_types[material] = material_types.get(material, 0) + 1
        
        materials_summary = "\n".join(f"- {material}: {count}" for material, count in material_types.items()) or "No materials collected"
        
        # Mining equipment (placeholder)
        mining_equipment = "Check current ship modules for mining equipment analysis"
        
        return {
            "cargo_used": cargo_used,
            "cargo_capacity": cargo_capacity,
            "materials_collected": materials_collected,
            "asteroids_mined": asteroids_mined,
            "mining_earnings": mining_earnings,
            "avg_value_per_ton": avg_value_per_ton,
            "materials_summary": materials_summary,
            "mining_equipment": mining_equipment
        }
    
    async def _build_mission_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for mission guidance."""
        mission_events = [e for e in recent_events if e.category == EventCategory.MISSION]
        completed_events = [e for e in mission_events if e.event_type == "MissionCompleted"]
        failed_events = [e for e in mission_events if e.event_type == "MissionFailed"]
        accepted_events = [e for e in mission_events if e.event_type == "MissionAccepted"]
        
        # Calculate mission metrics
        missions_completed = len(completed_events)
        missions_failed = len(failed_events)
        total_missions = missions_completed + missions_failed
        success_rate = (missions_completed / max(total_missions, 1)) * 100
        total_rewards = sum(e.raw_event.get("Reward", 0) for e in completed_events)
        
        # Active missions
        active_missions = "Check mission panel for current active missions"
        
        # Mission types
        mission_types = {}
        for event in accepted_events:
            mission_type = event.raw_event.get("Name", "Unknown")
            mission_types[mission_type] = mission_types.get(mission_type, 0) + 1
        
        mission_types_summary = "\n".join(f"- {mission_type}: {count}" for mission_type, count in mission_types.items()) or "No missions accepted"
        
        # Faction standings (placeholder)
        faction_reputation = "Check faction panel for current standings"
        faction_standings = "Review faction relationships in galaxy map"
        
        return {
            "faction_reputation": faction_reputation,
            "active_missions": active_missions,
            "missions_completed": missions_completed,
            "missions_failed": missions_failed,
            "success_rate": success_rate,
            "total_rewards": total_rewards,
            "mission_types_summary": mission_types_summary,
            "faction_standings": faction_standings
        }
    
    async def _build_engineering_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for engineering progress."""
        engineering_events = [e for e in recent_events if e.category == EventCategory.ENGINEERING]
        
        # Engineering metrics (placeholders as Elite Dangerous engineering events vary)
        engineer_standings = "Check engineer progress in right panel"
        engineers_visited = len(set(e.raw_event.get("Engineer") for e in engineering_events if "Engineer" in e.raw_event))
        modifications_applied = len([e for e in engineering_events if e.event_type == "EngineerContribution"])
        materials_used = "Review recent material usage for engineering"
        ship_modifications = "Check current ship modifications in outfitting"
        material_inventory = "Review materials inventory in right panel"
        blueprint_progress = "Check blueprint progress with engineers"
        
        return {
            "engineer_standings": engineer_standings,
            "engineers_visited": engineers_visited,
            "modifications_applied": modifications_applied,
            "materials_used": materials_used,
            "ship_modifications": ship_modifications,
            "material_inventory": material_inventory,
            "blueprint_progress": blueprint_progress
        }
    
    async def _build_journey_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for journey review."""
        jump_events = [e for e in recent_events if e.event_type == "FSDJump"]
        dock_events = [e for e in recent_events if e.event_type == "Docked"]
        
        # Journey metrics
        total_jumps = len(jump_events)
        total_distance = sum(e.raw_event.get("JumpDist", 0) for e in jump_events)
        systems_visited = len(set(e.raw_event.get("StarSystem") for e in jump_events if "StarSystem" in e.raw_event))
        stations_visited = len(set(e.raw_event.get("StationName") for e in dock_events if "StationName" in e.raw_event))
        
        avg_jump_distance = total_distance / max(total_jumps, 1)
        
        # Get current ship jump range (placeholder)
        jump_range = 30.0  # Default assumption
        
        # Route analysis
        route_analysis = f"Traveled through {systems_visited} unique systems with {total_jumps} total jumps"
        
        # Notable events
        notable_events_list = []
        for event in recent_events:
            if event.category in [EventCategory.EXPLORATION, EventCategory.COMBAT]:
                notable_events_list.append(f"- {event.summary}")
        
        notable_events = "\n".join(notable_events_list[:5]) or "No notable events during journey"
        
        # Efficiency metrics (placeholders)
        fuel_efficiency = "Analyze fuel usage patterns"
        navigation_time = f"{time_range_hours} hours total navigation time"
        
        return {
            "jump_range": jump_range,
            "total_jumps": total_jumps,
            "total_distance": total_distance,
            "systems_visited": systems_visited,
            "stations_visited": stations_visited,
            "route_analysis": route_analysis,
            "notable_events": notable_events,
            "avg_jump_distance": avg_jump_distance,
            "fuel_efficiency": fuel_efficiency,
            "navigation_time": navigation_time
        }
    
    async def _build_performance_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for performance review."""
        # Calculate earnings and spending
        earnings_events = [e for e in recent_events if "Reward" in e.raw_event and e.raw_event["Reward"] > 0]
        spending_events = [e for e in recent_events if "Cost" in e.raw_event and e.raw_event["Cost"] > 0]
        
        credits_earned = sum(e.raw_event.get("Reward", 0) for e in earnings_events)
        credits_spent = sum(e.raw_event.get("Cost", 0) for e in spending_events)
        net_profit = credits_earned - credits_spent
        credits_per_hour = credits_earned / max(time_range_hours, 1)
        
        # Get current total assets (placeholder)
        total_assets = self.data_store.get_game_state().credits
        
        # Activity breakdown
        activity_counts = {}
        for event in recent_events:
            category = event.category.value
            activity_counts[category] = activity_counts.get(category, 0) + 1
        
        activity_breakdown = "\n".join(f"- {activity}: {count} events" for activity, count in activity_counts.items()) or "No recent activity"
        
        # Efficiency metrics
        efficiency_metrics = f"Credits per hour: {credits_per_hour:,.0f} CR/hr\nProfit margin: {(net_profit/max(credits_earned, 1)*100):.1f}%"
        
        # Progress indicators (placeholder)
        progress_indicators = "Review rank progress in right panel"
        achievements = "Check recent achievements and milestones"
        
        return {
            "total_assets": total_assets,
            "credits_earned": credits_earned,
            "credits_spent": credits_spent,
            "net_profit": net_profit,
            "credits_per_hour": credits_per_hour,
            "activity_breakdown": activity_breakdown,
            "efficiency_metrics": efficiency_metrics,
            "progress_indicators": progress_indicators,
            "achievements": achievements
        }
    
    async def _build_strategic_context(self, recent_events: List, time_range_hours: int) -> Dict[str, Any]:
        """Build context for strategic planning."""
        # Activity focus analysis
        activity_counts = {}
        for event in recent_events:
            category = event.category.value
            activity_counts[category] = activity_counts.get(category, 0) + 1
        
        top_activity = max(activity_counts, key=activity_counts.get) if activity_counts else "none"
        activity_focus = f"Primary focus: {top_activity} ({activity_counts.get(top_activity, 0)} events)"
        
        # Current objectives (placeholder)
        current_objectives = "Analyze mission log and personal goals"
        
        # Opportunities (placeholder)
        opportunities = "Review galaxy map for current opportunities"
        
        # Resource assessment
        game_state = self.data_store.get_game_state()
        resource_assessment = f"Credits: {game_state.credits:,} CR\nShip: {game_state.current_ship}\nLocation: {game_state.current_system}"
        
        # Market conditions (placeholder)
        market_conditions = "Check commodity markets and galactic average prices"
        
        # Risk factors
        risk_factors = "Consider current galaxy state and faction conflicts"
        
        return {
            "activity_focus": activity_focus,
            "current_objectives": current_objectives,
            "opportunities": opportunities,
            "resource_assessment": resource_assessment,
            "market_conditions": market_conditions,
            "risk_factors": risk_factors
        }
