# rTorrent MCP - User Guide and Tutorials

This guide teaches you how to use rTorrent MCP in plain language. It assumes
you have the server configured (see INSTALL.md) and connected to a running
rTorrent instance. Every tutorial ends with a "Try it" example you can run
verbatim in your MCP client.

## 1. Getting Started

### 1.1 What the server does

rTorrent MCP is a bridge between an AI assistant and the rTorrent BitTorrent
client. With it, you can:

- Add torrents from magnet links (anime-first, Austrian legal context).
- Search anime on nyaa.si, movies on YTS, TV on Pirate Bay, ebooks on Anna's
  Archive, and enrich results with IMDb/TVDB metadata.
- Pause, resume, delete, and inspect torrents.
- Automatically post-process completed downloads: normalize filenames and
  move files into media ingestion folders.
- Download entire anime franchises (series, movies, OVAs, specials) in one
  coordinated workflow.
- Get plain-language legal context for Austrian copyright rules.
- Use natural language: "get me this weeks asw anime, 720p".

### 1.2 The seven tools you will use

1. `torrent_management` - everything about torrents and post-processing.
2. `search_management` - every search source behind one tool.
3. `nlp_management` - natural-language anime commands.
4. `legal_management` - Austrian legal context.
5. `system_management` - health, status, help.
6. `workflow_management` - franchise/batch/scheduled downloads.
7. `agentic_rtorrent_workflow` - let the LLM plan and execute a multi-step
   goal for you.

### 1.3 First steps

1. Verify the server is healthy:
   `system_management(action="health")`
2. Verify rTorrent connectivity:
   `torrent_management(action="status")`
3. See what is currently downloading/seeding:
   `torrent_management(action="list")`
4. Read the built-in tool catalog:
   `system_management(action="help")`

If `health` reports `rtorrent_connected: false`, rTorrent is not reachable.
Check that the rTorrent daemon is running and that `RTORRENT_HOST` /
`RTORRENT_PORT` in your `.env` match the XML-RPC endpoint (default
`http://127.0.0.1:12224/RPC2`, which the provided Docker Compose publishes).

## 2. Adding Your First Torrent

### 2.1 From a magnet link you already have

```
torrent_management(action="add", magnet_link="magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567&dn=Example+Anime")
```

The server validates the magnet format, adds the torrent, and stores the
category in rTorrent's `custom1` field. Anime is the default category; pass
`category="tv"` or `category="movies"` to route post-processing differently.

**Try it:** paste any real magnet link with `category="anime"`. The response
includes the torrent `hash` - keep it for follow-up calls.

### 2.2 Finding a magnet with search first (recommended)

Never guess a magnet link. Search, pick, then add:

```
search_management(action="anime", query="detective conan", resolution="720p", group="ASW", sort_by="seeds")
```

Pick the highest-seeded result that matches the group/resolution, then:

```
torrent_management(action="add", magnet_link="<magnet from the result>", category="anime")
```

**Try it:** search for any current anime, show the user 2-3 candidates with
title/size/seeders, and let them choose before adding.

### 2.3 After adding

```
torrent_management(action="list")
```

Look for the new row: state should be `downloading` and progress should be
rising on subsequent calls. If the torrent is missing from the list, rTorrent
may have rejected the magnet (e.g. duplicate infohash) - check the response
`message` field.

## 3. Managing Torrents

### 3.1 Pause, resume, delete

```
torrent_management(action="pause", torrent_hash="<hash>")
torrent_management(action="resume", torrent_hash="<hash>")
torrent_management(action="delete", torrent_hash="<hash>", delete_files=False)
```

Deleting with `delete_files=True` also erases the downloaded data. Always
confirm with the user before deleting, and prefer `info` first:

```
torrent_management(action="info", torrent_hash="<hash>")
```

**Try it:** list your torrents, pick one by name, `info` it, then `pause` it.
Explain the state change to the user.

### 3.2 Post-processing

When a download completes, the server can move the files into a media
ingestion folder and optionally notify Plex/Jellyfin:

1. Find completed downloads:
   `torrent_management(action="check_completed")`
2. Process one:
   `torrent_management(action="process", torrent_hash="<hash>")`
3. Notify media services:
   `torrent_management(action="notify_media")` (or per-torrent with a hash)

For fully automatic operation, start the background loop:

```
torrent_management(action="start_processing")
```

It polls every `poll_interval` seconds (configurable) and processes anything
new. Stop it anytime with `torrent_management(action="stop_processing")`.

**Try it:** after a download completes, run `check_completed`, show the user
what is ready, and ask before `process` moves files.

### 3.3 Previewing filename normalization

```
torrent_management(action="normalize", filename="[ASW] Detective Conan - 1234 [720p].mkv", category="anime")
```

Returns the normalized name without touching files:
`Detective Conan - 1234.mkv` (release-group tag stripped, spaces cleaned).

## 4. Searching

### 4.1 Anime on nyaa.si

```
search_management(action="anime", query="spy x family", resolution="1080p", group="Erai-raws")
```

Parameters worth knowing: `resolution` (480p/720p/1080p), `group` (ASW,
SubsPlease, Erai-raws, HorribleSubs, EMBER, Judas, and others), `subcategory`
(translated, raw, remux, english), `sort_by` (seeds, size, date),
`max_results` (default 20).

**Try it:** search a current-season anime with `sort_by="seeds"` and compare
the top 3 results by size/seeders for the user.

### 4.2 Manga and Japanese TV

```
search_management(action="manga", query="one piece")
search_management(action="japanese_tv", query="tonight's lineup")
```

Both use the nyaa.si backend with the same arguments as `anime`.

### 4.3 Movies on YTS

```
search_management(action="movies", query="interstellar", quality="1080p", sort_by="rating", limit=5)
```

YTS results include seeds, size, and the poster/rating where available.

### 4.4 TV on Pirate Bay - including smart queries

Plain search:

```
search_management(action="tv_shows", query="slow horses", resolution="1080p")
```

Smart search (parses conversational phrasing):

```
search_management(action="tv_smart", query="get new Only Murders in the Building episodes from piratebay")
search_management(action="tv_smart", query="find latest Slow Horses episodes")
search_management(action="tv_smart", query="download House of the Dragon from MeGusta")
```

`tv_smart` detects the show name, the "new only" intent, and quality
preferences, then applies quality scoring (MeGusta preference) and release-
group detection. Prefer it for anything phrased as a request.

### 4.5 Ebooks on Anna's Archive and Pirate Bay

```
search_management(action="ebooks_annas", query="machine learning", content_type="books", max_results=10)
search_management(action="ebooks_pb", query="programming", max_results=10)
```

To inspect a specific Anna's Archive result:

```
search_management(action="annas_detail", book_url="https://annas-archive.org/md5/<id>")
```

### 4.6 Comics

```
search_management(action="comics", query="batman", max_results=10)
```

### 4.7 IMDb and TVDB metadata

```
search_management(action="imdb_search", title="interstellar")
search_management(action="imdb", imdb_id="tt0816692")
search_management(action="tvdb", title="Slow Horses", year=2022)
```

IMDb metadata needs a free OMDb API key (`OMDB_API_KEY` in `.env`, or pass
`api_key`). TVDB needs a subscription key (`TVDB_API_KEY`). Without keys the
tools return a clear error explaining how to obtain them - they do not
silently fake data.

## 5. Natural-Language Commands

### 5.1 Parsing without executing

```
nlp_management(action="parse", text="get me this weeks asw anime 720p")
```

Returns the structured interpretation: query "asw anime", group "ASW",
resolution "720p", source inferred. Review it, then execute:

```
nlp_management(action="command", text="get me this weeks asw anime 720p")
```

### 5.2 Supported patterns

- `[get|download] <anime> <group> <resolution>` - "get spy x family erai
  raws 1080p"
- `asw <anime> <resolution>` - "asw detective conan 720p"
- German: `lade <anime> asw 720p`
- Japanese fragments are detected where the parser has coverage.

Language auto-detection (English/German/Japanese) is on by default; force it
with `nlp_management(action="command", text="...", language="de")`.

### 5.3 Getting help on patterns

```
nlp_management(action="help")
```

**Try it:** ask the user for a natural-language anime request, run `parse`,
show them the interpretation, and confirm before `command`.

## 6. Legal Context (Austria)

### 6.1 Risk check

```
legal_management(action="risk", content_type="movies", country="austria", activity="personal_download")
legal_management(action="risk", content_type="anime", country="austria", activity="seeding")
```

Returns a risk level with plain-language reasoning and suggestions.

