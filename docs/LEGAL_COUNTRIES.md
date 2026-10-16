# Country specifics (torrenting enforcement)

How the same swarm is a different risk in different places. General
orientation — your jurisdiction is the only one that matters, and it
changes, so verify locally. In every country below, *uploading/seeding*
infringing content is treated more severely than downloading.

> **Not legal advice.** Ask a lawyer in your country when it matters.

## Austria (home base — this tool's default context)

Private copying is levy-compensated and personal downloading is in practice
tolerated; enforcement targets uploaders and commercial operators, not
household downloaders. The built-in `legal_management` tool's risk model
assumes this context. "Tolerated in practice" is not "lawful" — it is
forbearance, and forbearance can change.

**The German Abmahnung machine never crossed the border.** No
mass-Abmahnung industry ever developed in Austria, for structural reasons:
Austrian ISPs face strict hurdles on disclosing subscriber data, without
which the mass-letter business model (pennies per letter, profit on the
settlement rate) cannot function. Sporadic individual cases exist — a
€2,000 letter via provider disclosure made the press in 2020 — but they
are anecdotes, not an industry. An Austrian Plexer is, practically
speaking, home free: the enforcement apparatus that makes German
torrenting a contact sport simply does not exist here. That holds unless
the law changes massively (EU-wide disclosure rules or a domestic
enforcement shift would be the tripwires to watch — this is what the
TorrentFreak feed in [safety](SAFETY_TORRENTING.md) §0 is for).

## Germany

The Abmahnindustrie is **not** defunct — rumors of its death are stale.
As of late 2026, Frommer Legal (formerly Waldorf Frommer, Munich) is still
actively sending filesharing Abmahnungen, alongside firms like Nimrod and
IPPC Law, with demands typically €850–2,500 per title (damages plus costs,
capped by §97a UrhG). Recent developments: firms have diversified beyond
classic P2P, and decade-old cases resurface as lawsuits (limitation games
included). The mechanism is unchanged: swarm monitoring → court-ordered ISP
disclosure → letter to the account holder. Even short seeding counts.
Operating a client for infringing content in Germany without serious
precautions remains the highest-risk ordinary-user scenario in Europe.

**Settlement dynamics (specifically German).** The €850–2,500 figure is an
opening bid, not a price. The industry runs on settlement rate: mass
letters at low marginal cost, a fraction of recipients paying a few
hundred euros to make it go away, funding the next wave. Litigating a
single download to judgment would not pencil out — which is precisely why
almost nobody should pay the headline figure, sign the attached
Unterlassungserklärung unmodified (it sets up contract penalties for any
repeat), or respond at all before a lawyer looks at the letter. Standard
German defense practice: ignore the deadline panic, have counsel file a
modified declaration (modifizierte Unterlassungserklärung), negotiate the
sum down to a fraction. None of this is legal advice — it is a description
of how the machine observably works. And note what this implies in
reverse: the machine needs its 5–10% payers. It gets them, every year,
which is why the letters are still being mailed in 2026.

## USA

DMCA notice-and-strike systems at major ISPs (warnings, throttling,
account review), plus periodic John-Doe lawsuits against swarm IPs and
criminal prosecution reserved for large-scale distributors. Universities
and employers often enforce their own (stricter) policies on their networks.

## UK

No broad private-copying exception (the 2014 exception was quashed in
2015). ISP warning-letter schemes have run in waves; enforcement is
sporadic but the legal position is strict on paper.

## Japan

The strictest of the listed countries for downloaders: criminal penalties
for knowing infringing downloads (up to 2 years imprisonment on paper),
ISP cooperation, and active enforcement. **Do not torrent infringing
content in Japan.** Lawful uses (FOSS, public domain) are unaffected —
the protocol is legal; the content rules are what bite.

## The rule behind the table

Three variables decide your risk everywhere: (1) what the content is,
(2) whether you uploaded (you almost certainly did — see
[safety](SAFETY_TORRENTING.md) §3), and (3) whether your country's
enforcement machine is currently pointed at people like you. Only (1) is
fully in your control. Act accordingly.
