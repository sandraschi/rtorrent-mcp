# Torrenting safety (even lawful use has sharp edges)

Technical risk notes for operating a client. These apply regardless of what
you download — some apply *especially* to lawful users moving valuable data.

> **Not legal advice.** General information for orientation only.

## 1. Swarm visibility: your IP is public

Every peer in a swarm sees your IP address, and so does anyone passively
monitoring the swarm — which, for popular infringing content, includes
professional anti-piracy firms continuously. Notices go to the account
holder (whosever name is on the internet contract), not necessarily the
person who clicked. Lawful swarms attract less monitoring, but the
visibility is a protocol property, not a content property.

## 2. VPNs move trust; they don't erase risk

A VPN replaces your IP with the provider's in the swarm. That is all it
does. It does not make infringing downloads lawful, it does not protect
against malware, and several "no-log" providers have produced logs when
compelled. Free VPNs monetize something — usually you. If you use one,
pay for it, read its jurisdiction and ownership, enable the kill switch,
and understand exactly which guarantee you bought (very few).

## 3. Default upload = default distribution liability

Clients seed while downloading, and most keep seeding after. Every byte
uploaded is an act of distribution in copyright terms — the liability
category pursued most aggressively in Germany (Abmahnungen), the US
(John-Doe suits), and Japan (criminal cases). Check your client's seeding
defaults *before* the first download: global ratio limits, per-torrent
seeding caps, and scheduler behavior. "I only wanted to download" does not
describe a client that uploaded 3 GB overnight.

## 4. Malware and fakes

Executables from untrusted swarms are a classic infection vector; fake
"codec packs" and passworded archives with URL-lures are the oldest tricks
in the book. Media files themselves are far less risky but not zero-risk
(subtitle exploits, malicious playlist files). Rules: scan everything,
never run bundled installers, prefer the containerized setup (the Docker
stack exists partly for this isolation), and treat password-protected
archives with links inside as hostile until proven otherwise.

## 5. Operational hygiene

- **Containerize.** Run rTorrent in Docker (the provided compose stack),
  not as your user on bare metal. A compromised client process then owns a
  container, not your documents.
- **Separate identities.** The email/account used for indexers and trackers
  should be a burner, unique per service. Breaches of tracker databases
  happen regularly.
- **Watch the disk.** Runaway seeding and completed-download retention fill
  disks silently; set quotas and completion actions (`LINK_MODE=hardlink`
  keeps seeding originals while Plex libraries reference links).
- **Separate the money.** Never pay for anything grey with a primary card
  or real identity. Better: don't pay for anything grey at all.
- **Know your country's enforcement style** — [country specifics](LEGAL_COUNTRIES.md).
  The same swarm is a different risk in Vienna, Berlin, Texas, London, and Tokyo.
