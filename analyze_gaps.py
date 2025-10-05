#!/usr/bin/env python3
"""
Comprehensive gap analysis script to compare MCP data with raw journal files.
This script systematically queries the MCP and compares it with physical journal data
to identify missing fields, events, or data inconsistencies.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Set
import re

# Add src to path
sys.path.append('src')

from utils.config import EliteConfig
from utils.data_store import get_data_store
from elite_mcp.mcp_tools import MCPTools
from elite_mcp.mcp_resources import MCPResources

class GapAnalyzer:
    def __init__(self):
        self.config = EliteConfig()
        self.data_store = get_data_store()
        self.mcp_tools = MCPTools(self.data_store)
        self.mcp_resources = MCPResources(self.data_store)
        self.journal_path = Path(self.config.journal_path)
        self.gap_reports_dir = Path("gap-reports")
        self.gap_reports_dir.mkdir(exist_ok=True)

    async def analyze_timeframe(self, start_date: str, end_date: str, timeframe_name: str):
        """Analyze a specific timeframe for gaps."""
        print(f"\n=== Analyzing {timeframe_name} ({start_date} to {end_date}) ===")

        # Convert to datetime objects
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        # Get journal files for this timeframe
        journal_files = self.get_journal_files_for_timeframe(start_dt, end_dt)
        print(f"Found {len(journal_files)} journal files for {timeframe_name}")

        if not journal_files:
            print(f"No journal files found for {timeframe_name}")
            return

        # Analyze journal data
        journal_data = self.analyze_journal_files(journal_files)

        # Query MCP for the same timeframe
        hours_duration = int((end_dt - start_dt).total_seconds() / 3600)
        mcp_data = await self.query_mcp_data(hours_duration)

        # Compare and identify gaps
        gaps = self.compare_data(journal_data, mcp_data, timeframe_name)

        # Generate gap reports
        await self.generate_gap_reports(gaps, timeframe_name, start_date, end_date)

    def get_journal_files_for_timeframe(self, start_dt: datetime, end_dt: datetime) -> List[Path]:
        """Get journal files that fall within the specified timeframe."""
        journal_files = []

        # Pattern for journal files: Journal.YYYY-MM-DDTHHMMSS.XX.log
        journal_pattern = re.compile(r'Journal\.(\d{4}-\d{2}-\d{2}T\d{6})\..*\.log')

        for file in self.journal_path.glob("Journal.*.log"):
            match = journal_pattern.match(file.name)
            if match:
                # Parse the date from filename
                date_str = match.group(1)
                try:
                    # Convert YYYYMMDDTHHMMSS to YYYY-MM-DDTHH:MM:SS
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T{date_str[9:11]}:{date_str[11:13]}:{date_str[13:15]}"
                    file_dt = datetime.fromisoformat(formatted_date).replace(tzinfo=timezone.utc)

                    if start_dt <= file_dt <= end_dt:
                        journal_files.append(file)
                except Exception as e:
                    print(f"Error parsing date from {file.name}: {e}")

        return sorted(journal_files)

    def analyze_journal_files(self, journal_files: List[Path]) -> Dict[str, Any]:
        """Analyze raw journal files to extract event information."""
        events_by_type = {}
        total_events = 0
        event_fields = {}
        parsing_errors = []

        for journal_file in journal_files:
            try:
                with open(journal_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            event = json.loads(line)
                            event_type = event.get('event', 'Unknown')

                            # Count events by type
                            if event_type not in events_by_type:
                                events_by_type[event_type] = 0
                            events_by_type[event_type] += 1
                            total_events += 1

                            # Track fields for each event type
                            if event_type not in event_fields:
                                event_fields[event_type] = set()
                            event_fields[event_type].update(event.keys())

                        except json.JSONDecodeError as e:
                            parsing_errors.append({
                                'file': journal_file.name,
                                'line': line_num,
                                'error': str(e),
                                'content': line[:100] + '...' if len(line) > 100 else line
                            })

            except Exception as e:
                parsing_errors.append({
                    'file': journal_file.name,
                    'line': 0,
                    'error': f"File read error: {e}",
                    'content': ''
                })

        return {
            'events_by_type': events_by_type,
            'total_events': total_events,
            'event_fields': {k: list(v) for k, v in event_fields.items()},
            'parsing_errors': parsing_errors,
            'files_analyzed': [f.name for f in journal_files]
        }

    async def query_mcp_data(self, hours: int) -> Dict[str, Any]:
        """Query MCP for various activity summaries and resource data."""
        mcp_data = {}

        try:
            # Activity summaries
            activities = ['exploration', 'trading', 'combat', 'mining', 'missions', 'engineering']
            mcp_data['activities'] = {}

            for activity in activities:
                try:
                    summary = await self.mcp_tools.get_activity_summary(activity, hours)
                    mcp_data['activities'][activity] = summary
                except Exception as e:
                    mcp_data['activities'][activity] = {'error': str(e)}

            # Journey summary
            try:
                mcp_data['journey'] = await self.mcp_tools.get_journey_summary(hours)
            except Exception as e:
                mcp_data['journey'] = {'error': str(e)}

            # System status
            try:
                mcp_data['status'] = await self.mcp_resources.get_resource("elite://status/current")
            except Exception as e:
                mcp_data['status'] = {'error': str(e)}

            # Recent events from data store
            try:
                recent_events = self.data_store.get_recent_events(minutes=hours*60)
                mcp_data['recent_events'] = {
                    'count': len(recent_events),
                    'event_types': list(set(e.event_type for e in recent_events)),
                    'categories': list(set(e.category.value for e in recent_events))
                }
            except Exception as e:
                mcp_data['recent_events'] = {'error': str(e)}

        except Exception as e:
            mcp_data['query_error'] = str(e)

        return mcp_data

    def compare_data(self, journal_data: Dict, mcp_data: Dict, timeframe_name: str) -> List[Dict]:
        """Compare journal data with MCP data to identify gaps."""
        gaps = []

        # Compare event counts
        journal_events = journal_data['events_by_type']
        mcp_events = mcp_data.get('recent_events', {})

        if 'error' not in mcp_events:
            mcp_event_types = set(mcp_events.get('event_types', []))
            journal_event_types = set(journal_events.keys())

            # Events in journal but not in MCP
            missing_in_mcp = journal_event_types - mcp_event_types
            if missing_in_mcp:
                gaps.append({
                    'type': 'missing_event_types',
                    'severity': 'high',
                    'description': f"Event types present in journal but missing from MCP data",
                    'details': {
                        'missing_events': list(missing_in_mcp),
                        'count': len(missing_in_mcp),
                        'timeframe': timeframe_name
                    }
                })

            # Compare total event counts
            journal_total = journal_data['total_events']
            mcp_total = mcp_events.get('count', 0)

            if abs(journal_total - mcp_total) > 10:  # Allow small differences
                gaps.append({
                    'type': 'event_count_mismatch',
                    'severity': 'medium',
                    'description': f"Significant difference in total event counts",
                    'details': {
                        'journal_count': journal_total,
                        'mcp_count': mcp_total,
                        'difference': abs(journal_total - mcp_total),
                        'timeframe': timeframe_name
                    }
                })
        else:
            gaps.append({
                'type': 'mcp_query_failure',
                'severity': 'high',
                'description': f"Failed to query MCP recent events",
                'details': {
                    'error': mcp_events.get('error', 'Unknown error'),
                    'timeframe': timeframe_name
                }
            })

        # Check for activity summary failures
        activities = mcp_data.get('activities', {})
        for activity, data in activities.items():
            if 'error' in data:
                gaps.append({
                    'type': 'activity_summary_failure',
                    'severity': 'medium',
                    'description': f"Failed to generate {activity} activity summary",
                    'details': {
                        'activity': activity,
                        'error': data['error'],
                        'timeframe': timeframe_name
                    }
                })

        # Check for parsing errors in journal files
        if journal_data['parsing_errors']:
            gaps.append({
                'type': 'journal_parsing_errors',
                'severity': 'low',
                'description': f"Errors parsing journal files",
                'details': {
                    'error_count': len(journal_data['parsing_errors']),
                    'errors': journal_data['parsing_errors'][:5],  # First 5 errors
                    'timeframe': timeframe_name
                }
            })

        return gaps

    async def generate_gap_reports(self, gaps: List[Dict], timeframe_name: str, start_date: str, end_date: str):
        """Generate detailed bug reports for identified gaps."""
        if not gaps:
            print(f"✅ No gaps found for {timeframe_name}")
            return

        print(f"⚠️  Found {len(gaps)} gaps for {timeframe_name}")

        for i, gap in enumerate(gaps, 1):
            report_filename = f"gap_report_{timeframe_name}_{gap['type']}_{i}.md"
            report_path = self.gap_reports_dir / report_filename

            report_content = self.generate_bug_report(gap, timeframe_name, start_date, end_date)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            print(f"📝 Created gap report: {report_filename}")

    def generate_bug_report(self, gap: Dict, timeframe_name: str, start_date: str, end_date: str) -> str:
        """Generate a formal bug report for a gap."""
        severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}

        report = f"""# Bug Report: {gap['description']}

