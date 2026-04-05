@echo off
echo ========================================
echo   rTorrent MCP Server - Installation
echo ========================================

REM Stop and remove any existing containers
echo [1/4] Cleaning up existing containers...
docker stop rtorrent-mcp >nul 2>&1
docker rm rtorrent-mcp >nul 2>&1

REM Find and remove any containers using port 12222
for /f "tokens=1" %%i in ('docker ps -a --filter "publish=12222" --format "{{.ID}}" 2^>nul') do (
    echo Removing container %%i using port 12222
    docker stop %%i >nul 2>&1
    docker rm %%i >nul 2>&1
)

echo [OK] Cleanup complete

REM Create directories
echo.
echo [2/4] Creating directories...
if not exist "config" mkdir config
if not exist "watch" mkdir watch
if not exist "logs" mkdir logs

REM Create download directory in Windows Downloads
set DOWNLOAD_PATH=%USERPROFILE%\Downloads\rtorrent
if not exist "%DOWNLOAD_PATH%" mkdir "%DOWNLOAD_PATH%"
echo [OK] Download directory: %DOWNLOAD_PATH%

REM Create rTorrent config
echo.
echo [3/4] Creating rTorrent configuration...
(
echo # SCGI Configuration
echo scgi_port = 0.0.0.0:5000
echo.
echo # Session Management
echo session.path.set = /data/session
echo session.use_lock.set = yes
echo.
echo # Download Directories
echo directory.default.set = /downloads
echo schedule2 = watch_directory, 5, 5, load.start=/watch/*.torrent
echo.
echo # Logging
echo log.execute = /data/rtorrent.log
echo log.add_output = info, /data/rtorrent.log
echo.
echo # Performance Settings
echo max_uploads.set = 50
echo max_connections.set = 200
echo max_peers.set = 100
) > config\rtorrent.rc
echo [OK] Configuration created

REM Create .env file
echo.
echo [4/4] Creating environment configuration...
(
echo # rTorrent settings
echo RTORRENT_HOST=localhost
echo RTORRENT_PORT=12222
echo RTORRENT_PATH=%DOWNLOAD_PATH%
echo.
echo # Nyaa.si settings
echo NYAA_BASE_URL=https://nyaa.si
echo.
echo # Application settings
echo DEBUG=false
echo LOG_LEVEL=INFO
) > .env
echo [OK] Environment configuration created

REM Start container with port 12222
echo.
echo Starting rTorrent container on port 12222...
docker run -d ^
  --name rtorrent-mcp ^
  --restart unless-stopped ^
  -p 12222:5000 ^
  -p 12223:8080 ^
  -p 51413:51413 ^
  -p 6881:6881/udp ^
  -v "%cd%\config:/data" ^
  -v "%DOWNLOAD_PATH%:/downloads" ^
  -v "%cd%\watch:/watch" ^
  -v "%cd%\logs:/logs" ^
  -e TZ=Europe/Vienna ^
  -e PUID=1000 ^
  -e PGID=1000 ^
  crazymax/rtorrent-rutorrent:latest

if %errorlevel% neq 0 (
    echo [FAIL] Failed to start container
    echo Check Docker logs: docker logs rtorrent-mcp
    pause
    exit /b 1
)

echo [OK] Container started successfully

REM Wait for container to be ready
echo.
echo Waiting for rTorrent to initialize...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo  Download directory: %DOWNLOAD_PATH%
echo.
echo  Access points:
echo    SCGI API:    http://localhost:12222/RPC2
echo    Web UI:      http://localhost:12223
echo.
echo [i]  Management commands:
echo    docker ps                    - Check container status
echo    docker logs rtorrent-mcp     - View logs
echo    docker restart rtorrent-mcp  - Restart container
echo    docker stop rtorrent-mcp     - Stop container
echo    docker rm rtorrent-mcp       - Remove container
echo.
echo Press any key to exit...
pause >nul
