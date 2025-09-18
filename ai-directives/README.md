# AI Directives for Elite Dangerous Local AI Tie-In MCP

## Agents.md And Cursor Rules (Read First)

- What is `AGENTS.md`?
  - A concise, enforceable ruleset for AI coding agents working in this repo.
  - It lives at the repository root and applies to all files here. If nested `AGENTS.md` files exist, deeper ones take precedence for their folders.
  - Agents must follow `AGENTS.md` and any direct user instructions.

- What is `.cursorrules`?
  - A portable subset of the same rules for the Cursor editor assistant.
  - Mirrors the critical conventions in a format Cursor recognizes.

- Critical rules (summary):
  - Use feature branches + PRs; do not merge without explicit approval.
  - ASCII-only program output; no Unicode/emoji in code or logs.
  - Timezone-aware UTC datetimes (`datetime.now(timezone.utc)`).
  - ProcessedEvent uses `raw_event`; use `key_data` for derived fields.
  - Do not call `get_all_events()`; use `query_events()`/`get_recent_events(minutes)` etc.
  - MCP resources return structured error objects, not `None`.
  - FastMCP: register tools with `@app.tool()`; do not rely on `app.tools`.
  - Template variable checks must handle formatted placeholders like `{credits:,}`.
  - Follow EDCoPilot chatter grammar in `docs/edcopilot-chatter-grammar.md` and replace all tokens with safe fallbacks.

- See also:
  - `AGENTS.md` (root): repository-wide binding rules for agents.
  - `.cursorrules` (root): Cursor-focused rule set.

---

## Documentation Update Protocol (MANDATORY)

When asked to "update the documentation" or to "add a rule", update these in lockstep so information stays consistent:

- `AGENTS.md` (root): binding agent rules and processes (short, enforceable).
- `.cursorrules` (root): portable mirror of essential agent rules for Cursor; keep wording aligned with `AGENTS.md`.
- `ai-directives/` (this folder): project context (goals, strategies, status, session reports, lessons, plans).

Checklist for any doc/rule change:
1) Add/modify the rule in `AGENTS.md`
2) Mirror the relevant rule in `.cursorrules`
3) Update context in `ai-directives` (this README or the right sub-file)
4) Cross-link related docs to avoid duplication
5) Commit with a clear `docs:` message describing the tri-file update

---

## Folder Guide

- `project_implementation_plan.md` — Milestones and implementation roadmap.
- `code_quality_lessons.md` — Collected rules and pitfalls from past fixes.
- `session-reports/` — Session logs, milestone notes, and knowledge preservation.

Recommended reading order for new contributors:
1) `AGENTS.md` (root) for ground rules
2) This README for project status/context
3) `project_implementation_plan.md` for roadmap
4) `code_quality_lessons.md` for do/don't details
5) `docs/` in the repo for API/features/testing guides

## 🚀 Quick Start for AI Assistants

**Project Goal**: Create an MCP server that connects Elite Dangerous journal data to Claude Desktop, enabling real-time game state queries and AI assistance.

**Before Starting Any Work**:
1. Review this document completely
2. Check recent session reports in `ai-directives/session-reports/`
3. Verify current milestone status below
4. Run `python scripts/check_environment.py` to validate setup
5. **MANDATORY**: Monitor conversation limits and execute session protocol when needed

## 📊 Current Project Status

### Completed Milestones ✅
1. **Project Structure** - Base configuration and setup
2. **Configuration Management** - Environment variables and path validation
3. **Journal File Discovery** - File parsing with comprehensive tests
4. **Real-time Monitoring** - File system watching with position tracking
5. **Event Processing** - 130+ event types across 17 categories
6. **Data Storage** - In-memory storage with thread safety and game state tracking
7. **MCP Server Framework** - FastMCP integration with background monitoring
8. **Core MCP Tools** - 15+ tools for game data queries and analysis
9. **MCP Resources** - 17+ dynamic resource endpoints with caching
10. **MCP Prompts** - 9 context-aware prompt templates for AI assistance

### Current State
- **Status**: Production Ready
- **Tests**: 275+ passing (99% success rate)
- **Coverage**: 95%+
- **Next Milestone**: 11 - EDCoPilot Integration
- **All Systems**: Core functionality operational and tested

### Current Project Status (Authoritative Update)

This section supersedes older counts above and reflects the present state.

