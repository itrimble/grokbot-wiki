# diagrams-pro — Professional network architecture diagrams

Replaces the simplistic Mermaid PNGs in `../diagrams/` for reading quality.

**Published 2026-10-18 (Ian approved):** embedded on the wiki Architecture page (`build.mjs`, section "Detailed diagrams") as the primary detailed images, with the current mermaid renders (`../diagrams/diagram-1..3*.png`, regenerated 2026-10-18 from current `ARCHITECTURE.md`) kept below as the current-docs fallback. Pro renders are a verified 2026-10-17 snapshot (they say 17 bots; current docs say 18 — mermaid renders are authoritative on counts). Diagram 4 is a DESIGN expansion of the approved Phase 0 orchestration mermaid and is captioned as such live. Decision documented here and in the 2026-10-18 wiki commit.

Generated 2026-10-17 (America/Chicago) from wiki sources only. No IPs, keys, tokens, or secrets in any file.

**Verified 2026-10-17** — correctness-audit fixes applied 2026-10-17 (see "Audit fixes" below). Items not live-checked are listed under "Known unverified".

## Files

| Diagram | PNG (2400px wide) | SVG (editable) | Mermaid mirror | Builder |
|---|---|---|---|---|
| 1 Network Architecture | `diagram-1-network-architecture.png` | `.svg` | `.mmd` | `src/build_diagrams.py` |
| 2 Local AI Flow | `diagram-2-local-ai-flow.png` | `.svg` | `.mmd` | same |
| 3 Bot Operating Model | `diagram-3-bot-operating-model.png` | `.svg` | `.mmd` | same |

