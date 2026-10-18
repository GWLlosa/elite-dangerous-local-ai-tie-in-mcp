# Implementation Plan: Configurable EDCoPilot Themes Directory

## Executive Summary

**Goal:** Let the user specify the directory used for `edcopilot_themes` storage. If the
specified directory is empty, seed it first by copying the contents of the local
(repo-bundled) `edcopilot_themes` directory into it.

**Configuration surfaces:** MCP server environment variable and the headless generation CLI.

**Estimated Effort:** 3-5 hours
**Complexity:** Low-Medium
**Breaking Changes:** None - default behavior is unchanged.

---

## Current State

- `src/edcopilot/theme_storage.py` (`ThemeStorage.__init__`) stores theme data in a
  hardcoded default:
  ```python
  self.storage_path = Path.cwd() / "edcopilot_themes"
  ```
  It already accepts an optional `storage_path` argument, but no caller supplies a
  configurable path.
- `src/edcopilot/theme_mcp_tools.py` constructs `ThemeStorage()` with no argument, so
  the MCP theme tools always use the `cwd` default.
- `src/server.py` calls `os.chdir(project_root)`, so the `cwd` default currently resolves
  to the repo-bundled `edcopilot_themes/` directory (`current_theme.json`,
  `ship_configurations.json`, `theme_history.json`, `theme_presets.json`).
- `src/utils/config.py` (`EliteConfig`, Pydantic settings) already provides env-var
  driven configuration with the `ELITE_` prefix (e.g. `ELITE_EDCOPILOT_PATH`).
- `scripts/generate_edcopilot.py` has a CLI but does not touch theme storage at all; its
  `--theme` / `--context` values are informational only.

## Desired Behavior

1. A new optional config value selects the directory used for theme storage.
2. When the value is unset (`None`), behavior is exactly as today: use the repo-bundled
   `edcopilot_themes` directory, no copying.
3. When the value is set and points to a directory that does not exist or exists but is
   empty, copy the contents of the bundled local `edcopilot_themes` into it first, then
   use it for storage.
