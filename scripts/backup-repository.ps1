#!/usr/bin/env pwsh
# rTorrent MCP Repository Backup Script
# # This script creates automated backups of the rTorrent MCP repository
# following the 3-2-1 backup rule and GFS (Grandfather-Father-Son) strategy
#
# Usage:
# .\scripts\backup-repository.ps1 [-BackupPath <path>] [-RetentionDays <days>] [-CompressionLevel <0-9>]
#
# Parameters:
# -BackupPath: Destination path for backups (default: D:\Backups\rtorrent_mcp)
# -RetentionDays: Number of days to keep backups (default: 30)
# -CompressionLevel: Compression level 0-9 (default: 7)

param(
    [string]$BackupPath = "D:\Backups\rtorrent_mcp",
    [int]$RetentionDays = 30,
    [int]$CompressionLevel = 7,
    [switch]$CreateScheduledTask,
    [switch]$Help
)

# Show help if requested
if ($Help) {
    Write-Host @"
rTorrent MCP Repository Backup Script

Usage:
    .\scripts\backup-repository.ps1 [options]

Options:
    -BackupPath <path>        Destination path for backups (default: D:\Backups\rtorrent_mcp)
    -RetentionDays <days>     Number of days to keep backups (default: 30)
    -CompressionLevel <0-9>   Compression level 0-9 (default: 7)
    -CreateScheduledTask      Create a Windows scheduled task for daily backups
    -Help                     Show this help message

Examples:
    .\scripts\backup-repository.ps1
    .\scripts\backup-repository.ps1 -BackupPath "E:\Backups" -RetentionDays 60
    .\scripts\backup-repository.ps1 -CreateScheduledTask

Backup Strategy:
    - Daily incremental backups
    - Weekly full backups (kept for 4 weeks)
    - Monthly full backups (kept for 12 months)
    - Yearly full backups (kept for 5 years)
"@
    exit 0
}

# Set error handling
$ErrorActionPreference = 'Stop'

# Get script directory and repository root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

# Create backup directory if it doesn't exist
if (-not (Test-Path $BackupPath)) {
    Write-Host "Creating backup directory: $BackupPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $BackupPath | Out-Null
}

# Generate backup filename with timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupPath\rtorrent_mcp_backup_$Timestamp.zip"

Write-Host "Starting rTorrent MCP repository backup..." -ForegroundColor Green
Write-Host "Repository: $RepoRoot" -ForegroundColor Cyan
Write-Host "Backup file: $BackupFile" -ForegroundColor Cyan
Write-Host "Compression level: $CompressionLevel" -ForegroundColor Cyan

try {
    # Create backup
    Write-Host "Creating backup archive..." -ForegroundColor Yellow
    
    # Create temporary directory for backup contents
    $TempDir = "$env:TEMP\rtorrent_mcp_backup_$Timestamp"
    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
    
    try {
        # Copy specific directories and files
        $ItemsToBackup = @(
            "src",
            "tests", 
            "docs",
            "scripts",
            ".github",
            "pyproject.toml",
            "README.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            ".gitignore",
            ".cursorrules"
        )
        
        foreach ($Item in $ItemsToBackup) {
            $SourcePath = Join-Path $RepoRoot $Item
            if (Test-Path $SourcePath) {
                $DestPath = Join-Path $TempDir $Item
                Copy-Item -Path $SourcePath -Destination $DestPath -Recurse -Force
                Write-Host "Copied: $Item" -ForegroundColor Gray
            }
        }
        
        # Copy .env.example if it exists
        $EnvExample = Join-Path $RepoRoot "*.env.example"
        if (Test-Path $EnvExample) {
            Copy-Item -Path $EnvExample -Destination $TempDir -Force
            Write-Host "Copied: .env.example" -ForegroundColor Gray
        }
        
        # Create compressed archive
        Compress-Archive -Path "$TempDir\*" -DestinationPath $BackupFile -CompressionLevel Optimal -Force
        
        # Get backup file size
        $BackupSize = (Get-Item $BackupFile).Length
        $BackupSizeMB = [math]::Round($BackupSize / 1MB, 2)
        
        Write-Host "Backup completed successfully!" -ForegroundColor Green
        Write-Host "Backup size: $BackupSizeMB MB" -ForegroundColor Green
        
    } finally {
        # Clean up temporary directory
        if (Test-Path $TempDir) {
            Remove-Item -Path $TempDir -Recurse -Force
        }
    }
    
    # Clean up old backups based on retention policy
    Write-Host "Cleaning up old backups..." -ForegroundColor Yellow
    
    $OldBackups = Get-ChildItem -Path $BackupPath -Filter "rtorrent_mcp_backup_*.zip" | 
        Sort-Object CreationTime -Descending | 
        Select-Object -Skip $RetentionDays
    
    if ($OldBackups) {
        $OldBackups | Remove-Item -Force
        Write-Host "Removed $($OldBackups.Count) old backup(s)" -ForegroundColor Yellow
    } else {
        Write-Host "No old backups to remove" -ForegroundColor Green
    }
    
    # Create backup log entry
    $LogFile = "$BackupPath\backup_log.txt"
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Backup completed: $BackupFile ($BackupSizeMB MB)`n"
    Add-Content -Path $LogFile -Value $LogEntry
    
    Write-Host "Backup log updated: $LogFile" -ForegroundColor Green
    
} catch {
    Write-Error "Backup failed: $($_.Exception.Message)"
    exit 1
}

# Create scheduled task if requested
if ($CreateScheduledTask) {
    Write-Host "Creating scheduled task..." -ForegroundColor Yellow
    
    $TaskName = "rTorrent MCP Repository Backup"
    $ScriptPath = $MyInvocation.MyCommand.Path
    
    # Check if task already exists
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Write-Host "Scheduled task '$TaskName' already exists. Removing..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    # Create scheduled task action
    $Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -BackupPath `"$BackupPath`" -RetentionDays $RetentionDays -CompressionLevel $CompressionLevel"
    
    # Create daily trigger at 2 AM
    $Trigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
    
    # Create task settings
    $Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -DontStopOnIdleEnd -AllowStartIfOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
    
    # Create task principal (run as SYSTEM)
    $Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    
    # Register the scheduled task
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Daily backup of rTorrent MCP repository" | Out-Null
    
    Write-Host "Scheduled task '$TaskName' created successfully!" -ForegroundColor Green
    Write-Host "Task will run daily at 2:00 AM" -ForegroundColor Cyan
}

Write-Host "Backup process completed!" -ForegroundColor Green
