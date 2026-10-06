set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Quality ---

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'; uv run ruff check .; Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome ci .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'; uv run ruff check . --fix --unsafe-fixes; uv run ruff format .; Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome check --write .

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    uv run safety check

# --- rtorrent-mcp  common tasks  install https just systems ---

stats:
    uv run python tools/repo_stats.py

sync:
    uv sync

test *ARGS:
    uv run pytest {{ARGS}}

format:
    uv run ruff format src/rtorrent_mcp tests

check: lint test

mcpb-build:
    uv run mcpb build

run-stdio:
    uv run rtorrent-mcp

run-http:
    uv run python -m rtorrent_mcp.server --transport http

# Format Python (ruff format) — pairs with lint
fmt:
    uv run ruff format .

# Serve the HTTP API backend (port 10910, fleet engine contract: server:app ASGI)
serve:
    uv run uvicorn rtorrent_mcp.server:app --host 127.0.0.1 --port 10910

# Local five-gate CI: ruff + format-check + pytest + tsc + biome + pyright
ci:
    uv run ruff check .
    uv run ruff format . --check
    uv run pytest tests/ -q
    uv run pyright src/
    Set-Location '{{justfile_directory()}}\web_sota'; npx tsc --noEmit; npx @biomejs/biome ci src

# Playwright e2e (needs backend on :10910 + frontend dev)
e2e:
    Set-Location '{{justfile_directory()}}\web_sota'; npx playwright test

# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --extra dev; uv run pre-commit install; Set-Location '{{justfile_directory()}}\web_sota'; npm ci; Write-Host "Pre-commit hooks installed." -ForegroundColor Green
