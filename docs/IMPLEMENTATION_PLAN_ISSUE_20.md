# Implementation Plan: Issue #20 - EDCoPilot Chatter Format Complete Rewrite

## Executive Summary

**Issue:** EDCoPilot chatter files use incorrect format causing 100% rejection of generated content.

**Approach:** Test-first, contract-oriented design ensuring compatibility with authoritative EDCoPilot format.

**Estimated Effort:** 6-8 hours
**Complexity:** High
**Breaking Changes:** Yes - complete format rewrite

---

## Design Principles

### 1. Test-First Development
- Write failing tests that define expected behavior
- Tests validate against authoritative EDCoPilot format
- Each phase begins with comprehensive test cases

### 2. Contract-Oriented Design
- Define clear interfaces (data classes) before implementation
- Contracts validated by tests
- Public API stability maintained where possible

### 3. Incremental Implementation
- Small, testable changes
- Each phase completes before moving to next
- Tests pass at end of each phase

---

## Phase 1: Token System Rewrite

### Objective
Replace TitleCase token names with lowercase tokens matching authoritative format.

### Contracts (Data Structures)

#### New: `EDCoPilotTokens` Class
```python
class EDCoPilotTokens:
    """Authoritative EDCoPilot tokens (lowercase format)."""

    # Commander tokens
    CMDR_NAME = "<cmdrname>"
    CMDR_ADDRESS = "<cmdraddress>"  # Sir/Ma'am/Commander

    # Ship tokens
    MY_SHIP_NAME = "<myshipname>"
    CALLSIGN = "<callsign>"

    # Location tokens
    STAR_SYSTEM = "<starsystem>"
    STATION_NAME = "<stationname>"
    LOCAL_DESTINATION = "<localdestination>"
    RANDOM_STAR_SYSTEM = "<randomstarsystem>"

    # Status tokens
    FUEL_LEVELS = "<fuellevels>"  # Percentage

    # Dialogue tokens
    FLIGHT_NUM = "<flightnum>"
    OTHER_CALLSIGN = "<othercallsign>"
    SHIP_CORPORATION = "<shipCorporation>"
```

### Tests to Write First

**File:** `tests/unit/test_edcopilot_tokens.py`

```python
def test_token_format_is_lowercase():
    """All tokens must use lowercase format per authoritative files."""
    assert EDCoPilotTokens.CMDR_NAME == "<cmdrname>"
    assert EDCoPilotTokens.STAR_SYSTEM == "<starsystem>"
    assert EDCoPilotTokens.STATION_NAME == "<stationname>"

def test_no_titlecase_tokens():
    """Verify old TitleCase tokens are removed."""
    with pytest.raises(AttributeError):
        _ = EDCoPilotTokens.COMMANDER_NAME  # Old name
    with pytest.raises(AttributeError):
        _ = EDCoPilotTokens.SYSTEM_NAME  # Old name
```

### Implementation Steps

1. Create new `EDCoPilotTokens` class with lowercase names
2. Deprecate old token names (keep for backwards compat temporarily)
3. Update token replacement in generator to map both old→new
4. Run tests - should pass

### Success Criteria
- All token tests pass
- Token names match authoritative format exactly
- Backwards compatibility maintained (for now)

---

## Phase 2: Space Conversation System

### Objective
Create conversation block infrastructure for Space Chatter (multi-speaker dialogues).

### Contracts (Data Structures)

#### New: `SpaceRole` Enum
```python
class SpaceRole(Enum):
    """Speaker roles for space chatter conversations."""
    SHIP1 = "[<ship1>]"
    SHIP2 = "[<ship2>]"
    SHIP3 = "[<ship3>]"
    SHIP4 = "[<ship4>]"
    STATION = "[<stationname>]"
```

#### New: `SpaceConversation` Data Class
```python
@dataclass
class SpaceConversation:
    """Multi-speaker conversation for space chatter."""
    dialogue_lines: List[Tuple[SpaceRole, str]]  # (speaker, text) pairs
    conditions: Optional[str] = None  # "(not-deep-space)" format

    def format_for_edcopilot(self) -> str:
        """Format as [example] block with speaker roles."""
        lines = []

        # Add condition to [example] tag if present
        if self.conditions:
            lines.append(f"[example] {self.conditions}")
        else:
            lines.append("[example]")

        # Add dialogue lines with speaker roles
        for speaker, text in self.dialogue_lines:
            lines.append(f"{speaker.value} {text}")

        # Close conversation
        lines.append("[\\example]")

        return "\n".join(lines)
```

### Tests to Write First

**File:** `tests/unit/test_space_conversation.py`

