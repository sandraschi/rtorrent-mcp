@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   rTorrent MCP Server - Uninstall
echo ========================================
echo.

REM Check if Docker is running
echo [1/3] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not in PATH
    echo Please install Docker Desktop for Windows first
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

echo ✅ Docker is running

REM Stop and remove containers
echo.
echo [2/3] Stopping and removing containers...
docker-compose down
if %errorlevel% neq 0 (
    echo ⚠️  Some containers may not have been running
)

REM Remove Docker images (optional)
echo.
echo Do you want to remove the Docker images? ^(This will free up disk space^)
echo [Y]es / [N]o ^(default: No^)
set /p remove_images="Choice: "
if /i "%remove_images%"=="Y" (
    echo Removing Docker images...
    docker rmi linuxserver/rtorrent:latest 2>nul
    docker rmi linuxserver/rutorrent:latest 2>nul
    echo ✅ Docker images removed
) else (
    echo ✅ Docker images kept
)

REM Ask about data removal
echo.
echo Do you want to remove all data? ^(config, downloads, logs^)
echo [Y]es / [N]o ^(default: No^)
set /p remove_data="Choice: "
if /i "%remove_data%"=="Y" (
    echo [3/3] Removing project data...
    if exist "config" rmdir /s /q "config"
    if exist "downloads" rmdir /s /q "downloads"
    if exist "watch" rmdir /s /q "watch"
    if exist "logs" rmdir /s /q "logs"
    if exist ".env" del ".env"
    echo ✅ Project data removed
) else (
    echo [3/3] Keeping project data...
    echo ✅ Project data preserved
)

echo.
echo ========================================
echo   Uninstall Complete!
echo ========================================
echo.
echo 🗑️  Removed:
echo    - Docker containers
if /i "%remove_images%"=="Y" (
    echo    - Docker images
)
if /i "%remove_data%"=="Y" (
    echo    - Project data ^(config, downloads, logs^)
) else (
    echo    - Project data preserved
)
echo.
echo 📁 Remaining files:
echo    - docker-compose.yml
echo    - install.bat
echo    - uninstall.bat
if /i "%remove_data%"=="N" (
    echo    - config\ ^(if exists^)
    echo    - downloads\ ^(if exists^)
    echo    - watch\ ^(if exists^)
    echo    - logs\ ^(if exists^)
    echo    - .env ^(if exists^)
)
echo.
echo Press any key to exit...
pause >nul



