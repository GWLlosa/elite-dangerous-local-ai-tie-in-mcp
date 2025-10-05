## Feature Request: Historical Data Search with Date Range Support

### Problem Statement

Currently, the MCP server lacks robust support for searching historical journal data using flexible date ranges. Users (both human and LLM) cannot easily query events like "all events from last month to two weeks ago" or "exploration data from January 1-15, 2025."

This limitation makes it difficult to:
- Analyze long-term gameplay patterns
- Compare performance across different time periods
- Generate historical reports for specific date ranges
- Track progression over weeks or months

### Current Limitations

**Existing Tools**:
- `get_recent_events(minutes=N)` - Only supports relative time from "now"
- `search_events(...)` - Limited time filtering capabilities
- Resources like `elite://journal/recent?minutes=N` - Only recent events

**Issues**:
1. **No absolute date support** - Cannot specify "January 15, 2025"
2. **No date range queries** - Cannot specify "from X to Y"
3. **Limited lookback** - Practical limit based on current data store retention
4. **No natural language date parsing** - LLMs must calculate relative minutes/hours

### Proposed Solution

Add a new MCP tool: `search_historical_events` with flexible date range support.

#### Tool Signature

```python
async def search_historical_events(
    start_date: Optional[str] = None,  # ISO format or relative: "2025-01-15", "last month", "30 days ago"
    end_date: Optional[str] = None,    # ISO format or relative: "2025-01-31", "two weeks ago", "yesterday"
    event_types: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    system_name: Optional[str] = None,
    limit: Optional[int] = 1000,
    sort_order: str = "desc"  # "asc" or "desc"
) -> Dict[str, Any]:
    """
    Search historical journal events with flexible date range support.

    Args:
        start_date: Start of date range (inclusive). Supports:
                   - ISO format: "2025-01-15" or "2025-01-15T10:30:00Z"
                   - Relative: "last month", "30 days ago", "2 weeks ago"
                   - If omitted, searches from beginning of available data
        end_date: End of date range (inclusive). Supports same formats as start_date.
                 If omitted, searches up to present time.
        event_types: Filter by specific event types (e.g., ["FSDJump", "Scan"])
        categories: Filter by event categories (e.g., ["exploration", "combat"])
        system_name: Filter by system name
        limit: Maximum number of events to return
        sort_order: "asc" (oldest first) or "desc" (newest first)

    Returns:
        {
            "events": [...],  # Matching events
            "total_count": int,  # Total matching events
            "date_range": {
                "start": "2025-01-15T00:00:00Z",
                "end": "2025-01-31T23:59:59Z"
            },
            "truncated": bool  # Whether results were limited
        }
    """
```

#### Example Queries from LLM Perspective

**Natural Language Request → Tool Call**:

1. **"Show me all events from last month to two weeks ago"**
   ```python
   await search_historical_events(
       start_date="last month",
       end_date="two weeks ago"
   )
   ```

2. **"Find all exploration scans in January 2025"**
   ```python
   await search_historical_events(
       start_date="2025-01-01",
       end_date="2025-01-31",
       categories=["exploration"],
       event_types=["Scan"]
   )
   ```

3. **"What systems did I visit between Christmas and New Year?"**
   ```python
   await search_historical_events(
       start_date="2024-12-25",
       end_date="2025-01-01",
       event_types=["FSDJump", "Location"]
   )
   ```

4. **"Show combat activity from 3 weeks ago to 1 week ago"**
   ```python
   await search_historical_events(
       start_date="3 weeks ago",
       end_date="1 week ago",
       categories=["combat"]
   )
   ```

5. **"All mining events on January 15th"**
   ```python
   await search_historical_events(
       start_date="2025-01-15",
       end_date="2025-01-15",
       categories=["mining"]
   )
   ```

### Implementation Details

#### Date Parsing

Support multiple date formats:

**Absolute Dates**:
- ISO 8601: `"2025-01-15"`, `"2025-01-15T10:30:00Z"`
- Date only: `"2025-01-15"` (defaults to start/end of day)

**Relative Dates** (parsed at query time):
- `"today"`, `"yesterday"`, `"tomorrow"`
- `"last week"`, `"last month"`, `"last year"`
- `"N days ago"`, `"N weeks ago"`, `"N months ago"`
- `"start of week"`, `"end of month"`, etc.

**Date Parser Implementation**:
```python
from dateutil.parser import parse as parse_iso
from datetime import datetime, timedelta, timezone
import re

def parse_date(date_str: str, is_start: bool = True) -> datetime:
    """
    Parse flexible date string into datetime object.

    Args:
        date_str: Date string to parse
        is_start: If True, default to start of day; if False, end of day
    """
    if not date_str:
        return None

    date_str = date_str.lower().strip()
    now = datetime.now(timezone.utc)

    # Relative dates
    if date_str == "today":
        base = now
    elif date_str == "yesterday":
        base = now - timedelta(days=1)
    elif date_str == "last week":
        base = now - timedelta(weeks=1)
    elif date_str == "last month":
        base = now - timedelta(days=30)
    elif (match := re.match(r"(\d+)\s+(day|week|month)s?\s+ago", date_str)):
        count, unit = int(match.group(1)), match.group(2)
        delta = {
            "day": timedelta(days=count),
            "week": timedelta(weeks=count),
            "month": timedelta(days=count * 30)
        }[unit]
        base = now - delta
    else:
        # Try ISO parse
        base = parse_iso(date_str)
        if base.tzinfo is None:
            base = base.replace(tzinfo=timezone.utc)
        return base

    # For relative dates, set to start/end of day
    if is_start:
        return base.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return base.replace(hour=23, minute=59, second=59, microsecond=999999)
```

