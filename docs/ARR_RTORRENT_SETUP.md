# Configuring rTorrent as a download client in *arr apps

For *arr-managed content (movies via Radarr, TV via Sonarr, etc.), the *arr
should communicate with rTorrent **directly** — not through rtorrent-mcp.

## Why not through rtorrent-mcp?

*arr apps are download **managers**. The flow is:

```
*arr (searches indexer, decides what to grab)
  → *arr sends magnet/torrent to rTorrent (via built-in Download Client config)
    → rTorrent downloads
      → *arr detects completion (polls rTorrent XML-RPC or watches download folder)
        → *arr imports + renames the files
          → *arr notifies Plex/Jellyfin
```

If rtorrent-mcp sat in the middle, it would break the completion-detection loop:
*arr would lose visibility into download progress and import timing.

## Setup: Radarr / Sonarr

1. In the *arr web UI, go to **Settings > Download Clients**
2. Click **+** (Add Download Client)
3. Select **rTorrent**
4. Configure:

   | Field | Value |
   |-------|-------|
   | Host | `localhost` (or your Docker host) |
   | Port | `12224` (TCP — nginx XML-RPC proxy) |
   | URL Path | `/RPC2` |
   | Category | `movies` (Radarr) / `tv` (Sonarr) — used for folder routing |
   | Directory | leave empty (rTorrent manages its own) |

5. Click **Test** — *arr should confirm connectivity
6. Click **Save**

## Setup: Prowlarr

Prowlarr manages indexers and can proxy download clients to other *arr apps.
Add rTorrent as a download client in Prowlarr for centralized management:

1. **Settings > Download Clients > + > rTorrent**
2. Same host/port/path as above
3. Prowlarr will push the client config to connected *arr apps

## Ports used

| Service | Port |
|---------|------|
| rTorrent XML-RPC (nginx) | `12224` |
| ruTorrent WebUI | `12222` |
| rtorrent-mcp backend | `10910` |
| rtorrent-mcp frontend (Vite) | `10911` |

## Verifying

After configuring, add a movie in Radarr or a series in Sonarr. The *arr will:
1. Search configured indexers
2. Pick the best release
3. Send the magnet/torrent to rTorrent via XML-RPC
4. Monitor progress
5. Import the files on completion
6. Trigger a Plex/Jellyfin library scan

You can verify by checking the *arr's **Activity** or **Queue** page — it should
show the download with progress in rTorrent.

## Troubleshooting

| Symptom | Likely cause |
|---------|-------------|
| *arr cannot test connection | Wrong port (use `12224`, not `5000`). Wrong path (appends `/RPC2`). rTorrent container not running. |
| *arr sends download but never imports | Check rTorrent downloads directory matches what *arr's **Remote Path Mapping** expects. |
| *arr shows "Completed/Failed" immediately | Magic save or unpack issue. Check rTorrent's download location and *arr's root folder settings. |
