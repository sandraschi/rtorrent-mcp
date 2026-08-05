Param([switch]$Headless, [switch]$NoBrowser)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$env:FASTMCP_LOG_LEVEL = 'WARNING'
$BackendPort = 10910
$FrontendPort = 10911

# rtorrent-mcp Start - Standards-Compliant SOTA
Write-Host 'Starting rtorrent-mcp...' -ForegroundColor Cyan
Set-Location $PSScriptRoot

# Clear zombie listeners on the registered ports before binding
foreach ($port in @($BackendPort, $FrontendPort)) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

Write-Host 'Starting Standardized Fullstack Hybrid...' -ForegroundColor Green
# Launch backend Hidden by default to prevent console spam
$env:MCP_PORT = "$BackendPort"
$env:MCP_HOST = '127.0.0.1'
Start-Process pwsh -ArgumentList '-NoProfile', '-Command', 'uv run -m rtorrent_mcp' -WindowStyle Hidden

# Backend readiness poll (not a fixed sleep)
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { }
    Start-Sleep -Seconds 1
}
if ($ready) {
    Write-Host "Backend ready on http://127.0.0.1:$BackendPort (MCP /mcp)" -ForegroundColor Green
} else {
    Write-Host "WARNING: backend not reachable on :$BackendPort after 60s" -ForegroundColor Yellow
}

if ($SkipFrontend) { return }
Set-Location web_sota
Start-Process pwsh -ArgumentList '-NoProfile', '-Command', "npm run dev -- --port $FrontendPort --host 127.0.0.1" -WindowStyle Hidden

# Auto-open browser once the frontend is reachable
if (-not $NoBrowser) {
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $fr = Invoke-WebRequest -Uri "http://127.0.0.1:$FrontendPort" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($fr.StatusCode -eq 200) {
                Start-Process "http://127.0.0.1:$FrontendPort"
                break
            }
        } catch { }
        Start-Sleep -Seconds 1
    }
}
