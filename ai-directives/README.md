# AI Directives

This directory contains comprehensive project guidance and implementation directives for AI assistants working on the Elite Dangerous Local AI Tie-In MCP project.

## 📋 Purpose

This directory serves as a central repository for:
- **Project implementation plans** with detailed milestone breakdowns
- **Development standards** and quality requirements
- **Testing procedures** and validation criteria
- **Architecture decisions** and design principles
- **AI collaboration guidelines** for consistent development

## 📚 Available Documents

### [`project_implementation_plan.md`](project_implementation_plan.md)
**Comprehensive 15-milestone implementation roadmap**

**Features:**
- [SUCCESS] **Enhanced milestone structure** with test review at each stage
- [SUCCESS] **Detailed implementation tasks** for each milestone
- [SUCCESS] **Testing criteria** and validation requirements
- [SUCCESS] **Test review procedures** to maintain quality
- [SUCCESS] **GitHub workflow guidelines** with commit standards
- [SUCCESS] **Current progress tracking** (Milestones 1-7 completed)

**Usage:**
- Reference for milestone planning and execution
- Guide for test quality standards and procedures
- Framework for maintaining development consistency
- Validation criteria for milestone completion

## 🔄 Session Transition and Knowledge Preservation

### **CRITICAL: Enhanced Proactive Conversation Limit Monitoring**

**UPDATED RULE: AI must monitor conversation limits more aggressively and execute end-of-session protocol when approaching ANY capacity threshold.**

#### **Enhanced Conversation Limit Assessment Protocol**
After EVERY AI response, the AI must:

1. **Aggressive Remaining Capacity Assessment**
   - Estimate remaining capacity using conversation length, complexity, and token patterns
   - Count total interactions in current session and estimate average token consumption
   - Account for technical discussions consuming 2-3x more tokens than simple responses
   - **New**: Include artifact creation, code generation, and file updates in token estimates

2. **Much More Conservative Threshold Detection**
   - **Updated Threshold**: If estimated remaining interactions ≤ 5-6 responses: **IMMEDIATELY execute end-of-session protocol**
   - **New Rule**: When working on milestones, after completing ANY significant implementation task: **IMMEDIATELY check capacity and pause if needed**
   - **New Rule**: Before starting any new milestone or major feature: **MANDATORY capacity check**
   - Account for artifacts, lengthy code examples, and detailed technical explanations

3. **Mandatory Milestone Pause Protocol**
   - **NEW**: After completing each milestone implementation: **MANDATORY pause to create session report**
   - **NEW**: Before beginning any new milestone: **MANDATORY check "Are we approaching conversation limits?"**
   - **NEW**: If more than 2 major tasks completed in session: **MANDATORY end-of-session protocol**
   - **NEW**: If conversation has >30 total interactions: **MANDATORY capacity assessment**

4. **Immediate Protocol Execution**
   - Do NOT wait for user to indicate session ending
   - Proactively announce: "**Conversation capacity threshold reached. Executing mandatory knowledge preservation protocol before continuing.**"
   - **NEW**: Always offer to continue work in fresh session after knowledge preservation
   - Immediately begin full end-of-session review process

#### **Why Enhanced Rules Are Critical**
- **Prevents Mid-Task Termination**: Ensures no work is lost during implementation
- **Milestone Preservation**: Guarantees milestone completion is properly documented
- **Continuous Progress**: Creates clean handoff points for sustained development
- **Knowledge Continuity**: All discoveries and corrections are captured
- **User Experience**: No unexpected session cuts during critical work
- **Development Efficiency**: Future sessions start with complete context

### **Mandatory Testing and Pause Instructions**

#### **Between-Milestone Pause Protocol**
When completing any milestone:

1. **MANDATORY Completion Verification**
   - Run comprehensive test suite to verify all functionality
   - Document any test failures or issues discovered
   - Update milestone status in project implementation plan
   - Verify all implementation requirements are met

2. **MANDATORY Knowledge Preservation**
   - Create session report with all new discoveries and corrections
   - Update ai-directives with any new rules or process improvements
   - Document all technical solutions and problem-solving approaches
   - Commit all changes to Git repository

3. **MANDATORY Session Pause Consideration**
   - Always ask: "Are we approaching conversation limits?"
   - Always offer: "Should we pause here for testing and create a fresh session for the next milestone?"
   - Always recommend: "I suggest we create a session report and start fresh for optimal development flow"
   - Never continue to next milestone without explicit user confirmation and capacity verification

4. **MANDATORY User Consultation**
   - Present milestone completion summary with test results
   - Offer to troubleshoot any issues or proceed to next milestone
   - **Always recommend pausing for testing**: "I recommend taking time to test this milestone thoroughly before proceeding"
   - Suggest starting fresh session for complex milestones (8+)

