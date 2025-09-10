# AI Directives for Elite Dangerous Local AI Tie-In MCP

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
2. **Journal Parsing** - Real-time monitoring and parsing
3. **Test Infrastructure** - 260+ unit tests with comprehensive coverage
4. **Automation Scripts** - Setup, testing, and validation tools
5. **Event Processing** - 130+ event types across 17 categories
6. **Data Storage** - In-memory storage with thread safety
7. **MCP Server Framework** - FastMCP integration with background monitoring
8. **Core MCP Tools** - 15+ tools across 6 categories for data access

### Current State
- **Tests**: 260+ passing with 92% coverage
- **Next Milestone**: 9 - MCP Resources Implementation
- **All Systems**: Operational and tested

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

**Apply to**: All production code, test code, and mock data generation

### Milestone Status Management
**RULE**: Never hardcode milestone references in code or test output

```python
# ❌ WRONG
print("Milestone 7: Basic MCP Server Framework - COMPLETED")

# ✅ CORRECT  
print("Completed Milestones:")
print("  - Milestone 1: Project Structure")
print("  - Milestone 2: Configuration Management")
# ... list all completed milestones
```

**IMPORTANT**: Either keep milestone messages dynamically updated with actual progress, or remove them entirely and use a list of completed milestones instead. Hardcoded milestone messages become misleading when new milestones are completed.

## 🔄 Session Management Protocol

### Conversation Limit Monitoring

**After EVERY response, assess if**:
- Estimated remaining interactions ≤ 5-6 responses
- More than 2 major tasks completed in session
- Conversation has >30 total interactions
- Any milestone implementation completed

**If ANY threshold reached**: 
1. Announce: "Conversation capacity threshold reached. Executing mandatory knowledge preservation protocol."
2. Create session report in `ai-directives/session-reports/`
3. Update ai-directives with new discoveries
4. Commit all changes to Git
5. Offer to continue in fresh session

### Session Report Template
```markdown
# AI Session Report - [DATE TIME]

## Session Summary
- Duration, Focus, Status

## New Rules Discovered
- Technical Corrections
- Process Improvements  
- Project Facts

## Work Completed
- Tasks, Commits, Milestones

## Next Steps
- Recommendations for future sessions

## Knowledge Preservation Notes
- Critical insights
- Successful patterns
- Things to avoid
```

### Between-Milestone Protocol

**MANDATORY when completing any milestone**:
1. Run comprehensive test suite
2. Create session report
3. Commit all changes
4. Ask: "Should we pause here for testing and start fresh for the next milestone?"
5. Recommend: "I suggest testing this milestone thoroughly before proceeding"

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

### MCP Server Specifics
- Server starts journal monitoring automatically on startup
- Background tasks managed with asyncio
- Signal handling for graceful shutdown
- Basic tools: server_status, get_recent_events, clear_data_store
- Core tools: 15+ tools for location, events, activities, journey, performance

## 📁 Project Resources

### Documentation
- **Implementation Plan**: [`project_implementation_plan.md`](project_implementation_plan.md) - 15-milestone roadmap
- **Session Reports**: [`session-reports/`](session-reports/) - Historical context and discoveries
- **Main README**: [`../README.md`](../README.md) - User-facing documentation

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
4. **Validate**: Run test suite
5. **Document**: Update relevant documentation
6. **Commit**: Clear, descriptive commit messages

### Quality Checklist
- [ ] Tests pass with required coverage
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

**Remember**: Quality over speed. Test thoroughly. Document everything. Preserve knowledge for future sessions.
