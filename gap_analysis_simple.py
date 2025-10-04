#!/usr/bin/env python3
"""
Simple gap analysis: Compare journal files with what we can extract.
This analyzes raw journal data without needing the MCP server running.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Any

JOURNAL_PATH = Path(r"C:\Users\gwllo\Saved Games\Frontier Developments\Elite Dangerous")
GAP_REPORTS_DIR = Path("gap-reports")
GAP_REPORTS_DIR.mkdir(exist_ok=True)

def parse_journal_filename_date(filename: str) -> datetime:
    """Parse date from journal filename format: Journal.YYYY-MM-DDTHHMMSS.XX.log"""
    pattern = r'Journal\.(\d{4})-(\d{2})-(\d{2})T(\d{2})(\d{2})(\d{2})\..*\.log'
    match = re.match(pattern, filename)
    if match:
        year, month, day, hour, minute, second = map(int, match.groups())
        return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    return None

def analyze_journal_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single journal file."""
    events_by_type = defaultdict(int)
    event_fields = defaultdict(set)
    total_events = 0
    parsing_errors = []
    sample_events = defaultdict(list)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                    event_type = event.get('event', 'Unknown')

                    events_by_type[event_type] += 1
                    event_fields[event_type].update(event.keys())
                    total_events += 1

                    # Keep sample events (first 2 of each type)
                    if len(sample_events[event_type]) < 2:
                        sample_events[event_type].append(event)

                except json.JSONDecodeError as e:
                    parsing_errors.append({
                        'line': line_num,
                        'error': str(e),
                        'content': line[:100]
                    })
    except Exception as e:
        parsing_errors.append({
            'line': 0,
            'error': f"File error: {e}",
            'content': ''
        })

    return {
        'file': file_path.name,
        'events_by_type': dict(events_by_type),
        'event_fields': {k: sorted(v) for k, v in event_fields.items()},
        'total_events': total_events,
        'parsing_errors': parsing_errors,
        'sample_events': {k: v for k, v in sample_events.items()}
    }

def analyze_recent_sessions(days_back: int = 7):
    """Analyze the most recent gaming sessions."""
    print(f"[*] Analyzing journal files from last {days_back} days...")

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days_back)

    journal_files = list(JOURNAL_PATH.glob("Journal.*.log"))
    recent_files = []

    for jf in journal_files:
        file_date = parse_journal_filename_date(jf.name)
        if file_date and file_date >= cutoff:
            recent_files.append((file_date, jf))

    recent_files.sort(reverse=True)

    print(f"[*] Found {len(recent_files)} recent journal files")

    all_event_types = set()
    all_event_fields = defaultdict(set)
    total_events_analyzed = 0
    files_analyzed = []
    all_parsing_errors = []

    # Analyze each file
    for file_date, file_path in recent_files[:20]:  # Analyze last 20 files
        print(f"  Analyzing {file_path.name}...")
        analysis = analyze_journal_file(file_path)

        all_event_types.update(analysis['events_by_type'].keys())
        for event_type, fields in analysis['event_fields'].items():
            all_event_fields[event_type].update(fields)

        total_events_analyzed += analysis['total_events']
        files_analyzed.append(analysis)
        all_parsing_errors.extend([{**err, 'file': file_path.name} for err in analysis['parsing_errors']])

    return {
        'files_analyzed': len(files_analyzed),
        'total_events': total_events_analyzed,
        'unique_event_types': sorted(all_event_types),
        'event_type_count': len(all_event_types),
        'event_fields': {k: sorted(v) for k, v in all_event_fields.items()},
        'parsing_errors': all_parsing_errors,
        'detailed_files': files_analyzed
    }

def generate_gap_report_from_analysis(analysis: Dict[str, Any]):
    """Generate comprehensive gap reports based on analysis."""

    # Report 1: Event type coverage
    report_path = GAP_REPORTS_DIR / "gap_report_event_type_coverage.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Gap Report: Event Type Coverage Analysis

## Summary
🔴 **Severity**: HIGH

**Issue Type**: event_coverage_analysis

**Date**: {datetime.now().isoformat()}

## Description
Comprehensive analysis of all event types present in Elite Dangerous journal files over the last 7 days.

## Statistics
- **Files Analyzed**: {analysis['files_analyzed']}
- **Total Events**: {analysis['total_events']:,}
- **Unique Event Types**: {analysis['event_type_count']}

## All Event Types Found
The following {analysis['event_type_count']} event types were found in the journal files:

""")
        for event_type in analysis['unique_event_types']:
            f.write(f"- `{event_type}`\n")

        f.write(f"""
## Event Fields Analysis

