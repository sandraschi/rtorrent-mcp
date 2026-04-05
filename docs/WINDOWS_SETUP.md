# Windows Setup Guide for RTorrent MCP Server

**Complete Windows-specific installation and configuration guide for rTorrent with MCP server integration**

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Method 1: Docker (Recommended)](#method-1-docker-recommended)
4. [Method 2: WSL2](#method-2-wsl2)
5. [Method 3: Windows Service](#method-3-windows-service)
6. [Configuration](#configuration)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)

---

## Overview

This guide provides Windows-specific instructions for setting up rTorrent with SCGI support for the RTorrent MCP Server. Since rTorrent is primarily a Linux application, we'll use containerization and virtualization to run it on Windows.

### Recommended Approach

**Docker Desktop** is the recommended method for Windows users as it provides:
- Native Windows integration
- Easy management and updates
- Consistent behavior across systems
- Simple backup and migration
- Web UI access (optional)

---

## Prerequisites

### System Requirements

- **Windows 10/11** (64-bit)
- **8GB RAM** minimum (16GB recommended)
- **50GB free disk space** for downloads
- **Stable internet connection**
- **Administrator privileges** for initial setup

### Required Software

1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop/
   - Enable WSL2 backend (recommended)
   - Enable Kubernetes (optional)

2. **PowerShell 7+** (for advanced scripting)
   - Download: https://github.com/PowerShell/PowerShell/releases

---

## Method 1: Docker (Recommended)

### Step 1: Install Docker Desktop

```powershell
# Download and install Docker Desktop
# Visit: https://www.docker.com/products/docker-desktop/

# Verify installation
docker --version
docker-compose --version

# Check Docker is running
docker info
```

### Step 2: Create Project Structure

```powershell
# Create project directory
New-Item -ItemType Directory -Path "C:\rtorrent-mcp" -Force
Set-Location "C:\rtorrent-mcp"

# Create subdirectories
New-Item -ItemType Directory -Path "config" -Force
New-Item -ItemType Directory -Path "downloads" -Force
New-Item -ItemType Directory -Path "watch" -Force
New-Item -ItemType Directory -Path "logs" -Force
```

### Step 3: Create Docker Compose Configuration

```powershell
# Create docker-compose.yml
@"
version: '3.8'

services:
  rtorrent:
    image: linuxserver/rtorrent:latest
    container_name: rtorrent-mcp
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Vienna
      - UMASK_SET=022
      - WEBUI_PORT=8080
    volumes:
      - ./config:/config
      - ./downloads:/downloads
      - ./watch:/watch
      - ./logs:/logs
    ports:
      - "5000:5000"  # SCGI port for MCP server
      - "8080:8080"  # Web UI (optional)
      - "51413:51413"  # DHT port
      - "51413:51413/udp"  # DHT UDP port
    restart: unless-stopped
    networks:
      - rtorrent-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/RPC2"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Web UI (ruTorrent)
  rutorrent:
    image: linuxserver/rutorrent:latest
    container_name: rutorrent-web
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Vienna
    volumes:
      - ./config:/config
      - ./downloads:/downloads
    ports:
      - "8081:80"  # Web UI port
    depends_on:
      - rtorrent
    restart: unless-stopped
    networks:
      - rtorrent-net

networks:
  rtorrent-net:
    driver: bridge
"@ | Out-File -FilePath "docker-compose.yml" -Encoding UTF8
```

### Step 4: Create rTorrent Configuration

```powershell
# Create rtorrent.rc configuration
@"
# SCGI Configuration for MCP Server
scgi_port = 0.0.0.0:5000

# Session Management
session.path.set = /config/session
session.use_lock.set = yes

# Download Directories
directory.default.set = /downloads
schedule2 = watch_directory, 5, 5, load.start=/watch/*.torrent

# Logging
log.execute = /logs/rtorrent.log
log.add_output = info, /logs/rtorrent.log
log.add_output = debug, /logs/rtorrent.debug.log

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

# Network Settings
network.port_range.set = 49164-65534
network.port_random.set = yes
dht.mode.set = auto
protocol.pex.set = yes

# Security Settings
encryption = allow_incoming, try_outgoing, enable_retry

# Austrian Legal Compliance
system.method.set_key = event.download.inserted_new, anime_category, "d.custom1.set=anime"
system.method.set_key = event.download.inserted_new, anime_legal_check, "execute.throw=check_austrian_legal,$d.name="

# File Management
system.file.max_size.set = 268435456
pieces.hash.on_completion.set = yes
pieces.preload.type.set = 2

# Monitoring
system.method.set_key = event.download.finished, anime_finished, "execute.throw=anime_downloaded,$d.name="
"@ | Out-File -FilePath "config\rtorrent.rc" -Encoding UTF8
```

### Step 5: Start the Container

```powershell
# Start rTorrent container
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f rtorrent

# Check container health
docker inspect rtorrent-mcp --format='{{.State.Health.Status}}'
```

### Step 6: Verify Installation

```powershell
# Test SCGI connection
$body = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/RPC2" -Method POST -ContentType "text/xml" -Body $body
    Write-Host "[OK] SCGI connection successful" -ForegroundColor Green
    Write-Host "Response: $response" -ForegroundColor Cyan
} catch {
    Write-Host "[FAIL] SCGI connection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Web UI (optional)
Start-Process "http://localhost:8081"
```

---

## Method 2: WSL2

### Step 1: Enable WSL2

```powershell
# Run as Administrator
# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer, then set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu

# Verify WSL2 installation
wsl --list --verbose
```

### Step 2: Install rTorrent in WSL2

```bash
# Launch WSL2 Ubuntu
wsl

# Update system
sudo apt update && sudo apt upgrade -y

# Install rTorrent
sudo apt install rtorrent -y

# Install additional dependencies
sudo apt install libxmlrpc-core-c3-dev libssl-dev curl -y

# Verify installation
rtorrent -h | grep -i scgi
```

### Step 3: Configure rTorrent in WSL2

```bash
# Create configuration directory
mkdir -p ~/.rtorrent

# Create rtorrent.rc configuration
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

# Create download directory
mkdir -p ~/Downloads

# Start rTorrent
rtorrent -d

# Verify it's running
pgrep rtorrent
```

### Step 4: Windows Integration

```powershell
# Access WSL2 rTorrent from Windows
# The SCGI port will be accessible at localhost:5000

# Test connection from Windows PowerShell
$body = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/RPC2" -Method POST -ContentType "text/xml" -Body $body
    Write-Host "[OK] WSL2 rTorrent connection successful" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] WSL2 rTorrent connection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Create Windows shortcut to WSL2 rTorrent
$shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\rTorrent WSL2.lnk")
$shortcut.TargetPath = "wsl"
$shortcut.Arguments = "rtorrent"
$shortcut.Save()
```

---

## Method 3: Windows Service

### Step 1: Install NSSM

```powershell
# Download NSSM (Non-Sucking Service Manager)
# Visit: https://nssm.cc/download

# Extract to C:\nssm
# Add C:\nssm\win64 to PATH

# Verify installation
nssm version
```

### Step 2: Create Windows Service

```powershell
# Create service for Docker container
nssm install rTorrent "C:\Program Files\Docker\Docker\resources\bin\docker.exe"

# Set service parameters
nssm set rTorrent Arguments "run --rm -d --name rtorrent-mcp -p 5000:5000 -v C:\rtorrent-mcp\config:/config -v C:\rtorrent-mcp\downloads:/downloads linuxserver/rtorrent:latest"
nssm set rTorrent AppDirectory "C:\rtorrent-mcp"
nssm set rTorrent AppStdout "C:\rtorrent-mcp\logs\rtorrent.log"
nssm set rTorrent AppStderr "C:\rtorrent-mcp\logs\rtorrent.error.log"
nssm set rTorrent Start SERVICE_AUTO_START
nssm set rTorrent DisplayName "rTorrent MCP Server"
nssm set rTorrent Description "rTorrent with SCGI support for MCP server"

# Start service
nssm start rTorrent

# Check service status
nssm status rTorrent
```

### Step 3: Service Management

```powershell
# Service management commands
nssm start rTorrent      # Start service
nssm stop rTorrent       # Stop service
nssm restart rTorrent    # Restart service
nssm status rTorrent     # Check status
nssm remove rTorrent     # Remove service

# Windows Service Manager
services.msc
```

---

## Configuration

### Environment Variables

Create a `.env` file in your project directory:

```powershell
# Create .env file
@"
# rTorrent settings
RTORRENT_HOST=localhost
RTORRENT_PORT=5000
RTORRENT_PATH=C:\rtorrent-mcp\downloads

# Nyaa.si settings
NYAA_BASE_URL=https://nyaa.si

# Application settings
DEBUG=false
LOG_LEVEL=INFO

# Austrian Legal Compliance
ALLOWED_CATEGORIES=Anime
ALLOWED_RESOLUTIONS=720p,1080p
DEFAULT_RESOLUTION=720p
PREFERRED_RELEASE_GROUP=ASW
"@ | Out-File -FilePath ".env" -Encoding UTF8
```

### MCP Server Configuration

Update your MCP server configuration:

```json
{
  "mcpServers": {
    "rtorrent-mcp": {
      "command": "python",
      "args": ["-m", "rtorrent_mcp.server", "--transport", "stdio"],
      "cwd": "D:\\Dev\\repos\\rtorrent_mcp",
      "env": {
        "PYTHONPATH": "D:\\Dev\\repos\\rtorrent_mcp\\src",
        "RTORRENT_HOST": "localhost",
        "RTORRENT_PORT": "5000",
        "NYAA_BASE_URL": "https://nyaa.si"
      }
    }
  }
}
```

---

## Verification

### Health Check Script

Create a PowerShell health check script:

```powershell
# Create health check script
@"
#!/usr/bin/env pwsh
# rtorrent-health-check.ps1

param(
    [string]$Host = "localhost",
    [int]$Port = 5000
)

Write-Host " Checking rTorrent health..." -ForegroundColor Cyan

# Check if Docker container is running (if using Docker)
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $containerStatus = docker ps --filter "name=rtorrent-mcp" --format "table {{.Status}}"
    if ($containerStatus -match "Up") {
        Write-Host "[OK] Docker container is running" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Docker container is not running" -ForegroundColor Red
        exit 1
    }
}

# Check if WSL2 process is running (if using WSL2)
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    $wslProcess = wsl pgrep rtorrent
    if ($wslProcess) {
        Write-Host "[OK] WSL2 rTorrent process is running" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] WSL2 rTorrent process is not running" -ForegroundColor Red
        exit 1
    }
}

# Check SCGI port
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect($Host, $Port)
    $tcpClient.Close()
    Write-Host "[OK] SCGI port $Port is accessible" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] SCGI port $Port is not accessible" -ForegroundColor Red
    exit 1
}

# Test XML-RPC connection
try {
    $body = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
    $response = Invoke-RestMethod -Uri "http://$Host`:$Port/RPC2" -Method POST -ContentType "text/xml" -Body $body -TimeoutSec 10
    
    if ($response -match "system.listMethods") {
        Write-Host "[OK] XML-RPC connection successful" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] XML-RPC connection failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[FAIL] XML-RPC connection failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host " rTorrent is healthy and ready for MCP server!" -ForegroundColor Green
"@ | Out-File -FilePath "rtorrent-health-check.ps1" -Encoding UTF8

# Make script executable
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run health check
.\rtorrent-health-check.ps1
```

### MCP Server Test

```powershell
# Test MCP server connection
cd D:\Dev\repos\rtorrent_mcp

# Run MCP server in test mode
python -m rtorrent_mcp.server --transport stdio

# In another terminal, test the connection
python -c "
import asyncio
import sys
sys.path.append('src')
from rtorrent_mcp.services.qbittorrent_client import RTorrentClient

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

---

## Troubleshooting

### Common Issues

#### 1. Docker Container Won't Start

```powershell
# Check Docker logs
docker-compose logs rtorrent

# Check container status
docker-compose ps

# Restart container
docker-compose restart

# Rebuild container
docker-compose down
docker-compose up -d --build
```

#### 2. SCGI Port Already in Use

```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# ports:
# - "5001:5000"  # Use port 5001 instead
```

#### 3. WSL2 Connection Issues

```bash
# Inside WSL2, check if rTorrent is running
pgrep rtorrent

# Check if port is listening
netstat -tlnp | grep :5000

# Restart rTorrent
pkill rtorrent
rtorrent -d

# Check WSL2 IP
ip addr show eth0
```

#### 4. Permission Issues

```powershell
# Fix Docker volume permissions
docker-compose down
docker-compose up -d

# Check file permissions
icacls C:\rtorrent-mcp\config
icacls C:\rtorrent-mcp\downloads
```

#### 5. Firewall Issues

```powershell
# Allow Docker through Windows Firewall
New-NetFirewallRule -DisplayName "Docker rTorrent" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow

# Allow WSL2 through Windows Firewall
New-NetFirewallRule -DisplayName "WSL2 rTorrent" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

### Debug Mode

```powershell
# Enable debug logging in Docker
docker-compose down
docker-compose up -d
docker-compose logs -f rtorrent

# Enable debug logging in WSL2
# Add to ~/.rtorrent.rc
log.add_output = debug, ~/.rtorrent/rtorrent.debug.log

# Restart rTorrent
pkill rtorrent
rtorrent -d
```

---

## Performance Optimization

### Docker Optimization

```powershell
# Update docker-compose.yml with performance settings
@"
version: '3.8'

services:
  rtorrent:
    image: linuxserver/rtorrent:latest
    container_name: rtorrent-mcp
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Vienna
      - UMASK_SET=022
    volumes:
      - ./config:/config
      - ./downloads:/downloads
      - ./watch:/watch
      - ./logs:/logs
    ports:
      - "5000:5000"
      - "8080:8080"
      - "51413:51413"
      - "51413:51413/udp"
    restart: unless-stopped
    networks:
      - rtorrent-net
    # Performance optimizations
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/RPC2"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  rtorrent-net:
    driver: bridge
"@ | Out-File -FilePath "docker-compose.yml" -Encoding UTF8
```

### Windows System Optimization

```powershell
# Increase file descriptor limits (if using WSL2)
# Add to ~/.bashrc in WSL2
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize Windows for Docker
# Enable Hyper-V (if not already enabled)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Optimize Windows Defender exclusions
Add-MpPreference -ExclusionPath "C:\rtorrent-mcp"
Add-MpPreference -ExclusionProcess "docker.exe"
Add-MpPreference -ExclusionProcess "com.docker.backend.exe"
```

### rTorrent Performance Tuning

```powershell
# Update rtorrent.rc with performance settings
@"
# Performance Settings
max_uploads.set = 100
max_connections.set = 500
max_peers.set = 200
throttle.min_peers.normal.set = 50
throttle.min_peers.seed.set = 100
throttle.max_peers.normal.set = 150
throttle.max_peers.seed.set = 200

# Memory optimization
pieces.memory.max.set = 1G
pieces.preload.type.set = 2

# Disk optimization
system.file.max_size.set = 536870912
pieces.hash.on_completion.set = yes

# Network optimization
network.max_open_files.set = 8192
network.max_open_sockets.set = 8192
"@ | Out-File -FilePath "config\rtorrent.rc" -Encoding UTF8 -Append
```

---

## Additional Resources

### Useful Commands

```powershell
# Docker management
docker-compose ps                    # Check container status
docker-compose logs -f rtorrent      # View logs
docker-compose restart               # Restart containers
docker-compose down                  # Stop containers
docker-compose up -d                 # Start containers

# WSL2 management
wsl --list --verbose                 # List WSL distributions
wsl --shutdown                       # Shutdown WSL2
wsl --terminate Ubuntu               # Terminate specific distribution

# Service management
nssm status rTorrent                 # Check service status
nssm restart rTorrent                # Restart service
nssm remove rTorrent                 # Remove service
```

### Monitoring Scripts

```powershell
# Create monitoring script
@"
# monitor-rtorrent.ps1
while ($true) {
    Clear-Host
    Write-Host "rTorrent MCP Server Monitor" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    
    # Check Docker container
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        $containerStatus = docker ps --filter "name=rtorrent-mcp" --format "table {{.Status}}"
        Write-Host "Docker Container:" -ForegroundColor Yellow
        Write-Host $containerStatus
    }
    
    # Check SCGI port
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("localhost", 5000)
        $tcpClient.Close()
        Write-Host "SCGI Port: [OK] Accessible" -ForegroundColor Green
    } catch {
        Write-Host "SCGI Port: [FAIL] Not accessible" -ForegroundColor Red
    }
    
    # Check XML-RPC
    try {
        $body = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
        $response = Invoke-RestMethod -Uri "http://localhost:5000/RPC2" -Method POST -ContentType "text/xml" -Body $body -TimeoutSec 5
        Write-Host "XML-RPC: [OK] Working" -ForegroundColor Green
    } catch {
        Write-Host "XML-RPC: [FAIL] Failed" -ForegroundColor Red
    }
    
    Write-Host "`nPress Ctrl+C to exit..."
    Start-Sleep -Seconds 10
}
"@ | Out-File -FilePath "monitor-rtorrent.ps1" -Encoding UTF8
```

---

## Next Steps

After completing the Windows setup:

1. **Test the MCP Server**: Run `python -m rtorrent_mcp.server --transport stdio`
2. **Configure Claude Desktop**: Add the MCP server to your configuration
3. **Test Anime Search**: Try searching for anime using natural language
4. **Monitor Performance**: Use the monitoring scripts to track health
5. **Optimize Settings**: Adjust configuration based on your usage patterns

---

**Made with  in Vienna, Austria (AT)**

*For Windows users who want reliable rTorrent integration with their MCP server.*