### 6.2 Compact check and free-form advice

```
legal_management(action="check", content_type="books")
legal_management(action="advice", torrent_info={"title": "Some TV series", "action": "personal_download"})
```

### 6.3 Status

```
legal_management(action="status")
```

Shows the configured content guardrails. Remember: this is informational
context, not legal advice; laws change, verify current local law for anything
serious.

**Try it:** before downloading a Hollywood movie, run `risk` and present the
summary plus suggestions to the user.

## 7. Franchise and Batch Workflows

### 7.1 Estimate before you commit

```
workflow_management(action="estimate", anime_family="one piece", resolution="1080p", group="Erai-raws")
```

Reports expected episode count, movies, OVAs, specials, and total volume.

### 7.2 Dry-run the plan

```
workflow_management(action="franchise", anime_family="one piece", resolution="1080p", group="Erai-raws", dry_run=True)
```

Shows exactly what would be downloaded without touching rTorrent.

### 7.3 Execute

```
workflow_management(action="franchise", anime_family="one piece", resolution="1080p", group="Erai-raws", dry_run=False, rate_limit=5)
```

### 7.4 Monitor, list, cancel

```
workflow_management(action="status", workflow_id="<id>")
workflow_management(action="list")
workflow_management(action="cancel", workflow_id="<id>")
```

### 7.5 Batch series and scheduling

```
workflow_management(action="batch_series", anime_family="detective conan", include_movies=False)
workflow_management(action="schedule", anime_family="one piece", schedule_time="02:30", rate_limit=3)
```

Scheduled downloads run at the given time with a bounded concurrency.

**Try it:** run `estimate` for a franchise the user likes, present the
numbers, and ask before starting the real run.

## 8. Agentic Workflows (LLM-driven)

When sampling is enabled (Ollama at `RTORRENT_SAMPLING_BASE_URL`, or host
LLM with `RTORRENT_SAMPLING_USE_CLIENT_LLM=1`), you can hand a high-level
goal to the server and let it plan and execute:

```
agentic_rtorrent_workflow(goal="Download the latest season of Detective Conan in 1080p from ASW and start processing when complete")
```

The agent loops through search -> pick -> add -> verify on its own. Without
sampling, the tool returns a structured error with setup instructions.

**Try it:** with Ollama running (`ollama pull llama3.2` once), ask for a
simple one-anime goal and watch the multi-step execution.

## 9. The Webapp

The companion webapp (Vite on port 10911, backend REST on 10910) gives you:

- **Overview** - live API/rTorrent status, torrent KPI cards, magnet add
  form, torrent table.
- **Tools** - the portmanteau catalog.
- **Status** - connection probes.
- **App Hub** - fleet webapp discovery across the reserved port range.
- **AI Command** - chat with your chosen LLM provider (auto-detected:
  Ollama :11434, LM Studio :1234); personalities, history, export.
- **Skills** - the bundled SKILL.md rendered.
- **Settings** - LLM provider/model selection, persisted in the browser.
- **Logs** - ring-buffer log viewer with filter/export.
- **Help** - documentation.

The webapp is optional for MCP use; the `/mcp` endpoint serves all tools.

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `rtorrent_unreachable` | rTorrent not running or wrong host/port | start rTorrent; check `.env` `RTORRENT_HOST`/`RTORRENT_PORT`; `docker compose up -d` for the bundled host |
| `invalid_magnet` | malformed magnet | use a magnet from a search result |
| Search returns empty | indexer blocklist/rate limit or no results | wait and retry; try another source (YTS vs nyaa) |
| `metadata_api_key_required` | OMDb/TVDB key missing | set `OMDB_API_KEY`/`TVDB_API_KEY` in `.env` |
| Agentic tool refuses | sampling unavailable | start Ollama, `ollama pull llama3.2`, set `RTORRENT_SAMPLING_BASE_URL` |
| Webapp shows "Request failed" | backend down or no LLM | start backend on 10910; install/start Ollama or LM Studio |
| Files not moved after completion | no ingestion folder for category | set `INGESTION_ANIME_PATH`/`INGESTION_TV_PATH`/`INGESTION_MOVIES_PATH` |
| Add succeeds but no hash returned | torrent duplicate or slow load | run `list` after a few seconds |

## 11. FAQ

