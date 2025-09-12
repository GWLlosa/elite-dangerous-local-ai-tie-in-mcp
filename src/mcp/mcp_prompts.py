"""
MCP Prompts for Elite Dangerous Context-Aware AI Assistance

Provides intelligent prompts for common Elite Dangerous tasks with context-aware
content generation based on current game state and recent activities.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from ..utils.data_store import DataStore
from ..journal.events import EventCategory

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

Current Loa