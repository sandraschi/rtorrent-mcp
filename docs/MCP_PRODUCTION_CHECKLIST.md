# MCP Server Production Audit Checklist

Use this checklist as a **self-review** before calling a server “production-ready” for *your* environment. It is not a guarantee or external audit.

## CORE MCP ARCHITECTURE

- [x] FastMCP 2.12+ framework implemented
- [x] stdio protocol for Claude Desktop connection
- [x] Proper tool registration with `@mcp.tool()` multiline decorators
- [x] No `"""` inside `"""` delimited decorators
- [x] Self-documenting tool descriptions present
- [x] **Multilevel help tool** implemented
- [x] **Status tool** implemented
- [x] **Health check tool** implemented
- [x] `prompts/` folder with example prompt templates

## CODE QUALITY

- [x] ALL `print()` / `console.log()` replaced with structured logging
- [x] Comprehensive error handling (try/catch everywhere)
- [x] Graceful degradation on failures
- [x] Type hints (Python) / TypeScript types throughout
- [x] Input validation on ALL tool parameters
- [x] Proper resource cleanup (connections, files, processes)
- [x] No memory leaks (verified)

## PACKAGING & DISTRIBUTION

- [x] Anthropic `mcpb validate` passes successfully
- [x] Anthropic `mcpb pack` creates valid package
- [x] Package includes ALL dependencies (not just code)
- [x] Claude Desktop config example in README
- [x] Virtual environment setup script (`venv` for Python)
- [x] Installation instructions tested and working

## TESTING

- [x] Unit tests in `tests/unit/` covering all tools
- [x] Integration tests in `tests/integration/`
- [x] Test fixtures and mocks created
- [x] Coverage reporting configured (target: >80%)
- [x] PowerShell test runner scripts present
- [x] All tests passing

## DOCUMENTATION

- [x] README.md updated: features, installation, usage, troubleshooting
- [x] PRD updated with current capabilities
- [x] API documentation for all tools
- [x] `CHANGELOG.md` following Keep a Changelog format
- [x] Wiki pages: architecture, development guide, FAQ
- [x] `CONTRIBUTING.md` with contribution guidelines
- [x] `SECURITY.md` with security policy

## GITHUB INFRASTRUCTURE

- [x] CI/CD workflows in `.github/workflows/`: test, lint, build, release
- [x] Dependabot configured for dependency updates
- [x] Issue templates created
- [x] PR templates created
- [x] Release automation with semantic versioning
- [x] Branch protection rules documented
- [ ] GitHub Actions all passing

## PLATFORM REQUIREMENTS (Windows/PowerShell)

- [x] No Linux syntax (`&&`, `||`, etc.)
- [x] PowerShell cmdlets used (`New-Item` not `mkdir`, `Copy-Item` not `cp`)
- [x] File paths use backslashes
- [x] Paths with spaces properly quoted
- [x] Cross-platform path handling (`path.join` where needed)
- [x] All PowerShell scripts tested on Windows

## EXTRAS

- [x] Example configurations for common use cases
- [x] Performance benchmarks (if applicable)
- [x] Rate limiting/quota handling (where relevant)
- [x] Secrets management documentation (env vars, config)
- [x] Error messages are user-friendly
- [x] Logging levels properly configured

## FINAL REVIEW

- [x] All dependencies up to date
- [x] No security vulnerabilities (npm audit / pip-audit)
- [x] License file present and correct
- [x] Version number follows semantic versioning
- [x] Git tags match releases
- [ ] Repository description and topics set on GitHub

---

**Total items:** 60 (example count—adjust for your repo)

**Completed:** _fill in when you run the audit_

**Auditor:** _your name / team_
**Date:** _YYYY-MM-DD_
**Repo:** rtorrent_mcp
**Status:** In progress | Ready for internal review | Deployed internally (terms defined by you)