#### Data Store Enhancement

The `DataStore` may need enhancement to support efficient historical queries:

```python
class DataStore:
    def query_historical_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[Set[str]] = None,
        categories: Optional[Set[EventCategory]] = None,
        system_name: Optional[str] = None,
        limit: int = 1000,
        sort_order: str = "desc"
    ) -> List[ProcessedEvent]:
        """Query events with date range support."""
        # Implementation filters events by timestamp range
        # May need to load additional historical data if not in memory
```

**Considerations**:
1. **Memory limits**: Current data store holds recent events in memory
2. **Historical data loading**: May need to re-parse old journal files on demand
3. **Caching**: Cache historical query results for performance
4. **Pagination**: Support pagination for large result sets

### Alternative/Complementary Approaches

#### 1. Extend Existing `search_events` Tool

Add date range parameters to existing tool:
```python
async def search_events(
    # ... existing parameters ...
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
)
```

**Pros**: No new tool needed
**Cons**: May complicate existing tool signature

#### 2. Add Historical Resource Endpoints

New MCP resources:
```
elite://history/events?start=2025-01-01&end=2025-01-31
elite://history/exploration?start=last_month&end=last_week
elite://history/combat?start=2025-01-15&end=2025-01-20
```

**Pros**: RESTful, consistent with existing resources
**Cons**: Less flexible than tool-based approach

#### 3. Lazy-Load Historical Data on Demand

Instead of loading last 24 hours on startup, load historical data only when requested:

```python
def load_historical_range(start_date: datetime, end_date: datetime):
    """Load journal data for specific date range on demand."""
    # Parse journal files within date range
    # Add to data store cache
    # Return loaded events
```

**Pros**: Reduces memory usage
**Cons**: First query may be slow

### LLM Interaction Examples

#### Example 1: Progression Analysis

**User**: "Compare my exploration earnings from last month versus this month"

**LLM Thinking**:
- Need two date ranges: last month (approx Jan 1-31) and this month (approx Feb 1-28)
- Need exploration category events
- Calculate earnings from SellExplorationData events

**Tool Calls**:
```python
# Get last month's data
last_month = await search_historical_events(
    start_date="2025-01-01",
    end_date="2025-01-31",
    categories=["exploration"]
)

# Get this month's data
this_month = await search_historical_events(
    start_date="2025-02-01",
    end_date="2025-02-28",
    categories=["exploration"]
)

# Analyze and compare earnings
```

#### Example 2: Activity Patterns

**User**: "What days did I play Elite Dangerous in the past month?"

**LLM Thinking**:
- Get all events from past month
- Group by date
- Identify days with activity

**Tool Call**:
```python
events = await search_historical_events(
    start_date="last month",
    end_date="today"
)

# Group events by date to find active days
```

#### Example 3: Specific System Visits

**User**: "When was the last time I visited Shinrarta Dezhra before December?"

**LLM Thinking**:
- Search for location/jump events to Shinrarta Dezhra
- Date range: beginning to end of November
- Sort descending to get most recent

**Tool Call**:
```python
events = await search_historical_events(
    start_date=None,  # From beginning
    end_date="2024-11-30",
    system_name="Shinrarta Dezhra",
    event_types=["FSDJump", "Location"],
    limit=1,
    sort_order="desc"
)
```

### Success Criteria

- [ ] LLMs can query arbitrary date ranges using natural language
- [ ] Support both absolute ("2025-01-15") and relative ("last month") dates
- [ ] Efficient querying without loading entire journal history into memory
- [ ] Clear error messages when requested date range has no data
- [ ] Documentation with examples for common use cases
- [ ] Integration tests covering various date range scenarios

### Related Issues

- Historical data loading (Milestone 12)
- Data store memory management
- Journal file parsing optimization

### Priority

**Medium-High**: This feature significantly improves the utility of the MCP server for long-term gameplay analysis and would be frequently used by LLMs when users ask about historical gameplay patterns.

### Estimated Complexity

**Medium**:
- Date parsing logic: ~2-3 hours
- Data store enhancements: ~3-4 hours
- MCP tool implementation: ~2 hours
- Testing and documentation: ~2-3 hours
- **Total**: ~10-12 hours

### Additional Notes

This feature would complement the existing gap analysis work (Milestone 17) by making it easier to query the comprehensive event coverage over any time period, not just recent activity.

The implementation should be designed with pagination in mind for future enhancement, as some date ranges could return thousands of events.
