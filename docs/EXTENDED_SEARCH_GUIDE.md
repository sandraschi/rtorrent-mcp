# Extended Search Tools Guide

Complete guide to using the extended search capabilities of RTorrent MCP Server.

## Overview

The RTorrent MCP Server provides comprehensive search capabilities across multiple sources:

- **nyaa.si**: Anime, manga, and Japanese TV shows
- **The Pirate Bay**: TV series, comics, ebooks
- **YTS (yify)**: Movies (gold standard for movies)
- **Anna's Archive**: Ebooks and academic papers (60M+ books!)

---

## Anime & Manga Search (nyaa.si)

### Basic Anime Search

```python
# Search for anime with ASW preference
results = await search_anime("Detective Conan", resolution="720p", group="ASW")

# Search with different release group
results = await search_anime("One Piece", resolution="1080p", group="Erai-raws")
```

**Parameters:**
- `query` (str): Anime name to search for
- `resolution` (str): Preferred resolution - "720p" or "1080p" (default: "720p")
- `group` (str): Release group preference (default: "ASW")

**Returns:** Array of anime releases with quality scoring and torrent details

### Manga Search

```python
# Search for translated manga
results = await search_manga("One Piece", subcategory="translated")

# Search for raw manga
results = await search_manga("Naruto", subcategory="raw")

# Search for English manga
results = await search_manga("Attack on Titan", subcategory="english")
```

**Parameters:**
- `query` (str): Manga name to search for
- `subcategory` (str): "raw", "translated", or "english" (default: "translated")

**Returns:** Array of manga releases with torrent details

### Japanese TV Search

```python
# Search for translated Japanese TV shows
results = await search_japanese_tv("Terrace House", subcategory="translated")

# Search for raw Japanese TV
results = await search_japanese_tv("Ame Talk", subcategory="raw")
```

**Parameters:**
- `query` (str): TV series name to search for
- `subcategory` (str): "raw" or "translated" (default: "translated")

**Returns:** Array of Japanese TV releases with torrent details

---

## Movie Search (YTS)

YTS is the gold standard for movie torrents with high-quality releases.

### Basic Movie Search

```python
# Search for movies
results = await search_movies("The Matrix", quality="1080p", sort_by="seeds")

# Search with different quality
results = await search_movies("Inception", quality="2160p", sort_by="rating")

# Search with custom limit
results = await search_movies("Interstellar", quality="1080p", limit=10)
```

**Parameters:**
- `query` (str): Movie name to search for
- `quality` (str): Preferred quality - "720p", "1080p", "2160p", "3D" (default: "1080p")
- `sort_by` (str): Sort by "seeds", "peers", "year", "rating", "downloads" (default: "seeds")
- `limit` (int): Maximum results to return (default: 20)

**Returns:** Array of movie releases with torrent details and IMDb codes

### Example Response

```json
[
  {
    "title": "The Matrix (1999) [1080p] [BluRay] [x265] [YTS.MX]",
    "magnet": "magnet:?xt=urn:btih:...",
    "size": "1.8 GB",
    "seeds": 1234,
    "peers": 567,
    "imdb_code": "tt0133093",
    "quality": "1080p",
    "year": 1999
  }
]
```

---

## Ebook & Paper Search

### Anna's Archive (Gold Standard!)

Anna's Archive has 60M+ books and 50M+ papers. Very idiosyncratic UI, but we love Anna!

```python
# Search for books
results = await search_ebooks_annas("Python Programming", content_type="books", max_results=20)

# Search for academic papers
results = await search_ebooks_annas("machine learning", content_type="papers", max_results=10)
```

**Parameters:**
- `query` (str): Book/paper title, author, or ISBN
- `content_type` (str): "books" or "papers" (default: "books")
- `max_results` (int): Maximum results (default: 20)

**Returns:** Array of book/paper releases with detail URLs

### Get Detailed Torrent Info

After searching, get full torrent details including magnet links:

```python
# Get detailed torrent information
detail = await get_annas_detail("https://annas-archive.org/search?q=python")

# Returns magnet links and download mirrors
```

**Parameters:**
- `book_url` (str): Full URL to Anna's Archive book/paper detail page

**Returns:** Dictionary with detailed torrent info including magnet links

### Anna's Archive: Datasets, Quality & Bulk Torrents (*Caveat Downloador*)

> [!NOTE]
> **Bulk Torrents & AI Training Datasets**:
> Anna's Archive hosts both single-book mirrors and massive **bulk torrent batches** (ranging from moderate ~5TB thematic collections to multi-terabyte / 100TB+ full catalog dumps). Historically, AI corporations aggressively fetched these bulk torrent dumps for LLM training data (which subsequently sparked high-profile copyright litigation).
>
> For regular users, downloading specific individual e-books via `search_ebooks_annas` and `annas_detail` is recommended over fetching multi-terabyte dataset archives.

> [!WARNING]
> **Duplicates & Quality Variance**:
> Anna's Archive aggregates across LibGen, Z-Library, Sci-Hub, and Internet Archive. Consequently:
> - **Duplicates**: Multiple entries exist for popular titles across different editions and scans.
> - **Format Variance**: File formats vary dramatically—ranging from **pristine digital `.epub` and vector `.pdf`** files to **raw bitmap image scans packed inside `.cbz` or raster `.pdf`** containers.
> - **Recommendation**: Inspect the format extension (`.epub`, `.pdf`, `.cbz`), file size, and page count in `annas_detail` before sending to rTorrent!

### Pirate Bay Ebook Search

For ebooks on Pirate Bay (weaker selection, but available):

```python
# Search Pirate Bay for ebooks
results = await search_ebooks_pb("Python Cookbook", max_results=20)
```

**Note:** For better results, use `search_ebooks_annas` - Anna's Archive is the gold standard!

---

## Comic Search

Search The Pirate Bay for western comics:

```python
# Search for comics
results = await search_comics("Watchmen", max_results=20)

# Search for specific series
results = await search_comics("The Walking Dead", max_results=10)
```

**Parameters:**
- `query` (str): Comic book title to search for
- `max_results` (int): Maximum results (default: 20)

**Returns:** Array of comic releases with torrent details

---

## Metadata Services

### IMDb Metadata

Get detailed metadata for movies and TV shows:

```python
# Get metadata by title
metadata = await get_imdb_metadata("The Matrix", year=1999)

# Get metadata by IMDb ID
metadata = await get_imdb_metadata(imdb_id="tt0133093")

# With API key (free at omdbapi.com)
metadata = await get_imdb_metadata("Inception", year=2010, api_key="your_key")
```

**Parameters:**
- `title` (str): Movie/TV show title
- `year` (int, optional): Release year for disambiguation
- `imdb_id` (str, optional): IMDb ID (e.g., "tt1234567") for direct lookup
- `api_key` (str, optional): OMDb API key (free at omdbapi.com)

**Returns:** Dictionary with IMDb metadata (title, year, rating, plot, etc.)

### Search IMDb

Search IMDb for multiple matches:

```python
# Search for multiple matches
results = await search_imdb("Matrix", year=1999)

# Search without year
results = await search_imdb("Inception")
```

**Parameters:**
- `title` (str): Movie/TV show title to search
- `year` (int, optional): Release year for disambiguation
- `api_key` (str, optional): OMDb API key

**Returns:** List of matching titles with basic info and IMDb IDs

### TVDB Metadata

Get TVDB metadata for TV shows (requires TVDB API subscription):

```python
# Get TVDB metadata
metadata = await get_tvdb_metadata("Breaking Bad", year=2008, api_key="your_key", pin="your_pin")

# Get by TVDB ID
metadata = await get_tvdb_metadata(tvdb_id=81189, api_key="your_key", pin="your_pin")
```

**Parameters:**
- `title` (str): TV show title
- `year` (int, optional): Release year
- `tvdb_id` (int, optional): TVDB ID if known
- `api_key` (str, optional): TVDB API key
- `pin` (str, optional): TVDB PIN

**Returns:** Dictionary with TVDB metadata (series info, episodes, etc.)

---

## Search Tips & Best Practices

### 1. Release Group Prioritization

**Anime (nyaa.si):**
- **ASW** (AkihitoSubsWeeklies): Preferred for anime, often 1080p HEVC x265
- **SubsPlease**: High quality, reliable
- **Erai-raws**: Good quality, frequent releases