```python
def test_space_conversation_basic_format():
    """Test conversation block structure matches authoritative format."""
    conv = SpaceConversation(
        dialogue_lines=[
            (SpaceRole.SHIP1, "Requesting docking."),
            (SpaceRole.STATION, "Cleared to land.")
        ]
    )

    result = conv.format_for_edcopilot()

    assert result == (
        "[example]\n"
        "[<ship1>] Requesting docking.\n"
        "[<stationname>] Cleared to land.\n"
        "[\\example]"
    )

def test_space_conversation_with_condition():
    """Test conditional conversations use inline format."""
    conv = SpaceConversation(
        dialogue_lines=[
            (SpaceRole.SHIP1, "Deep space operations."),
        ],
        conditions="(not-deep-space)"
    )

    result = conv.format_for_edcopilot()

    assert "[example] (not-deep-space)" in result

def test_space_conversation_with_tokens():
    """Test tokens are preserved in dialogue."""
    conv = SpaceConversation(
        dialogue_lines=[
            (SpaceRole.SHIP1, f"{EDCoPilotTokens.STATION_NAME} control, requesting docking."),
            (SpaceRole.STATION, f"{EDCoPilotTokens.CALLSIGN}, cleared to land.")
        ]
    )

    result = conv.format_for_edcopilot()

    assert "<stationname>" in result
    assert "<callsign>" in result
```

### Implementation Steps

1. Create `SpaceRole` enum
2. Create `SpaceConversation` dataclass
3. Implement `format_for_edcopilot()` method
4. Run tests - should pass

### Success Criteria
- All conversation tests pass
- Output matches authoritative conversation blocks exactly
- Tokens preserved in dialogue

---

## Phase 3: Space Chatter Template Rewrite

### Objective
Replace single-line format with conversation blocks in `SpaceChatterTemplate`.

### Contracts (Behavior)

#### Updated: `SpaceChatterTemplate`
```python
class SpaceChatterTemplate:
    """Generate EDCoPilot Space Chatter using conversation blocks."""

    def __init__(self):
        self.conversations: List[SpaceConversation] = []
        self.filename = "EDCoPilot.SpaceChatter.Custom.txt"

    def add_conversation(self, conversation: SpaceConversation) -> None:
        """Add a space conversation block."""
        self.conversations.append(conversation)

    def generate_navigation_conversations(self) -> None:
        """Generate docking/departing conversations."""
        # Docking request conversation
        docking_conv = SpaceConversation(
            dialogue_lines=[
                (SpaceRole.SHIP1, f"{EDCoPilotTokens.STATION_NAME} control, requesting docking clearance."),
                (SpaceRole.STATION, f"{EDCoPilotTokens.CALLSIGN}, this is {EDCoPilotTokens.STATION_NAME} control. Sending landing pad now."),
                (SpaceRole.SHIP1, "Copy that, proceeding to pad.")
            ]
        )
        self.conversations.append(docking_conv)

        # Add more conversations...

    def to_file_content(self) -> str:
        """Generate file content WITHOUT comments."""
        lines = []

        # NO HEADER COMMENTS - EDCoPilot doesn't support them

        for conversation in self.conversations:
            lines.append(conversation.format_for_edcopilot())
            lines.append("")  # Blank line between conversations

        return "\n".join(lines)
```

### Tests to Write First

**File:** `tests/unit/test_space_chatter_template.py`

```python
def test_space_chatter_template_no_comments():
    """Space chatter must not contain any comment lines."""
    template = SpaceChatterTemplate()
    template.generate_navigation_conversations()

    content = template.to_file_content()

    # No lines should start with #
    for line in content.split("\n"):
        assert not line.strip().startswith("#"), f"Found comment line: {line}"

def test_space_chatter_uses_conversation_blocks():
    """All space chatter must use [example] conversation blocks."""
    template = SpaceChatterTemplate()
    template.generate_navigation_conversations()

    content = template.to_file_content()

    # Should have [example] and [\example] markers
    assert "[example]" in content
    assert "[\\example]" in content

def test_space_chatter_has_speaker_roles():
    """All dialogue must have speaker role tags."""
    template = SpaceChatterTemplate()
    template.generate_navigation_conversations()

    content = template.to_file_content()

    # Should have speaker roles
    assert "[<ship1>]" in content or "[<stationname>]" in content

def test_space_chatter_uses_lowercase_tokens():
    """Tokens must use lowercase format."""
    template = SpaceChatterTemplate()
    template.generate_navigation_conversations()

    content = template.to_file_content()

    # Should have lowercase tokens
    assert "<stationname>" in content or "<callsign>" in content
    # Should NOT have TitleCase tokens
    assert "<StationName>" not in content
    assert "<SystemName>" not in content

def test_generated_space_chatter_matches_authoritative_structure():
    """Generated content should match structure of authoritative files."""
    template = SpaceChatterTemplate()
    template.generate_navigation_conversations()

    content = template.to_file_content()
    lines = content.split("\n")

    # Find first conversation block
    example_start = None
    for i, line in enumerate(lines):
        if line.strip() == "[example]":
            example_start = i
            break

    assert example_start is not None, "No [example] block found"

    # Next non-empty line should be speaker role
    next_line = lines[example_start + 1].strip()
    assert next_line.startswith("[<"), f"Expected speaker role, got: {next_line}"
```