**Do I need Docker?** No. Docker Compose is provided only to run the rTorrent
host container easily; the server talks to any reachable rTorrent XML-RPC
endpoint.

**Is this legal advice?** No. `legal_management` provides informational
Austrian copyright context only.

**Can I use it with Claude Desktop?** Yes - stdio transport; add the
`rtorrent-mcp` command to your MCP config.

**Can I use it with Cursor?** Yes - stdio or HTTP (`http://127.0.0.1:10910/mcp`).

**Does the server download the content itself?** No - rTorrent does the
downloading. The server adds magnets, monitors, and post-processes.

**How do I reset the processed-hash memory?** Restart the server; the set is
in-memory and capped at 10000 entries.

**What happens if I delete a torrent that is mid-post-processing?** The
process action will fail gracefully with a structured error; re-run after the
deletion.

**Where do normalized files go?** Into the ingestion folder for the torrent's
category (anime/tv/movies), configured via `INGESTION_*_PATH`.

**Can the server run without a webapp?** Yes - the webapp is optional; all
functionality is exposed through the MCP tools.

**How do I upgrade?** Pull the latest release, run `uv sync`, restart. The
`.mcpb` bundle installs via Claude Desktop's MCPB flow.

**Does it work with a VPN?** It works over whatever network rTorrent can
reach; legal/risk context is unaffected by network topology.

## 12. Advanced Torrent Management

### 12.1 Working with categories

Categories control both search defaults and post-processing routing. The
built-in categories are `anime` (default), `tv`, and `movies`. When you add a
torrent you choose its category; when it completes, `process` moves its files
into the matching ingestion folder. This means a well-categorized library
stays tidy without manual file moves.

```
torrent_management(action="add", magnet_link="magnet:?xt=urn:btih:...", category="tv")
torrent_management(action="add", magnet_link="magnet:?xt=urn:btih:...", category="movies")
```

**Try it:** the next time you add content, deliberately assign the correct
category and later verify with `list` that the custom field stuck (the
response echoes the category).

### 12.2 State semantics

rTorrent states map to friendly labels: `stopped`, `downloading`, `seeding`,
`hashing`, `paused`. `list` returns the raw state integer plus progress; the
webapp translates them for humans. When progress sits at 0 with state
"downloading", the torrent is fetching metadata from peers; give it a
moment before judging.

### 12.3 Deleting safely

Always `info` a torrent before deleting it - names are more reliable than
hashes for humans to confirm. Then delete without files first:

```
torrent_management(action="info", torrent_hash="<hash>")
torrent_management(action="delete", torrent_hash="<hash>", delete_files=False)
```

Only reach for `delete_files=True` when the user explicitly wants the data
gone (e.g. re-download with a different group).

### 12.4 The post-processing pipeline in detail

The pipeline has four stages:

1. **Detection** - `check_completed` polls rTorrent for torrents at 99.9%+
   progress. A per-hash processed set prevents double-processing within a
   session.
2. **Path resolution** - `process` asks rTorrent for the torrent's base
   path, verifies it exists, and lists video files (mkv, mp4, avi, m4v,
   mov, mpg, mpeg, flv, webm).
3. **Normalization** - with `NORMALIZE_FILENAMES` on, each filename is
   cleaned: release-group tags are stripped, underscores become spaces,
   whitespace is collapsed, punctuation trimmed.
4. **Move + notify** - files are moved into the category ingestion folder;
   `notify_media` then pings Plex/Jellyfin (when configured) so the library
   scans the new content. With `DELETE_TORRENT_AFTER_COMPLETE`, the torrent
   is removed from rTorrent after a successful move.

Run the stages manually for a demo: `check_completed`, show results, `process`
one hash, then `notify_media`.

### 12.5 Background loop semantics

`start_processing` launches an in-process background poller. It is
per-server-process: restarting the server stops it. `stop_processing` is
idempotent. The loop is safe to run while the webapp and IDE clients are
connected - they share the same client instance.

## 13. Search Deep Dive

### 13.1 Choosing the right source

| Need | Source | Action |
|------|--------|--------|
| Current anime, specific group/resolution | nyaa.si | `anime` |
| Manga | nyaa.si | `manga` |
| Japanese TV | nyaa.si | `japanese_tv` |
| Hollywood/independent movies | YTS | `movies` |
| Western TV, conversational query | Pirate Bay | `tv_smart` |
| Western TV, keyword | Pirate Bay | `tv_shows` |
| Books/ebooks | Anna's Archive | `ebooks_annas` |
| Books via torrent | Pirate Bay | `ebooks_pb` |
| Comics | Pirate Bay | `comics` |
| Movie metadata | OMDb/IMDb | `imdb`, `imdb_search` |
| TV metadata | TVDB | `tvdb` |