#### **Testing Phase Requirements**
After each milestone completion:

1. **Comprehensive Test Validation**
   - All unit tests must pass with >90% coverage
   - Integration tests must demonstrate full functionality
   - Performance tests must meet real-time requirements
   - Cross-platform compatibility must be verified

2. **User Testing Opportunity**
   - Provide clear instructions for user testing
   - Document expected behavior and success criteria
   - Offer troubleshooting support for any issues
   - Create testing checklist for user verification

3. **Issue Resolution Protocol**
   - If tests fail: immediate debugging and fixing
   - If performance issues: optimization and re-testing
   - If integration problems: component-by-component verification
   - All issues must be resolved before milestone sign-off

#### **Fresh Session Benefits**
- **Clean Context**: Fresh start with updated directives
- **Full Capacity**: Maximum conversation length for complex tasks
- **Optimal Performance**: No accumulated context confusion
- **Better Planning**: Full session dedicated to milestone development
- **Enhanced Focus**: Clear separation between implementation phases

### **Thread Continuity Protocol**

When nearing the end of a conversation session due to token/thread limits, follow this protocol to preserve knowledge and maintain project continuity:

#### **End-of-Session Review Process**
When the user indicates "we are nearing the end of a session" OR when proactive monitoring detects approaching limits:

1. **New Rules Identification**
   - Review the entire current conversation for "new rules" - corrections, additions, or clarifications made by the user
   - Identify facts, workflows, or assumptions that differ from the existing ai-directives
   - Note any process improvements or project-specific preferences discovered

2. **Categorize New Knowledge**
   - **Technical Corrections**: Fixes to code, dependencies, or implementation details
   - **Process Improvements**: Enhanced workflows, testing procedures, or setup steps
   - **Project Facts**: Specific requirements, constraints, or architectural decisions
   - **User Preferences**: Coding styles, reporting formats, or interaction patterns

3. **Document Integration**
   - Update the relevant ai-directives files with new facts and corrections
   - Ensure all new rules are integrated into the appropriate sections
   - Maintain the existing structure and formatting standards
   - Add timestamps or session references where helpful

4. **Create Session Report**
   - **MANDATORY**: Create a session report file in `ai-directives/session-reports/` directory
   - Use filename format: `session-YYYY-MM-DD-HH-MM.md`
   - Include: new rules discovered, technical corrections, process improvements, work completed, next steps
   - **SAVE TO GIT**: Commit the session report to the repository for future reference
   - This creates a permanent record that future AI assistants can reference
   - Do not report "tests are passing" unless you have seen output confirming tests are passing.  Sometimes an AI assistant believes it has fixed the last problem and reports tests are passing, but we uncover new problems masked by that problem.  

5. **Verification Checklist**
   - Confirm all user corrections have been captured
   - Verify no contradictions exist with existing directives
   - Ensure new rules are clearly documented for future AI assistants
   - **Verify session report is committed to Git**
   - Test that the updated directives would prevent the same misunderstandings

#### **Session Report Template**
```markdown
# AI Session Report - [DATE TIME]

## Session Summary
- **Duration**: [start time] to [end time]
- **Focus**: [main topics covered]
- **Status**: [completed work and current state]

## New Rules Discovered
### Technical Corrections
- [list technical fixes and corrections]

### Process Improvements
- [list workflow and procedure improvements]

### Project Facts
- [list new requirements or constraints discovered]

## Work Completed
- [list specific tasks completed]
- [list commits made]
- [list milestones achieved]

## Next Steps for Future Sessions
- [list recommended next actions]
- [list any incomplete work]
- [list any issues to investigate]

## Knowledge Preservation Notes
- [list any critical insights for future AI assistants]
- [list patterns or approaches that worked well]
- [list things to avoid or be careful about]
```

#### **Examples of "New Rules" to Capture**

- **Package Import Mapping**: `python-dateutil` imports as `dateutil`, not `python_dateutil`
- **Setup Script Behavior**: Must verify individual package installation, not just pip install success
- **Error Handling Requirements**: Scripts must report accurate failure status and exit codes
- **Testing Standards**: Real verification vs. placeholder success reporting
- **Directory Structure**: Specific path requirements or configuration preferences
- **Workflow Preferences**: Preferred troubleshooting steps or debugging approaches
- **Async/Threading Coordination**: Event loop management in watchdog-based monitoring
- **Status File Handling**: Throttling initialization and file path parameter usage
- **Conversation Management**: Proactive limit monitoring and knowledge preservation
- **Session Documentation**: All sessions must create permanent Git records
- **Test Failure Analysis**: Systematic approach to identifying and fixing validation issues
- **Event Validation Logic**: Enhanced validation must detect malformed events comprehensively
- **Category Mapping Requirements**: All EventCategory enum values must have mapped event types
- **Milestone Status Management**: Avoid hardcoded milestone references in automation scripts
- **MCP Server Framework**: FastMCP integration patterns and lifecycle management
- **Server Testing Standards**: Comprehensive unit tests for all MCP tools and server functionality

