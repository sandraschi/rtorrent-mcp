# RTorrent MCP Server MCPB Packaging Script
# Uses the official Anthropic MCPB tool for packaging

param(
    [switch]$NoSign,
    [string]$OutputDir = "dist"
)

Write-Host "🚀 Building RTorrent MCP Server with MCPB" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if MCPB is installed
try {
    $mcpbVersion = & mcpb --version 2>$null
    Write-Host "✅ MCPB version: $mcpbVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ MCPB not found. Please install with: npm install -g @anthropic-ai/mcpb" -ForegroundColor Red
    exit 1
}

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host "📦 Using MCPB to validate and build package..." -ForegroundColor Yellow

try {
    # Validate the manifest
    Write-Host "🔍 Validating manifest..." -ForegroundColor Cyan
    & mcpb validate dxt/manifest.json
    if ($LASTEXITCODE -ne 0) {
        throw "Manifest validation failed"
    }

    # Create a temporary directory with the proper MCPB structure
    $tempDir = Join-Path $env:TEMP "mcpb-build-$(Get-Random)"
    New-Item -ItemType Directory -Path $tempDir | Out-Null

    try {
        # Copy the manifest
        Copy-Item "dxt/manifest.json" -Destination $tempDir

        # Copy source files
        Write-Host "📋 Copying source files..." -ForegroundColor Cyan
        Copy-Item -Path "src" -Destination $tempDir -Recurse -Force

        # Install dependencies to the temp directory
        Write-Host "📚 Installing dependencies..." -ForegroundColor Cyan
        $libDir = Join-Path $tempDir "lib"
        New-Item -ItemType Directory -Path $libDir | Out-Null

        # Install dependencies
        & dxt_env\Scripts\pip.exe install -r requirements.txt --target $libDir --no-deps

        # Pack the directory using MCPB
        Write-Host "🗜️  Creating MCPB package..." -ForegroundColor Cyan
        $packagePath = "$OutputDir/rtorrent-mcp-1.0.0.mcpb"
        & mcpb pack $tempDir $packagePath

        if ($LASTEXITCODE -ne 0) {
            throw "MCPB pack failed"
        }

    } finally {
        # Clean up temp directory
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force
        }
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
Write-Host "🏁 MCPB Build process completed" -ForegroundColor Green
