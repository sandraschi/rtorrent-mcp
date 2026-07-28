# Per-repo fleet start config for qbt-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'qbt-mcp'
    BackendPort  = 10910
    FrontendPort = 10911
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\qbt-mcp\web_sota'
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
