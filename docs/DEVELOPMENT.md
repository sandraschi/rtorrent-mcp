# Development Setup

## Tools required

```bash
# Windows (winget)
winget install astral-sh.uv
winget install Git.Git
winget install Casey.Just

# Verify
uv --version
git --version
just --version
```

## Setup

```bash
git clone https://github.com/sandraschi/rtorrent-mcp.git
cd rtorrent-mcp
uv sync --all-extras
```

## Running from source

```bash
# stdio transport (for Claude Desktop / MCP clients)
uv run python -m rtorrent_mcp.server

# HTTP transport (for the web dashboard)
uv run uvicorn rtorrent_mcp.server:app --port 10910
```

The `web_sota/` frontend (Vite + React) runs separately:

```powershell
.\web_sota\start.ps1
```

## Common tasks

```bash
just              # interactive recipe dashboard
just bootstrap    # install all dependencies
just serve        # start the backend
just web          # start the frontend
just kill-all     # clear fleet ports 10700-11000 if something's stuck
```

## Tests

```bash
# All tests (coverage gate: 55%)
uv run pytest

# Specific file, verbose
uv run pytest tests/test_media_integrator.py -v -o "addopts="

# With HTML coverage report
uv run pytest --cov=rtorrent_mcp --cov-report=html

# Playwright e2e (frontend)
cd web_sota
npx playwright test
```

Windows users can also use the PowerShell test runner:

```powershell
.\scripts\run-tests.ps1            # all tests
.\scripts\run-tests.ps1 -Coverage  # with coverage
.\scripts\run-tests.ps1 -Unit      # unit tests only
```

## Code style

```bash
uv run ruff format .          # format
uv run ruff check . --fix     # lint
uv run pyright                # type checking
uv run bandit -r src/         # security scan
uv run safety scan            # dependency vulnerability scan
```

## Building

```bash
uv build                  # build the Python wheel
uv run twine check dist/*  # validate the package
```

Native Tauri installer build: see
[`mcp-central-docs/standards/rules/tauri_nsis_building.md`](../../mcp-central-docs/standards/rules/tauri_nsis_building.md)
and the repo's `native/build.ps1`.

## CI

GitHub Actions runs lint, type check, and tests on every push — see
`.github/workflows/`. [`docs/MCP_PRODUCTION_CHECKLIST.md`](MCP_PRODUCTION_CHECKLIST.md)
is a self-review hardening checklist, not a third-party certification.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Full code standards: `mcp-central-docs/standards/` (see repo-root
[AGENTS.md](../AGENTS.md) for per-repo overrides — ports, test commands,
architecture, key files).
