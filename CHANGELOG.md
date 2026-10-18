# Changelog

All notable changes to the Elite Dangerous Local AI Tie-In MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Configurable EDCoPilot themes directory. New setting `edcopilot_themes_path`
  (environment variable `ELITE_EDCOPILOT_THEMES_PATH`) and headless CLI flag
  `--edcopilot-themes-path`. When the specified directory is empty it is seeded
  with a copy of the bundled `edcopilot_themes` contents; when unset, the bundled
  directory is used as before. The MCP theme tools and the CLI now honour it.
- Initial project structure and configuration
- Basic MCP server framework setup
- Journal monitoring system foundation
- EDCoPilot integration framework
- Comprehensive testing infrastructure
- Documentation and setup guides

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2024-09-06

### Added
- Initial project repository setup
- Core dependencies and build configuration
- Python project structure with modular design
- Basic documentation and setup instructions
- Development workflow and testing framework
- Git configuration and ignore patterns

### Notes
- This is the initial release with basic project structure
- MCP server functionality to be implemented in subsequent releases
- Elite Dangerous journal monitoring to be added in future versions
- EDCoPilot integration planned for upcoming milestones

---

**Legend:**
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities
