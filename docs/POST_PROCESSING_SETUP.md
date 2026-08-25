# Post-Processing Configuration Guide

## Overview

The post-processing system automatically handles completed downloads:
1. **Completion Detection** - Polls rTorrent for 100% complete downloads
2. **Torrent Removal** - Removes torrent from queue (no sharing)
3. **Filename Normalization** - Cleans filenames (removes release group tags)
4. **Ingestion Folders** - Moves files to temporary ingestion folders (staging area before Plex organizes)

---

## Configuration

### Environment Variables (.env file)

Add these to your `.env` file:

```bash
# Post-processing settings
POST_PROCESSING_ENABLED=false              # Set to true to enable automatic post-processing
POST_PROCESSING_POLL_INTERVAL=60           # Seconds between polling for completed downloads (default: 60)
DELETE_TORRENT_AFTER_COMPLETE=false        # Set to true to remove torrent after completion (no sharing)
NORMALIZE_FILENAMES=true                   # Normalize filenames before moving/linking (default: true)
LINK_MODE=hardlink                         # Link mode: hardlink (default), symlink, copy, move (preserves seeding)

# Temporary ingestion folders (staging area before Plex organizes)
# These are simple category-based folders - Plex will organize into specific libraries later
INGESTION_ANIME_PATH=D:/Ingestion/Anime             # Temporary folder for anime
INGESTION_TV_PATH=D:/Ingestion/TV                   # Temporary folder for TV shows
INGESTION_MOVIES_PATH=D:/Ingestion/Movies           # Temporary folder for movies
```

### Windows Path Format

Use forward slashes or double backslashes:
```bash
# Good (forward slashes)
INGESTION_ANIME_PATH=D:/Ingestion/Anime

# Good (double backslashes)
INGESTION_ANIME_PATH=D:\\Ingestion\\Anime

# Bad (single backslash - won't work)
INGESTION_ANIME_PATH=D:\Ingestion\Anime
```

### Linux/macOS Path Format

Use standard Unix paths:
```bash
INGESTION_ANIME_PATH=/home/user/Ingestion/Anime
INGESTION_TV_PATH=/home/user/Ingestion/TV
INGESTION_MOVIES_PATH=/home/user/Ingestion/Movies
```

---

## How It Works

### Completion Detection (Polling)

**rTorrent doesn't support XMLRPC callbacks**, so we use **polling**:
- Checks for completed downloads every `POST_PROCESSING_POLL_INTERVAL` seconds
- A torrent is considered complete when `progress >= 99.9%` (handles rounding)
- Tracks processed torrents to avoid re-processing

### Torrent Removal (No Sharing)

When `DELETE_TORRENT_AFTER_COMPLETE=true`:
- After files are moved, the torrent is removed from rTorrent
- Uses `d.close()` then `d.erase()` - files already moved, so no sharing
- This ensures no seeding/uploading of your downloads

### Filename Normalization

When `NORMALIZE_FILENAMES=true`:
- Removes release group tags: `[ASW]`, `[SubsPlease]`, `[MeGusta]`, etc.
- Removes hash codes: `[C5819381]`
- Cleans up multiple spaces, dots, dashes
- Preserves file extensions
- Example: `[ASW] Detective Conan - 1182 [1080p HEVC x265][AAC].mkv` → `Detective Conan - 1182 [1080p HEVC x265][AAC].mkv`

### Ingestion Folder Routing

Files are moved to temporary ingestion folders based on category (set when adding torrent):
- **anime** → `INGESTION_ANIME_PATH` (e.g., `D:/Ingestion/Anime`)
- **TV** or **tv-shows** → `INGESTION_TV_PATH` (e.g., `D:/Ingestion/TV`)
- **movies** → `INGESTION_MOVIES_PATH` (e.g., `D:/Ingestion/Movies`)

These are **staging folders** - Plex can watch these folders and organize files into specific libraries (e.g., "TV - Thrillers", "Anime - 2025", "Movies - Horror") later.

If an ingestion folder is not configured for a category, the file is **not moved** but the torrent can still be removed if configured.

---

## Usage

### Starting Post-Processing

Use the MCP tool to start the polling loop:

```python
# Start post-processing (runs in background)
start_post_processing()
```