4. When the value is set and the directory already contains files, use it as-is (never
   overwrite the user's existing data).
5. The value can be supplied three ways, in precedence order (highest first):
   - CLI flag `--edcopilot-themes-path` (headless CLI only)
   - Environment variable `ELITE_EDCOPILOT_THEMES_PATH` (MCP server + CLI)
   - Default (unset) -> bundled local `edcopilot_themes`

## Design Decisions

- **New config field name:** `edcopilot_themes_path`.
  - Env var: `ELITE_EDCOPILOT_THEMES_PATH` (matches the existing `ELITE_` prefix and the
    `edcopilot_path` naming pattern).
  - Type: `Optional[Path]`, default `None`. `None` preserves current behavior.
- **Seed source:** the bundled local directory, resolved relative to the module rather than
  `cwd` so it is stable no matter where the CLI is launched:
  ```python
  Path(__file__).resolve().parents[2] / "edcopilot_themes"   # repo root
  ```
  Fall back to `Path.cwd() / "edcopilot_themes"` if the module-relative path does not
  exist (covers packaged/installed layouts). Both can be overridden in tests.
- **"Empty" definition:** the directory is missing, or `not any(path.iterdir())`. Hidden
  files count as content, so a directory containing only `.gitkeep` is not seeded.
- **Seeding only runs for a custom path.** When the resolved path equals the seed source,
  seeding is skipped (guards against copying a directory onto itself).
- **Copy semantics:** copy all contents (files and subdirectories) with metadata preserved;
  create parent directories as needed. Use `shutil.copytree(src, dst, dirs_exist_ok=True)`
  or per-entry `copy2`.
- **ASCII only, UTC only, structured error returns** per `AGENTS.md`.

---

## Phase 1: Config Field

### Objective
Add the `edcopilot_themes_path` setting to `EliteConfig`.

### Implementation Steps
1. In `src/utils/config.py`, add:
   ```python
   edcopilot_themes_path: Optional[Path] = Field(
       default=None,
       description="Optional directory for EDCoPilot theme storage; "
                   "seeded from the bundled edcopilot_themes when empty"
   )
   ```
2. Add a `@field_validator('edcopilot_themes_path', mode='before')` that:
   - returns `None` for `None`,
   - `expanduser().resolve()` for `str`/`Path`,
   - otherwise raises `ValueError`.
3. Include the field in `get_summary()` (as `str(...)` or `None`).
4. Add `ELITE_EDCOPILOT_THEMES_PATH` to the `_environment_variables` block in
   `create_sample_config()`.

### Tests (write first)
`tests/unit/test_config.py`:
- `test_edcopilot_themes_path_defaults_to_none`
- `test_edcopilot_themes_path_from_env_var` (patch `ELITE_EDCOPILOT_THEMES_PATH`)
- `test_edcopilot_themes_path_expands_user`

### Success Criteria
- Field parses from env var and file; unset stays `None`; existing config tests pass.

---

## Phase 2: ThemeStorage Seeding

### Objective
Make `ThemeStorage` seed a custom, empty directory from the bundled `edcopilot_themes`.

### Implementation Steps
1. Add module-level helpers in `src/edcopilot/theme_storage.py`:
   ```python
   THEMES_DIRNAME = "edcopilot_themes"

   def get_bundled_themes_dir() -> Path:
       """Repo-bundled edcopilot_themes directory (module-relative, cwd fallback)."""
       candidate = Path(__file__).resolve().parents[2] / THEMES_DIRNAME
       return candidate if candidate.exists() else (Path.cwd() / THEMES_DIRNAME)

   def _is_empty_dir(path: Path) -> bool:
       return (not path.exists()) or (not any(path.iterdir()))
   ```
2. Extend the constructor to `ThemeStorage(storage_path=None, seed_source=None)`:
   - `storage_path is None` -> `self.storage_path = get_bundled_themes_dir()` (no seeding).
   - `storage_path` provided -> resolve as today.
   - When `seed_source` is provided, the target is missing/empty, and the source is a
     different existing directory, copy every entry in with `_seed_from` before loading.
3. `_seed_from(source)` copies files and subdirectories without overwriting existing
   entries, logs each copy, and records `self.seeded_from`.
4. Surface `seeded_from` through `get_storage_info()` for diagnostics.

**Note on backwards compatibility:** seeding is opt-in via the explicit `seed_source`
argument rather than being default-on for any passed path. Existing callers and tests
that construct `ThemeStorage(some_dir)` keep their current (empty, non-seeded) behavior;
the config/CLI/MCP layer passes `seed_source=get_bundled_themes_dir()` to enable seeding
for user-specified directories.

### Tests (write first)
`tests/unit/test_theme_storage.py` (new class `TestThemeStorageSeeding`):
- `test_missing_custom_dir_is_created_and_seeded`
- `test_empty_custom_dir_is_seeded`
- `test_custom_dir_with_existing_files_is_not_overwritten`
- `test_no_seeding_without_seed_source`
- `test_self_copy_is_skipped`
- `test_missing_seed_source_is_ignored`
- `test_storage_info_reports_seed_source`
- `test_storage_info_seeded_from_none`

### Success Criteria
- Seeding happens only for empty/missing custom dirs; existing data is never modified;
  all new tests pass with >90% coverage on the new code.

---

## Phase 3: Wire Config into Theme MCP Tools

### Objective
Have the MCP theme tools honor the configured directory.

### Implementation Steps
1. In `src/edcopilot/theme_mcp_tools.py`:
   - `ThemeMCPTools.__init__` already calls `load_config()`. Move/reuse that call so the
     config is loaded once, then build storage with the configured path:
     ```python
     config = load_config()
     themes_path = config.edcopilot_themes_path  # Optional[Path]
     self.theme_storage = ThemeStorage(themes_path)
     self.theme_generator = ThemeGenerator(self.theme_storage)
     self.edcopilot_generator = EDCoPilotGenerator(
         data_store, config.edcopilot_path, theme_storage=self.theme_storage
     )
     ```
   - Passing `theme_storage` into the generator is optional but makes themed generation
     consistent with the configured directory.
2. Ensure `get_theme_status()` continues to report the resolved storage path (already via
   `get_storage_info()`), now including the seed source.

### Tests (write first)
`tests/unit/test_theme_mcp_tools.py`:
- `test_theme_tools_use_configured_themes_path` (patch env var, assert
  `tools.theme_storage.storage_path` matches and is seeded)
- Existing tests that inject `tool.theme_storage` must still pass.

### Success Criteria
- MCP theme tools read the env var and use the configured directory; no regressions.

---

## Phase 4: CLI Flag

### Objective
Expose the same option on the headless CLI.

### Implementation Steps
1. In `scripts/generate_edcopilot.py` (`parse_args`), add:
   ```python
   parser.add_argument(
       "--edcopilot-themes-path",
       dest="edcopilot_themes_path",
       type=str,
       help="Directory for EDCoPilot theme storage (seeded from local edcopilot_themes when empty)",
   )
   ```
2. In `main()`:
   - Resolve precedence: CLI flag -> `config.edcopilot_themes_path` -> unset.
   - When a path is resolved, build `ThemeStorage(path)` and pass it through.
3. Thread `theme_storage` into `generate_and_write(...)` and construct the generator as
   `EDCoPilotContentGenerator(data_store, output_dir, theme_storage=theme_storage)` so the
   resolved theme is applied to generated chatter. When unset, pass `None` (unchanged
   output).
4. Log the resolved themes directory and whether seeding occurred.

### Tests (write first)
`tests/unit/test_generate_edcopilot_cli.py` (or extend the existing CLI test module):
- `test_cli_defaults_themes_path_to_none`
- `test_cli_accepts_edcopilot_themes_path_flag`
- `test_cli_env_var_used_when_flag_absent`
- `test_generate_and_write_accepts_theme_storage` (mock generator)

### Success Criteria
- `--edcopilot-themes-path` is parsed and takes precedence over the env var; unset keeps
  current behavior.

---

## Phase 5: Documentation

### Objective
Document the new option and precedence.

### Implementation Steps
1. `README.md`: add `ELITE_EDCOPILOT_THEMES_PATH` to the environment variables list and to
   the `claude_desktop_config.json` `env` example.
2. `docs/HEADLESS_CLI.md`: add `--edcopilot-themes-path PATH` under "Paths" plus an example.
3. `docs/THEME_SYSTEM_GUIDE.md`: short section explaining the configurable storage
   directory and empty-directory seeding behavior.
4. `CHANGELOG.md`: add an entry describing the new option (no breaking change).
5. Per the AGENTS documentation protocol, if this is treated as a rule change, mirror the
   relevant lines into `.cursorrules` and `ai-directives/`. Since this is a feature (not a
   binding rule), a note in `ai-directives/README.md` or a session report is sufficient.

---

## Phase 6: Full Validation

1. `python scripts/check_dependencies.py`
2. `python scripts/run_tests.py` (or `pytest`) - all tests pass, coverage maintained >90%.
3. Manual checks:
   - MCP: set `ELITE_EDCOPILOT_THEMES_PATH` to a fresh empty dir, start the server, call
     `get_theme_status`, and confirm the directory is seeded and used.
   - CLI: `python scripts/generate_edcopilot.py --edcopilot-themes-path C:\temp\edc-themes --hours 1`
     against an empty directory and confirm seeding + generation.

---

## Rollback Plan

The change is additive and defaults to current behavior. If a problem appears, revert the
Phase 1 config field and the `ThemeStorage.__init__` branch; the MCP tools and CLI then fall
back to the existing `cwd`-relative default.

## Risk Mitigation

- **Accidental data loss on seed:** seeding only triggers when the target directory is
  missing or empty, and never when the target equals the source.
- **Wrong cwd for the seed source:** resolve the bundled directory module-relative with a
  `cwd` fallback, and allow an override for tests.
- **Test pollution:** existing tests construct `ThemeStorage(temp_dir)` directly; keep the
  seeding logic keyed on the empty check so temp dirs behave predictably. Tests that assert
  "empty storage" should use a source override that points at an empty temp dir.

## Success Metrics

- New env var and CLI flag both work and honor precedence.
- An empty specified directory is seeded with the bundled theme JSON files.
- A populated directory is used unchanged.
- Default behavior (no option set) is byte-for-byte identical to today.
- All existing tests pass; new code has >90% coverage.