Completed Milestones
1. Project Structure
2. Configuration Management
3. Journal File Discovery
4. Real-time Monitoring
5. Event Processing (130+ types, 17 categories)
6. Data Storage (thread-safe, game state tracking)
7. MCP Server Framework (FastMCP + background monitoring)
8. Core MCP Tools (comprehensive toolset)
9. MCP Resources (dynamic endpoints with caching)
10. MCP Prompts (context-aware templates)
11. EDCoPilot Integration (templates/chatter + tokens/conditions)
12. Historical Data Loading (last 24h on startup)
13. Journal Parser Fixes (filename/timestamp extraction)
14. AsyncIO Stability (reliable Claude Desktop connection)
15. Dynamic Multi-Crew Theme System (AI themes, ship-specific crews)

Current State
- Status: Production Ready
- Tests: 400+ passing (high coverage)
- Coverage: 95%+
- Next Milestone: None (core milestones complete); enhancements proceed via scoped feature branches
- All Systems: Core functionality operational, documented, and tested

## 🔄 Development Workflow Standard

### Pull Request Workflow (MANDATORY)
**This is the standard workflow for all development going forward:**

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/milestone-name
   ```

2. **Implement Changes**
   - Write code following all quality standards
   - Create/update tests alongside implementation
   - Update documentation as needed

3. **Create Pull Request**
   - Push branch to GitHub
   - Create PR with comprehensive description
   - List all changes and features implemented

4. **Test Verification Phase**
   - Run tests on the feature branch
   - Share test results with user
   - **WAIT FOR USER CONFIRMATION** - Do not merge until user confirms tests pass
   - Fix any issues identified

5. **Merge Only After Approval**
   - User must explicitly state "tests pass" or "merge approved"
   - Only then merge PR to main
   - Document completion in milestone status file

### Example Workflow Communication
```
AI: "I've created PR #X for Milestone Y. The tests are showing [results]. 
     Please review and let me know when tests pass so I can merge."
User: "Tests pass, you can merge."
AI: "Merging PR #X now..."
```

## 🔧 Development Standards

### Code Quality Requirements
- **PEP 8 compliance** with type hints
- **Comprehensive documentation** with docstrings
- **Test coverage >90%** for new code
- **Real tests, not stubs** - proper assertions required
- **Error handling** with graceful failure
- **Cross-platform compatibility** (Windows, Linux, macOS)

### Character Encoding Rules
**CRITICAL**: Use ASCII-only characters in all output and scripts

#### ✅ ALLOWED
- ASCII printable characters (32-126)
- Status indicators: `[SUCCESS]`, `[FAILED]`, `[ERROR]`, `[WARNING]`, `[INFO]`
- ASCII box drawing: `=`, `-`, `|`, `+`

#### ❌ FORBIDDEN  
- Unicode emojis (cause Windows cp1252 errors)
- Extended Unicode symbols
- Smart quotes
- Mathematical symbols (use ASCII: <=, >=, +/-, etc.)

### Datetime Timezone Consistency
**CRITICAL**: All datetime objects must be timezone-aware using UTC

```python
# ❌ WRONG - Creates timezone-naive datetime
timestamp = datetime.utcnow()

# ✅ CORRECT - Creates timezone-aware datetime
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc)
```

### ProcessedEvent Data Structure
**IMPORTANT**: ProcessedEvent uses `raw_event` parameter, not `data`

```python
# ❌ WRONG
ProcessedEvent(data={"key": "value"})
event.data.get("key")  # Use raw_event instead

# ✅ CORRECT
ProcessedEvent(raw_event={"key": "value"})
event.raw_event.get("key")  # Access data through raw_event
```

### FastMCP Framework Rules
**CRITICAL**: FastMCP limitations and patterns

```python
# ❌ WRONG - FastMCP decorators that don't exist
@app.resource()  # Does not exist
@app.prompt()    # Does not exist

# ❌ WRONG - FastMCP attribute that doesn't exist
server.app.tools.keys()  # 'tools' attribute doesn't exist

# ✅ CORRECT - Only tool decorator is supported
@app.tool()  # All handlers use tool decorator

# ✅ CORRECT - Access patterns
# FastMCP doesn't expose tools collection directly
# Handlers are configured but not accessible via attributes
```

### DataStore Method Names
**IMPORTANT**: Use correct method names for data access

```python
# ❌ WRONG - Method doesn't exist
data_store.get_all_events()

