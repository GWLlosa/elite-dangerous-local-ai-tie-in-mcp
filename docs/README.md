# Documentation

This directory contains comprehensive documentation for the Elite Dangerous Local AI Tie-In MCP project.

## 📚 Available Documentation

### [`TESTING_GUIDE.md`](TESTING_GUIDE.md)
**Complete testing and setup guide**

**Features:**
- ✅ **Automated setup** with script instructions
- ✅ **Manual setup** with step-by-step PowerShell commands
- ✅ **Troubleshooting** section for common issues
- ✅ **Validation checklist** to verify functionality
- ✅ **Performance testing** and coverage reporting

**When to use:**
- First time project setup
- Verifying development environment
- Troubleshooting dependency issues
- Validating test coverage and functionality

### [`CHATGPT_CODEX_INTEGRATION.md`](CHATGPT_CODEX_INTEGRATION.md)
**Use with ChatGPT/Codex via MCP clients**

**Features:**
- ChatGPT‑class model integration through MCP‑capable clients (Continue, Cursor, Cline)
- One‑time configuration with `mcpServers` command/args/env
- Usage examples and troubleshooting

**When to use:**
- You want Claude‑level MCP functionality with ChatGPT models
- You use VS Code/JetBrains (Continue), Cursor, or Cline

### Additional Documentation (Future)
- **API Reference** - MCP tools, resources, and prompts documentation
- **Configuration Guide** - Detailed configuration options and examples
- **Development Guide** - Contributing guidelines and architecture overview
- **Integration Guide** - Claude Desktop and EDCoPilot setup instructions

## 🚀 Quick Navigation

### For New Users:
1. **Start here**: [Testing Guide - Automated Setup](TESTING_GUIDE.md#automated-testing-recommended)
2. **Run**: `python scripts/setup_dependencies.py`
3. **Test**: `python scripts/run_tests.py`

### For Developers:
1. **Setup**: Follow [Manual Testing Instructions](TESTING_GUIDE.md#manual-testing-instructions)
2. **Validate**: Use [Validation Checklist](TESTING_GUIDE.md#manual-step-12-validation-checklist)
3. **Troubleshoot**: Check [Common Issues](TESTING_GUIDE.md#manual-step-10-troubleshooting-common-issues)

### For Troubleshooting:
1. **Check dependencies**: `python scripts/check_dependencies.py`
2. **Review**: [Troubleshooting section](TESTING_GUIDE.md#troubleshooting-common-issues)
3. **Fix**: `python scripts/setup_dependencies.py`

### For ChatGPT/Codex Users:
- See: [`CHATGPT_CODEX_INTEGRATION.md`](CHATGPT_CODEX_INTEGRATION.md)

## 🔗 Related Resources

- **[Scripts Documentation](../scripts/README.md)** - Automation script details
- **[Project README](../README.md)** - Main project overview and quick start
- **[Milestone Status Documents](../)** - Implementation progress tracking
- **[Source Code](../src/)** - Implementation with inline documentation

## 📋 Documentation Standards

All documentation in this project follows these principles:

- ✅ **Clear step-by-step instructions** with expected outputs
- ✅ **Cross-platform compatibility** (Windows, Linux, macOS)
- ✅ **Comprehensive error handling** and troubleshooting
- ✅ **Automated alternatives** where possible
- ✅ **Regular updates** to match implementation progress

## 🆘 Getting Help

If documentation doesn't answer your question:

1. **Run diagnostics**: `python scripts/check_dependencies.py`
2. **Check error messages** - they include specific remediation steps
3. **Verify prerequisites** - Python 3.9+, Git, and virtual environment
4. **Review troubleshooting** sections in relevant guides

Most issues can be resolved by ensuring you're in the project root directory and have activated the virtual environment correctly.
