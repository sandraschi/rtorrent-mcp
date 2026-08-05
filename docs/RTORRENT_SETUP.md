# rTorrent Installation & Configuration Guide

**Complete guide for installing and configuring rTorrent with SCGI support for the rTorrent MCP Server**

---

## TL;DR - Quick Start with Docker (Recommended)

**We use [crazymax/rtorrent-rutorrent](https://github.com/crazy-max/docker-rtorrent-rutorrent) Docker image.**

This is the recommended setup - provides rTorrent + ruTorrent WebUI + nginx XMLRPC proxy all in one.

```bash
# 1. Clone the repo (if not already)
cd D:\Dev\repos\rtorrent-mcp

# 2. Start rTorrent in Docker
docker-compose up -d

# 3. Verify it's running
docker logs rtorrent-mcp

# 4. Test XMLRPC connection (what MCP server uses)
curl -X POST http://localhost:12224/RPC2 -H "Content-Type: text/xml" \
  -d "<?xml version='1.0'?><methodCall><methodName>system.client_version</methodName></methodCall>"
```

**Access Points:**
| Service | URL | Description |
|---------|-----|-------------|
| **XMLRPC** | `http://localhost:12224/RPC2` | MCP server connects here |
| **ruTorrent WebUI** | `http://localhost:12222` | Visual torrent management |
| **Downloads** | `%USERPROFILE%\Downloads\rtorrent` | Downloaded files |

**How it works:**
```
MCP Server → HTTP/XMLRPC (port 12224) → nginx → Unix Socket → rTorrent
```

The `docker-compose.yml` in the repo root is pre-configured for this setup.

---

## Bundled ruTorrent Plugins (crazymax/rtorrent-rutorrent)

The image ships ruTorrent with many plugins enabled by default; see the [upstream image docs](https://github.com/crazy-max/docker-rtorrent-rutorrent) for the current list.

### Core Plugins (Always Available)

| Plugin | Purpose | MCP Integration |
|--------|---------|-----------------|
| **_task** | Background task scheduler for ruTorrent | Could trigger MCP workflows |
| **autotools** | Auto-label, auto-move, auto-watch downloads | * Anime auto-categorization |
| **cpuload** | CPU usage monitoring display | System monitoring |
| **create** | Create .torrent files from local data | - |
| **datadir** | Change torrent data directory | File management |
| **diskspace** | Disk space monitoring and alerts | * MCP can monitor |
| **edit** | Edit torrent trackers in-place | - |
| **erasedata** | Delete torrent + associated data | Cleanup operations |
| **extsearch** | External search engine integration | ** Add Nyaa.si! |
| **feeds** | RSS/Atom feed management | ** Auto-anime feeds |
| **geoip** | Peer geolocation display | Analytics |
| **history** | Download history tracking | * MCP analytics |
| **httprpc** | HTTP RPC interface | Core MCP communication |
| **ipad** | iPad/mobile-optimized interface | - |
| **ratio** | Upload/download ratio management | * Seeding compliance |
| **retrackers** | Automatic tracker addition | - |
| **rss** | RSS auto-download rules | *** KEY for anime automation! |
| **rutracker_check** | Rutracker integration | - |
| **scheduler** | Download time scheduling | ** Night downloads |
| **screenshots** | Video screenshot extraction | Media preview |
| **seedingtime** | Track seeding duration | * Ratio management |
| **source** | Show torrent source info | - |
| **theme** | Theme/skin support | UI customization |
| **throttle** | Per-torrent speed throttling | * Bandwidth control |
| **tracklabels** | Auto-label by tracker | * Organize by source |
| **trafic** | Traffic graphs and statistics | Analytics |
| **unpack** | Auto-extract RAR/ZIP archives | ** Post-processing! |

### Key Plugins for Anime Automation 

**RSS Plugin** - The bread and butter:
```
./config/rutorrent/plugins-conf/rss.conf.php
```
- Monitor SubsPlease, ASW, Erai-raws release feeds
- Auto-match by regex patterns
- Quality filtering (1080p preferred)

**Autotools Plugin** - Automatic organization:
```
./config/rutorrent/plugins-conf/autotools.conf.php
```
- Auto-move completed anime to Plex library
- Auto-label by release group
- Auto-watch folders for .torrent drops

**Scheduler Plugin** - Austrian-friendly timing:
```
./config/rutorrent/plugins-conf/scheduler.conf.php
```
- Download during off-peak hours
- Pause during business hours
- Maximize seeding at night

### Plugin Configuration Location

```
./config/rutorrent/
├── conf/
│   └── plugins.ini          ← Enable/disable plugins
├── plugins/                  ← Custom/third-party plugins (add here)
├── plugins-conf/             ← Plugin configuration overrides
│   ├── rss.conf.php
│   ├── autotools.conf.php
│   └── {plugin}.conf.php
└── themes/                   ← Custom UI themes
```

### Adding Third-Party Plugins

Popular additions for anime:

| Plugin | Source | Purpose |
|--------|--------|---------|
| **autodl-irssi** | github.com/autodl-community/autodl-rutorrent | *** IRC announce monitoring - instant anime grabs! |
| **filemanager** | github.com/nelu/rutorrent-thirdparty-plugins | File operations |
| **mediainfo** | Novik/ruTorrent contrib | Media file metadata |
| **mobile** | Novik/ruTorrent contrib | Better mobile UI |

**Installation:**
```powershell
# Example: Add autodl-irssi
cd D:\Dev\repos\rtorrent-mcp\config\rutorrent\plugins
git clone https://github.com/autodl-community/autodl-rutorrent autodl-irssi

# Restart container
docker-compose restart
```

### Disabling Unwanted Plugins

Use the `RU_REMOVE_CORE_PLUGINS` environment variable in `docker-compose.yml`:
```yaml
environment:
  - RU_REMOVE_CORE_PLUGINS=ipad,rutracker_check
```

Or edit `./config/rutorrent/conf/plugins.ini`:
```ini
[ipad]
enabled = no

[rutracker_check]
enabled = no
```

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation by Platform](#installation-by-platform)
4. [SCGI Configuration](#scgi-configuration)
5. [Service Management](#service-management)
6. [Verification & Testing](#verification--testing)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)
9. [Security Considerations](#security-considerations)
10. [Performance Tuning](#performance-tuning)

---

## Overview

rTorrent is a lightweight, high-performance BitTorrent client that supports SCGI (Simple Common Gateway Interface) for remote control. This guide covers installation, configuration, and optimization for use with the RTorrent MCP Server.

### Key Features Required

- **SCGI Support**: Essential for MCP server communication
- **XML-RPC Interface**: Required for remote control
- **Session Management**: For persistent torrent state
- **Directory Management**: For organized downloads

---

## System Requirements

### Minimum Requirements

- **CPU**: 1 GHz processor
- **RAM**: 512 MB (1 GB recommended)
- **Storage**: 1 GB free space
- **Network**: Stable internet connection
- **OS**: Linux, macOS, or Windows (with WSL)

### Recommended Requirements

- **CPU**: 2+ GHz multi-core processor
- **RAM**: 2+ GB
- **Storage**: 10+ GB free space
- **Network**: High-speed broadband connection

---

## Installation by Platform

### Linux (Ubuntu/Debian)

#### Method 1: Package Manager (Recommended)

```bash
# Update package list
sudo apt update

# Install rTorrent
sudo apt install rtorrent

# Install additional dependencies
sudo apt install libxmlrpc-core-c3-dev libssl-dev

# Verify installation
rtorrent -h | grep -i scgi
```

#### Method 2: Compile from Source (Advanced)

```bash
# Install build dependencies
sudo apt install build-essential libtool automake autoconf \
    libssl-dev libcurl4-openssl-dev libxmlrpc-core-c3-dev \
    libncurses5-dev libcppunit-dev

# Download and compile
wget https://github.com/rakshasa/rtorrent/releases/download/v0.9.8/rtorrent-0.9.8.tar.gz
tar -xzf rtorrent-0.9.8.tar.gz
cd rtorrent-0.9.8

# Configure with SCGI support
./configure --with-xmlrpc-c
make
sudo make install
```

### Linux (CentOS/RHEL/Fedora)

#### CentOS/RHEL 7/8

```bash
# Enable EPEL repository
sudo yum install epel-release

# Install rTorrent
sudo yum install rtorrent

# Install dependencies
sudo yum install libxmlrpc-c3-dev openssl-devel
```

#### Fedora

```bash
# Install rTorrent
sudo dnf install rtorrent

# Install dependencies
sudo dnf install libxmlrpc-c3-devel openssl-devel
```

### macOS

#### Method 1: Homebrew (Recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install rTorrent
brew install rtorrent

# Verify installation
rtorrent -h | grep -i scgi
```

#### Method 2: MacPorts

```bash
# Install MacPorts if not already installed
# Download from https://www.macports.org/install.php

# Install rTorrent
sudo port install rtorrent

# Verify installation
rtorrent -h | grep -i scgi
```

### Windows

#### Method 1: Docker (Recommended for Windows)

**Docker Desktop Setup:**

```powershell
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop/

# Verify Docker installation
docker --version
docker-compose --version
```

**rTorrent Docker Container (Recommended - crazymax/rtorrent-rutorrent):**

```powershell
# Create project directory
mkdir C:\rtorrent-mcp
cd C:\rtorrent-mcp

# Create docker-compose.yml
@"
services:
  rtorrent:
    image: crazymax/rtorrent-rutorrent:latest
    container_name: rtorrent-mcp
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Vienna
    volumes:
      - C:\rtorrent-mcp\config:/data
      - C:\rtorrent-mcp\downloads:/downloads
      - C:\rtorrent-mcp\watch:/watch
      - C:\rtorrent-mcp\logs:/logs
    ports:
      - "12224:8000"  # XMLRPC port for MCP server (through nginx)
      - "12222:8080"  # Web UI (ruTorrent)
      - "51413:51413"  # DHT port
      - "6881:6881/udp"  # DHT UDP port
    restart: unless-stopped
    networks:
      - rtorrent-net

networks:
  rtorrent-net:
    driver: bridge
"@ | Out-File -FilePath "docker-compose.yml" -Encoding UTF8

# Start rTorrent container
docker-compose up -d

# Check container status
docker-compose ps
docker logs rtorrent-mcp

# Test XMLRPC connection
curl -X POST http://localhost:12224/RPC2 -H "Content-Type: text/xml" -d "<?xml version='1.0'?><methodCall><methodName>system.client_version</methodName></methodCall>"
```

**Important Notes:**
- The `crazymax/rtorrent-rutorrent` image provides XMLRPC through nginx on port 8000 by default
- No custom SCGI configuration needed - nginx handles the translation
- rTorrent uses Unix socket internally; nginx exposes it as HTTP/XMLRPC
- MCP server should connect to `http://localhost:12224/RPC2` using standard XMLRPC

#### Method 2: WSL2 (Windows Subsystem for Linux)

**WSL2 Setup:**

```powershell
# Enable WSL2 (run as Administrator)
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer, then set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu

# Launch Ubuntu and follow Linux installation
wsl
```

**Inside WSL2 Ubuntu:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install rTorrent
sudo apt install rtorrent -y

# Create configuration
mkdir -p ~/.rtorrent
cat > ~/.rtorrent.rc << 'EOF'
# SCGI Configuration for MCP Server
scgi_port = 0.0.0.0:5000

# Session Management
session.path.set = ~/.rtorrent/session
session.use_lock.set = yes

# Download Directories
directory.default.set = ~/Downloads
schedule2 = watch_directory, 5, 5, load.start=~/Downloads/*.torrent

# Logging
log.execute = ~/.rtorrent/rtorrent.log
log.add_output = info, ~/.rtorrent/rtorrent.log

# Performance Settings
max_uploads.set = 50
max_connections.set = 200
max_peers.set = 100

# Austrian Legal Compliance
system.method.set_key = event.download.inserted_new, anime_category, "d.custom1.set=anime"
EOF

# Start rTorrent
rtorrent -d

# Verify it's running
pgrep rtorrent
```

**Windows Integration:**

```powershell
# Access WSL2 rTorrent from Windows
# The SCGI port will be accessible at localhost:5000

# Test connection from Windows PowerShell
Invoke-RestMethod -Uri "http://localhost:5000/RPC2" -Method POST -ContentType "text/xml" -Body '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
```

#### Method 3: Pre-compiled Binary (Advanced)

**Download and Setup:**

```powershell
# Create rTorrent directory
mkdir C:\rtorrent
cd C:\rtorrent

# Download rTorrent for Windows (if available)
# Note: Official rTorrent doesn't provide Windows binaries
# You may need to use a community build or compile from source

# Alternative: Use qBittorrent with Web API
# Download from: https://www.qbittorrent.org/download.php

# Install qBittorrent and enable Web UI
# This would require modifying the MCP server to use qBittorrent API instead
```

#### Method 4: Windows Service with Docker

**Create Windows Service:**

```powershell
# Install NSSM (Non-Sucking Service Manager)
# Download from: https://nssm.cc/download

# Create service for Docker container
nssm install rTorrent "C:\Program Files\Docker\Docker\resources\bin\docker.exe" "run --rm -d --name rtorrent-mcp -p 5000:5000 -v C:\rtorrent-mcp\config:/config -v C:\rtorrent-mcp\downloads:/downloads linuxserver/rtorrent:latest"

# Set service parameters
nssm set rTorrent AppDirectory "C:\rtorrent-mcp"
nssm set rTorrent AppStdout "C:\rtorrent-mcp\rtorrent.log"
nssm set rTorrent AppStderr "C:\rtorrent-mcp\rtorrent.error.log"
nssm set rTorrent Start SERVICE_AUTO_START

# Start service
nssm start rTorrent
```

---

## SCGI/XMLRPC Configuration

### Docker Setup (crazymax/rtorrent-rutorrent)

**No configuration needed!** The image provides XMLRPC through nginx on port 8000 by default.

- XMLRPC is accessible at `http://localhost:12224/RPC2` (if mapped as `12224:8000`)
- rTorrent uses Unix socket internally (`/var/run/rtorrent/scgi.socket`)
- nginx handles HTTP/XMLRPC to SCGI translation automatically

### Native Installation Configuration

For native rTorrent installations, create the configuration file:

```bash
# Create configuration directory
mkdir -p ~/.rtorrent

# Create main configuration file
cat > ~/.rtorrent.rc << 'EOF'
# SCGI Configuration for MCP Server
network.scgi.open_port = 0.0.0.0:5000

# Session Management
session.path.set = ~/.rtorrent/session
session.use_lock.set = yes

# Download Directories
directory.default.set = ~/Downloads
schedule2 = watch_directory, 5, 5, load.start=~/Downloads/*.torrent

# Logging
log.execute = ~/.rtorrent/rtorrent.log
log.add_output = info, ~/.rtorrent/rtorrent.log

# Performance Settings
max_uploads.set = 50
max_connections.set = 200
max_peers.set = 100
throttle.min_peers.normal.set = 20
throttle.min_peers.seed.set = 30
throttle.max_peers.normal.set = 60
throttle.max_peers.seed.set = 80

# Bandwidth Settings (adjust as needed)
throttle.global_down.max_rate.set_kb = 0
throttle.global_up.max_rate.set_kb = 0

# Security Settings
encryption = allow_incoming, try_outgoing, enable_retry

# Austrian Legal Compliance
system.method.set_key = event.download.inserted_new, anime_category, "d.custom1.set=anime"
system.method.set_key = event.download.inserted_new, anime_legal_check, "execute.throw=check_austrian_legal,$d.name="
EOF
```

### Advanced Configuration

For production use, consider these additional settings:

```bash
# Advanced configuration
cat >> ~/.rtorrent.rc << 'EOF'

# Network Settings
network.port_range.set = 49164-65534
network.port_random.set = yes
dht.mode.set = auto
protocol.pex.set = yes

# File Management
system.file.max_size.set = 268435456
pieces.hash.on_completion.set = yes
pieces.preload.type.set = 2

# Austrian Anime Optimization
schedule2 = anime_quality_check, 10, 10, "d.custom1.set=anime"
system.method.set_key = event.download.inserted_new, anime_quality, "execute.throw=check_anime_quality,$d.name="

# Monitoring
system.method.set_key = event.download.finished, anime_finished, "execute.throw=anime_downloaded,$d.name="
EOF
```

---

## Service Management

### Systemd Service (Linux)

Create a systemd service for automatic startup:

```bash
# Create service file
sudo tee /etc/systemd/system/rtorrent.service > /dev/null << 'EOF'
[Unit]
Description=rTorrent BitTorrent Client
After=network.target

[Service]
Type=forking
User=rtorrent
Group=rtorrent
ExecStart=/usr/bin/rtorrent -d
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=5

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/rtorrent/.rtorrent
ReadWritePaths=/home/rtorrent/Downloads

[Install]
WantedBy=multi-user.target
EOF

# Create rtorrent user
sudo useradd -r -s /bin/false -d /home/rtorrent rtorrent
sudo mkdir -p /home/rtorrent/.rtorrent
sudo mkdir -p /home/rtorrent/Downloads
sudo chown -R rtorrent:rtorrent /home/rtorrent

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable rtorrent
sudo systemctl start rtorrent
sudo systemctl status rtorrent
```

### LaunchAgent (macOS)

Create a LaunchAgent for automatic startup:

```bash
# Create LaunchAgent directory
mkdir -p ~/Library/LaunchAgents

# Create plist file
cat > ~/Library/LaunchAgents/com.rtorrent.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rtorrent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/rtorrent</string>
        <string>-d</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/$(whoami)/.rtorrent/rtorrent.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/$(whoami)/.rtorrent/rtorrent.error.log</string>
</dict>
</plist>
EOF

# Load the service
launchctl load ~/Library/LaunchAgents/com.rtorrent.plist
launchctl start com.rtorrent
```

### Windows Service

For Windows, use NSSM (Non-Sucking Service Manager):

```powershell
# Download NSSM
# Visit: https://nssm.cc/download

# Install rTorrent as service
nssm install rTorrent "C:\rtorrent\rtorrent.exe" "-d"
nssm set rTorrent AppDirectory "C:\rtorrent"
nssm set rTorrent AppStdout "C:\rtorrent\rtorrent.log"
nssm set rTorrent AppStderr "C:\rtorrent\rtorrent.error.log"

# Start service
nssm start rTorrent
```

---

## Verification & Testing

### Basic Connection Test

```bash
# Test SCGI connection
curl -X POST -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>' \
  http://localhost:5000/RPC2
```

### MCP Server Test

```bash
# Test with MCP server
python -m rtorrent_mcp.server --transport stdio

# In another terminal, test connection
python -c "
import asyncio
from rtorrent_mcp.services.rtorrent_client import RTorrentClient

async def test():
    client = RTorrentClient()
    result = await client.connect()
    print(f'Connection: {result}')
    if result:
        status = await client.get_torrents()
        print(f'Torrents: {len(status)}')

asyncio.run(test())
"
```

### Health Check Script

Create a health check script:

```bash
#!/bin/bash
# rtorrent-health-check.sh

RTORRENT_HOST="localhost"
RTORRENT_PORT="5000"

echo " Checking rTorrent health..."

# Check if process is running
if pgrep -x "rtorrent" > /dev/null; then
    echo "[OK] rTorrent process is running"
else
    echo "[FAIL] rTorrent process is not running"
    exit 1
fi

# Check SCGI port
if nc -z $RTORRENT_HOST $RTORRENT_PORT; then
    echo "[OK] SCGI port $RTORRENT_PORT is open"
else
    echo "[FAIL] SCGI port $RTORRENT_PORT is not accessible"
    exit 1
fi

# Test XML-RPC connection
RESPONSE=$(curl -s -X POST -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>' \
  http://$RTORRENT_HOST:$RTORRENT_PORT/RPC2)

if echo "$RESPONSE" | grep -q "system.listMethods"; then
    echo "[OK] XML-RPC connection successful"
else
    echo "[FAIL] XML-RPC connection failed"
    exit 1
fi

echo " rTorrent is healthy and ready for MCP server!"
```

---

## Troubleshooting

### Common Issues

#### 1. SCGI Port Already in Use

```bash
# Check what's using port 5000
sudo netstat -tlnp | grep :5000
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>

# Or change port in .rtorrent.rc
scgi_port = localhost:5001
```

#### 2. Permission Denied

```bash
# Fix ownership
sudo chown -R $USER:$USER ~/.rtorrent
sudo chown -R $USER:$USER ~/Downloads

# Fix permissions
chmod 755 ~/.rtorrent
chmod 755 ~/Downloads
```

#### 3. rTorrent Won't Start

```bash
# Check configuration syntax
rtorrent -n -o import=~/.rtorrent.rc

# Check for errors in log
tail -f ~/.rtorrent/rtorrent.log

# Test with minimal config
rtorrent -n -o scgi_port=localhost:5000
```

#### 4. XML-RPC Connection Failed

```bash
# Check firewall
sudo ufw status
sudo firewall-cmd --list-all

# Allow port 5000
sudo ufw allow 5000
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

#### 5. SCGI Support Missing

```bash
# Check if SCGI is compiled in
rtorrent -h | grep -i scgi

# If missing, recompile with SCGI support
sudo apt install libxmlrpc-core-c3-dev
# Then reinstall rtorrent
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Add to .rtorrent.rc
log.add_output = debug, ~/.rtorrent/rtorrent.debug.log

# Start with debug output
rtorrent -n -o import=~/.rtorrent.rc
```

### Log Analysis

```bash
# Monitor logs in real-time
tail -f ~/.rtorrent/rtorrent.log

# Search for errors
grep -i error ~/.rtorrent/rtorrent.log

# Check connection attempts
grep -i "scgi\|xmlrpc" ~/.rtorrent/rtorrent.log
```

---

## Security Considerations

### Network Security

```bash
# Bind SCGI to localhost only
scgi_port = 127.0.0.1:5000

# Use firewall rules
sudo ufw deny 5000
sudo ufw allow from 127.0.0.1 to any port 5000
```

### File Permissions

```bash
# Secure configuration files
chmod 600 ~/.rtorrent.rc
chmod 700 ~/.rtorrent

# Secure download directory
chmod 755 ~/Downloads
```

### User Isolation

```bash
# Run as dedicated user
sudo useradd -r -s /bin/false -d /home/rtorrent rtorrent
sudo chown -R rtorrent:rtorrent /home/rtorrent
```

---

## Performance Tuning

### System Limits

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Apply immediately
ulimit -n 65536
```

### rTorrent Optimization

```bash
# Add to .rtorrent.rc
# Network optimization
network.max_open_files.set = 4096
network.max_open_sockets.set = 4096

# Memory optimization
pieces.memory.max.set = 512M
pieces.preload.type.set = 2

# Disk optimization
system.file.max_size.set = 268435456
pieces.hash.on_completion.set = yes
```

### Austrian Anime Optimization

```bash
# Add to .rtorrent.rc
# Prioritize Austrian release groups
system.method.set_key = event.download.inserted_new, anime_priority, "d.priority.set=1"
system.method.set_key = event.download.inserted_new, anime_category, "d.custom1.set=anime"

# Quality-based prioritization
system.method.set_key = event.download.inserted_new, quality_check, "execute.throw=check_quality,$d.name="
```

---

## Additional Resources

### Official Documentation

- [rTorrent Official Site](https://rakshasa.github.io/rtorrent/)
- [rTorrent GitHub Repository](https://github.com/rakshasa/rtorrent)
- [SCGI Documentation](https://python.ca/scgi/protocol.txt)

### Community Resources

- [rTorrent Wiki](https://github.com/rakshasa/rtorrent/wiki)
- [Austrian Anime Communities](https://www.animexx.de/)
- [MCP Server Documentation](https://fastmcp.anthropic.com)

### Support

- [GitHub Issues](https://github.com/sandraschi/rtorrent-mcp/issues)
- [Discord Community](https://discord.gg/rtorrent)
- [Reddit rTorrent](https://www.reddit.com/r/rtorrent/)

---

## Next Steps

After completing rTorrent installation and configuration:

1. **Test the MCP Server**: Run `python -m rtorrent_mcp.server --transport stdio`
2. **Configure Claude Desktop**: Add the MCP server to your configuration
3. **Test Anime Search**: Try searching for anime using natural language
4. **Monitor Performance**: Use the system status tools to monitor health
5. **Optimize Settings**: Adjust configuration based on your usage patterns

---

**Made with  in Vienna, Austria (AT)**

*For Austrian anime enthusiasts who value both quality and legal compliance.*