**Try it:** for a mixed request ("find me the movie Interstellar and the TV
show Slow Horses"), demonstrate source selection to the user: `movies` for
the film, `tv_smart` for the show.

### 13.2 Reading a search result

Every result carries: `title` (with group/resolution tags), `magnet` (the
add-ready link), `size`, `seeders`, `leechers` where available, and a detail
URL. Use seeders as the primary quality signal, then size sanity, then group
preference. Never strip the magnet from a result and paste it from memory.

### 13.3 Smart TV parsing details

`tv_smart` understands phrasings like:

- "get new <show> episodes from piratebay"
- "find latest <show> episodes"
- "download <show> from <group>"
- "search for new episodes of <show>"

It extracts show name, action, "new only" flag, and source, then scores
candidates with `calculate_tv_quality_score` (which prefers MeGusta-style
groups and the requested resolution). When the parser cannot resolve a show
name, the result carries `show_name: null` and a low confidence score -
fall back to `tv_shows` with the raw query.

### 13.4 IMDb enrichment workflow

A common pattern: search a movie on YTS, then enrich the result for the user:

```
search_management(action="movies", query="dune part two", quality="1080p")
search_management(action="imdb_search", title="dune part two")
search_management(action="imdb", imdb_id="tt15239678")
```

Present the synopsis, rating, and year alongside the torrent options. This
turns a bare torrent list into a decision-ready summary.

## 14. Natural Language in Practice

### 14.1 The parse-review-execute loop

Never execute an ambiguous command blindly:

1. `nlp_management(action="parse", text="lade one piece asw 720p")` - returns
   the structured intent (German detected, query "one piece", group ASW,
   720p).
2. Confirm the interpretation with the user.
3. `nlp_management(action="command", text="lade one piece asw 720p")` -
   executes.

### 14.2 Combining NLP with search

`command` executes the intent directly; for full control, run `parse`, then
drive `search_management` + `torrent_management` yourself from the parsed
fields. The `parse` result is designed to be consumed by tools.

### 14.3 Multi-language sessions

The parser auto-detects language per call. In a German conversation, plain
commands work: `lade <titel> <gruppe> <aufloesung>`. You can also force
Japanese: `nlp_management(action="parse", text="<japanese>", language="ja")`.

## 15. Legal Usage Patterns

### 15.1 Pre-download check habit

For anything outside the configured default (anime), run a risk check before
adding:

```
legal_management(action="risk", content_type="movies")
```

Present the risk level and suggestions; proceed only with explicit user
consent. This is the recommended habit: it documents the decision and keeps
the user informed.

### 15.2 Seeding and ratio context

Seeding shares content upstream, which is the legally sensitive part of
BitTorrent in Austria. Use `legal_management(action="advice", torrent_info={...})`
to get context on seeding behavior, and remind the user that private trackers
and VPNs do not change the underlying legal assessment.

### 15.3 Multiple countries

`legal_management` takes a `country` parameter (default austria). The
knowledge base is Austria-oriented; other countries return best-effort
context with a disclaimer. Do not overstate precision for other
jurisdictions.

## 16. Workflow Automation Recipes

### 16.1 Saturday anime night

Schedule the weekly batch:

```
workflow_management(action="schedule", anime_family="detective conan", schedule_time="20:00", rate_limit=4)
```

The queue picks up at 20:00, adds up to 4 torrents concurrently, and stops
when the family is complete. Check it later with `status`.

### 16.2 Complete franchise archival

For completionist archival:

```
workflow_management(action="franchise", anime_family="gintama", resolution="1080p", group="ASW", include_series=True, include_movies=True, include_ovas=True, include_specials=True, episode_start=1, episode_end=367)
```

`estimate` first to confirm the scale. This is the heaviest operation the
server supports; rate-limit it (`rate_limit=3`) on slower connections.

### 16.3 Dry-run as a habit

Every mutating workflow accepts `dry_run`. Use it once, show the plan, then
re-run with `dry_run=False`. The plan lists every torrent that would be
added, so the user can veto specific entries.

### 16.4 Batch multiple families

`batch_series` accepts the family parameter as a set of families; it fans out
`franchise`-style downloads for each. Estimate and dry-run each family
individually first.

## 17. Agentic Workflow Recipes

### 17.1 Setup checklist

1. Ollama installed and running (`ollama serve`).
2. Model present: `ollama pull llama3.2`.
3. `.env`: `RTORRENT_SAMPLING_BASE_URL=http://127.0.0.1:11434/v1`,
   `RTORRENT_SAMPLING_MODEL=llama3.2`.
4. Restart the server.

Host-LLM mode: set `RTORRENT_SAMPLING_USE_CLIENT_LLM=1` and the client's own
model powers the agent loop instead.

### 17.2 Good goals vs bad goals

Good: "Download the first season of Spy x Family in 1080p from Erai-raws and
verify it starts".

Bad: "Download everything ever" (no bound), "get me that anime" (no name).

The agent reasons best with: title + season/family scope + resolution +
group preference + completion signal.

### 17.3 Watching the agent

The agent reports each step's outcome (search found N candidates, chose X,
add returned hash Y, list confirms state downloading). Verify the final list
yourself and confirm with the user.

