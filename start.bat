@echo off
REM rTorrent MCP - fleet-standard launcher (delegates to start.ps1)
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
