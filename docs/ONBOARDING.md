# Onboarding

rtorrent-mcp needs two external things before it is fully useful:

1. **rTorrent** (the BitTorrent client it drives) - a Docker container.
2. **Anna's Archive** (optional ebook/paper search) - a free account, because its
   slow downloads are now gated behind registration (anti-bot).

This page is your setup checklist. Skip Anna's Archive if you only want
torrents - search and download links for Anna's simply stay hidden.

---

## 1. rTorrent (required)

Run the bundled container (or your own rTorrent/ruTorrent):

```powershell
docker compose up -d
```

This starts `crazymax/rtorrent-rutorrent` with nginx XML-RPC on the host port
mapped in `docker-compose.yml`. Default host/port for the MCP:

```env
RTORRENT_HOST=127.0.0.1
RTORRENT_PORT=12224
```

Sanity check (from a PowerShell prompt):

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:12224/RPC2" -Method POST `
  -ContentType "text/xml" -Body '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
```

If you get the method list back, rTorrent is reachable and the Dashboard's Host
App card will flip from UNREACHABLE to READY.

Full setup, plugins, RSS and troubleshooting: `docs/RTORRENT_SETUP.md`.

---

## 2. Anna's Archive (optional, but recommended for ebooks)

Anna's Archive now requires an account even for the free "slow" downloads
(anti-bot). Register once and hand the MCP a session cookie.

### Register (use a burner email)

1. Go to `https://annas-archive.is`.
2. Register a free account. **Using a burner email is a good idea** - archives
   like this are frequent targets and privacy-sensitive; don't tie your real
   inbox to it.
3. Log in.

### Grab the session cookie

Open your browser DevTools (F12) and copy the `session` cookie value:

- Chrome / Edge: DevTools > Application (or Storage) > Cookies >
  `https://annas-archive.is` > `session` > `Value`.
- Firefox: DevTools > Storage > Cookies > `session`.

Paste either the full `name=value` pair or just the value.

### Set it in the MCP (two ways)

**A. In the webapp Settings (recommended, persisted)**

Start the webapp (`start.ps1`), open **Settings > Anna's Archive session**, paste
the cookie, click **Save session**. The cookie is stored server-side in
`data/annas_session.cookie` (gitignored - never committed).

**B. In `.env`**

```env
ANNAS_SESSION_COOKIE=session=<your-value>
# ANNAS_SESSION_COOKIE_NAME=session   # only if the cookie has a different name
# ANNAS_ARCHIVE_BASE=https://annas-archive.is
```

Then restart the backend.

### Verify

- Open the Anna's Archive page: the amber "Downloads need a session" banner
  disappears once the cookie is set.
- Open a book detail: download links (magnet / direct) now appear where the
  book has them.

Search works with **no** account. Note the search base is configurable
(`ANNAS_ARCHIVE_BASE` / `ANNAS_ARCHIVE_MIRRORS`) because Anna's rotates domains -
`.org` no longer resolves and `.li`/`.gl` are anti-bot gated.

---

## Sanity checklist

- [ ] `docker compose up -d` and rTorrent responds on `/RPC2`
- [ ] Dashboard Host App card shows READY
- [ ] (optional) Anna's Archive session cookie saved in Settings
- [ ] (optional) Anna's search returns real results; detail shows download links
