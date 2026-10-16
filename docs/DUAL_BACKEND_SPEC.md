# SPEC: dual torrent backend (rTorrent + qBittorrent)

**Status:** spec (no code yet — approved plan required before implementation).
**Motivation:** rTorrent lives in Docker (awkward daily driver); the
maintainer dogfoods qBittorrent. qBittorrent's WebUI API (v2.15.1 @ v5.2.4,
Sept 2026) is complete for everything this repo does. The repo itself began
as a qBittorrent prototype (`qbtmcp`) before pivoting — this is a
full-circle return, not a new direction.

## 1. Competitor teardown (what we filched)

Analyzed October 2026 from live clones (see `/tmp/opencode/qb-mcp*` —
scratch copies, not vendored):

| Repo | Stars | Shape | Verdict |
|---|---|---|---|
| `pickpppcc/qbittorrent-mcp` | 27 | 14 flat tools, host/user/pass **per call** | Most popular, worst architecture. Filch: endpoint coverage checklist only (add/delete/pause/resume/trackers/limits/file-priority/tags/list/search). Reject: per-call creds (we use env singleton), flat tools (we use portmanteau), string returns. |
| `arr-mcps/qbittorrent-mcp` (SavageCore) | 3 | Single-file ~90 endpoint wrappers, grouped into **10 portmanteau tools** with `operation` enums | Best architecture — independently converged on our portmanteau pattern (their AGENTS.md cites the same token-budget rationale). **Filch:** (a) full endpoint inventory as our client coverage checklist (app/log/sync/transfer/torrents/search/rss groups); (b) `sync/maindata?rid=` delta polling for completion detection (better than blind polling); (c) cookie-session with lazy login + re-auth on 403; (d) API-key auth (qBittorrent ≥ v5.2.0) preferred over user/pass; (e) their `test_live.py` pattern (env-gated live tests). |
| `nicholaswilde/qbittorrent-mcp-rs` | 9 | Rust, Docker image | Filch: nothing code-wise (different stack); note as proof Docker-first distribution works for this category. |
| `Knuckles-Team/qbittorrent-agent` | — | Production agent + MCP | Filch: the agent-over-tools shape validates our `agentic_rtorrent_workflow`; no code taken. |

**Filch list (concrete):** 90-endpoint coverage checklist; `sync/maindata`
delta polling; lazy cookie-session + API-key auth; `/torrents/setShareLimits`
per-torrent + `/app/setPreferences` global share limits (this is the
programmatic no-seed enforcement — see §4); categories/tags mapping to our
post-processing routing; env-gated live tests.

## 2. Architecture

- **Selection:** `TORRENT_BACKEND=rtorrent|qbittorrent` (default `rtorrent`
  — no behavior change for existing installs). Invalid value fails fast at
  startup with the valid set named.
- **Seam:** new `src/rtorrent_mcp/services/torrent_backend.py` defining the
  `TorrentBackend` protocol (the ~10 methods tools actually use):
  `connect`, `get_torrents`, `add_torrent`, `pause_torrent`,
  `resume_torrent`, `delete_torrent`, `get_torrent_base_path`,
  `get_torrent_directory`, `is_torrent_complete`, plus
  `enforce_no_seed()` (backend-specific) and `backend_name`.
- **Implementations:** existing `RTorrentClient` adapted to the protocol
  (no behavior change); new `QBittorrentClient` (`services/qbittorrent_client.py`,
  httpx + cookie jar, API key preferred, user/pass fallback).
- **Tools above the seam stay untouched:** `torrent_management`,
  `post_processor`, `media_integrator` talk to the protocol, never to
  XML-RPC or WebUI directly. The two `client.server` escape hatches in
  `post_processor.py` get protocol methods instead (no raw-protocol leaks).
- **WebUI base:** `QBITTORRENT_URL` (default `http://localhost:8080`),
  `QBITTORRENT_API_KEY` (preferred), `QBITTORRENT_USERNAME/PASSWORD`
  (fallback). All in `.env.example` + `settings.py` + docs.

## 3. No-seed enforcement per backend (non-negotiable, both must hold)

- **rTorrent (shipped):** `event.download.finished,stop_completed` in
  `config/rtorrent.rc` + `DELETE_TORRENT_AFTER_COMPLETE=True`.