#### **Session Handoff Protocol**

**Before ending session:**
1. Complete the new rules review and documentation
2. Update ai-directives files with new knowledge
3. **Create and commit session report to Git**
4. Provide a brief summary of what was learned/corrected
5. Note any incomplete work or next steps

**Starting new session:**
1. User will ask AI to "review the ai-directives"
2. AI should read all directive files to understand current project state
3. **Review recent session reports** in `ai-directives/session-reports/` for context
4. Pay special attention to recent updates and new rules
5. Confirm understanding of project status and next steps

This protocol ensures continuity across conversation threads and prevents repeated mistakes or misunderstandings.

## 🌐 Cross-Platform Compatibility Standards

### **Character Encoding and Unicode Guidelines**

To ensure compatibility across all development environments and platforms, follow these character usage rules:

#### **[SUCCESS] ALLOWED Characters**
- **ASCII printable characters** (32-126): Standard letters, numbers, punctuation
- **Standard ASCII symbols**: `! @ # $ % ^ & * ( ) - _ = + [ ] { } | \\ : ; " ' < > , . ? /`
- **Plain text status indicators**: `[SUCCESS]`, `[FAILED]`, `[ERROR]`, `[WARNING]`, `[INFO]`
- **ASCII box drawing**: Use `=`, `-`, `|`, `+` for borders and formatting

#### **[FAILED] FORBIDDEN Characters**
- **Unicode emojis**: (cause Windows cp1252 encoding errors)
- **Extended Unicode symbols**: (not supported in all terminals)
- **Non-ASCII characters** in subprocess commands or script output
- **Smart quotes**: (use standard ASCII quotes instead)
- **Mathematical symbols**: (use ASCII equivalents: <=, >=, +/-, etc.)

#### **Implementation Rules**

1. **Subprocess Commands**: Never include Unicode characters in subprocess print statements
   ```python
   # [FAILED] WRONG - causes encoding errors
   run_command([python, "-c", "import module; print('[SUCCESS] Success')"])
   
   # [SUCCESS] CORRECT - uses ASCII only
   run_command([python, "-c", "import module; print('[SUCCESS] Module imported')"])
   ```

2. **Script Output**: Use plain text status indicators
   ```python
   # [FAILED] WRONG - Unicode emojis
   print("✅ All tests passed")
   print("❌ Some tests failed")
   
   # [SUCCESS] CORRECT - ASCII status indicators
   print("[SUCCESS] All tests passed")
   print("[FAILED] Some tests failed")
   ```

3. **File Content**: Stick to ASCII for configuration files, scripts, and documentation
   ```bash
   # [FAILED] WRONG - Unicode arrows
   echo "➜ Installing dependencies"
   
   # [SUCCESS] CORRECT - ASCII indicators
   echo "-> Installing dependencies"
   ```

4. **Cross-Platform Testing**: Always test scripts on Windows (cp1252), Linux (UTF-8), and macOS

#### **Rationale**

- **Windows Compatibility**: Windows PowerShell/cmd uses cp1252 encoding by default
- **Terminal Support**: Not all terminals support Unicode rendering consistently
- **CI/CD Compatibility**: Build systems may not handle Unicode in logs properly
- **Debugging Ease**: ASCII-only output is easier to search, parse, and debug
- **Universal Access**: Ensures functionality for users with older systems or limited Unicode support

#### **Quick Reference**

| Status Type | Use This | Not This |
|-------------|----------|----------|
| Success     | `[SUCCESS]` | Unicode checkmarks |
| Failure     | `[FAILED]` | Unicode X marks |
| Error       | `[ERROR]` | Unicode warning signs |
| Warning     | `[WARNING]` | Unicode caution symbols |
| Info        | `[INFO]` | Unicode info symbols |
| Arrow       | `->` | Unicode arrows |
| Checkmark   | `[OK]` | Unicode checkmarks |
| Cross       | `[X]` | Unicode crosses |

This standard ensures that all project scripts, documentation, and output work reliably across all supported platforms and development environments.

## 🎯 Key Principles

