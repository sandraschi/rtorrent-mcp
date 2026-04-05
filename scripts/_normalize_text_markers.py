"""Normalize stray variation selectors and common emoji to ASCII markers (run from repo root)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    "target",
    ".venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    "htmlcov",
    ".windsurf",
}
# Archived template bundle; keep edits minimal unless we bulk-convert later
SKIP_UNDER = {"docs/github"}

REPLACEMENTS: list[tuple[str, str]] = [
    ("### \ufe0f ", "### "),
    ("## \ufe0f ", "## "),
    ("## Configuration \ufe0f", "## Configuration"),
    ("echo \ufe0f  ", "echo [i]  "),
    ('print("\ufe0f  ', 'print("[i]  '),
    ('Write-Host "\ufe0f  ', 'Write-Host "[i]  '),
    ("[skip]  ", "[skip]  "),
    ("[OK]", "[OK]"),
    ("[NO]", "[NO]"),
    ("[WARN]", "[WARN]"),
    ("[stat]", "[stat]"),
    ("[tip]", "[tip]"),
    ("(AT)", "(AT)"),
]


def collapse_markdown_heading_spaces(text: str) -> str:
    """After removing decorative symbols, fix `##  Title` -> `## Title`."""
    return re.sub(r"^(#{1,6})\s{2,}", r"\1 ", text, flags=re.MULTILINE)


def should_process(path: Path) -> bool:
    if path.suffix.lower() not in {".md", ".py", ".bat", ".ps1", ".json"}:
        return False
    parts = set(path.parts)
    if SKIP_DIRS & parts:
        return False
    rel = path.relative_to(ROOT)
    try:
        rel.as_posix().split("/")
    except ValueError:
        return False
    s = rel.as_posix()
    if any(s.startswith(p + "/") or s == p for p in SKIP_UNDER):
        return False
    return True


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*")):
        try:
            if not path.is_file():
                continue
        except OSError:
            continue
        if not should_process(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new = text
        for old, repl in REPLACEMENTS:
            new = new.replace(old, repl)
        new = collapse_markdown_heading_spaces(new)
        if new != text:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
            print(path.relative_to(ROOT))
    print(f"Updated {changed} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
