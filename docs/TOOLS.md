# Tool Reference

rtorrent-mcp exposes six portmanteau tools (one tool, many `action` values)
plus one agentic workflow tool. See [ARCHITECTURE.md](ARCHITECTURE.md) for
the action-count summary; this page shows how to call each family.

## `torrent_management` — add, monitor, and post-process torrents

```python
# Add torrent from magnet link
await torrent_management(action="add", magnet="magnet:?xt=urn:btih:...", category="anime")

# Monitor and manage downloads
await torrent_management(action="list")
await torrent_management(action="pause", torrent_hash="...")
await torrent_management(action="resume", torrent_hash="...")
await torrent_management(action="delete", torrent_hash="...", delete_files=True)
await torrent_management(action="status")

# Post-processing
await torrent_management(action="check_completed")
await torrent_management(action="process", torrent_hash="...")
await torrent_management(action="start_processing")   # background polling
await torrent_management(action="stop_processing")
await torrent_management(action="normalize", filename="Show.Name.S01E01.RELEASE-GROUP.mkv", category="tv")
await torrent_management(action="notify_media", torrent_hash="...", category="tv")
```

## `search_management` — anime, manga, TV, movies, ebooks, comics, metadata

```python
# Anime (nyaa.si)
await search_management(action="anime", query="Detective Conan", resolution="720p", group="ASW")

# Manga / Japanese TV
await search_management(action="manga", query="One Piece", subcategory="translated")
await search_management(action="japanese_tv", query="Terrace House", subcategory="translated")

# Movies (YTS) / TV
await search_management(action="movies", query="The Matrix", quality="1080p", sort_by="seeds")
await search_management(action="tv_shows", query="Breaking Bad")

# Ebooks and comics
await search_management(action="ebooks_annas", query="Python Programming", content_type="books")
await search_management(action="ebooks_gutenberg", query="Pride and Prejudice")
await search_management(action="comics", query="Watchmen", max_results=20)
await search_management(action="annas_detail", url="https://annas-archive.org/...")

# Metadata
await search_management(action="imdb", title="The Matrix", year=1999)
await search_management(action="imdb_search", query="Matrix", year=1999)
await search_management(action="tvdb", title="Breaking Bad", year=2008)
```

Anna's Archive downloads require a session cookie — see
[ONBOARDING.md](ONBOARDING.md).

## `nlp_management` — natural-language commands (English/German)

```python
await nlp_management(action="command", text="get me this weeks asw anime, 720p")
await nlp_management(action="command", text="lade detective conan asw 720p")   # German
await nlp_management(action="parse", text="asw attack on titan 1080p")          # parse without executing
await nlp_management(action="help")
```

## `legal_management` — Austrian legal-context hints

```python
await legal_management(action="check", jurisdiction="austria")
await legal_management(action="check", jurisdiction="germany")
await legal_management(action="risk", torrent_info=info)
await legal_management(action="advice")
```

Interpretation of results is on you — this is not legal advice. See
[README.md](../README.md#austrian-context) for the jurisdiction context this
tool encodes.

## `system_management` — health and diagnostics

```python
await system_management(action="help")     # tool listing
await system_management(action="status")   # rTorrent connection status
await system_management(action="health")   # system health check
await system_management(action="analyze")  # analyze the repository
```

## `workflow_management` — franchise and batch downloads

```python
await workflow_management(action="franchise", name="One Piece", resolution="1080p")
await workflow_management(action="batch_series", series=["Show A", "Show B"])
await workflow_management(action="status", workflow_id="...")
await workflow_management(action="schedule", cron="0 6 * * *", query="...")
await workflow_management(action="queue")
await workflow_management(action="estimate", workflow_id="...")
await workflow_management(action="list")
await workflow_management(action="cancel", workflow_id="...")
```

## `agentic_rtorrent_workflow` — LLM-orchestrated multi-step workflow

Requires a local Ollama endpoint (default) or a client LLM
(`RTORRENT_SAMPLING_USE_CLIENT_LLM=1`) — see
[CONFIGURATION.md](CONFIGURATION.md). Give it a goal in natural language and
it plans and executes the necessary `torrent_management` /
`search_management` calls itself.