This section documents all fields found for each event type. This can be used to verify
that the MCP is capturing all available data from each event.

""")

        for event_type in sorted(analysis['event_fields'].keys()):
            fields = analysis['event_fields'][event_type]
            f.write(f"""
### {event_type}
**Fields** ({len(fields)}): {', '.join(f'`{f}`' for f in fields)}

""")

    print(f"[+] Created: gap_report_event_type_coverage.md")

    # Report 2: Parsing errors
    if analysis['parsing_errors']:
        report_path = GAP_REPORTS_DIR / "gap_report_parsing_errors.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Gap Report: Journal Parsing Errors

## Summary
MEDIUM **Severity**: MEDIUM

**Issue Type**: parsing_errors

**Date**: {datetime.now().isoformat()}

## Description
{len(analysis['parsing_errors'])} parsing errors were encountered while reading journal files.

## Error Details
""")
            for i, error in enumerate(analysis['parsing_errors'][:50], 1):
                f.write(f"""
### Error {i}
- **File**: {error.get('file', 'Unknown')}
- **Line**: {error.get('line', 'N/A')}
- **Error**: {error.get('error', 'Unknown')}
- **Content**: `{error.get('content', '')}`

""")
        print(f"[+] Created: gap_report_parsing_errors.md")

    # Report 3: Detailed file analysis
    report_path = GAP_REPORTS_DIR / "gap_report_detailed_analysis.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Gap Report: Detailed File Analysis

## Summary
INFO **Purpose**: Detailed breakdown of event distribution

**Date**: {datetime.now().isoformat()}

## Per-File Analysis

""")
        for file_info in analysis['detailed_files'][:10]:
            f.write(f"""
### {file_info['file']}
- **Total Events**: {file_info['total_events']}
- **Event Types**: {len(file_info['events_by_type'])}

#### Event Distribution
""")
            sorted_events = sorted(file_info['events_by_type'].items(), key=lambda x: x[1], reverse=True)
            for event_type, count in sorted_events[:20]:
                f.write(f"- {event_type}: {count}\n")

    print(f"[+] Created: gap_report_detailed_analysis.md")

    # Report 4: Mining-specific analysis
    mining_events = {}
    for file_info in analysis['detailed_files']:
        for event_type in file_info['sample_events']:
            if any(keyword in event_type.lower() for keyword in ['mining', 'mined', 'refined', 'asteroid', 'prospect']):
                if event_type not in mining_events:
                    mining_events[event_type] = []
                mining_events[event_type].extend(file_info['sample_events'][event_type])

    if mining_events:
        report_path = GAP_REPORTS_DIR / "gap_report_mining_events_analysis.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Gap Report: Mining Events Analysis

## Summary
MEDIUM **Severity**: MEDIUM

**Issue Type**: mining_events_verification

**Date**: {datetime.now().isoformat()}

## Description
Analysis of all mining-related events found in journal files to verify the fix for GitHub issue #8.

## Mining Event Types Found
""")
            for event_type in sorted(mining_events.keys()):
                samples = mining_events[event_type]
                f.write(f"""
### {event_type}
**Sample Count**: {len(samples)}

**Sample Event**:
```json
{json.dumps(samples[0], indent=2)}
```

**Fields**: {', '.join(f'`{k}`' for k in samples[0].keys())}

""")
        print(f"[+] Created: gap_report_mining_events_analysis.md")

def main():
    """Run the gap analysis."""
    print("=" * 70)
    print("COMPREHENSIVE GAP ANALYSIS")
    print("=" * 70)
    print()

    if not JOURNAL_PATH.exists():
        print(f"[!] Journal path not found: {JOURNAL_PATH}")
        return

    print(f"[*] Journal Path: {JOURNAL_PATH}")
    print(f"[*] Reports will be saved to: {GAP_REPORTS_DIR}")
    print()

    # Analyze recent sessions
    analysis = analyze_recent_sessions(days_back=7)

    print()
    print("=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"[+] Files analyzed: {analysis['files_analyzed']}")
    print(f"[+] Total events: {analysis['total_events']:,}")
    print(f"[+] Unique event types: {analysis['event_type_count']}")
    if analysis['parsing_errors']:
        print(f"[!] Parsing errors: {len(analysis['parsing_errors'])}")
    print()

    # Generate reports
    print("=" * 70)
    print("GENERATING GAP REPORTS")
    print("=" * 70)
    generate_gap_report_from_analysis(analysis)

    print()
    print("=" * 70)
    print("[+] GAP ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nCheck the '{GAP_REPORTS_DIR}' folder for detailed findings.")

if __name__ == "__main__":
    main()
