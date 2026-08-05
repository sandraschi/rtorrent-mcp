# pyright: reportUnusedFunction=false
"""
FastMCP Prompt Templates for rTorrent MCP Server

Parameterized MCP prompt templates for search, legal, and workflow flows.
Prompts provide structured interaction patterns for common workflows.
"""

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all prompt templates with the FastMCP server."""

    @mcp.prompt()
    def anime_search_prompt(anime_name: str, resolution: str = "720p") -> str:
        """
        Prompt template for searching anime with Austrian preferences.

        Args:
            anime_name: Name of the anime to search
            resolution: Preferred resolution (720p, 1080p)
        """
        return f"""Search for anime "{anime_name}" with these preferences:

**Austrian Anime Preferences (ASW Standard):**
- Resolution: {resolution}
- Release Groups: ASW > SubsPlease > Erai-raws
- Subtitles: English (or German)
- Format: MKV preferred

**Search Strategy:**
1. First search nyaa.si for ASW releases
2. Fall back to SubsPlease if not found
3. Check legal status for Austria (should be safe)

Use `search_management(action="anime", query="{anime_name}", resolution="{resolution}", group="ASW")`
"""

    @mcp.prompt()
    def franchise_download_prompt(franchise_name: str) -> str:
        """
        Prompt template for downloading entire anime franchise.

        Args:
            franchise_name: Name of the anime franchise (e.g., "one piece", "naruto")
        """
        return f"""Download the complete "{franchise_name}" franchise.

**[WARN] WARNING: This is a large operation that could take DAYS!**

**Franchise Contents:**
- TV Series (potentially 100s-1000s of episodes)
- Movies
- OVAs (Original Video Animations)
- Specials

**Recommended Workflow:**
1. First estimate the download:
   `workflow_management(action="estimate", anime_family="{franchise_name}")`

2. Review the size and decide what to include

3. Start with dry_run to preview:
   `workflow_management(action="franchise", anime_family="{franchise_name}", dry_run=True)`

4. If satisfied, start the actual download:
   `workflow_management(action="franchise", anime_family="{franchise_name}")`

**Or schedule for overnight:**
   `workflow_management(action="schedule", anime_family="{franchise_name}", schedule_time="02:00")`
"""

    @mcp.prompt()
    def legal_check_prompt(country: str = "austria") -> str:
        """
        Prompt template for checking legal status of torrenting.

        Args:
            country: Country to check legal status for
        """
        return f"""Check legal status for torrenting in {country.title()}.

**Use these tools:**
1. `legal_management(action="check", country="{country}")`
2. `legal_management(action="risk", country="{country}")`

**Austrian Legal Framework (Sandra's Location):**
- Personal use downloading: Generally tolerated
- Uploading/Sharing: Legal grey area
- Commercial use: Illegal
- Recommendation: Use for personal viewing only

**High-Risk Countries:**
- Germany (strict enforcement, fines common)
- Japan (very strict, criminal penalties)
- USA (DMCA enforcement)

**Safe Countries:**
- Austria (personal use OK)
- Switzerland (personal use OK)
- Netherlands (personal use OK)
"""

    @mcp.prompt()
    def tv_show_search_prompt(show_name: str) -> str:
        """
        Prompt template for searching Western TV shows.

        Args:
            show_name: Name of the TV show
        """
        return f"""Search for TV show "{show_name}" on The Pirate Bay.

**Quality Preferences:**
- Release Group: MeGusta (prioritized for quality)
- Resolution: 1080p preferred
- Codec: HEVC/x265 preferred (smaller files)

**Search Strategy:**
1. Smart NLP search (understands natural language):
   `search_management(action="tv_smart", query="get new {show_name} episodes")`

2. Direct search:
   `search_management(action="tv_shows", query="{show_name}", resolution="1080p")`

**Episode Tracking:**
Use downloaded_episodes parameter to filter out already-downloaded episodes.
"""

    @mcp.prompt()
    def ebook_search_prompt(book_title: str) -> str:
        """
        Prompt template for searching ebooks.

        Args:
            book_title: Title of the book to search
        """
        return f"""Search for ebook "{book_title}".

**Gold standard: Anna's Archive**
- 60M+ books available
- 50M+ academic papers
- Best ebook search on the internet

**Search Strategy:**
1. First try Anna's Archive:
   `search_management(action="ebooks_annas", query="{book_title}")`

2. Get details for a specific book:
   `search_management(action="annas_detail", book_url="<url from results>")`

3. Fallback to Pirate Bay (weaker):
   `search_management(action="ebooks_pb", query="{book_title}")`

**Formats:**
- EPUB: Best for e-readers
- PDF: Best for technical/academic
- MOBI: Kindle compatible
"""

    @mcp.prompt()
    def torrent_workflow_prompt() -> str:
        """
        Prompt template for standard torrent workflow.
        """
        return """Standard Torrent Workflow

**1. Search for content:**
```
search_management(action="anime", query="<name>")
search_management(action="movies", query="<name>")
search_management(action="tv_shows", query="<name>")
```

**2. Add torrent:**
```
torrent_management(action="add", magnet_link="<magnet>", category="anime")
```

**3. Monitor progress:**
```
torrent_management(action="list")
torrent_management(action="info", torrent_hash="<hash>")
```

**4. Post-processing (automatic):**
```
torrent_management(action="check_completed")
torrent_management(action="process", torrent_hash="<hash>")
```

**5. Manage torrents:**
```
torrent_management(action="pause", torrent_hash="<hash>")
torrent_management(action="resume", torrent_hash="<hash>")
torrent_management(action="delete", torrent_hash="<hash>", delete_files=False)
```
"""

    @mcp.prompt()
    def system_status_prompt() -> str:
        """
        Prompt template for checking system status.
        """
        return """System Status Check

**Check all systems:**
```
torrent_management(action="status")  # rTorrent connection
system_management(action="status")   # Server status
system_management(action="health")   # Health check
workflow_management(action="queue")  # Workflow queue
```

**Available Portmanteau Tools (6 total):**
1. `torrent_management` - Torrent operations + post-processing
2. `search_management` - All search operations
3. `nlp_management` - Natural language processing
4. `legal_management` - Legal compliance
5. `system_management` - System operations
6. `workflow_management` - Complex workflows

**Get help:**
```
system_management(action="help")
nlp_management(action="help")
```
"""
