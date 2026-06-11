Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Webapp start: uvicorn backend (repo root) + Vite (this folder)
$WebPort = 10911
$BackendPort = 10910
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath

$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 1. Free ports (dev restarts)
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Frontend deps
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }

# Sync Python deps
Push-Location $ProjectRoot
uv sync
Pop-Location

# 3. Backend in a second window (must run from repo root for pyproject + .env)
Write-Host "Starting Python backend on 127.0.0.1:$BackendPort ..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$ProjectRoot'; uv run uvicorn rtorrent_mcp.server:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Wait until uvicorn is listening (Vite proxies to this; starting Vite first causes ECONNREFUSED)
Write-Host "Waiting for backend to accept connections on $BackendPort..." -ForegroundColor Cyan
$ready = $false
$attempts = 120
for ($i = 0; $i -lt $attempts; $i++) {
    $listen = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue
    if ($listen) {
        $ready = $true
        break
    }
    Start-Sleep -Milliseconds 500
}

if (-not $ready) {
    Write-Host ""
    Write-Host "Backend did not bind to port $BackendPort within 60s." -ForegroundColor Red
    Write-Host "Check the other PowerShell window: uv PATH, ``uv sync``, import errors, or port already in use." -ForegroundColor Yellow
    exit 1
}

Write-Host "Backend is listening on 127.0.0.1:$BackendPort" -ForegroundColor Green

# 5. Vite dev (proxies /api and /mcp to 10910)
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green

# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev -- --port $WebPort --host