### Test-Driven Development
Every milestone includes:
- **Comprehensive unit tests** with >90% coverage requirement
- **Test review and documentation** phase
- **Automation script integration** for reliability
- **Performance validation** and benchmarking
- **Integration testing** for end-to-end functionality

### Quality Standards
- **Code quality**: PEP 8, type hints, documentation
- **Test quality**: Real tests, not stubs, with proper assertions
- **Documentation**: Comprehensive guides with examples
- **Automation**: Scripts for setup, testing, and validation
- **Error handling**: Graceful failure and recovery procedures

### Development Workflow
1. **Implementation** following milestone tasks
2. **Unit testing** with comprehensive coverage
3. **Test review** to validate quality and completeness
4. **Documentation update** including automation scripts
5. **Integration validation** with existing components
6. **Performance verification** meeting requirements

## 🚀 For AI Assistants

When working on this project:

### Before Starting a Milestone:
1. **Review the implementation plan** for the specific milestone
2. **Understand testing requirements** and quality standards
3. **Check current project status** and completed milestones
4. **Validate environment** using automation scripts
5. **Review recent session reports** for context and continuity
6. **MANDATORY**: Check conversation capacity before starting major work

### During Development:
1. **Follow implementation tasks** as outlined in the plan
2. **Write comprehensive tests** alongside code implementation
3. **Use automation scripts** for validation and testing
4. **Maintain code quality** standards throughout
5. **Apply cross-platform compatibility** rules for all output and scripts
6. **Monitor conversation limits** after every interaction
7. **MANDATORY**: After each major task completion, assess if session pause is needed

### At Milestone Completion:
1. **Execute test review procedure** as defined in the plan
2. **Validate all testing criteria** are met
3. **Update documentation** and automation scripts
4. **Verify integration** with existing components
5. **Update project status** and milestone tracking
6. **MANDATORY**: Execute milestone pause protocol and create session report
7. **MANDATORY**: Offer to continue in fresh session for next milestone

### Quality Checkpoints:
- [SUCCESS] **All tests pass** with required coverage
- [SUCCESS] **Tests are comprehensive**, not stubs or placeholders
- [SUCCESS] **Documentation is updated** with new functionality
- [SUCCESS] **Automation scripts work** with new components
- [SUCCESS] **Performance meets requirements** for real-time operation
- [SUCCESS] **Cross-platform compatibility** verified (Windows, Linux, macOS)
- [SUCCESS] **Conversation limits monitored** proactively
- [SUCCESS] **Session reports created** and committed to Git
- [SUCCESS] **Milestone pause protocol executed** for testing opportunities

## 📊 Current Project Status

**Completed Milestones:** 1-7 [SUCCESS]
- Project structure and configuration [SUCCESS]
- Journal parsing and real-time monitoring [SUCCESS]
- Comprehensive test infrastructure [SUCCESS]
- Automation scripts and documentation [SUCCESS]
- Event processing and classification [SUCCESS]
- Journal data storage and retrieval [SUCCESS]
- **Basic MCP server framework [SUCCESS]** **[JUST COMPLETED]**

**Test Infrastructure:**
- 200+ unit tests with comprehensive coverage [SUCCESS]
- Automation scripts for setup/check/test [SUCCESS]
- Comprehensive testing documentation [SUCCESS]
- Mock data for reliable testing [SUCCESS]
- All test failures resolved [SUCCESS]

**MCP Server Framework:**
- [SUCCESS] **FastMCP server integration** with Elite Dangerous monitoring
- [SUCCESS] **Automatic journal monitoring startup** with background task management
- [SUCCESS] **MCP tools implementation**: server_status, get_recent_events, clear_data_store
- [SUCCESS] **Comprehensive unit test suite** with 23+ test methods for server functionality
- [SUCCESS] **Error handling and logging** for production use
- [SUCCESS] **Server lifecycle management** with proper startup/shutdown procedures
- [SUCCESS] **Integration with existing components** (journal monitoring, event processing, data storage)
- [SUCCESS] **Signal handling and graceful termination** for reliable operation

**Recent Milestone 7 Completion:**
- [SUCCESS] **EliteDangerousServer class** with full MCP integration
- [SUCCESS] **Background journal monitoring** with async task management
- [SUCCESS] **Event processing pipeline** from journal events to MCP tools
- [SUCCESS] **Real-time data access** through MCP protocol
- [SUCCESS] **Production-ready error handling** and logging systems
- [SUCCESS] **Comprehensive test coverage** for all server functionality
- [SUCCESS] **Server singleton pattern** with proper lifecycle management
- [SUCCESS] **Cross-platform compatibility** verified for server operations