- **qBittorrent (new):** on connect, set global share limits via
  `/app/setPreferences` (`max_ratio_enabled=true, max_ratio=0` semantics
  verified live — exact keys confirmed against the running instance during
  P1, never assumed), AND set per-torrent share limits via
  `/torrents/setShareLimits` on every add (ratio 0 / seeding-time 1 min),
  AND keep `DELETE_TORRENT_AFTER_COMPLETE` removal after processing.
  `enforce_no_seed()` performs the global step and is re-run on every
  client (re)connect so restarts can't silently re-enable seeding.
- **Proof:** P2 gate includes a live test against the maintainer's
  qBittorrent: add → complete → assert stopped within poll window →
  processed → removed. No parroting "it should work."

## 4. Completion detection

rTorrent path keeps polling (`is_torrent_complete`, `progress >= 99.9%`).
qBittorrent path uses `sync/maindata?rid=` deltas (filched from arr-mcps):
track `rid`, treat `torrents` entries with `progress == 1` /
`state == "uploading"|"stalledUP"|"pausedUP"` as completion candidates,
confirm via `torrents/properties`. Same `check_completed`/`process` tool
surface; different detection underneath.

## 5. Phases

- **P0 — client + seam.** `torrent_backend.py` protocol;
  `qbittorrent_client.py` with auth (key → user/pass → re-login on 403);
  unit tests with httpx MockTransport (mirror existing mock style) +
  env-gated live tests (`tests/test_qbittorrent_live.py`, skipped without
  `QBITTORRENT_TEST_URL`). RTorrentClient untouched behaviorally.
- **P1 — tools above the seam.** Backend factory
  (`get_torrent_backend()` reading `TORRENT_BACKEND`); `torrent_management`
  + `post_processor` + `media_integrator` consume the protocol; remove the
  two `client.server` escape hatches. Full existing suite must stay green.
- **P2 — no-seed proof + docs.** Live no-seed test on the maintainer's
  instance; README backend switch section; help page backend card;
  AGENTS.md cross-connect update; `legal_management` `status` reports
  active backend + no-seed state.
- **P3 (deferred, not this build):** qBittorrent search plugins + RSS API
  as `search_management` backends; Usenet/BREIN-specific notes; Docker
  Compose variant with qBittorrent instead of rTorrent.

## 6. Non-goals

No migration of existing rTorrent installs. No breaking change to any tool
signature or REST route. No feature parity with all 90 arr-mcps endpoints —
client covers the seam + share limits + completion; the rest on demand.
No private-tracker ratio support (incompatible with no-seed by design;
documented, not apologized for).

## 7. Open questions for the maintainer (answer before P0)

1. qBittorrent version + WebUI credentials on your machine (API key
   available, or user/pass)? — **Answered 2026-10-16: v5.1.4 native exe
   (`C:\Program Files\qBittorrent\qbittorrent.exe`), not currently running.
   v5.1.x predates API-key auth (needs ≥ v5.2.0) → P0 implements cookie
   session with lazy login + re-auth on 403; API-key path added when the
   maintainer upgrades past 5.2. Still needed before P0 live tests: WebUI
   port (default 8080?) + credentials in local `.env` (never in chat).
2. Default backend stays `rtorrent`? (Recommended: yes.) — **Answered:
   yes, stays for now.**
3. Docker Compose qBittorrent variant wanted in P2, or later? —
   **Answered: no. qBittorrent runs as a native Windows exe; a compose
   variant would add Docker awkwardness back for zero benefit. P2 covers
   native only.**

## 8. P2 live proof (2026-10-16, maintainer's v5.1.4 @ 127.0.0.1:18080)

Proven end to end with a Debian 13.7.0 netinst torrent (lawful, ~700 MB):

- `enforce_no_seed()`: global `max_seeding_time` 3 → 1 min, read-back verified.
- Upload-add of `.torrent` bytes → hash found → completed in 30 s.
- Post-complete state went `stalledUP` → `stoppedUP` **60 s after
  completion** — the 1-minute cap firing exactly on schedule. No-seed lag: 60 s.
- `delete_torrent(delete_files=True)` → client empty again.

Two findings baked in: (a) qBittorrent URL-adds fail on picky hosts
(archive.org 401s its fetcher while browsers pass) — `.torrent` file
upload is the robust path, and `add_torrent` callers should prefer it;
(b) in-download piece uploads are protocol, not policy — the caps govern
only the post-completion tail, exactly as documented.
