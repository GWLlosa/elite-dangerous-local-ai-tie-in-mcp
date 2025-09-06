"""
Elite Dangerous Local AI Tie-In MCP Server

Main entry point for the Model Context Protocol server that provides integration
between Elite Dangerous, Claude Desktop, and EDCoPilot.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Configuration system (Milestone 2 - IMPLEMENTED)
from .utils.config import EliteConfig, load_config

# Future imports - will be implemented in later milestones
# from mcp.server.fastmcp import FastMCP, Context
# from .journal.monitor import JournalMonitor
# from .journal.parser import JournalParser
# from .journal.events import EventProcessor
# from .utils.data_store import EventStore
# from .edcopilot.generator import EDCoPilotGenerator

# Configure logging - will be enhanced with config settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('elite_mcp_server.log')
    ]
)

logger = logging.getLogger(__name__)


class EliteDangerousLocalAITieInMCPServer:
    """
    Main MCP server class for Elite Dangerous integration.
    
    This class will be fully implemented in subsequent milestones to provide:
    - Real-time journal monitoring
    - MCP tools, resources, and prompts
    - EDCoPilot custom file generation
    - AI-powered gameplay analysis
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize the MCP server with configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        logger.info("Initializing Elite Dangerous Local AI Tie-In MCP Server")
        
        # Load configuration (Milestone 2 - IMPLEMENTED)
        try:
            self.config = load_config(config_file)
            
            # Configure logging based on config
            if self.config.debug:
                logging.getLogger().setLevel(logging.DEBUG)
                logger.debug("Debug logging enabled")
            
            # Log configuration summary
            logger.info("Configuration loaded successfully:")
            for key, value in self.config.get_summary().items():
                logger.info(f"  {key}: {value}")
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
        
        # These will be implemented in Milestone 7 (MCP Framework)
        # self.mcp = FastMCP("Elite Dangerous Local AI Tie-In", version="1.0.0")
        # self.event_store = EventStore(max_events=self.config.max_recent_events)
        
        # These will be implemented in Milestone 4 (Journal Monitoring)
        # self.journal_monitor = None
        # self.journal_parser = None
        # self.event_processor = None
        
        # These will be implemented in Milestone 12 (EDCoPilot Generation)
        # self.edcopilot_generator = None
        
        logger.info("Server initialization completed successfully")
    
    def setup_mcp_handlers(self):
        """
        Register MCP tools, resources, and prompts.
        
        Will be implemented in Milestones 8-10.
        """
        logger.info("MCP handlers setup placeholder")
        # TODO: Implement in Milestone 8 (MCP Tools)
        # TODO: Implement in Milestone 9 (MCP Resources)  
        # TODO: Implement in Milestone 10 (MCP Prompts)
        pass
    
    async def start_monitoring(self):
        """
        Start journal monitoring in background.
        
        Will be implemented in Milestone 4.
        """
        logger.info("Journal monitoring startup placeholder")
        logger.info(f"Will monitor journal path: {self.config.journal_path}")
        logger.info(f"Check interval: {self.config.file_check_interval}s")
        # TODO: Implement in Milestone 4 (Journal Monitoring)
        pass
    
    async def run(self):
        """
        Run the MCP server.
        
        Will be fully implemented in Milestone 7.
        """
        logger.info("Starting Elite Dangerous Local AI Tie-In MCP Server")
        
        try:
            # Validate configuration paths
            logger.info("Validating configuration paths...")
            validation_results = self.config.validate_paths()
            
            # Check if critical paths are accessible
            journal_ok = validation_results['journal_path']['exists']
            edcopilot_ok = validation_results['edcopilot_path']['exists'] or validation_results['edcopilot_path']['writable']
            
            if not journal_ok:
                logger.warning("⚠️  Journal path not accessible - journal monitoring will be limited")
            
            if not edcopilot_ok:
                logger.warning("⚠️  EDCoPilot path not accessible - custom file generation will be disabled")
            
            # Start background monitoring
            await self.start_monitoring()
            
            # Setup MCP handlers
            self.setup_mcp_handlers()
            
            # This will run the actual MCP server in Milestone 7
            # await self.mcp.run()
            
            # Placeholder for now - demonstrate configuration is working
            logger.info("Server configuration validated and ready:")
            logger.info(f"  📁 Journal Path: {self.config.journal_path}")
            logger.info(f"  📁 EDCoPilot Path: {self.config.edcopilot_path}")
            logger.info(f"  🔧 Debug Mode: {self.config.debug}")
            logger.info(f"  📊 Max Events: {self.config.max_recent_events}")
            logger.info("Server would be running (placeholder implementation)")
            logger.info("Press Ctrl+C to stop")
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(self.config.file_check_interval)
                
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources on shutdown."""
        logger.info("Cleaning up server resources")
        # TODO: Implement cleanup in later milestones
        pass


def main():
    """Main entry point for the MCP server."""
    import argparse
    
    # Command line argument parsing
    parser = argparse.ArgumentParser(
        description="Elite Dangerous Local AI Tie-In MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  ELITE_JOURNAL_PATH       Path to Elite Dangerous journal directory
  ELITE_EDCOPILOT_PATH     Path to EDCoPilot custom files directory  
  ELITE_DEBUG              Enable debug logging (true/false)
  ELITE_MAX_RECENT_EVENTS  Maximum recent events to store

Examples:
  python -m src.server
  python -m src.server --config config.json
  python -m src.server --create-sample-config
  ELITE_DEBUG=true python -m src.server
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--create-sample-config',
        type=Path,
        help='Create a sample configuration file and exit'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate configuration and exit'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Handle special actions
    if args.create_sample_config:
        from .utils.config import create_sample_config
        try:
            if create_sample_config(args.create_sample_config):
                print(f"✅ Sample configuration created: {args.create_sample_config}")
                return
            else:
                print(f"❌ Failed to create sample configuration")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error creating sample configuration: {e}")
            sys.exit(1)
    
    if args.validate_config:
        try:
            config = load_config(args.config)
            print("✅ Configuration validation successful:")
            for key, value in config.get_summary().items():
                print(f"  {key}: {value}")
            
            validation_results = config.validate_paths()
            for path_name, result in validation_results.items():
                status = "✅" if result['exists'] else "⚠️"
                print(f"  {status} {path_name}: {result['message']}")
            return
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            sys.exit(1)
    
    # Override debug setting if specified
    if args.debug:
        import os
        os.environ['ELITE_DEBUG'] = 'true'
    
    # Run the server
    try:
        server = EliteDangerousLocalAITieInMCPServer(config_file=args.config)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()