**Current Setup Status:**
- [SUCCESS] **requirements.txt** includes all necessary dependencies including `mcp>=1.0.0`
- [SUCCESS] **setup_dependencies.py** properly maps package names to import names
- [SUCCESS] **Error handling** accurately reports setup failures and provides detailed troubleshooting
- [SUCCESS] **Package verification** tests actual imports rather than relying on pip install success
- [SUCCESS] **Cross-platform compatibility** ensured with ASCII-only characters in all script output
- [SUCCESS] **All automation scripts** use consistent package import name mapping
- [SUCCESS] **Event processing system** with 130+ event types, 17 categories, enhanced validation
- [SUCCESS] **Data storage system** with comprehensive in-memory storage and thread safety
- [SUCCESS] **MCP server framework** ready for tool and resource expansion

**Next Milestone:** 8 - Core MCP Tools Implementation

## 📋 Milestone Status Management Rule

### **CRITICAL: Avoid Hardcoded Milestone References in Code**

**NEW RULE: Never include hardcoded milestone numbers or "ready for milestone X" messages in automation scripts, tests, or code output.**

#### **Why This Rule Is Important**
- **Maintenance Burden**: Hardcoded references become outdated and require manual updates
- **Consistency Issues**: Different scripts may report different milestone statuses
- **User Confusion**: Outdated status messages mislead users about project progress
- **Development Friction**: Forces updates to non-functional code when milestones advance

#### **Implementation Standards**

1. **Use Generic Status Messages**
   ```python
   # [FAILED] WRONG - hardcoded milestone reference
   print("All milestones 1-4 functionality verified")
   print("Ready for Milestone 5: Event Processing")
   
   # [SUCCESS] CORRECT - generic status messages
   print("All implemented functionality verified and working")
   print("Development environment ready for continued work")
   ```

2. **Dynamic Status from Configuration**
   ```python
   # [SUCCESS] CORRECT - read status from external source
   from src.utils.config import get_current_milestone
   milestone = get_current_milestone()
   print(f"Current development phase: {milestone}")
   ```

3. **Test-Based Status Reporting**
   ```python
   # [SUCCESS] CORRECT - derive status from what actually works
   components = test_all_components()
   working_components = [c for c in components if c.status == 'working']
   print(f"{len(working_components)} components verified and operational")
   ```

#### **Approved Milestone Reference Locations**
- **AI Directives Documentation**: Project implementation plan and status tracking
- **Session Reports**: Historical records of milestone completion
- **README Files**: High-level project status (updated manually)
- **Release Notes**: Formal milestone completion announcements

#### **Enforcement Checklist**
- ✅ **Scripts Output**: No hardcoded "milestone X" or "ready for milestone Y" messages
- ✅ **Test Descriptions**: Focus on functionality, not milestone numbers
- ✅ **Error Messages**: Provide actionable guidance, not milestone context
- ✅ **Status Reports**: Derive from actual working functionality
- ✅ **Documentation**: Keep project status in designated tracking files only

#### **Migration Strategy for Existing Code**
When updating existing scripts:
1. Replace milestone-specific messages with functionality-based status
2. Remove "ready for milestone X" statements
3. Use generic success/completion messages
4. Test actual working components rather than assuming milestone status

This rule ensures automation scripts remain accurate and useful throughout the project lifecycle without requiring constant maintenance updates.

## 🔄 Continuous Improvement

This directory and its contents should be:
- **Updated regularly** as the project evolves
- **Enhanced with lessons learned** from each milestone
- **Maintained as the source of truth** for project direction
- **Used to ensure consistency** across development sessions
- **Continuously improved** with new rules and corrections from each session
- **Supplemented with session reports** providing detailed historical context

The goal is to maintain high-quality development standards while ensuring efficient progress through the implementation milestones.

## 🎯 Success Metrics

Each milestone completion should demonstrate:
- [SUCCESS] **Functional implementation** meeting all requirements
- [SUCCESS] **Comprehensive testing** with excellent coverage
- [SUCCESS] **Updated documentation** reflecting new functionality
- [SUCCESS] **Working automation** validating the implementation
- [SUCCESS] **Integration success** with existing components
- [SUCCESS] **Performance compliance** for real-time operation
- [SUCCESS] **Cross-platform compatibility** verified across all target systems
- [SUCCESS] **Knowledge preservation** through proactive conversation monitoring
- [SUCCESS] **Session documentation** committed to Git for future reference
- [SUCCESS] **Milestone pause protocol** executed for testing and user validation
- [SUCCESS] **Fresh session recommendation** for optimal development flow

This ensures the project maintains quality and reliability throughout the development process while building toward the ultimate goal of seamless Elite Dangerous and Claude Desktop integration.