### Implementation Steps

1. Write all tests (they will fail)
2. Update `SpaceChatterTemplate.__init__` to use `conversations` list
3. Rewrite `generate_navigation_conversations()` to create `SpaceConversation` objects
4. Rewrite `generate_exploration_conversations()`, `generate_combat_conversations()`, etc.
5. Update `to_file_content()` to remove comments and iterate conversations
6. Run tests - should pass

### Success Criteria
- No comment lines in output
- All content uses conversation blocks
- Speaker roles present on all dialogue lines
- Tokens are lowercase
- Tests validate structure matches authoritative format

---

## Phase 4: Crew Chatter & Deep Space Chatter

### Objective
Remove comments from Crew and Deep Space chatter (they already use conversation blocks).

### Implementation Steps

1. Update `CrewChatterTemplate.to_file_content()` - remove comment header
2. Update `DeepSpaceChatterTemplate.to_file_content()` - remove comment header
3. Update crew chatter to use lowercase tokens
4. Run tests

### Tests to Write First

```python
def test_crew_chatter_no_comments():
    """Crew chatter must not contain comments."""
    template = CrewChatterTemplate()
    template.generate_default_chatter()
    content = template.to_file_content()

    for line in content.split("\n"):
        assert not line.strip().startswith("#")

def test_deep_space_chatter_no_comments():
    """Deep space chatter must not contain comments."""
    template = DeepSpaceChatterTemplate()
    template.generate_default_chatter()
    content = template.to_file_content()

    for line in content.split("\n"):
        assert not line.strip().startswith("#")
```

### Success Criteria
- No comments in any chatter file
- Crew chatter still uses conversation blocks
- Deep space chatter still uses conversation blocks

---

## Phase 5: Generator Integration

### Objective
Update generator to use new token names and ensure no comments are added.

### Implementation Steps

1. Update `EDCoPilotContentGenerator._replace_tokens_in_content()` to map old→new tokens
2. Verify `write_files()` doesn't add extra comments
3. Update any hardcoded token references in generator
4. Run integration tests

### Tests to Write First

```python
def test_generator_uses_lowercase_tokens():
    """Generator must output lowercase tokens."""
    generator = EDCoPilotContentGenerator(data_store, edcopilot_path)
    files = generator.generate_contextual_chatter()

    space_chatter = files["EDCoPilot.SpaceChatter.Custom.txt"]

    assert "<stationname>" in space_chatter or "<cmdrname>" in space_chatter
    assert "<StationName>" not in space_chatter

def test_generated_files_have_no_comments():
    """Generated files must not contain any comments."""
    generator = EDCoPilotContentGenerator(data_store, edcopilot_path)
    files = generator.generate_contextual_chatter()

    for filename, content in files.items():
        for line in content.split("\n"):
            assert not line.strip().startswith("#"), \
                f"Found comment in {filename}: {line}"
```

### Success Criteria
- Generator outputs lowercase tokens
- No comments in generated files
- Token replacement works for both old and new names

---

## Phase 6: Grammar Documentation Update

### Objective
Rewrite grammar specification to match authoritative format.

### Implementation Steps

1. Rewrite `docs/edcopilot-chatter-grammar.md`
2. Remove all references to:
   - Single-line format
   - Comment support
   - TitleCase tokens
3. Add comprehensive examples from authoritative files
4. Document conversation block structure
5. Document speaker roles

### Success Criteria
- Grammar spec matches authoritative format
- Examples are from actual EDCoPilot files
- No incorrect information

---

## Phase 7: Test Suite Validation

### Objective
Ensure all existing tests pass or are updated appropriately.

### Implementation Steps

1. Run full test suite: `venv/Scripts/python.exe scripts/run_tests.py`
2. Identify failing tests
3. Update tests that expect old format:
   - Tests expecting comments → remove comment assertions
   - Tests expecting single-line format → update to expect conversation blocks
   - Tests expecting TitleCase tokens → update to expect lowercase
4. Re-run tests until all pass

### Success Criteria
- All unit tests pass
- All integration tests pass
- Test coverage remains >90%
- No regressions in existing functionality

---

## Phase 8: Manual Validation with EDCoPilot

### Objective
Verify generated files actually work with EDCoPilot application.

### Implementation Steps

