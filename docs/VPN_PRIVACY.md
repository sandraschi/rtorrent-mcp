# VPNs and lawful torrenting (dual-use privacy tools)

What VPNs legitimately do, where they are genuinely necessary, how to pick
one for torrenting — and what they cannot do. Written for lawful use
(FOSS, public domain, your own files): a VPN does not make infringing
downloads lawful anywhere.

> **Not legal advice.** Product facts verified October 2026; providers
> change features — re-check before buying.

## 1. Justified uses (no apology needed)

- **Repressive regimes.** China (Great Firewall), Iran, Russia, and
  similar environments block, throttle, or criminalize ordinary internet
  use. A VPN there is basic access infrastructure — and note the paradox:
  unauthorized VPNs are themselves restricted in China, so this use is
  cat-and-mouse even when the underlying activity is perfectly innocent.
- **Hostile networks.** Public Wi-Fi, hotel and campus networks, and
  snooping ISPs (several monetize browsing data where lawful). Encryption
  to a trusted endpoint is standard hygiene.
- **Lawful torrent privacy.** Seeding Linux ISOs or public-domain films
  still broadcasts your IP to the swarm and to monitors who cannot tell
  lawful from unlawful at a glance. Keeping your address out of bulk
  collection is legitimate even when you have nothing to hide — it also
  keeps you out of opportunistic shakedown datasets.
- **Circumventing blocking overreach.** Piracy Shield-style systems
  over-block legitimate sites (documented: Google Drive, NGOs caught in
  Italian blocks). A VPN with non-local DNS restores access to lawful
  content caught in the net.

## 2. What a VPN does and does not do

**Does:** encrypts traffic to the provider's server, replaces your IP with
theirs in swarms and logs, defeats ISP-level snooping and crude blocking,
with a kill switch preventing leaks on reconnect.

**Does not:** make infringing downloads lawful; protect against malware;
hide you from the provider itself (it sees everything your ISP used to);
protect accounts logged in over the VPN (Google/Reddit/coordination
accounts correlate trivially); survive a provider that logs when compelled.
"No-logs" is a claim about *retention*, verified only by audits and by the
few providers whose servers were seized or subpoenaed with nothing to hand
over. Marketing is not evidence — see §4.

## 3. Selection criteria (in order)

1. **Jurisdiction + ownership.** Who can compel them, and who profits.
   Note consolidations: Kape Technologies (ex-Crossrider) owns
   ExpressVPN, CyberGhost, and Private Internet Access — three brands, one
   parent. That is disclosed here so you can decide what it means to you.
2. **Independent audits, recent.** No-logs and infrastructure audits by
   named firms (Deloitte, KPMG, Cure53), dated, repeated — not a 2019 PDF.
3. **Court/server-seizure record.** The strongest evidence available: PIA
   handed over nothing under FBI subpoenas (2016, 2018); similar
   seizure-tests exist for a handful of others. An audit says "we checked";
   an empty-handed subpoena says "there was nothing."
4. **Kill switch + leak protection.** Non-negotiable for torrenting: IPv6
   and DNS leak blocking, kill switch on by default, and — critically —
   **bind the torrent client to the VPN interface** (qBittorrent/rTorrent
   network interface setting) so a dropped tunnel halts traffic instead of
   leaking your real IP mid-swarm.
5. **Port forwarding (for seeding).** Without an open port you can
   download but barely seed (no incoming connections). Providers differ —
   see §4. Irrelevant if you only download lawful ISOs once; decisive for
   ratio-tracked communities and long-term seeding.
6. **Payment and identity.** Anonymous options (cash, Monero) exist at the
   serious providers; paying with your primary card under your real name
   undoes half the privacy you bought.

## 4. Named providers (torrent-relevant notes, Oct 2026)

| Provider | Base | P2P/port-forward | Notes |
|---|---|---|---|
| **Proton VPN** (paid) | Switzerland | P2P on paid servers (⇄ mark), native port forwarding (NAT-PMP, dynamic port) | Audited, open-source apps; free tier exists but blocks P2P — free is for browsing, not torrents. Best all-rounder for lawful seeding. |
| **Private Internet Access** | USA (Kape-owned) | Port forwarding, P2P everywhere | Court-tested no-logs (empty-handed FBI subpoenas), Deloitte-audited, open-source. US jurisdiction and Kape ownership are the honest caveats — weigh the seizure record against them. |
| **Mullvad** | Sweden | P2P allowed, **no port forwarding since May 2023** (abuse-driven removal, still gone) | Excellent privacy posture (account numbers, cash accepted, audits) but poor seeder: fine for downloading lawful torrents, wrong tool for ratio-tracked seeding. |
| **CyberGhost** (this machine's VPN) | Romania, Kape-owned | P2P on dedicated servers only ("For torrenting" tab), **no port forwarding** | Deloitte-audited 2022/2024/2025 (third audit Feb 2026), quarterly transparency reports, cheap long plans. Fine for downloading (privacy posture solid); poor seeder — no incoming connections, same caveat as Mullvad. Kape ownership caveat applies as with PIA. If it is already paid and running here: keep it, use a P2P server, enable kill switch, bind the client to its interface. |
| **AirVPN** | Italy | Port forwarding, P2P-friendly | Long-standing torrent-community favorite; smaller, technical, fewer audits than the above — verify current audit status before committing. |
| **IVPN** | Gibraltar | P2P allowed, no port forwarding | Privacy-first, audited, transparent team; same seeding caveat as Mullvad. |

**What does NOT work:** free VPNs for torrenting (bandwidth caps,
crowded IPs already flagged, and the well-documented monetization problem
— if you're not paying, your traffic is the product); browser "VPNs" that
are mere HTTPS proxies (they don't cover the torrent client at all); any
setup without a kill switch plus client-interface binding (one reconnect
gap exposes your real IP to the whole swarm); and "no-logs" claims with no
audit and no court record.

## 5. China and repressive contexts, briefly

Where VPN use itself is restricted (China: only state-approved providers
lawful; Iran, Russia, others variously), standard consumer setups may not
connect at all — obfuscation (Shadowsocks, VLESS+REALITY, Tor bridges)
replaces them, which is circumvention-infrastructure territory with its own
risk profile. This doc does not give operational instructions for those
environments beyond: understand that the VPN question there is separate
from and prior to any torrenting question, and get local advice.
