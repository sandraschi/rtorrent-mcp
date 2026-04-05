# Troubleshooting Guide

## Search Tools Returning Empty Results

### Problem Description

**Symptoms:**
- `search_anime` tool returns empty results `[]`
- Natural language commands like `"get me gachiakuta latest episode"` parse correctly but find no torrents
- No error messages, just silent failures
- MCP tools appear to work but return no data

### Root Cause Analysis

The issue was **missing Python dependencies** causing silent import failures:

1. **Missing `import json`** in `nyaa_search.py` - caused crashes when formatting responses
2. **Incorrect package name** - `xmlrpc-client` doesn't exist, should be `xmlrpc3`  
3. **Outdated FastMCP version** - using 2.10.0 instead of required 2.12.0
4. **Missing core dependencies** for web scraping and system monitoring

### Impact

- Search tools appeared to be "mocks" but were actually **real implementations** failing silently
- nyaa.si scraping completely broken due to import errors
- rTorrent SCGI communication unavailable
- System monitoring and health checks non-functional

## **Solution**

### Step 1: Fix Package Dependencies

Update `requirements.txt` with correct package names:

```txt
# Core dependencies
fastmcp[all]>=2.12.0
python-dotenv>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Web and API - Critical for nyaa.si search
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
requests>=2.31.0
python-multipart>=0.0.6

# rTorrent integration - CORRECT PACKAGE NAME
xmlrpc3>=1.0.0

# System monitoring and health
psutil>=5.9.0

# Data processing
pyyaml>=6.0
python-dateutil>=2.8.2
```

### Step 2: Fix Missing Import

Add missing `json` import to `src/rtorrent_mcp/services/nyaa_search.py`:

```python
import json  # ADD THIS LINE
import logging
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
```

### Step 3: Install Dependencies

```bash
cd D:\Dev\repos\rtorrent_mcp
pip install -r requirements.txt --upgrade
```

### Step 4: Verify Fix

Test search functionality:

```bash
python -c "
import sys
sys.path.insert(0, 'src')
import asyncio
from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

async def test():
    results = await search_nyaa_anime('test', '720p', 'ASW')
    print(f'Search working: {len(results) > 0}')

asyncio.run(test())
"
```

### Step 5: Restart Claude Desktop

After installing dependencies, restart Claude Desktop to pick up the changes.

## **Verification**

After applying the fix, these commands should work:

- `search_anime("gachiakuta", "720p", "ASW")` - Returns real nyaa.si results
- `sandra_anime_command("get me gachiakuta latest episode")` - Finds and suggests torrents
- `get_status()` - Shows rTorrent connection status

## **Key Learnings**

1. **Always check import statements** - Missing imports cause silent failures
2. **Verify package names** - `xmlrpc-client` vs `xmlrpc3` 
3. **Keep FastMCP updated** - Version compatibility is critical
4. **Test dependencies explicitly** - Don't assume tools are "mocks"

## **Prevention**

- Add dependency checks to CI/CD pipeline
- Include import validation in unit tests  
- Document exact package requirements
- Test search functionality in development environment

---

**Last Updated:** September 26, 2025  
**Status:** [OK] Resolved - Search tools now fully functional
