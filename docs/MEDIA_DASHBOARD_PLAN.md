# Media Dashboard Plan - Lifting fullstack-demo for rtorrent_mcp

## Overview

Adapting the fullstack-demo repository to create a fullstack media dashboard for rtorrent_mcp that displays:
- Torrent downloads and status
- Search results (anime, movies, books, comics, etc.)
- Post-processing status
- Media library (Plex/ingestion folders)
- rTorrent status and metrics

## Architecture

### Frontend (React + TypeScript + Chakra UI)
- **Media Dashboard**: Main overview with torrents, downloads, library stats
- **Torrent Manager**: List active/pending/completed torrents, control (pause/resume/delete)
- **Search Interface**: Unified search for anime/movies/books/comics with results display
- **Media Library**: Browse ingestion folders, track media files
- **Post-Processing Monitor**: View processing queue and status
- **rTorrent Status**: Connection status, performance metrics

### Backend (FastAPI)
- **MCP Integration**: Call rtorrent_mcp MCP tools via stdio/HTTP
- **Media API**: REST endpoints for torrents, searches, library
- **Real-time Updates**: WebSocket for live torrent status
- **Search Proxy**: Proxy search requests to rtorrent_mcp MCP tools
- **Post-Processing API**: Monitor and control post-processing

### Database (PostgreSQL)
- **Torrents**: Track downloads, status, metadata
- **Search History**: Store search queries and results
- **Media Library**: Index files in ingestion folders
- **Post-Processing Queue**: Track processing jobs

## Implementation Steps

1. **Backend API Layer**
   - Create FastAPI app with rtorrent_mcp integration
   - Expose rtorrent_mcp MCP tools as REST endpoints
   - Add WebSocket for real-time updates
   - Database models for media tracking

2. **Frontend Components**
   - MediaDashboard.tsx - Main overview
   - TorrentList.tsx - Active torrents with controls
   - SearchInterface.tsx - Unified search UI
   - MediaLibrary.tsx - Browse ingestion folders
   - PostProcessingMonitor.tsx - Processing queue
   - RTorrentStatus.tsx - Connection and metrics

3. **Integration**
   - Connect backend to rtorrent_mcp MCP server
   - Poll rTorrent for status updates
   - Stream search results to frontend
   - Track post-processing progress

4. **Infrastructure**
   - Update docker-compose for rtorrent_mcp context
   - Configure monitoring for media metrics
   - Set up database migrations

## File Structure

```
rtorrent_mcp/
├── backend/              # FastAPI backend (from fullstack-demo)
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── torrents.py
│   │   │       ├── search.py
│   │   │       ├── media.py
│   │   │       └── post_processing.py
│   │   ├── models/
│   │   │   ├── torrent.py
│   │   │   ├── media.py
│   │   │   └── search.py
│   │   ├── services/
│   │   │   ├── mcp_client.py    # Call rtorrent_mcp MCP tools
│   │   │   ├── rtorrent.py      # Direct rTorrent integration
│   │   │   └── media_library.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/             # React frontend (from fullstack-demo)
│   ├── src/
│   │   ├── components/
│   │   │   ├── MediaDashboard.tsx
│   │   │   ├── TorrentList.tsx
│   │   │   ├── SearchInterface.tsx
│   │   │   ├── MediaLibrary.tsx
│   │   │   ├── PostProcessingMonitor.tsx
│   │   │   └── RTorrentStatus.tsx
│   │   ├── pages/
│   │   │   ├── Torrents.tsx
│   │   │   ├── Search.tsx
│   │   │   ├── Library.tsx
│   │   │   └── Settings.tsx
│   │   └── services/
│   │       └── api.ts           # API client
│   └── package.json
└── docker-compose.yml    # Updated for rtorrent_mcp
```

## Key Adaptations

1. **MCP Client Service**: Create service to call rtorrent_mcp MCP tools (list_torrents, search_anime, etc.)
2. **Torrent Models**: Track torrents with hash, name, status, progress, category
3. **Search Integration**: Proxy all search tools (anime, movies, books, comics) through API
4. **Real-time Updates**: WebSocket for live torrent progress and status changes
5. **Media Library**: Index ingestion folders, track file metadata

## Benefits

- **Unified Interface**: Single dashboard for all media operations
- **Real-time Updates**: Live torrent status and progress
- **Search Integration**: Easy access to all search services
- **Library Management**: Track and organize media files
- **Monitoring**: Track downloads, processing, and library growth
- **Extensible**: Easy to add new features and integrations



