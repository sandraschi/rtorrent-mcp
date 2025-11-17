# RTorrent MCP Server MCPB Packaging Script
# Uses UV for dependency management and MCPB for packaging

param(
    [switch]$NoSign,
    [string]$OutputDir = "dist"
)

Write-Host "🚀 Building RTorrent MCP Server with UV + MCPB" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Check if UV is available
try {
    $uvVersion = & uv --version 2>$null
    Write-Host "✅ UV found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ UV not found. Please install with: pip install uv" -ForegroundColor Red
    exit 1
}

# Check if MCPB is installed
try {
    $mcpbVersion = & mcpb --version 2>$null
    Write-Host "✅ MCPB version: $mcpbVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ MCPB not found. Please install with: npm install -g @anthropic-ai/mcpb" -ForegroundColor Red
    exit 1
}

# Ensure dependencies are installed
Write-Host "📚 Ensuring dependencies are installed..." -ForegroundColor Yellow
& uv sync --dev
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host "📦 Building Python package with UV..." -ForegroundColor Yellow

try {
    # Build the Python package first
    & uv build
    if ($LASTEXITCODE -ne 0) {
        throw "UV build failed"
    }

    # Validate the manifest
    Write-Host "🔍 Validating MCPB manifest..." -ForegroundColor Cyan
    & mcpb validate dxt/manifest.json
    if ($LASTEXITCODE -ne 0) {
        throw "Manifest validation failed"
    }

    # Create MCPB package
    Write-Host "🗜️  Creating MCPB package..." -ForegroundColor Cyan
    $packagePath = "$OutputDir/rtorrent-mcp.mcpb"
    
    if (Test-Path "dxt") {
        & mcpb pack dxt $packagePath
    } else {
        Write-Host "⚠️  dxt directory not found, creating fallback package..." -ForegroundColor Yellow
        # Create a basic package structure
    $tempDir = Join-Path $env:TEMP "mcpb-build-$(Get-Random)"
    New-Item -ItemType Directory -Path $tempDir | Out-Null

    try {
            # Copy essential files
            Copy-Item "pyproject.toml" -Destination $tempDir
        Copy-Item -Path "src" -Destination $tempDir -Recurse -Force

            # Create basic manifest if not exists
            if (!(Test-Path "dxt/manifest.json")) {
                $manifest = @{
                    name = "rtorrent-mcp"
                    version = "1.0.0"
                    description = "RTorrent MCP Server - Austrian anime automation"
                    author = "Sandra's Austrian Anime Automation"
                    license = "MIT"
                } | ConvertTo-Json -Depth 3
                $manifest | Out-File -FilePath "$tempDir/manifest.json" -Encoding UTF8
            }
            
        & mcpb pack $tempDir $packagePath
        } finally {
            if (Test-Path $tempDir) {
                Remove-Item $tempDir -Recurse -Force
            }
        }
    }

        if ($LASTEXITCODE -ne 0) {
            throw "MCPB pack failed"
    }

    # Check if package was created
    if (Test-Path $packagePath) {
        $fileSize = (Get-Item $packagePath).Length
        Write-Host "📊 Package size: $([math]::Round($fileSize / 1MB, 2)) MB" -ForegroundColor Green

        # Verify package
        Write-Host "✅ Verifying package..." -ForegroundColor Cyan
        & mcpb verify $packagePath
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Package verification successful" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Package verification failed, but continuing..." -ForegroundColor Yellow
        }
    } else {
        throw "Package file not found after build"
    }

    Write-Host ""
    Write-Host "🎉 MCPB Package created successfully!" -ForegroundColor Green
    Write-Host "📍 Location: $packagePath" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Installation Instructions:" -ForegroundColor Yellow
    Write-Host "   1. Locate $packagePath" -ForegroundColor White
    Write-Host "   2. Drag the .mcpb file to Claude Desktop" -ForegroundColor White
    Write-Host "   3. Configure rTorrent connection settings in the extension setup" -ForegroundColor White
    Write-Host "   4. Restart Claude Desktop" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Configuration Required:" -ForegroundColor Yellow
    Write-Host "   - rTorrent host: localhost (default)" -ForegroundColor White
    Write-Host "   - rTorrent port: 5000 (default)" -ForegroundColor White
    Write-Host "   - Download directory: Choose your preferred location" -ForegroundColor White

} catch {
    Write-Host "❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🏁 UV + MCPB Build process completed" -ForegroundColor Green
