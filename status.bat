@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   rTorrent MCP Server - Status
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

echo [OK] Docker is running

REM Show container status
echo.
echo Container Status:
docker-compose ps

REM Check SCGI port
echo.
echo Testing SCGI connection...
powershell -Command "try { $body = '<?xml version=\"1.0\"?><methodCall><methodName>system.listMethods</methodName></methodCall>'; $response = Invoke-RestMethod -Uri 'http://localhost:12224/RPC2' -Method POST -ContentType 'text/xml' -Body $body -TimeoutSec 5; if ($response -match 'system.listMethods') { Write-Host '[OK] SCGI connection successful' -ForegroundColor Green } else { Write-Host '[FAIL] SCGI connection failed' -ForegroundColor Red } } catch { Write-Host '[FAIL] SCGI connection failed: ' $_.Exception.Message -ForegroundColor Red }"

REM Show recent logs
echo.
echo Recent Logs ^(last 10 lines^):
docker-compose logs --tail=10

REM Show disk usage
echo.
echo Disk Usage:
if exist "downloads" (
    for /f %%i in ('dir downloads /s /-c ^| find "File(s)"') do echo Downloads: %%i bytes
) else (
    echo Downloads: 0 bytes
)

if exist "config" (
    for /f %%i in ('dir config /s /-c ^| find "File(s)"') do echo Config: %%i bytes
) else (
    echo Config: 0 bytes
)

echo.
echo ========================================
echo   Status Check Complete!
echo ========================================
echo.
echo  Access points:
echo    SCGI API:    http://localhost:12224/RPC2
echo    Web UI:      http://localhost:12222 ^(ruTorrent^)
echo.
echo [i]  Management commands:
echo    start.bat    - Start containers
echo    stop.bat     - Stop containers
echo    status.bat   - Check status
echo    uninstall.bat - Remove everything
echo.
echo Press any key to exit...
pause >nul