Icons: `icons/*.svg` from Simple Icons CDN (cdn.simpleicons.org, fetched 2026-10-17): Tailscale, Apple, AMD, Debian, Linux, Ollama, GitHub, Xcode, Swift, Python, Docker, TypeScript. OpenAI icon fetch returned empty and was **not** fabricated — cloud APIs are a labeled shape. Every icon is paired with a text label, so diagrams work if icons are stripped. Licenses/branding belong to their owners; use is nominative (identifying the platform in Ian's own stack).

Regenerate: `python3 src/build_diagrams.py` (needs `cairosvg`, `pip install --break-system-packages cairosvg`). Edit layout/text in that script, re-run, then visually Read the PNGs.

## Diagram 1 — Network Architecture: relationships in plain prose

- **Box → Mac mini (SSH 22 via tssh, HTTPS 443 for oMLX):** The shared Debian VM (17 bots, no GPU) reaches the Mini two ways only. SSH is work (files, builds, commands); 443 is inference (oMLX `/v1`). ACL allows exactly 22+443 to Mini, 22-only to MBP/Neo.
- **Box → MBP / Neo (SSH 22 only):** No AI serving there. Neo is often offline, so nothing may depend on it synchronously.
- **Box → NAS: deliberately absent.** NAS is a backup mirror reachable from the Mini side; the agent host has no ACL path. Backup access ≠ runtime permission.
- **Nothing → Box inbound; no Funnel:** The Box only dials out (userspace `tailscaled` + SOCKS5 `localhost:1055`, because a shared VM has no privileged kernel TUN). Mini serving is tailnet-only; the old public Funnel (8765) is gone.
- **Mini → NAS mirror:** `~/projects` on the Mini is canonical; `/Volumes/nas/projects` mirrors it. Ian settled 2026-10-16 that NAS edits are allowed — editable mirror, still not source of truth.
- **Omarchy → Cloud (HTTPS egress):** The Ryzen/ROCm PC is a tailnet member (`omarchy-ai`) and strongest coding/local-AI box, but Linux, so Xcode builds stay on the Mini.
- **Box → Omarchy: UNVERIFIED.** No documented box→omarchy Ollama service path or ACL/port for it — both diagrams draw it dashed and labeled "path/ACL not documented — UNVERIFIED". Use Omarchy via Grok Bot machine access, not as a documented Ollama service endpoint from the Box.
- **Cloud (Diagram 1):** Hermes cloud **primaries + fallbacks** (see Diagram 2) — not fallbacks only.
- **Mini storage (live 2026-10-17):** models ~104 GB (Ollama ~25 GB + HF cache ~79 GB); disk ~923 GiB free. (Box disk, where mentioned in source docs: 20 GB used / ~106 GB avail.)

Enthusiast notes on the diagram: why userspace Tailscale + SOCKS5, least-privilege ACL blast-radius, unified-memory budget, canonical-vs-mirror.

## Diagram 2 — Local AI Flow: relationships in plain prose

- **Request sources → Box SOCKS5 proxy:** Bots/Hermes never touch a GPU directly; they make an API/task call. Box egress is userspace Tailscale SOCKS5 (`localhost:1055`). **Verified 2026-10-17:** oMLX answers through that proxy — SOCKS5 `/v1/models` returned Ornith-1.5-9B-oQ4e-mtp, bge-m3, gemma, Qwen3-TTS.
- **Proxy → Mini oMLX (HTTPS 443, `tailscale serve`, tailnet-only):** OpenAI-compatible `/v1`, so tools swap base-URL not code. Models: Ornith-1.5-9B (~17 tok/s main chat), gemma-4-e4b-it-4bit (fast), bge-m3-mlx-8bit (embeddings/RAG vectors — not chat), Qwen3-TTS (audio — not chat). Limits that shape design: one 9B at a time, max 2 concurrent, ~6s cold load into unified memory; 4/8-bit quantization is how 9B fits the ~11.3 GiB GPU budget of a 16 GB M4 (shared CPU+GPU pool, no separate VRAM).
- **Proxy → Mini Ollama via SSH only:** Ollama on the Mini is local-only; you SSH in, there is no tailnet Ollama API. Live list (2026-10-17): qwen3.5:9b, qwen3:8b, qwen3:4b, gemma3:4b, gemma4:e4b. (The former Qwen3.6-35B IQ2_M line was removed — it is not on the Mini.)
- **Tailnet → Omarchy Ollama/ROCm:** RX 6600 XT `gfx1032` with qwen3:8b + bge-m3, 62 GB RAM — strongest local coding/AI, with the caveat that gfx1032 is an older ROCm tier (verify per-model, no CUDA parity assumed).
- **Two Hermeses, opposite philosophies (most-confused relationship):** Box Hermes v0.22.2 is cloud-first (primary gpt-6.1-sol via openai-codex; fallbacks DeepSeek-V4-Pro → MiniMax-M3; aux pinned gpt-5.6-terra; oMLX *not configured*; no cron/gateway; tuned by Hermes Tuner). Mini Hermes v0.22.2 is cloud-then-local (primary MiniMax-M3 cloud; *only* fallback local oMLX; 7 total cron jobs — 6 active + 1 paused oMLX warm-up (Warden, never run) — so cron health depends on cloud plus a manually started `omlx start` after reboot — it is not a login item; Oct 15 four jobs failed "Connection error" (history — recovered Oct 16–17, all active jobs ok). Fallback arrows show exactly this, no secrets.

## Diagram 3 — Bot Operating Model: relationships in plain prose

- **Atlas is the portfolio gate:** X Bookmarks flags, Book Growth's Friday Amazon, Archivist's meaningful changes, and Foreman's read-only PROJECTS/ACTIVITY all flow *into* Atlas; Atlas routes work *out* to Beacon (sites), Scout (listening), Ledger (experiments). Nothing self-promotes to shipped.
- **Scout ↔ Ledger ↔ Studio loop:** Scout's success data feeds Ledger; Studio supplies experiment IDs to Ledger; Ledger owns the numbers/IDs. Scout delegates bulk research down to Hermes (CLI execution engine, not a bot).
- **Runtime split (Oct 10, 2026):** Atlas sends runtime failures to Warden (runtime owner); Improve My Bots owns config/profiles and forwards symptoms to Warden; Hermes Tuner tunes only the *Box* Hermes install and trades incident context with Warden. Warden gates Scout's X MCP access.
- **Foreman → Hermes, Foreman → Atlas:** Foreman owns the single canonical root `AIMacMini:~/projects`, delegates heavy coding to Hermes, and reports status read-only to Atlas (reporters cannot edit the plan). NAS mirror status follows Diagram 1.

## Legend (all diagrams)

Navy = Box/gate/decision · Teal = Mini/local MLX serving/signals · Blue = Omarchy GPU PC/sites/projects/proxy · Amber = storage/experiments · Purple = Hermes execution/content · Rose = cloud egress/runtime/constraint. Solid arrow = documented path (label = port/protocol/purpose); dashed large boundary = Tailscale tailnet. ⚠ = caveat or unverified item, explicitly marked.

## Sources

`content/ARCHITECTURE.md`, `content/infra/{tailnet,local-ai,macs,box,omarchy}.md`, `content/bots/*.md` in this wiki repo (which cite `/workspace/tailscale/{PLAN,LOCAL-AI}.md`, audits, Hermes Tuner notes). Speeds, model names, budgets as documented Oct 2026.

## Wiki embed (done 2026-10-18; original proposal below)

In `content/ARCHITECTURE.md`, after the Mermaid blocks, propose adding:

```markdown
## Detailed diagrams (professional renders)
![Network architecture](assets/diagrams-pro/diagram-1-network-architecture.png)
![Local AI flow](assets/diagrams-pro/diagram-2-local-ai-flow.png)
![Bot operating model](assets/diagrams-pro/diagram-3-bot-operating-model.png)
See assets/diagrams-pro/README.md for prose explanations, legend, and regeneration.
```

Path may need adjusting to however `build.mjs` serves `assets/` — verify before publishing. This task did not publish/deploy, change DNS, or edit `content/*.md`.

## Audit fixes applied 2026-10-17

1. oMLX via Box SOCKS5: UNVERIFIED warning removed — verified live 2026-10-17 (SOCKS5 `/v1/models` returned Ornith-1.5-9B-oQ4e-mtp, bge-m3, gemma, Qwen3-TTS). Diagrams/README/`.mmd` now state "Verified 2026-10-17".
2. Mini Hermes cron: "6 jobs" → "7 total — 6 active + 1 paused oMLX warm-up (Warden, never run)". Oct 15 4-job failure dated as history; recovered Oct 16–17 (all active jobs ok).
3. Qwen3.6-35B IQ2_M Ollama line removed from Diagram 2. Live Mini Ollama: qwen3.5:9b, qwen3:8b, qwen3:4b, gemma3:4b, gemma4:e4b.
4. Diagram 1 cloud box: "Hermes cloud fallbacks only" → "Hermes cloud primaries + fallbacks (see Diagram 2)".
5. Box → Omarchy consistent in both diagrams: dashed + "path/ACL not documented — UNVERIFIED"; use Omarchy via Grok Bot machine access, not a documented box→omarchy Ollama service path. No port/ACL invented.
6. Storage refreshed: Mini models ~104 GB (Ollama ~25 GB + HF cache ~79 GB), disk ~923 GiB free (live 2026-10-17).
7. "Verified 2026-10-17" footer/date on all three diagrams plus the Known unverified callout below.

## Known unverified

Not live-checked in the 2026-10-17 audit — do not treat as verified:

- Tailnet ACL details (no ACL file check was available).
- Omarchy specs (Ian/Atlas-verified only).
- ~17 tok/s + concurrency limits (unbenchmarked).
- oMLX login-item status.

## Known limitations

Subtitles under card titles are small at thumbnail size (legible at full 2400px). Diagram 2's Omarchy route line crosses the Box-Hermes card gutter. Mermaid `.mmd` mirrors are simplified (no icons/colors) for quick edits; the SVG/Python builder is the professional source of truth.

## Orchestration update — 2026-10-17 (design, not published)
Source: `/workspace/orchestration-design-2026-10-17.md`. Diagrams 1–3 revised in `src/build_diagrams.py` to add model use cases on every model/service (Ornith-1.5-9B=main local chat/cron fallback; gemma-4-e4b=fast/small; bge-m3=embeddings/RAG; Qwen3-TTS=speech; mini/omarchy Ollama qwen3:8b=local/bulk coding assist+sweeps; cloud gpt-6.1-sol/MiniMax-M3/DeepSeek primaries+fallback order) with existing Simple Icons + text labels, and to carry the orchestration design (Box control plane: Atlas gate publish/spend/send/ship + file queue/run log; Warden health; Ledger EXP metrics).

| Diagram | PNG | SVG | Mermaid mirror | Builder |
|---|---|---|---|---|
| 4 Orchestration — Control Plane, Routing & Failover (DESIGN) | `diagram-4-orchestration.png` | `.svg` | `.mmd` | `src/build_diagrams.py` |

Diagram 4 nodes/edges: Ian→Atlas→Box file queue → (tssh SSH22, SOCKS5→oMLX HTTPS443, machine connector, HTTPS egress) → mini (Xcode/oMLX/Ollama/cron), omarchy (bulk/heavy, conditional ACL), MBP (video+deputy restore), Box-as-worker (cloud CLIs); bottom band = 5-min probes/dead-man/load-shed, Ledger dashboard→EXP→ROUTING.md, failover (oMLX→launchd→cloud; mini→MBP restore; Box→MBP nightly copy). Dashed/conditional = omarchy serving port, LiteLLM pilot. Verified 2026-10-17 facts retained; no publishing/deploy/DNS done.

## Apple platform chips — added 2026-10-18 (preview branch)

A `PLATFORMS:` strip was added under the header of all 4 diagrams via `src/build_diagrams.py` (`SVG.chip`/`platform_strip`, regenerated PNG+SVG with `python3 src/build_diagrams.py`, cairosvg):

- Diagram 1: `macOS · Mac mini / MacBook Pro / Neo`, `iOS · apps built on Mac mini`
- Diagram 2: `macOS · Mac mini (oMLX / Ollama host)`
- Diagram 3: `macOS · AIMacMini ~/projects (Foreman)`
- Diagram 4: `macOS · Mac mini / MacBook Pro`

Only platforms present in the docs/diagrams were chipped (macOS machines; iOS apps built on the Mini per `infra/macs.md` + `infra/apple-dev.md`). iPadOS, tvOS and watchOS do **not** appear in the docs, so no chips were invented for them.

Icon source/license: the glyph inside each chip is the existing `icons/apple.svg` in this folder — from Simple Icons (cdn.simpleicons.org, fetched 2026-10-17; Simple Icons is CC0-1.0, brand trademarks belong to their owners, use here is nominative with a text label). No Apple logo was drawn, scraped, or fabricated; every chip pairs the glyph with plain platform-name text so it reads correctly if the icon is stripped.
