# Issue Investigation and Bugfix Workflow

## Purpose

This document defines the mandatory workflow for investigating and resolving GitHub issues. This ensures systematic problem-solving, proper test coverage, and maintainable code.

## When This Workflow Applies

Use this workflow when the user requests:
- "Investigate issue #N"
- "Resolve issue #N"
- "Address issue #N"
- "Fix issue #N"
- Any similar phrasing indicating issue investigation/resolution

## Workflow Steps

### Step 1: Read and Understand the Issue

1. Fetch the issue from GitHub using `gh issue view <number>`
2. Read the complete issue description, comments, and context
3. Identify:
   - The problem statement
   - Expected vs actual behavior
   - Reproduction steps (if provided)
   - Any relevant system information
4. Review any related issues, PRs, or documentation mentioned

### Step 2: Validate the Issue

1. **Create investigation scripts or tests to reproduce the issue**
2. **Execute the reproduction steps**
3. **Document findings**:

   **If Issue is VALID (reproduced)**:
   - Proceed to Step 3
   - Document exact reproduction conditions
   - Note any additional context discovered

   **If Issue is NOT VALID (cannot reproduce)**:
   - Post a comment on GitHub explaining:
     - What was tested
     - Why it could not be reproduced
     - Steps taken to verify
     - Request for additional information if needed
   - **Do NOT close the issue automatically**
   - Wait for user decision on next steps
   - End workflow here

### Step 3: Create Bugfix Branch

1. **Branch naming convention**: `bugfix/<issue-number>-<brief-description>`

   Examples:
   - `bugfix/12-file-monitoring-race-condition`
   - `bugfix/45-missing-event-data`
   - `bugfix/78-theme-persistence-error`

2. **Create and checkout the branch**:
   ```bash
   git checkout -b bugfix/<issue-number>-<brief-description>
   ```

3. **Verify branch creation**:
   ```bash
   git branch --show-current
   ```

### Step 4: Create Failing Unit Tests

1. **Create new test file or add to existing test suite** that captures the root cause

2. **Test file requirements**:
   - Clear test names describing the failure scenario
   - Comments linking to the GitHub issue
   - Brief summary of test intent

3. **Test comment format**:
   ```python
   def test_issue_NNN_description_of_problem():
       """
       Test for Issue #NNN: <Brief Summary>

       GitHub Issue: https://github.com/<owner>/<repo>/issues/NNN

       Problem: <One-line description of what was failing>
       Expected: <What should happen>
       Actual (before fix): <What was happening>
       """
       # Test implementation
   ```

4. **Example**:
   ```python
   def test_issue_12_file_write_buffer_race_condition():
       """
       Test for Issue #12: File System Event Race Condition

       GitHub Issue: https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp/issues/12

       Problem: New journal events not ingested when file size check happens before OS flush
       Expected: All written events should be read regardless of timing
       Actual (before fix): Events discarded if size check occurs before flush completes
       """
       # Simulate race condition
       # Write data
       # Trigger size check before flush
       # Assert data is still read correctly
   ```

5. **Run tests to verify they fail**:
   ```bash
   pytest path/to/test_file.py::test_issue_NNN_description -v
   ```

6. **Commit the failing tests**:
   ```bash
   git add tests/
   git commit -m "test: add failing tests for issue #NNN

   - Add test_issue_NNN_description_of_problem
   - Captures root cause: <brief description>
   - Tests currently fail as expected

   Issue: #NNN"
   ```

### Step 5: Fix the Code

1. **Implement the fix** following all code quality standards
2. **Ensure the new tests now pass**
3. **Run the full test suite** to verify no regressions
4. **Document the fix** with clear comments explaining the solution

5. **Commit the fix**:
   ```bash
   git add src/
   git commit -m "fix: resolve <brief description> (fixes #NNN)

   <Detailed description of the fix>

   Changes:
   - <Change 1>
   - <Change 2>

   Tests: All new tests passing, no regressions

   Fixes #NNN"
   ```

### Step 6: Update Test Documentation

1. **Update test count in README.md** if applicable
2. **Update test coverage statistics** if applicable
3. **Add entry to CHANGELOG.md** (if exists) describing the bugfix

4. **Commit documentation updates**:
   ```bash
   git add README.md CHANGELOG.md docs/
   git commit -m "docs: update test counts and changelog for issue #NNN"
   ```

### Step 7: Create Pull Request

1. **Push the bugfix branch**:
   ```bash
   git push -u origin bugfix/<issue-number>-<brief-description>
   ```

