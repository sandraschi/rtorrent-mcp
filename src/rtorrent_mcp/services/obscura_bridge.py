"""obscura_bridge.py - shared headless-browser fallback for bot-gated fetches.

Wraps the Obscura Rust engine (same one obscura-mcp wraps) so any service in
this repo can render a page past a JS unlock countdown or an anti-bot
challenge (Cloudflare, DDoS-Guard) without depending on the API layer.

Moved out of ``api/web_routes.py`` (2026-09-08) so ``services/`` code (e.g.
``annas_archive_search.py``) can use it without a backwards api-to-service
import. Behavior is unchanged from the original web_routes.py functions.
"""

import os
import shutil
import subprocess
from pathlib import Path


def obscura_bin() -> str | None:
    for c in (
        os.environ.get("RTORRENT_OBSCURA_BIN"),
        r"D:\Dev\repos\external\obscura\target\release\obscura.exe",
        r"D:\Dev\repos\external\obscura\target\debug\obscura.exe",
        shutil.which("obscura"),
    ):
        if c and os.path.exists(c):
            return c
    return None


def obscura_available() -> bool:
    if os.environ.get("RTORRENT_OBSCURA_FALLBACK", "").lower() in ("0", "false", "no", "off"):
        return False
    return obscura_bin() is not None


def obscura_render(url: str, timeout: int = 45) -> str:
    """Render a page past its JS unlock/challenge using the Obscura engine."""
    binary = obscura_bin()
    if not binary:
        raise FileNotFoundError("Obscura binary not found")
    cmd = [
        binary,
        "fetch",
        url,
        "--dump",
        "html",
        "--wait-until",
        "networkidle0",
        "--stealth",
        "--timeout",
        str(timeout),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15)
    return result.stdout or ""


def obscura_download(url: str, dest: Path, timeout: int = 180) -> bool:
    """Download ``url`` to ``dest`` binary-safely via Obscura. Returns True on success."""
    binary = obscura_bin()
    if not binary:
        return False
    cmd = [binary, "fetch", url, "--dump", "original", "--stealth", "--timeout", str(timeout), "-o", str(dest)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 20)
    if result.returncode != 0:
        return False
    if not dest.exists() or dest.stat().st_size == 0:
        return False
    return not _looks_like_html(dest)


def _looks_like_html(path: Path, sample: int = 512) -> bool:
    try:
        with open(path, "rb") as fh:
            head = fh.read(sample).lower()
    except OSError:
        return True
    stripped = head.lstrip()
    return stripped.startswith(b"<!doctype") or stripped.startswith(b"<html") or b"<?xml" in head[:256]