# ✅ CORRECT - Use existing methods
data_store.get_recent_events(minutes=60)
data_store.get_events_by_type("FSDJump")
data_store.get_events_by_category(EventCategory.EXPLORATION)
```

## 🔄 Session Management Protocol

### Conversation Limit Monitoring

**After EVERY response, assess if**:
- Estimated remaining interactions ≤ 5-6 responses
- More than 2 major tasks completed in session
- Conversation has >30 total interactions
- Any milestone implementation completed
- PR created and awaiting test verification

**If ANY threshold reached**: 
1. Announce: "Conversation capacity threshold reached. Executing mandatory knowledge preservation protocol."
2. Create session report in `ai-directives/session-reports/`
3. Update ai-directives with new discoveries
4. Commit all changes to Git
5. Note any pending PRs awaiting test results
6. Offer to continue in fresh session

### Session Report Template
```markdown
# AI Session Report - [DATE TIME]

## Session Summary
- Duration, Focus, Status
- PRs created and their status

## New Rules Discovered
- Technical Corrections
- Process Improvements  
- Project Facts

## Work Completed
- Tasks, Commits, Milestones
- Test results and issues found

## Pending Items
- PRs awaiting test verification
- Issues to be fixed

## Next Steps
- Recommendations for future sessions

## Knowledge Preservation Notes
- Critical insights
- Successful patterns
- Things to avoid
```

## 📚 Technical Rules & Patterns

### Package Import Mapping
- `python-dateutil` imports as `dateutil`, not `python_dateutil`
- FastMCP server uses singleton pattern with proper lifecycle management
- Background tasks require proper async/await patterns

### Error Handling Requirements
- Scripts must report accurate failure status and exit codes
- Real verification vs. placeholder success reporting
- Detailed error messages with troubleshooting steps

### Testing Standards
- Use same datetime patterns in tests as production
- Mock data must match production data structures
- Integration tests verify cross-component functionality
- Always run tests before merging PRs

### MCP Server Specifics
- Server starts journal monitoring automatically on startup
- Background tasks managed with asyncio
- Signal handling for graceful shutdown
- All handlers use @app.tool() decorator (no resource/prompt decorators)
- Resources and prompts accessed via tool functions

## 📁 Project Resources

### Documentation
- **Implementation Plan**: [`project_implementation_plan.md`](project_implementation_plan.md) - 15-milestone roadmap
- **Session Reports**: [`session-reports/`](session-reports/) - Historical context and discoveries
- **Main README**: [`../README.md`](../README.md) - User-facing documentation
- **EDCoPilot Grammar**: [`../docs/edcopilot-chatter-grammar.md`](../docs/edcopilot-chatter-grammar.md) - Formal specification for chatter file generation

### Key Scripts
- `setup_dependencies.py` - Install and verify packages
- `check_environment.py` - Validate development environment
- `run_tests.py` - Execute test suite with coverage
- `server.py` - MCP server entry point

## ✅ Development Workflow

### For Each Task
1. **Plan**: Review relevant milestone requirements
2. **Implement**: Follow coding standards
3. **Test**: Write tests alongside code
4. **Create PR**: Push to feature branch
5. **Verify**: Run tests and share results
6. **Wait**: Get user confirmation before merge
7. **Document**: Update relevant documentation
8. **Commit**: Clear, descriptive commit messages

### Quality Checklist
- [ ] Tests written and passing
- [ ] PR created with description
- [ ] Test results shared with user
- [ ] User approval received before merge
- [ ] Documentation updated
- [ ] Cross-platform compatibility verified
- [ ] No hardcoded milestone references
- [ ] Timezone-aware datetimes used
- [ ] ASCII-only output
- [ ] Error handling implemented
- [ ] Session report created if needed

## 🎯 Success Metrics

Each milestone must demonstrate:
- Functional implementation meeting requirements
- Comprehensive testing with >90% coverage
- PR created and reviewed before merge
- Test verification by user
- Updated documentation
- Working automation scripts
- Integration with existing components
- Performance meeting real-time requirements
- Cross-platform compatibility
- Knowledge preservation through session reports

## 🔄 Continuous Improvement

This document should be:
- Updated with each new discovery
- Enhanced with lessons learned
- Maintained as source of truth
- Used to ensure consistency across sessions
- Reviewed at start of each new session

---

**Remember**: Quality over speed. Test thoroughly. Wait for approval. Document everything. Preserve knowledge for future sessions.
