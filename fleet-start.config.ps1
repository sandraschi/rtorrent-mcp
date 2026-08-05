# Per-repo fleet start config for rtorrent-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'rtorrent-mcp'
    BackendPort  = 10910
    FrontendPort = 10911
    HealthPath   = '/api/health'
    WebRoot      = 'D:\Dev\repos\rtorrent-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'rtorrent_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10910' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
