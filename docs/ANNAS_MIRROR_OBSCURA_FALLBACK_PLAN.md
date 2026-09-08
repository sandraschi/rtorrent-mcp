# Plan: Obscura fallback for bot-gated Anna's Archive mirrors

**Status:** Scoped, not implemented
**Scoped:** 2026-09-08
**Trigger:** User confirms `.gl` (Greenland) works as a mirror alongside `.is`
(Iceland) in a real browser; a plain HTTP probe of `.gl` returns `403
DDoS-Guard` (see [BUG-032](../../mcp-central-docs/troubleshooting/details/BUG-032_Annas_Archive_Selector_Rot_Fake_Success.md)
for the selector-drift fix that preceded this).

## Problem

`ANNAS_ARCHIVE_MIRRORS` lists four domains (`is,gl,li,org`), but only `.is`
actually returns usable HTML to a plain `aiohttp` GET. Confirmed by direct
probe:

| Mirror | Plain HTTP result |
|---|---|
| `.is` | `200`, real results page, no challenge markers |
| `.gl` | `302` self-redirect to `?check=1`, then **`403 DDoS-Guard`** |
| `.li` | Cloudflare + fingerprint anti-bot gate (per existing code comment) |
| `.org` | `NXDOMAIN` (per existing code comment) |

`.gl` works for the user in a real browser because DDoS-Guard's challenge is
a JS/cookie check a headless HTTP client can't pass — not because the mirror
itself is down. `search_annas_archive()`'s mirror-failover loop currently
just skips a mirror on non-200 and tries the next; `.gl` and `.li` are
permanently dead weight in that loop rather than usable fallbacks.

## What already exists (reuse, don't rebuild)

`src/rtorrent_mcp/api/web_routes.py` already drives the Obscura Rust engine
for exactly this problem, but only on the **detail/download** path (Anna's
Archive slow-mirror unlock countdown pages), never on **search**:

```python
_obscura_bin() -> str | None          # binary discovery, 3 fallback paths + env override
_obscura_available() -> bool          # env kill-switch: RTORRENT_OBSCURA_FALLBACK=0
_obscura_render(url, timeout=45) -> str   # subprocess: obscura fetch <url> --dump html --stealth --wait-until networkidle0
_obscura_download(url, dest, timeout=180) -> bool  # binary-safe file fetch
```

Call sites: `web_routes.py:814-853`, inside the download-unlock flow only.
~12x faster / ~6x lighter than Chromium per obscura-mcp's own README, with
Chrome-145 TLS fingerprinting specifically built to pass Cloudflare-class
challenges — the right tool, just not wired to search.

## Proposed change

### 1. Relocate the four helpers out of the API layer

They currently live in `api/web_routes.py`, but the consumer
(`services/annas_archive_search.py`) is a layer below the API — importing
from `web_routes` into a service would be a backwards dependency. Move
`_obscura_bin` / `_obscura_available` / `_obscura_render` / `_obscura_download`
verbatim into a new `services/obscura_bridge.py`; have `web_routes.py` import
them from there. Pure move, zero behavior change to the existing
download/unlock flow.

### 2. Add a bot-gate detector

```python
_CHALLENGE_MARKERS = ("ddos-guard", "just a moment", "attention required", "checking your browser", "cf-chl")

def _looks_bot_gated(status: int, html: str) -> bool:
    if status in (403, 503):
        return True
    head = html[:2000].lower()
    return any(m in head for m in _CHALLENGE_MARKERS)
```

### 3. Wire the fallback into `_search_annas_on`

After the existing `aiohttp` fetch, if `_looks_bot_gated(...)` and
`_obscura_available()`: re-fetch the **same URL** via `_obscura_render()`
and feed its HTML into the same (already-fixed, post-BUG-032) BeautifulSoup
parsing path — no second parser to maintain, the fix already applies to
whatever HTML string it's given.

```
aiohttp GET  ──200, clean──────────────────────────► parse (fast path, unchanged)
             ──403/503/challenge markers──► Obscura available?
                                                  │yes → obscura fetch --stealth → parse
                                                  │no  → treat as mirror failure, next mirror
```

### 4. Keep mirror order as-is

`.is` stays first — it's free (no subprocess spawn) and already correct.
Obscura's cost is only paid for `.gl`/`.li` when `.is` comes up empty, which
also keeps the common case fast.

### 5. Timeout budget needs its own number, not the download default

`_obscura_render`'s existing 45s default was tuned for the download/unlock
flow, which the user isn't blocking a chat response on. Search is
interactive — recommend starting at 20s for the search path specifically
(pass an explicit `timeout=` rather than reusing the default) and adjusting
from real latency once it's running.

### 6. No regression when Obscura isn't installed

`_obscura_available()` already returns `False` cleanly when the binary isn't
found or `RTORRENT_OBSCURA_FALLBACK=0` — environments without the Rust
engine keep today's behavior (skip the gated mirror, land on `.is`).

## Out of scope for this pass

- `.li` — not confirmed working by the user (only `.gl` + `.is` were).
  Same code path would cover it once wired, but don't specifically verify.
- `.org` — `NXDOMAIN`, not a bot-gate problem, Obscura doesn't help.
- Session-cookie-based bypass (`ANNAS_SESSION_COOKIE`) — orthogonal; already
  exists for the donor/member fast-download path, unrelated to this gate.

## Testing

No existing test file covers `annas_archive_search.py` (checked; none
exists). The CSS-selector drift just found and fixed (BUG-032) went
undetected for however long because nothing asserted the search path
actually returns real results for a known-good query. Recommend a smoke
test alongside this change: known public-domain title → `.is` fast path
returns `count > 0` with real titles; a forced-gated mirror (mock or `.gl`
directly) → Obscura fallback fires and also returns real titles, not the
`403`/challenge page contents.
