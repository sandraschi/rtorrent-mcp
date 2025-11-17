# rTorrent SCGI Connection Problem Report & Fix Plan

**Date:** 2025-11-17  
**Status:** ✅ RESOLVED - Using XMLRPC through nginx (port 8000)

---

## Problem Summary

rTorrent MCP server cannot connect to rTorrent via SCGI. The connection is being established (no more DNS errors), but the SCGI response parsing fails with "Unable to split response into header and body sections".

---

## Current State

### What Works ✅
- rTorrent container is running (`rtorrent-mcp`)
- rTorrent UI accessible on port 12222 (ruTorrent web interface)
- rTorrent process is running inside container
- Unix socket exists: `/var/run/rtorrent/scgi.socket`
- socat is running and bridging Unix socket → TCP:5000
- Port 12224 (host) → 5000 (container) is mapped and listening
- SCGI client can establish TCP connection (no more "getaddrinfo failed")

### What's Broken ❌
- SCGI client connects but fails to parse response
- Error: "Unable to split response into header and body sections"
- MCP server reports "disconnected" status
- Cannot execute any rTorrent commands via SCGI

---

## Root Cause Analysis

### Issue #1: rTorrent Default Config Uses Unix Socket
The `crazymax/rtorrent-rutorrent` Docker image:
- Default config at `/etc/rtorrent/.rtlocal.rc` enables Unix socket SCGI
- Our custom config at `/data/rtorrent.rc` is NOT being loaded
- rTorrent starts with: `rtorrent -D -o import=/etc/rtorrent/.rtlocal.rc`
- Our config override attempts have failed

### Issue #2: socat Bridge Mangles SCGI Protocol
- socat does raw TCP↔Unix socket bridging
- SCGI protocol has specific format: `length:headers,body`
- socat may not preserve exact byte boundaries/format
- Response parsing expects specific header/body separation

### Issue #3: Library Bug in rtorrent_xmlrpc
- `SCGIServerProxy` parses `scgi://127.0.0.1:12224` incorrectly
- Host becomes `//127.0.0.1:12224` (double slash)
- Fixed with workaround: strip leading `//` from host
- But response parsing still fails

---

## What We've Tried (Failed Attempts)

1. ✅ Fixed `.env` port from 12222 → 12224
2. ✅ Fixed SCGI client to use `127.0.0.1` instead of `localhost`
3. ✅ Fixed library bug: strip `//` from host after parsing
4. ✅ Set up socat bridge: Unix socket → TCP:5000
5. ❌ Tried to override rTorrent config via `RTORRENT_CMD` env var
6. ❌ Tried to modify `/etc/rtorrent/.rtlocal.rc` inside container (gets overwritten)
7. ❌ Tried to disable Unix socket in default config (causes "SCGI already enabled" error)
8. ❌ Tried to add TCP port to default config (causes "SCGI already enabled" error)

---

## Fix Plan

### Option 1: Configure rTorrent for TCP SCGI Directly (RECOMMENDED)

**Goal:** Make rTorrent listen on TCP port 5000 directly, eliminating socat bridge.

**Steps:**
1. **Override container's rTorrent startup script**
   - Create custom entrypoint script
   - Modify rTorrent command to load our config AFTER default config
   - Use: `rtorrent -D -o import=/etc/rtorrent/.rtlocal.rc -o import=/data/rtorrent.rc`

2. **Fix config file to properly disable Unix socket**
   ```ini
   # Must be empty string, not commented out
   network.scgi.open_local =
   # Then enable TCP
   network.scgi.open_port = 0.0.0.0:5000
   ```

3. **Create custom Dockerfile or entrypoint**
   - Override the s6 service script for rtorrent
   - Or use volume mount to override `/etc/s6-overlay/s6-rc.d/rtorrent/run`

**Implementation:**
```yaml
# docker-compose.yml
services:
  rtorrent:
    # ... existing config ...
    volumes:
      - ./config:/data
      - ./scripts/rtorrent-run.sh:/etc/s6-overlay/s6-rc.d/rtorrent/run:ro
```

**Script:** `scripts/rtorrent-run.sh`
```bash
#!/bin/sh
exec rtorrent -D -o import=/etc/rtorrent/.rtlocal.rc -o import=/data/rtorrent.rc
```

---

### Option 2: Fix socat SCGI Protocol Handling

**Goal:** Make socat properly handle SCGI protocol format.

**Problem:** socat does raw byte forwarding, may not preserve SCGI format exactly.

**Solution:** Use `socat` with proper SCGI protocol handling, or use a proper SCGI proxy.

**Alternative:** Use `nginx` or `lighttpd` as SCGI proxy instead of socat.

---

### Option 3: Use Different rTorrent Docker Image