## Summary
{severity_emoji.get(gap['severity'], '⚪')} **Severity**: {gap['severity'].upper()}

**Issue Type**: {gap['type']}

**Timeframe Analyzed**: {timeframe_name} ({start_date} to {end_date})

## Description
{gap['description']}

## Details
"""

        # Add detailed information
        details = gap.get('details', {})
        for key, value in details.items():
            if isinstance(value, (list, dict)):
                report += f"- **{key.replace('_', ' ').title()}**:\n```json\n{json.dumps(value, indent=2)}\n```\n\n"
            else:
                report += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        report += f"""
## Reproduction Steps
1. Query MCP for data in timeframe: {start_date} to {end_date}
2. Compare with raw journal files for the same period
3. Observe the reported discrepancy

## Expected Behavior
The MCP should accurately reflect all data present in the Elite Dangerous journal files.

## Actual Behavior
{gap['description']}

## Environment
- Analysis Date: {datetime.now().isoformat()}
- Timeframe: {timeframe_name}
- MCP Version: Current development version

## Additional Context
This issue was identified during a comprehensive gap analysis comparing MCP data with raw Elite Dangerous journal files.

## Priority
{gap['severity'].upper()} - Should be addressed {'immediately' if gap['severity'] == 'high' else 'in upcoming sprint' if gap['severity'] == 'medium' else 'when time permits'}.
"""

        return report

async def main():
    """Main analysis function."""
    analyzer = GapAnalyzer()

    print("🔍 Starting comprehensive MCP gap analysis...")
    print(f"📁 Journal path: {analyzer.journal_path}")
    print(f"📊 Gap reports will be saved to: {analyzer.gap_reports_dir}")

    # Define timeframes for analysis (going back a month)
    now = datetime.now(timezone.utc)
    timeframes = [
        # Last 24 hours
        {
            'name': 'last_24h',
            'start': (now - timedelta(days=1)).isoformat(),
            'end': now.isoformat()
        },
        # Last 3 days
        {
            'name': 'last_3d',
            'start': (now - timedelta(days=3)).isoformat(),
            'end': now.isoformat()
        },
        # Last week
        {
            'name': 'last_week',
            'start': (now - timedelta(days=7)).isoformat(),
            'end': now.isoformat()
        },
        # Last 2 weeks
        {
            'name': 'last_2w',
            'start': (now - timedelta(days=14)).isoformat(),
            'end': now.isoformat()
        },
        # Last month
        {
            'name': 'last_month',
            'start': (now - timedelta(days=30)).isoformat(),
            'end': now.isoformat()
        }
    ]

    for timeframe in timeframes:
        try:
            await analyzer.analyze_timeframe(
                timeframe['start'],
                timeframe['end'],
                timeframe['name']
            )
        except Exception as e:
            print(f"❌ Error analyzing {timeframe['name']}: {e}")
            import traceback
            traceback.print_exc()

    print("\n✅ Gap analysis complete! Check the gap-reports folder for detailed findings.")

if __name__ == "__main__":
    asyncio.run(main())