Or enable it automatically by setting `POST_PROCESSING_ENABLED=true` and the server will start it on startup.

### Manual Processing

You can manually process a specific torrent:

```python
# Check for completed downloads
completed = check_completed_downloads()

# Process a specific torrent
process_completed_download(torrent_hash="ABC123...")
```

### Testing Filename Normalization

```python
# Test filename normalization
normalize_filename("[ASW] Detective Conan - 1182 [1080p].mkv", "anime")
# Returns: "Detective Conan - 1182 [1080p].mkv"
```

### Stopping Post-Processing

```python
# Stop the polling loop
stop_post_processing()
```

---

## MCP Tools

### `check_completed_downloads`
Returns list of torrents that are 100% complete and ready for processing.

### `process_completed_download`
Processes a specific completed torrent: normalizes filename and moves to Plex folder.

**Args:**
- `torrent_hash` (str): The hash identifier of the torrent

**Returns:**
```json
{
  "status": "success",
  "torrent_hash": "ABC123...",
  "torrent_name": "Detective Conan - 1182",
  "category": "anime",
  "moved_files": ["D:/Ingestion/Anime/Detective Conan - 1182.mkv"],
  "ingestion_folder": "D:/Ingestion/Anime"
}
```

### `start_post_processing`
Starts the background polling loop for automatic post-processing.

### `stop_post_processing`
Stops the background polling loop.

### `normalize_filename`
Normalizes a filename by removing release group tags.

**Args:**
- `filename` (str): The filename to normalize
- `category` (str): Category for context (default: "anime")

**Returns:**
```json
{
  "original": "[ASW] Detective Conan - 1182 [1080p].mkv",
  "normalized": "Detective Conan - 1182 [1080p].mkv",
  "category": "anime"
}
```

---

## Example Workflow

1. **Add a torrent** with category:
   ```python
   add_torrent("magnet:...", category="anime")
   ```

2. **rTorrent downloads** the files

3. **Post-processor polls** every 60 seconds (configurable)

4. **When complete** (100%):
   - Gets torrent files
   - Normalizes filenames (removes `[ASW]` tags)
   - Moves to `INGESTION_ANIME_PATH` (e.g., `D:/Ingestion/Anime`)
   - Removes torrent from rTorrent (no sharing)

5. **Files are staged** in ingestion folders - Plex can watch these or you can organize manually later

---

## Troubleshooting

### Files Not Moving

- **Check ingestion folder paths** are configured correctly
- **Verify paths exist** or have permissions to create
- **Check category** matches configured ingestion folders (anime/TV/movies)

### Torrents Not Being Removed

- **Check `DELETE_TORRENT_AFTER_COMPLETE`** is set to `true`
- **Verify files were moved successfully** - torrent only removed after move

### Post-Processing Not Running

- **Check `POST_PROCESSING_ENABLED`** is set to `true`
- **Check poll interval** - might be waiting for next poll
- **Check logs** for errors

### Filenames Not Normalized

- **Check `NORMALIZE_FILENAMES`** is set to `true`
- **Review normalization patterns** - might need to add more release group tags

---

## Advanced Configuration

### Custom Normalization Patterns

Edit `src/rtorrent_mcp/services/post_processor.py` `normalize_filename()` method to add custom patterns.

### Custom Ingestion Folder Logic

Edit `src/rtorrent_mcp/services/post_processor.py` `get_ingestion_folder()` method to customize routing.

**Future Enhancement:** More specific library routing (e.g., "TV - Thrillers", "Anime - 2025") can be added later based on content analysis or configuration rules.

### Polling Interval

Adjust `POST_PROCESSING_POLL_INTERVAL`:
- **Lower** (30s) = Faster detection, more API calls
- **Higher** (120s) = Slower detection, fewer API calls

---

## Notes

- **No sharing**: Torrents are removed after completion to avoid seeding
- **File safety**: Files are moved (not copied) to preserve space
- **Duplicate handling**: If destination file exists, adds `_1`, `_2`, etc. suffix
- **Error handling**: Partial failures are logged but don't stop processing
- **Processed tracking**: Torrents are tracked to avoid re-processing

---

*See also: [RTORRENT_SETUP.md](RTORRENT_SETUP.md) for rTorrent configuration*