## 18. Multi-Client Sessions

The same server can serve Claude Desktop (stdio), Cursor (stdio or HTTP),
the webapp (REST), and the Tauri desktop app simultaneously - one process,
one rTorrent connection, one post-processing loop. This is by design: tools
are stateless per call; only the background poller and the processed-hash set
are process-global.

**Try it:** start the HTTP server (`MCP_PORT=10910 uv run python -m
rtorrent_mcp.server --transport http`), open the webapp, and issue a tool
call from an IDE client. Both views show the same torrents.

## 19. Backup and Maintenance

- **Config**: `.env` at the repo root is the single source of truth; back it
  up (it holds API keys).
- **rTorrent state**: rTorrent itself persists torrents across restarts; the
  MCP server does not need to persist anything for basic operation.
- **Logs**: `logs/` captures server logs; the webapp Logs page reads the
  in-memory ring buffer (lost on restart).
- **Upgrades**: `git pull`, `uv sync`, restart. The `.mcpb` bundle is the
  Claude Desktop distribution format.

## 20. End-to-End Scenario Script

The following script is a complete session for a new user:

1. `system_management(action="health")` - confirm server + rTorrent up.
2. `system_management(action="help")` - orient on the tool catalog.
3. `search_management(action="anime", query="spy x family", resolution="720p", group="SubsPlease")` - find candidates.
4. Present top 2 results; user picks; `torrent_management(action="add", magnet_link="<magnet>")`.
5. `torrent_management(action="list")` - confirm downloading.
6. `legal_management(action="risk", content_type="movies")` - when the user asks about legality for non-anime content.
7. After completion: `torrent_management(action="check_completed")`; `torrent_management(action="process", torrent_hash="<hash>")`; `torrent_management(action="notify_media")`.
8. `workflow_management(action="estimate", anime_family="one piece")` - when the user wants a franchise; then dry-run + real run.
9. `torrent_management(action="start_processing")` - hand over automation to the background loop.

Follow this script the first few sessions and you will internalize the
ordering rules that keep operations safe and reversible.

## 21. Edge Cases and Expert Patterns

### 21.1 Duplicate torrents

rTorrent rejects duplicate infohashes. If `add` succeeds but `list` shows no
new row, the torrent was almost certainly already present (or still loading).
Check the response message and the full list; do not re-add blindly - the
duplicate may already be seeding.

### 21.2 Partial seasons and episode ranges

Use `episode_start`/`episode_end` on `franchise` to bound a partial season:

```
workflow_management(action="franchise", anime_family="detective conan", episode_start=1100, episode_end=1112)
```

This is the correct way to "catch up" without re-downloading the catalog.

### 21.3 Remux and raw content

`subcategory` on nyaa searches covers raw/remux tiers: pass
`subcategory="raw"` for untranslated raws or `subcategory="remux"` for
remuxed encodes. Pair with `resolution` and `group` for precise matching.
Raw content bypasses translation groups entirely - confirm intent when the
user asks for it (it is usually a niche preference).

### 21.4 Rate limiting and polite search

