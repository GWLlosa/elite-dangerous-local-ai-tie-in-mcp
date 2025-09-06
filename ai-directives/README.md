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
- ✅ **Enhanced milestone structure** with test review at each stage
- ✅ **Detailed implementation tasks** for each milestone
- ✅ **Testing criteria** and validation requirements
- ✅ **Test review procedures** to maintain quality
- ✅ **GitHub workflow guidelines** with commit standards
- ✅ **Current progress tracking** (Milestones 1-4 completed)

**Usage:**
- Reference for milestone planning and execution
- Guide for test quality standards and procedures
- Framework for maintaining development consistency
- Validation criteria for milestone completion

## 🔄 Session Transition and Knowledge Preservation

### **Thread Continuity Protocol**

When nearing the end of a conversation session due to token/thread limits, follow this protocol to preserve knowledge and maintain project continuity:

#### **End-of-Session Review Process**
When the user indicates "we are nearing the end of a session":

1. **📝 New Rules Identification**
   - Review the entire current conversation for "new rules" - corrections, additions, or clarifications made by the user
   - Identify facts, workflows, or assumptions that differ from the existing ai-directives
   - Note any process improvements or project-specific preferences discovered

2. **📋 Categorize New Knowledge**
   - **Technical Corrections**: Fixes to code, dependencies, or implementation details
   - **Process Improvements**: Enhanced workflows, testing procedures, or setup steps
   - **Project Facts**: Specific requirements, constraints, or architectural decisions
   - **User Preferences**: Coding styles, reporting formats, or interaction patterns

3. **✍️ Document Integration**
   - Update the relevant ai-directives files with new facts and corrections
   - Ensure all new rules are integrated into the appropriate sections
   - Maintain the existing structure and formatting standards
   - Add timestamps or session references where helpful

4. **🔍 Verification Checklist**
   - Confirm all user corrections have been captured
   - Verify no contradictions exist with existing directives
   - Ensure new rules are clearly documented for future AI assistants
   - Test that the updated directives would prevent the same misunderstandings

#### **Examples of "New Rules" to Capture**

- **Package Import Mapping**: `python-dateutil` imports as `dateutil`, not `python_dateutil`
- **Setup Script Behavior**: Must verify individual package installation, not just pip install success
- **Error Handling Requirements**: Scripts must report accurate failure status and exit codes
- **Testing Standards**: Real verification vs. placeholder success reporting
- **Directory Structure**: Specific path requirements or configuration preferences
- **Workflow Preferences**: Preferred troubleshooting steps or debugging approaches

#### **Session Handoff Protocol**

**Before ending session:**
1. Complete the new rules review and documentation
2. Commit all updates to the ai-directives
3. Provide a brief summary of what was learned/corrected
4. Note any incomplete work or next steps

**Starting new session:**
1. User will ask AI to "review the ai-directives"
2. AI should read all directive files to understand current project state
3. Pay special attention to recent updates and new rules
4. Confirm understanding of project status and next steps

This protocol ensures continuity across conversation threads and prevents repeated mistakes or misunderstandings.

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

### During Development:
1. **Follow implementation tasks** as outlined in the plan
2. **Write comprehensive tests** alongside code implementation
3. **Use automation scripts** for validation and testing
4. **Maintain code quality** standards throughout

### At Milestone Completion:
1. **Execute test review procedure** as defined in the plan
2. **Validate all testing criteria** are met
3. **Update documentation** and automation scripts
4. **Verify integration** with existing components
5. **Update project status** and milestone tracking

### Quality Checkpoints:
- ✅ **All tests pass** with required coverage
- ✅ **Tests are comprehensive**, not stubs or placeholders
- ✅ **Documentation is updated** with new functionality
- ✅ **Automation scripts work** with new components
- ✅ **Performance meets requirements** for real-time operation

## 📊 Current Project Status

**Completed Milestones:** 1-4 ✅
- Project structure and configuration ✅
- Journal parsing and real-time monitoring ✅
- Comprehensive test infrastructure ✅
- Automation scripts and documentation ✅

**Test Infrastructure:**
- 47+ unit tests with >96% coverage
- Automation scripts for setup/check/test
- Comprehensive testing documentation
- Mock data for reliable testing

**Current Setup Status:**
- ✅ **requirements.txt** includes all necessary dependencies including `pydantic-settings>=2.5.2`
- ✅ **setup_dependencies.py** properly maps package names to import names (e.g., `python-dateutil` → `dateutil`)
- ✅ **Error handling** accurately reports setup failures and provides detailed troubleshooting
- ✅ **Package verification** tests actual imports rather than relying on pip install success

**Next Milestone:** 5 - Event Processing and Classification

## 🔄 Continuous Improvement

This directory and its contents should be:
- **Updated regularly** as the project evolves
- **Enhanced with lessons learned** from each milestone
- **Maintained as the source of truth** for project direction
- **Used to ensure consistency** across development sessions
- **Continuously improved** with new rules and corrections from each session

The goal is to maintain high-quality development standards while ensuring efficient progress through the implementation milestones.

## 🎯 Success Metrics

Each milestone completion should demonstrate:
- ✅ **Functional implementation** meeting all requirements
- ✅ **Comprehensive testing** with excellent coverage
- ✅ **Updated documentation** reflecting new functionality
- ✅ **Working automation** validating the implementation
- ✅ **Integration success** with existing components
- ✅ **Performance compliance** for real-time operation

This ensures the project maintains quality and reliability throughout the development process while building toward the ultimate goal of seamless Elite Dangerous and Claude Desktop integration.