**TV Shows (Pirate Bay):**
- **MeGusta**: Preferred for TV shows, excellent small rips with high quality
- **RARBG**: Good quality, wide selection
- **EZTV**: Reliable TV releases

**Movies (YTS):**
- YTS is the gold standard - all releases are high quality
- Sort by "seeds" for best availability
- Sort by "rating" for best quality

### 2. Resolution Fallback

When searching for anime with ASW:
- ASW often releases in 1080p even when 720p is requested
- The search automatically falls back to 1080p if no 720p ASW releases found
- This ensures you get ASW releases even if they're higher resolution

### 3. Quality Scoring

All search results include quality scores:
- **ASW**: +130 bonus points (highest priority)
- **MeGusta**: +155 bonus points (TV shows)
- Resolution match: +50 points
- Seeders/peers: Factor into final score

### 4. Search Depth

- **nyaa.si**: Searches top 50 results (increased from 20)
- **Pirate Bay**: Searches top 20 results
- **YTS**: Configurable limit (default: 20)
- **Anna's Archive**: Configurable max_results (default: 20)

### 5. Error Handling

All search tools include robust error handling:
- Network errors are caught and logged
- Empty results return empty arrays (not errors)
- Invalid parameters return helpful error messages
- User-Agent headers prevent blocking

---

## Configuration

### Environment Variables

Add these to your `.env` file for extended search:

```env
# Search engine URLs (usually defaults are fine)
NYAA_BASE_URL=https://nyaa.si
PIRATEBAY_BASE_URL=https://thepiratebay.org
YTS_BASE_URL=https://yts.mx
ANNAS_ARCHIVE_BASE_URL=https://annas-archive.org

# Metadata API keys (optional)
OMDB_API_KEY=your_omdb_key_here  # Free at omdbapi.com
TVDB_API_KEY=your_tvdb_key_here  # Requires subscription
TVDB_PIN=your_tvdb_pin_here
```

---

## Examples

### Complete Workflow: Search and Download Anime

```python
# 1. Search for anime
results = await search_anime("Detective Conan", resolution="720p", group="ASW")

# 2. Get best result
best_result = results[0]  # Already sorted by quality score

# 3. Add to rTorrent
await add_torrent(best_result["magnet"], category="anime")

# 4. Monitor download
torrents = await list_torrents()
```

### Complete Workflow: Search Movie with Metadata

```python
# 1. Search for movie
results = await search_movies("The Matrix", quality="1080p")

# 2. Get IMDb metadata
metadata = await get_imdb_metadata("The Matrix", year=1999)

# 3. Add best result
best_result = results[0]
await add_torrent(best_result["magnet"], category="movies")
```

### Complete Workflow: Search Ebook

```python
# 1. Search Anna's Archive
results = await search_ebooks_annas("Python Programming", content_type="books")

# 2. Get detailed torrent info
detail = await get_annas_detail(results[0]["detail_url"])

# 3. Add torrent (can be 100TB+!)
await add_torrent(detail["magnet"], category="ebooks")
```

---

## Troubleshooting

### No Results Found

- **Check spelling**: Search terms are case-insensitive but spelling matters
- **Try variations**: "One Piece" vs "OnePiece" vs "one-piece"
- **Remove special characters**: Some search engines don't handle special chars well
- **Check release group**: Some groups may not have releases for specific shows

### Slow Searches

- **Reduce max_results**: Lower limits return faster
- **Check network**: Network issues can slow searches
- **Use specific queries**: More specific queries are faster than broad searches

### Metadata Errors

- **OMDb API**: Free API key available at omdbapi.com
- **TVDB API**: Requires paid subscription
- **Rate Limits**: Some APIs have rate limits - add delays if needed

---

## Related Documentation

- [README.md](../README.md) - Main project documentation
- [POST_PROCESSING_SETUP.md](POST_PROCESSING_SETUP.md) - Post-processing guide
- [STATUS_REPORT.md](STATUS_REPORT.md) - Project status and metrics
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

---

*Last Updated: 2025-01-27*  
*Version: 1.0.0*

