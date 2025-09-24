# RTorrent MCP Server Test Runner
# PowerShell script to run tests on Windows

param(
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Coverage,
    [switch]$Verbose,
    [string]$TestPath = "tests"
)

Write-Host "🧪 Running RTorrent MCP Server Tests" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if pytest is available
try {
    $pytestVersion = & python -m pytest --version 2>$null
    Write-Host "✅ pytest found: $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pytest not found. Please install with: pip install pytest pytest-cov" -ForegroundColor Red
    exit 1
}

# Build pytest arguments
$args = @()

if ($Unit) {
    $args += "-m", "unit"
    Write-Host "🎯 Running unit tests only" -ForegroundColor Cyan
}

if ($Integration) {
    $args += "-m", "integration"
    Write-Host "🔗 Running integration tests only" -ForegroundColor Cyan
}

if ($Coverage) {
    $args += "--cov=qbtmcp", "--cov-report=term-missing", "--cov-report=html:htmlcov", "--cov-fail-under=80"
    Write-Host "📊 Running with coverage reporting" -ForegroundColor Cyan
}

if ($Verbose) {
    $args += "-v", "--tb=short"
}

$args += $TestPath

Write-Host "🚀 Executing: pytest $($args -join ' ')" -ForegroundColor Yellow
Write-Host ""

try {
    # Run pytest
    & python -m pytest @args

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ All tests passed!" -ForegroundColor Green

        if ($Coverage) {
            Write-Host "📊 Coverage report available at: htmlcov/index.html" -ForegroundColor Cyan
        }
    } else {
        Write-Host ""
        Write-Host "❌ Some tests failed. Exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "❌ Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🏁 Test execution completed" -ForegroundColor Green
