@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   rTorrent MCP Server - Start
echo ========================================
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Docker is not installed or not in PATH
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo [FAIL] docker-compose.yml not found
    echo Please run install.bat first
    pause
    exit /b 1
)

echo [OK] Starting rTorrent containers...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [FAIL] Failed to start containers
    echo Check Docker logs: docker-compose logs
    pause
    exit /b 1
)

echo [OK] Containers started successfully

REM Wait a moment for containers to initialize
echo.
echo Waiting for rTorrent to initialize...
timeout /t 5 /nobreak >nul

REM Show container status
echo.
echo Container Status:
docker-compose ps

REM Test connection
echo.
echo Testing SCGI connection...
powershell -Command "try { $body = '<?xml version=\"1.0\"?><methodCall><methodName>system.listMethods</methodName></methodCall>'; $response = Invoke-RestMethod -Uri 'http://localhost:12224/RPC2' -Method POST -ContentType 'text/xml' -Body $body -TimeoutSec 10; if ($response -match 'system.listMethods') { Write-Host '[OK] SCGI connection successful' -ForegroundColor Green } else { Write-Host '[FAIL] SCGI connection failed' -ForegroundColor Red } } catch { Write-Host '[FAIL] SCGI connection failed: ' $_.Exception.Message -ForegroundColor Red }"

echo.
echo ========================================
echo   rTorrent MCP Server Started!
echo ========================================
echo.
echo  Access points:
echo    SCGI API:    http://localhost:12224/RPC2
echo    Web UI:      http://localhost:12222 ^(ruTorrent^)
echo.
echo [i]  Management commands:
echo    docker-compose ps          - Check container status
echo    docker-compose logs -f     - View logs
echo    docker-compose restart     - Restart containers
echo    docker-compose down        - Stop containers
echo.
echo Press any key to exit...
pause >nul



