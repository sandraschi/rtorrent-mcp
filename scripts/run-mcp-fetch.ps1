# PowerShell wrapper script to ensure only ONE mcp/fetch container runs
# This script ensures a single persistent container is used for mcp/fetch
# Uses the container's entrypoint command: mcp-server-fetch

$ContainerName = "mcp-fetch-singleton"
$ImageName = "mcp/fetch"

# Check if container exists (running or stopped)
$containerExists = docker ps -a --filter "name=^${ContainerName}$" --format "{{.Names}}"

if ($containerExists) {
    # Container exists - check if it's running
    $isRunning = docker ps --filter "name=^${ContainerName}$" --format "{{.Names}}"
    
    if ($isRunning) {
        # Container is running - exec the server command (entrypoint)
        docker exec -i $ContainerName mcp-server-fetch
    } else {
        # Container exists but is stopped - start and attach (runs entrypoint)
        docker start -ai $ContainerName
    }
} else {
    # Container doesn't exist - create it with fixed name (no --rm, runs entrypoint)
    docker run -i --name $ContainerName $ImageName
}