Upstream indexers throttle aggressive scraping. Space searches out; prefer
`max_results` caps (10-20) over paging deep. When a search returns an empty
list, check whether the indexer is reachable at all (`system_management`
health) before retrying. `sort_by="seeds"` both improves quality and reduces
the need to fetch many pages.

### 21.5 Scheduling across restarts

`schedule` jobs live in the server process; a server restart clears the
queue. For durable scheduling, re-issue the `schedule` call after a restart
(or use the host's own scheduler - e.g. a Windows Scheduled Task calling the
CLI). Document this limitation to users who rely on nightly queues.

### 21.6 Post-processing path mapping (Docker)

When rTorrent runs in Docker (the bundled compose), base paths are
container-side (e.g. `/downloads/...`). If the ingestion folders are host
paths, the server warns when a torrent path does not exist and skips the
move. Map `INGESTION_*_PATH` to paths the server process can actually see,
or bind the container's download volume to a host path the server can
traverse.

### 21.7 Media library scans

Plex/Jellyfin scans are triggered via `notify_media` after moves. Configure
`PLEX_URL`/`PLEX_TOKEN` or `JELLYFIN_URL`/`JELLYFIN_API_KEY` in `.env`.
Without media-service config, `notify_media` reports a clean no-op - it does
not error, but no scan fires. Mention this to users who expect their library
to update automatically.

### 21.8 Sampling fallback behavior

With `RTORRENT_SAMPLING_USE_CLIENT_LLM=0` (default) the server always calls
its configured endpoint. If that endpoint is down, the agentic workflow
fails with `sampling_unavailable`. With `=1`, the server prefers the host
LLM when the client supports sampling and falls back to the endpoint
otherwise. For Ollama-only setups, keep the default and verify the endpoint
with `system_management(action="health")` (it reports sampling status).

### 21.9 Large libraries

`list` returns the full torrent table; for very large libraries prefer
`info` (single torrent) and `check_completed` (bounded) over repeated full
lists. The webapp caps its table render for readability. The processed-hash
set caps at 10000 entries - older hashes are pruned, which only matters for
re-processing already-seen torrents in a long-lived server.

### 21.10 API key hygiene

The REST bridge (`/api/*`) honors `API_KEY` when set; clients must send
`Authorization: Bearer <key>` or `X-API-Key: <key>`. Unauthenticated access
returns 401 with a clear error code. Keys live in `.env` only - never hardcode
them in tools or scripts.

## 22. Conversation Examples

### Example A: Catching up on a show

User: "I want to catch up on Slow Horses season 4"

1. `search_management(action="tv_smart", query="get new slow horses episodes")`
2. Present matches (season 4 episodes with seeders).
3. `torrent_management(action="add", magnet_link="<best>", category="tv")`
4. `torrent_management(action="list")` - confirm downloading.

### Example B: Movie night with metadata

User: "Find me something good to watch tonight - a sci-fi movie"

1. `search_management(action="movies", query="sci-fi", sort_by="rating", limit=5)`
2. For the top pick: `search_management(action="imdb", imdb_id="<id>")`
3. Present title, year, rating, synopsis + torrent options.

### Example C: The whole backlog

User: "Get me every One Piece episode I'm missing"

1. `workflow_management(action="estimate", anime_family="one piece", resolution="1080p", group="Erai-raws")`
2. `workflow_management(action="franchise", anime_family="one piece", resolution="1080p", group="Erai-raws", dry_run=True)`
3. After approval: execute for real with `rate_limit=5`.

### Example D: Legal double-check

User: "Is it OK to grab this Hollywood movie?"

1. `legal_management(action="risk", content_type="movies", activity="personal_download")`
2. Present the summary + suggestions; note it is informational.
3. Proceed only with explicit consent; add with `category="movies"`.

### Example E: Automating the library

User: "Can you handle everything automatically from now on?"

1. `torrent_management(action="start_processing")` - background poll loop.
2. Explain the loop (interval, category routing, media notify).
3. For franchises: `workflow_management(action="schedule", ...)`.

## 23. Final Reminders

- Search first, add second, verify third.
- `dry_run` and `estimate` are free - use them before mutating.
- Present `message` fields to the user; use `data` for follow-ups.
- `system_management(action="help")` is the runtime source of truth.
- Legal context is informational; the user decides.
- When in doubt, `info` before `delete`, and confirm hashes with names.
