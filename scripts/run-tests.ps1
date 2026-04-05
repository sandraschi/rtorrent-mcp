# RTorrent MCP Server Test Runner
# PowerShell script to run tests on Windows using UV

param(
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Coverage,
    [switch]$Verbose,
    [string]$TestPath = "tests"
)

Write-Host " Running RTorrent MCP Server Tests" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if UV is available
try {
    $uvVersion = & uv --version 2>$null
    Write-Host "[OK] UV found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] UV not found. Please install with: pip install uv" -ForegroundColor Red
    Write-Host "   Then run: uv sync --dev" -ForegroundColor Yellow
    exit 1
}

# Check if dependencies are installed
if (-not (Test-Path ".venv")) {
    Write-Host "[WARN]  Virtual environment not found. Installing dependencies..." -ForegroundColor Yellow
    & uv sync --dev
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Build pytest arguments
$args = @()

if ($Unit) {
    $args += "-m", "unit"
    Write-Host " Running unit tests only" -ForegroundColor Cyan
}

if ($Integration) {
    $args += "-m", "integration"
    Write-Host " Running integration tests only" -ForegroundColor Cyan
}

if ($Coverage) {
    $args += "--cov=src/rtorrent_mcp", "--cov-report=term-missing", "--cov-report=html:htmlcov", "--cov-fail-under=80"
    Write-Host " Running with coverage reporting" -ForegroundColor Cyan
}

if ($Verbose) {
    $args += "-v", "--tb=short"
}

$args += $TestPath

Write-Host " Executing: uv run pytest $($args -join ' ')" -ForegroundColor Yellow
Write-Host ""

try {
    # Run pytest with UV
    & uv run pytest @args

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] All tests passed!" -ForegroundColor Green

        if ($Coverage) {
            Write-Host " Coverage report available at: htmlcov/index.html" -ForegroundColor Cyan
        }
    } else {
        Write-Host ""
        Write-Host "[FAIL] Some tests failed. Exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "[FAIL] Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host " Test execution completed" -ForegroundColor Green