1. Generate chatter files using updated code
2. Copy to EDCoPilot custom files directory
3. Start EDCoPilot
4. Check logs for "bad line" warnings
5. Verify chatter actually plays during gameplay

### Success Criteria
- Zero "bad line" warnings in EDCoPilot logs
- Generated chatter loads successfully
- Chatter plays appropriately during gameplay

---

## Rollback Plan

If issues arise:

1. **Phase 1-3 Issues:** Revert to branch point, fix contracts
2. **Phase 4-6 Issues:** Keep token/conversation changes, roll back specific phase
3. **Critical Failure:** Mark branch as WIP, create minimal fix (just remove comments)

---

## Testing Strategy Summary

### Test Pyramid

**Unit Tests (Fast, Focused)**
- Token format validation
- Conversation block structure
- Template output format
- No comments validation

**Integration Tests (Moderate, Realistic)**
- End-to-end file generation
- Token replacement accuracy
- Multi-file generation

**Manual Tests (Slow, Comprehensive)**
- Actual EDCoPilot loading
- Gameplay validation
- Log file inspection

### Test-First Workflow

For each phase:
1. **RED:** Write failing tests defining expected behavior
2. **GREEN:** Implement minimum code to make tests pass
3. **REFACTOR:** Clean up while keeping tests green
4. **VALIDATE:** Run full suite to ensure no regressions

---

## Risk Mitigation

### High-Risk Areas

1. **Breaking Existing Tests:** Many tests expect old format
   - **Mitigation:** Update tests incrementally, phase by phase

2. **Token Replacement Compatibility:** Old code may use old token names
   - **Mitigation:** Support both old→new mapping temporarily

3. **Conversation Complexity:** Multi-speaker dialogues are more complex
   - **Mitigation:** Start with simple 2-speaker conversations, expand gradually

### Validation Checkpoints

After each phase:
- [ ] All unit tests for that phase pass
- [ ] No regressions in previous phases
- [ ] Code review for contract compliance
- [ ] Integration tests still pass

---

## Success Metrics

### Quantitative
- Zero "bad line" warnings in EDCoPilot logs (currently 40+)
- All tests pass (currently unknown how many will fail)
- Test coverage >90% (maintain current level)
- Generated files <5KB (reasonable size)

### Qualitative
- Code is maintainable and well-documented
- Contracts are clear and testable
- Format matches authoritative files exactly
- Chatter sounds natural during gameplay

---

## Timeline Estimate

| Phase | Estimated Time | Critical Path |
|-------|---------------|---------------|
| Phase 1: Tokens | 30 minutes | Yes |
| Phase 2: Conversations | 45 minutes | Yes |
| Phase 3: Space Template | 90 minutes | Yes |
| Phase 4: Other Templates | 30 minutes | No |
| Phase 5: Generator | 45 minutes | Yes |
| Phase 6: Documentation | 30 minutes | No |
| Phase 7: Test Fixes | 120 minutes | Yes |
| Phase 8: Manual Validation | 30 minutes | Yes |
| **Total** | **6-7 hours** | |

---

## Post-Implementation Tasks

1. Update CHANGELOG.md with breaking changes
2. Create migration guide for users with existing custom files
3. Update README.md examples
4. Create PR with comprehensive testing results
5. Document lessons learned in ai-directives

---

## Appendix: Contract Validation Examples

### Example Test: Conversation Block Format
```python
def test_conversation_matches_authoritative():
    """Validate output matches actual EDCoPilot file structure."""
    # Load authoritative example
    auth_example = """[example]
[<ship1>] Requesting docking.
[<stationname>] Cleared to land.
[\\example]"""

    # Generate our version
    conv = SpaceConversation(
        dialogue_lines=[
            (SpaceRole.SHIP1, "Requesting docking."),
            (SpaceRole.STATION, "Cleared to land.")
        ]
    )

    our_output = conv.format_for_edcopilot()

    # Should match exactly
    assert our_output == auth_example
```

### Example Test: No Comments Contract
```python
def test_no_comments_contract():
    """Contract: Generated files must never contain comment lines."""
    generator = EDCoPilotContentGenerator(data_store, path)
    files = generator.generate_contextual_chatter()

    for filename, content in files.items():
        lines = content.split("\n")
        comment_lines = [l for l in lines if l.strip().startswith("#")]

        assert len(comment_lines) == 0, \
            f"{filename} contains {len(comment_lines)} comment lines, expected 0"
```

---

## Conclusion

This test-first, contract-oriented approach ensures:
- Correctness: Tests validate against authoritative format
- Safety: Each phase validated before moving forward
- Maintainability: Clear contracts and comprehensive tests
- Quality: No regressions, high test coverage maintained

Estimated completion: 6-7 focused hours with this systematic approach.