**Goal:** Use an image that supports TCP SCGI out of the box.

**Options:**
- `linuxserver/rtorrent` - May have better config options
- `cguenther/rtorrent` - Simpler, more configurable
- Build custom image based on Alpine with rTorrent

---

### Option 4: Fix Response Parsing in Client

**Goal:** Make the SCGI client handle malformed responses from socat bridge.

**Problem:** `rtorrent_xmlrpc` expects specific header/body format.

**Solution:** 
- Patch `response_split_header()` to be more lenient
- Or create wrapper that fixes response format before parsing
- Or switch to different SCGI client library

---

## ✅ SOLUTION IMPLEMENTED: Use XMLRPC through nginx

**Final Solution:** Use the built-in XMLRPC interface through nginx (port 8000)

The `crazymax/rtorrent-rutorrent` Docker image provides XMLRPC through nginx on port 8000 by default. No custom SCGI configuration needed!

**Key Discovery:**
- The image exposes XMLRPC through nginx on port 8000 (not SCGI directly on port 5000)
- rTorrent uses Unix socket internally (`/var/run/rtorrent/scgi.socket`)
- nginx handles the translation from HTTP/XMLRPC to SCGI protocol
- Standard `xmlrpc.client.ServerProxy` works perfectly with this setup

**Implementation:**
1. Updated `docker-compose.yml` to map port `12224:8000` (XMLRPC through nginx)
2. Removed custom startup script approach (not needed)
3. Removed socat bridge approach (not needed)
4. Connection verified: `curl http://localhost:12224/RPC2` returns rTorrent version 0.15.5

**Why This Works:**
- No need to configure rTorrent SCGI settings
- No need for custom startup scripts
- No need for socat bridge
- Uses standard XMLRPC protocol (not raw SCGI)
- More reliable and simpler than direct SCGI configuration

---

## Implementation Steps

### Step 1: Create Custom rTorrent Startup Script
```bash
# scripts/rtorrent-run.sh
#!/bin/sh
exec rtorrent -D \
  -o import=/etc/rtorrent/.rtlocal.rc \
  -o import=/data/rtorrent.rc
```

### Step 2: Update docker-compose.yml
```yaml
volumes:
  - ./config:/data
  - ./scripts/rtorrent-run.sh:/etc/s6-overlay/s6-rc.d/rtorrent/run:ro
```

### Step 3: Update config/rtorrent.rc
```ini
# Disable Unix socket (must be empty, not commented)
network.scgi.open_local =
# Enable TCP port
network.scgi.open_port = 0.0.0.0:5000
```

### Step 4: Remove socat from docker-compose.yml
- Remove the `command:` override
- Let container start normally
- rTorrent should now listen on TCP:5000 directly

### Step 5: Test Connection
```python
from rtorrent_xmlrpc import SCGIServerProxy
proxy = SCGIServerProxy('scgi://127.0.0.1:12224')
print(proxy.system.client_version())
```

---

## Testing Checklist

- [x] rTorrent starts without errors
- [x] Port 8000 (XMLRPC) is listening inside container
- [x] Port 12224 is accessible from host
- [x] XMLRPC client can connect
- [x] XMLRPC client can parse response
- [x] `system.client_version()` works (returns 0.15.5)
- [ ] `d.multicall2()` works (list torrents) - To be tested
- [ ] MCP server `get_status` tool works - To be tested
- [ ] MCP server `list_torrents` tool works - To be tested

**Connection Test:**
```bash
curl -X POST http://localhost:12224/RPC2 \
  -H "Content-Type: text/xml" \
  -d "<?xml version='1.0'?><methodCall><methodName>system.client_version</methodName></methodCall>"
# Returns: <?xml version="1.0"?><methodResponse><params><param><value><string>0.15.5</string></value></param></params></methodResponse>
```

---

## Fallback Plan

If Option 1 fails:
1. Try Option 3 (different Docker image)
2. If that fails, implement Option 4 (fix response parsing)
3. Last resort: Use Option 2 (proper SCGI proxy instead of socat)

---

## Notes

- The `crazymax/rtorrent-rutorrent` image uses s6-overlay for process management
- s6 service scripts are in `/etc/s6-overlay/s6-rc.d/<service>/run`
- rTorrent config is loaded in order: default → custom (if specified)
- Multiple `-o import=` flags load configs in sequence (later overrides earlier)
- rTorrent cannot have both Unix socket AND TCP port enabled simultaneously

---

## References

- rTorrent SCGI docs: https://rtorrent-docs.readthedocs.io/en/latest/SCGI.html
- rtorrent_xmlrpc library: https://github.com/dbowring/rtorrent_xmlrpc
- crazymax/rtorrent-rutorrent: https://github.com/crazy-max/docker-rtorrent-rutorrent

