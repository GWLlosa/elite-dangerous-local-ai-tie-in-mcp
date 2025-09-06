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

# Journal system (Milestone 3 - IMPLEMENTED)  
from .journal.parser import JournalParser

# Future imports - will be implemented in later milestones
# from mcp.server.fastmcp import FastMCP, Context
# from .journal.monitor import JournalMonitor
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
        
        # Initialize journal parser (Milestone 3 - IMPLEMENTED)
        try:
            self.journal_parser = JournalParser(self.config.journal_path)
            logger.info("Journal parser initialized successfully")
            
            # Get journal summary
            journal_summary = self.journal_parser.get_journal_summary()
            logger.info("Journal system status:")
            logger.info(f"  📁 Total files: {journal_summary['total_files']}")
            logger.info(f"  📄 Active files: {journal_summary['active_files']}")
            logger.info(f"  🗄️  Backup files: {journal_summary['backup_files']}")
            logger.info(f"  💾 Total size: {journal_summary['total_size_mb']} MB")
            
            if journal_summary['latest_file']:
                latest_file = Path(journal_summary['latest_file'])
                logger.info(f"  📊 Latest file: {latest_file.name}")
                
                # Try to get file header for version info
                header = self.journal_parser.get_file_header(latest_file)
                if header:
                    version = header.get('gameversion', 'unknown')
                    build = header.get('build', 'unknown')
                    logger.info(f"  🎮 Game version: {version} ({build})")
            
        except Exception as e:
            logger.error(f"Failed to initialize journal parser: {e}")
            # Don't fail completely, journal parsing is optional
            self.journal_parser = None
        
        # These will be implemented in Milestone 7 (MCP Framework)
        # self.mcp = FastMCP("Elite Dangerous Local AI Tie-In", version="1.0.0")
        # self.event_store = EventStore(max_events=self.config.max_recent_events)
        
        # These will be implemented in Milestone 4 (Journal Monitoring)
        # self.journal_monitor = None
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
        
        # Demonstrate journal parser functionality (Milestone 3 - IMPLEMENTED)
        if self.journal_parser:
            await self.demonstrate_journal_functionality()
        
        # TODO: Implement real-time monitoring in Milestone 4
        pass
    
    async def demonstrate_journal_functionality(self):
        """
        Demonstrate journal parser functionality with current data.
        
        This shows the journal system working with available data.
        """
        logger.info("🔍 Demonstrating journal parser functionality...")
        
        try:
            # Get latest active journal
            latest_journal = self.journal_parser.get_active_journal()
            if latest_journal:
                logger.info(f"📖 Reading latest journal: {latest_journal.name}")
                
                # Read some recent entries
                entries = self.journal_parser.read_journal_file_complete(latest_journal)
                if entries:
                    logger.info(f"📊 Found {len(entries)} total entries")
                    
                    # Show first few entries
                    for i, entry in enumerate(entries[:3]):
                        timestamp = entry.get('timestamp', 'unknown')
                        event = entry.get('event', 'unknown')
                        logger.info(f"  {i+1}. {timestamp} - {event}")
                    
                    if len(entries) > 3:
                        logger.info(f"  ... and {len(entries) - 3} more entries")
                    
                    # Show event type summary
                    event_types = {}
                    for entry in entries:
                        event_type = entry.get('event', 'unknown')
                        event_types[event_type] = event_types.get(event_type, 0) + 1
                    
                    logger.info("📈 Event type summary:")
                    for event_type, count in sorted(event_types.items()):
                        logger.info(f"  {event_type}: {count}")
                        
                else:
                    logger.info("📭 No entries found in latest journal")
            else:
                logger.info("📂 No active journal files found")
                
                # Check for any journal files
                all_files = self.journal_parser.find_journal_files()
                if all_files:
                    logger.info(f"Found {len(all_files)} journal files (all may be backups)")
                    for file_path in all_files[-3:]:  # Show last 3
                        logger.info(f"  📄 {file_path.name}")
                        
        except Exception as e:
            logger.error(f"Error demonstrating journal functionality: {e}")
    
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
            
            # Demonstrate current functionality
            logger.info("🎉 Server functionality demonstration:")
            logger.info(f"  📁 Journal Path: {self.config.journal_path}")
            logger.info(f"  📁 EDCoPilot Path: {self.config.edcopilot_path}")
            logger.info(f"  🔧 Debug Mode: {self.config.debug}")
            logger.info(f"  📊 Max Events: {self.config.max_recent_events}")
            
            if self.journal_parser:
                summary = self.journal_parser.get_journal_summary()
                logger.info(f"  📊 Journal Files: {summary['total_files']} ({summary['total_size_mb']} MB)")
            
            logger.info("🚀 Server is ready for MCP integration (Milestone 7)")
            logger.info("⏰ Journal monitoring ready for real-time implementation (Milestone 4)")
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
  python -m src.server --test-journal-parser
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
        '--test-journal-parser',
        action='store_true',
        help='Test journal parser functionality and exit'
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
    
    if args.test_journal_parser:
        try:
            print("🧪 Testing journal parser functionality...")
            config = load_config(args.config)
            parser = JournalParser(config.journal_path)
            
            summary = parser.get_journal_summary()
            print(f"📊 Journal Summary:")
            print(f"  Total files: {summary['total_files']}")
            print(f"  Active files: {summary['active_files']}")
            print(f"  Backup files: {summary['backup_files']}")
            print(f"  Total size: {summary['total_size_mb']} MB")
            
            if summary['latest_file']:
                print(f"  Latest file: {Path(summary['latest_file']).name}")
            
            # Test parsing latest file
            latest = parser.get_latest_journal()
            if latest:
                entries = parser.read_journal_file_complete(latest)
                print(f"📖 Parsed {len(entries)} entries from {latest.name}")
                
                if entries:
                    print("📋 Sample entries:")
                    for entry in entries[:3]:
                        timestamp = entry.get('timestamp', 'unknown')
                        event = entry.get('event', 'unknown')
                        print(f"  {timestamp} - {event}")
            
            print("✅ Journal parser test completed successfully")
            return
            
        except Exception as e:
            print(f"❌ Journal parser test failed: {e}")
            import traceback
            traceback.print_exc()
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