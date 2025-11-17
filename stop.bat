@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   rTorrent MCP Server - Stop
echo ========================================
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not in PATH
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found
    echo Please run install.bat first
    pause
    exit /b 1
)

echo ✅ Stopping rTorrent containers...
docker-compose down

if %errorlevel% neq 0 (
    echo ❌ Failed to stop containers
    echo Check Docker logs: docker-compose logs
    pause
    exit /b 1
)

echo ✅ Containers stopped successfully

REM Show container status
echo.
echo Container Status:
docker-compose ps

echo.
echo ========================================
echo   rTorrent MCP Server Stopped!
echo ========================================
echo.
echo 🛠️  To start again:
echo    start.bat
echo.
echo 🛠️  Management commands:
echo    docker-compose up -d      - Start containers
echo    docker-compose restart    - Restart containers
echo    docker-compose logs -f    - View logs
echo.
echo Press any key to exit...
pause >nul