2. **Create PR with comprehensive description**:
   ```bash
   gh pr create --title "Fix: <Issue Title> (fixes #NNN)" --body "$(cat <<'EOF'
   ## Summary

   Fixes #NNN - <Brief description>

   ## Root Cause Analysis

   <Explanation of what was causing the issue>

   ## Solution

   <Explanation of how the fix works>

   ## Changes Made

   - <Change 1>
   - <Change 2>

   ## Testing

   **New Tests Added:**
   - `test_issue_NNN_description` - <Purpose>

   **Test Results:**
   - All new tests passing
   - No regressions in existing test suite
   - <Total test count> tests passing

   ## Documentation Updates

   - Updated README.md with new test count
   - Updated relevant documentation

   Fixes #NNN
   EOF
   )"
   ```

### Step 8: Post PR Link to GitHub Issue

**Post comment linking to the PR**:
```bash
gh issue comment <issue-number> --body "## Fix Implemented

This issue has been resolved in PR #<pr-number>.

### Changes Made
<Brief list of changes>

### Testing
- X new comprehensive tests covering all aspects of the fix
- All tests passing with no regressions
- Total: X tests (up from Y)

### Pull Request
**PR #<pr-number>**: <PR URL>

Ready for review and testing."
```

### Step 9: Provide PR Link to User

**Response format**:
```
Investigation of issue #NNN complete.

**Issue Status:** VALID - Successfully reproduced and fixed

**Root Cause:** <Brief explanation>

**Solution:** <Brief explanation>

**Testing:**
- Added X new tests specifically for this issue
- All tests passing (X total)
- No regressions detected

**Pull Request:** <PR URL>

The fix is ready for your review and approval.
```

## Quality Standards

### Test Requirements
- Tests must actually fail before the fix
- Tests must pass after the fix
- Tests must be maintainable and clear
- Tests must have proper issue links in comments

### Branch Requirements
- Follow naming convention: `bugfix/<issue-number>-<brief-description>`
- Branch from latest `main`
- Keep commits focused and logical

### PR Requirements
- Comprehensive description with root cause analysis
- Link to original issue with `Fixes #NNN`
- Test results documented
- All quality checks passing

### Documentation Requirements
- Update test counts if changed
- Update changelog if exists
- Update any affected documentation
- Clear commit messages following conventional commits

## Error Handling

### If Issue Cannot Be Reproduced
1. Post detailed comment on GitHub issue
2. Explain what was tested and why reproduction failed
3. Request additional information
4. **Do NOT close the issue**
5. Wait for user guidance

### If Tests Fail After Fix
1. Investigate the failure
2. Fix the implementation
3. Ensure all tests pass
4. Update the PR with new commits
5. Document what was adjusted

### If PR Creation Fails
1. Check GitHub CLI authentication: `gh auth status`
2. Verify branch is pushed: `git branch -r`
3. Create PR manually via GitHub UI if needed
4. Provide the manual PR link to user

## Examples

### Example 1: Race Condition Bug
```
Issue #12: File System Event Race Condition

Branch: bugfix/12-file-monitoring-race-condition

Tests Added:
- test_issue_12_file_write_buffer_race_condition()
- test_issue_12_no_events_missed_on_rapid_writes()

Fix: Removed early return in read_journal_file_incremental() that
     caused events to be skipped when size check occurred before flush

PR: https://github.com/user/repo/pull/13
```

### Example 2: Data Validation Issue
```
Issue #45: Theme Validation Rejects Valid Input

Branch: bugfix/45-theme-validation-empty-string

Tests Added:
- test_issue_45_empty_string_treated_as_default()
- test_issue_45_none_still_raises_error()

Fix: Updated validation logic to treat empty string as "use default"
     while None still raises ValidationError for required fields

PR: https://github.com/user/repo/pull/46
```

## Best Practices

1. **Always link tests to issues** - Future developers need context
2. **Document root cause** - Explain why, not just what
3. **Test the reproduction** - Ensure issue is real before fixing
4. **No assumptions** - If can't reproduce, ask for more info
5. **Comprehensive testing** - Add multiple test cases for edge cases
6. **Clear commits** - Each commit should have a clear purpose
7. **Update docs** - Keep documentation in sync with code changes

## Workflow Checklist

- [ ] Read and understand the issue
- [ ] Create investigation/reproduction test
- [ ] Validate issue (reproduce or document non-reproduction)
- [ ] Create bugfix branch with proper naming
- [ ] Write failing unit tests with issue links
- [ ] Implement fix
- [ ] Verify all tests pass
- [ ] Update documentation and test counts
- [ ] Create comprehensive pull request
- [ ] Post PR link as comment on GitHub issue
- [ ] Provide PR link to user
- [ ] Wait for user approval before merging

---

**Remember**: This workflow ensures every bug fix is:
- Properly investigated
- Well-tested
- Thoroughly documented
- Traceable to the original issue
- Reviewable and maintainable
