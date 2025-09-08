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
- [SUCCESS] **Current progress tracking** (Milestones 1-5 completed)

**Usage:**
- Reference for milestone planning and execution
- Guide for test quality standards and procedures
- Framework for maintaining development consistency
- Validation criteria for milestone completion

## 🔄 Session Transition and Knowledge Preservation

### **CRITICAL: Proactive Conversation Limit Monitoring**

**NEW RULE: After every interaction, the AI must check conversation limits and proactively execute the end-of-session protocol when approaching limits.**

#### **Conversation Limit Assessment Protocol**
After EVERY AI response:

1. **Estimate Remaining Capacity**
   - Analyze conversation length and complexity patterns
   - Estimate tokens consumed by average interactions in this conversation
   - Calculate likely remaining interactions before hitting limits

2. **Proactive Threshold Detection**
   - If estimated remaining interactions ≤ 8-10 responses: **IMMEDIATELY execute end-of-session protocol**
   - Consider complexity: technical discussions consume more tokens than simple questions
   - Account for code examples, long explanations, or detailed documentation
   - **Updated threshold provides 2-3x more safety margin** to prevent session truncation

3. **Immediate Protocol Execution**
   - Do NOT wait for user to indicate "nearing end of session"
   - Proactively announce: "We are approaching conversation limits. Executing knowledge preservation protocol."
   - Immediately begin the full end-of-session review process

#### **Why This Rule Is Critical**
- **Prevents Knowledge Loss**: Ensures we capture all corrections and improvements before hitting limits
- **Maintains Continuity**: Future AI assistants will have complete context
- **Preserves Work**: Technical fixes and problem-solving insights are never lost
- **User Experience**: No interruption of work due to unexpected session termination
- **Adequate Buffer Time**: More conservative threshold prevents session summary truncation

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

### During Development:
1. **Follow implementation tasks** as outlined in the plan
2. **Write comprehensive tests** alongside code implementation
3. **Use automation scripts** for validation and testing
4. **Maintain code quality** standards throughout
5. **Apply cross-platform compatibility** rules for all output and scripts
6. **Monitor conversation limits** after every interaction

### At Milestone Completion:
1. **Execute test review procedure** as defined in the plan
2. **Validate all testing criteria** are met
3. **Update documentation** and automation scripts
4. **Verify integration** with existing components
5. **Update project status** and milestone tracking

### Quality Checkpoints:
- [SUCCESS] **All tests pass** with required coverage
- [SUCCESS] **Tests are comprehensive**, not stubs or placeholders
- [SUCCESS] **Documentation is updated** with new functionality
- [SUCCESS] **Automation scripts work** with new components
- [SUCCESS] **Performance meets requirements** for real-time operation
- [SUCCESS] **Cross-platform compatibility** verified (Windows, Linux, macOS)
- [SUCCESS] **Conversation limits monitored** proactively
- [SUCCESS] **Session reports created** and committed to Git

## 📊 Current Project Status

**Completed Milestones:** 1-5 [SUCCESS]
- Project structure and configuration [SUCCESS]
- Journal parsing and real-time monitoring [SUCCESS]
- Comprehensive test infrastructure [SUCCESS]
- Automation scripts and documentation [SUCCESS]
- Event processing and classification [SUCCESS] **[JUST COMPLETED]**

**Test Infrastructure:**
- 174+ unit tests with comprehensive coverage [SUCCESS]
- Automation scripts for setup/check/test [SUCCESS]
- Comprehensive testing documentation [SUCCESS]
- Mock data for reliable testing [SUCCESS]
- All test failures resolved [SUCCESS]

**Recent Test Fixes Completed:**
- [SUCCESS] **Async/Threading Issues**: Fixed RuntimeError: no running event loop with proper event loop coordination
- [SUCCESS] **Status.json Handling**: Resolved throttling and file path handling in monitoring tests
- [SUCCESS] **Cross-Platform Compatibility**: Fixed Windows encoding errors, established ASCII-only standards
- [SUCCESS] **Package Import Mapping**: Corrected python-dateutil → dateutil mapping across all scripts
- [SUCCESS] **Test Infrastructure Cleanup**: Removed obsolete imports and functions
- [SUCCESS] **Event Processing Test Fixes**: Fixed EventCategory.OTHER mapping and enhanced validation logic
- [SUCCESS] **Malformed Event Detection**: Enhanced validation to detect 5+ invalid events in stress tests

**Current Setup Status:**
- [SUCCESS] **requirements.txt** includes all necessary dependencies including `pydantic-settings>=2.5.2`
- [SUCCESS] **setup_dependencies.py** properly maps package names to import names (e.g., `python-dateutil` → `dateutil`)
- [SUCCESS] **Error handling** accurately reports setup failures and provides detailed troubleshooting
- [SUCCESS] **Package verification** tests actual imports rather than relying on pip install success
- [SUCCESS] **Cross-platform compatibility** ensured with ASCII-only characters in all script output
- [SUCCESS] **All automation scripts** use consistent package import name mapping
- [SUCCESS] **Event processing system** with 130+ event types, 17 categories, enhanced validation

**Next Milestone:** 6 - Journal Data Storage and Retrieval

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

This ensures the project maintains quality and reliability throughout the development process while building toward the ultimate goal of seamless Elite Dangerous and Claude Desktop integration.