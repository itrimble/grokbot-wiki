import re, os, html
import cairosvg
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR=os.path.join(BASE,"icons")
def icon_path(name):
    p=os.path.join(ICON_DIR,name+".svg")
    if not os.path.exists(p): return None
    t=open(p).read()
    m=re.search(r'<path[^>]*\bd="([^"]+)"',t)
    f=re.search(r'fill="([^"]+)"',t)
    return (m.group(1), f.group(1) if f else "#111") if m else None

COLORS={"navy":"#0F2A44","teal":"#0E9A8B","blue":"#2563EB","amber":"#D97706","rose":"#E11D48","slate":"#64748B","purple":"#7C3AED","green":"#15803D"}
class SVG:
    def __init__(self,w,h,title,subtitle):
        self.w=w; self.h=h; self.parts=[]
        self.parts.append(f'<rect width="{w}" height="{h}" fill="#F4F7FB"/>')
        self.parts.append(f'<rect width="{w}" height="118" fill="#0F2A44"/>')
        self.parts.append(f'<text x="48" y="52" font-family="Inter,Arial,sans-serif" font-size="36" font-weight="800" fill="white">{html.escape(title)}</text>')
        self.parts.append(f'<text x="48" y="88" font-family="Inter,Arial,sans-serif" font-size="21" fill="#BFD7EA">{html.escape(subtitle)}</text>')
        self.parts.append(f'<text x="{w-48}" y="52" font-family="Inter,Arial,sans-serif" font-size="20" font-weight="700" fill="white" text-anchor="end">REMNANT SECURITY  •  GROK BOT FLEET</text>')
        self.parts.append(f'<text x="{w-48}" y="84" font-family="Inter,Arial,sans-serif" font-size="17" fill="#8FB0CC" text-anchor="end">Verified 2026-10-17  •  No IPs / keys shown</text>')
        # defs marker
        self.defs='<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#334155"/></marker><marker id="arrT" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#0E9A8B"/></marker><marker id="arrA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#D97706"/></marker></defs>'
    def icon(self,name,x,y,size=34):
        d=icon_path(name)
        if not d: return
        path,fill=d
        scale=size/24
        self.parts.append(f'<g transform="translate({x},{y}) scale({scale})"><path d="{path}" fill="{fill}"/></g>')
    def chip(self,x,y,label,icon="apple"):
        w=34+len(label)*9.5
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="13" fill="white" stroke="#94A3B8" stroke-width="1.2"/>')
        self.icon(icon,x+8,y+4,18)
        self.parts.append(f'<text x="{x+30}" y="{y+18}" font-family="Inter,Arial,sans-serif" font-size="16" font-weight="700" fill="#0F2A44">{html.escape(label)}</text>')
        return w
    def platform_strip(self,labels):
        x=48
        self.parts.append(f'<text x="{x}" y="{140}" font-family="Inter,Arial,sans-serif" font-size="16" font-weight="800" fill="#475569">PLATFORMS:</text>')
        x+=118
        for lab in labels:
            x+=self.chip(x,122,lab)+12
    def card(self,x,y,w,h,title,bullets,accent="blue",icon=None,subtitle=None,title_size=26):
        c=COLORS[accent]
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="white" stroke="#D7E0EC" stroke-width="1.5"/>')
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="4" fill="{c}"/>')
        tx=x+22
        if icon:
            self.icon(icon,x+18,y+22,36); tx=x+66
        self.parts.append(f'<text x="{tx}" y="{y+42}" font-family="Inter,Arial,sans-serif" font-size="{title_size}" font-weight="800" fill="#0F2A44">{html.escape(title)}</text>')
        yy=y+72
        if subtitle:
            self.parts.append(f'<text x="{x+22}" y="{yy}" font-family="Inter,Arial,sans-serif" font-size="17" font-weight="700" fill="{c}">{html.escape(subtitle)}</text>'); yy+=28
        for b in bullets:
            # wrap manually: split by |
            for line in b.split("|"):
                self.parts.append(f'<text x="{x+22}" y="{yy}" font-family="Inter,Arial,sans-serif" font-size="19" fill="#334155">•  {html.escape(line)}</text>'); yy+=24
            # small gap handled by line height
        return (x,y,w,h)
    def box(self,x,y,w,h,label,fill="#EEF2F7",stroke="#CBD5E1",size=19,weight=600,color="#1E293B",rx=10):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>')
        self.parts.append(f'<text x="{x+w/2}" y="{y+h/2+7}" font-family="Inter,Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="middle">{html.escape(label)}</text>')
    def arrow(self,x1,y1,x2,y2,label=None,color="#334155",dashed=False,marker="arr",lx=None,ly=None,label_size=17):
        dash=' stroke-dasharray="8 6"' if dashed else ''
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5" marker-end="url(#{marker})"{dash}/>')
        if label:
            mx=lx if lx is not None else (x1+x2)/2; my=ly if ly is not None else (y1+y2)/2
            # pill
            w=len(label)*9.2+22
            self.parts.append(f'<rect x="{mx-w/2}" y="{my-16}" width="{w}" height="32" rx="16" fill="white" stroke="{color}"/>')
            self.parts.append(f'<text x="{mx}" y="{my+6}" font-family="Inter,Arial,sans-serif" font-size="{label_size}" font-weight="700" fill="{color}" text-anchor="middle">{html.escape(label)}</text>')
    def poly(self,pts,label=None,color="#334155",dashed=False,marker="arr",lx=None,ly=None):
        dash=' stroke-dasharray="8 6"' if dashed else ''
        p=" ".join(f"{x},{y}" for x,y in pts)
        self.parts.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="2.5" marker-end="url(#{marker})"{dash}/>')
        if label and lx is not None:
            w=len(label)*9.2+22
            self.parts.append(f'<rect x="{lx-w/2}" y="{ly-16}" width="{w}" height="32" rx="16" fill="white" stroke="{color}"/>')
            self.parts.append(f'<text x="{lx}" y="{ly+6}" font-family="Inter,Arial,sans-serif" font-size="17" font-weight="700" fill="{color}" text-anchor="middle">{html.escape(label)}</text>')
    def note(self,x,y,w,h,title,bullets,accent="amber"):
        c=COLORS[accent]
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#FFF7ED" stroke="{c}" stroke-width="1.5"/>')
        self.parts.append(f'<text x="{x+20}" y="{y+34}" font-family="Inter,Arial,sans-serif" font-size="21" font-weight="800" fill="{c}">⚠  {html.escape(title)}</text>')
        yy=y+62
        for b in bullets:
            for line in b.split("|"):
                self.parts.append(f'<text x="{x+20}" y="{yy}" font-family="Inter,Arial,sans-serif" font-size="18" fill="#7C2D12">{html.escape(line)}</text>'); yy+=23
    def legend(self,x,y,items):
        self.parts.append(f'<rect x="{x}" y="{y}" width="720" height="{34+len(items)*26}" rx="12" fill="white" stroke="#D7E0EC"/>')
        self.parts.append(f'<text x="{x+18}" y="{y+28}" font-family="Inter,Arial,sans-serif" font-size="19" font-weight="800" fill="#0F2A44">LEGEND</text>')
        yy=y+56
        for col,lab in items:
            self.parts.append(f'<rect x="{x+18}" y="{yy-14}" width="26" height="14" rx="4" fill="{COLORS[col]}"/>')
            self.parts.append(f'<text x="{x+54}" y="{yy}" font-family="Inter,Arial,sans-serif" font-size="18" fill="#334155">{html.escape(lab)}</text>'); yy+=26
    def save(self,name):
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">{self.defs}'+"".join(self.parts)+'</svg>'
        open(os.path.join(BASE,name+".svg"),"w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(BASE,name+".png"), output_width=2400)
        print(name, "saved")

# DIAGRAM 1
s=SVG(2400,1680,"1  •  Network Architecture — Machines, Tailnet & Trust Boundaries","How Ian's fleet reaches each other: tailnet-only, least-privilege ACLs, no public Funnel, no inbound to the Box")
# tailnet boundary
s.parts.append('<rect x="40" y="150" width="2320" height="1180" rx="24" fill="#EAF6F3" fill-opacity="0.55" stroke="#0E9A8B" stroke-width="3" stroke-dasharray="14 8"/>')
s.parts.append('<text x="70" y="190" font-family="Inter,Arial" font-size="22" font-weight="800" fill="#0B6B5E">TAILSCALE TAILNET  —  PRIVATE TRUST BOUNDARY  •  No Funnel  •  Tailnet-only serving</text>')
s.platform_strip(["macOS \u00b7 Mac mini / MacBook Pro / Neo","iOS \u00b7 apps built on Mac mini"])
s.icon("tailscale",2280,158,40)
# Box
s.card(80,230,620,360,"THE BOX — Shared Agent Host",[
 "Debian 13 • 8 vCPU Xeon • 15 GB RAM • NO GPU",
 "17 Grok Bots (one shared VM, separate desktops)",
 "CLIs: claude • codex • hermes • swift • xtool",
 "Userspace tailscaled (no kernel TUN / root net)",
 "SOCKS5 proxy: localhost:1055  →  tailnet egress",
 "SSH helper: /workspace/tailscale/tssh (paramiko)",
 "ORCHESTRATION CONTROL PLANE (design 2026-10-17):|Atlas gate + file queue + run log (see Diag. 4)",
 "⛔  NEVER run local models here (no GPU, low RAM)",
],"navy",icon="debian",subtitle="tag:grokbox  •  NOTHING connects inbound to grokbox")
# Mini
s.card(880,230,680,360,"MAC MINI  M4  —  Canonical + Apple + Local AI",[
 "Apple M4 • 16 GB unified memory (~11.3 GiB GPU budget)",
 "CANONICAL: ~/projects  (single source of truth)",
 "Xcode builds: SnapDog (macOS) + iOS apps",
 "oMLX: OpenAI-compatible /v1 via tailscale serve",
 "oMLX USE: Ornith-9B = chat / cron fallback","gemma = fast • bge-m3 = embed/RAG • TTS = speech",
 "Ollama (SSH-only): qwen3/3.5-9b, gemma = local|coding assist, sweeps, classification",
 "Hermes v0.22.2 (separate)",
 "Models ~104 GB: Ollama ~25 GB + HF cache ~79 GB",
 "Disk ~923 GiB free (live 2026-10-17)",
],"teal",icon="apple",subtitle="AIMacMini  •  grokbox → mini : TCP 22 + 443 ONLY")
# Omarchy
s.card(1740,230,580,360,"OMARCHY — Strongest Dev / AI PC",[
 "Ryzen 9 5950X 16c/32t • 62 GB RAM • 1.9 TB",
 "Radeon RX 6600 XT • ROCm gfx1032 (working)",
 "Ollama: qwen3:8b + bge-m3 (embeddings)",
 "claude • codex • hermes • Grok Bot",
 "USE: heavy coding/builds, bulk local inference|(Phase 1, if ACL port approved — see Diag. 4)",
 "Linux → NO Xcode (Apple builds stay on Mini)",
],"blue",icon="amd",subtitle="tailnet: omarchy-ai  •  heavy coding + local AI")
# bottom row
s.card(80,700,520,300,"MACBOOK PRO  M4 Max",[
 "Video / studio work (proposed renders)",
 "Reachable: SSH 22 ONLY from grokbox",
 "No oMLX / Ollama role documented",
],"purple",icon="apple",subtitle="grokbox → MBP : TCP 22 only")
s.card(680,700,520,300,"THE NEO — Laptop",[
 "Often offline — design for async / retry",
 "Reachable: SSH 22 ONLY from grokbox",
 "No always-on services assumed",
],"slate",icon="apple",subtitle="grokbox → Neo : TCP 22 only")
s.card(1280,700,520,300,"NAS — Backup Mirror",[
 "Mirror: /Volumes/nas/projects",
 "Mini ~/projects stays CANONICAL",
 "All NAS edits allowed (Ian, 2026-10-16)",
 "⛔  NO Box access (ACL denied)",
],"amber",subtitle="Mirror ≠ canonical  •  editable ≠ source of truth")
s.card(1880,700,440,300,"CLOUD APIs (outside tailnet)",[
 "Hermes cloud primaries + fallbacks|(see Diagram 2)",
 "gpt-6.1-sol = Box Hermes primary coding","MiniMax-M3 = Mini primary • DeepSeek = Box|fallback #1 (see Diagram 2)",
 "Reached via normal HTTPS egress",
 "Not a tailnet member • no keys shown",
],"rose",subtitle="Egress only  •  see Diagram 2")
# arrows box->mini etc routed in gutter
s.arrow(700,340,880,340,"SSH 22  •  tssh",lx=790,ly=315)
s.arrow(700,430,880,430,"HTTPS 443  •  oMLX /v1",color="#0E9A8B",marker="arrT",lx=790,ly=460)
s.poly([(400,590),(400,660),(340,660),(340,700)],"SSH 22",lx=400,ly=640)
s.poly([(500,590),(500,640),(940,640),(940,700)],"SSH 22",lx=720,ly=625)
s.poly([(2000,590),(2000,640),(2050,640),(2050,700)],"HTTPS egress",color="#E11D48",lx=2050,ly=625)
# NAS arrow from mini
s.poly([(1240,590),(1240,650),(1540,650),(1540,700)],"Mini → NAS mirror",color="#D97706",marker="arrA",lx=1390,ly=640)
# insight row
s.note(80,1060,720,220,"WHY THIS SHAPE? (ENTHUSIAST NOTES)",[
 "Userspace Tailscale = agent VM joins tailnet without|privileged kernel networking; apps opt-in via SOCKS5.",
 "Least-privilege ACL: Box can SSH, only Mini gets 443|for oMLX. Compromised bot ≠ full LAN access.",
 "Tailnet-only (no Funnel) = oMLX API is never public."])
s.note(840,1060,720,220,"UNIFIED MEMORY IN ONE LINE",[
 "M4's 16 GB is shared CPU+GPU — no PCIe VRAM copy,|but the model, OS, and apps compete for same pool.",
 "That is why GPU budget is ~11.3 GiB, not 16 GiB,|and why only one 9B model loads at a time."])
s.note(1600,1060,720,220,"CANONICAL vs MIRROR",[
 "Edit ~/projects on Mini; NAS is a mirror you may|also edit — it does not become the source of truth.",
 "Box has NO NAS path: backup access is not an|agent-runtime permission."])
s.poly([(700,270),(730,205),(1710,205),(1740,270)],"Box \u2192 Omarchy: UNVERIFIED \u2014 path/ACL not documented (machine access, not Ollama svc)",dashed=True,lx=1220,ly=205)
s.legend(80,1340,[("navy","Box / agent host"),("teal","Mac mini / local-AI serving"),("blue","Omarchy / discrete-GPU dev PC"),("amber","Storage / mirror"),("rose","External cloud (egress only)")])
s.parts.append('<text x="840" y="1365" font-family="Inter,Arial" font-size="19" font-weight="700" fill="#0F2A44">READING THE EDGES</text>')
for i,t in enumerate(["Solid = documented, verified path  •  Label = port + protocol + purpose","Dashed boundary = Tailscale tailnet. Anything outside needs explicit HTTPS egress.","If a line is not drawn, ACL denies it — especially: inbound → grokbox, and Box → NAS."]):
    s.parts.append(f'<text x="840" y="{1395+i*26}" font-family="Inter,Arial" font-size="18" fill="#475569">{t}</text>')
s.note(80,1520,2320,95,"KNOWN UNVERIFIED \u2014 Verified 2026-10-17; items below were NOT live-checked in this audit",[
 "Tailnet ACL details (no ACL file check)  \u2022  Omarchy specs (Ian/Atlas-verified only)|~17 tok/s + concurrency (unbenchmarked)  \u2022  oMLX login-item status"])
s.parts.append('<text x="48" y="1645" font-family="Inter,Arial" font-size="16" fill="#64748B">Sources: wiki content/infra/{tailnet,box,macs,omarchy,local-ai}.md + ARCHITECTURE.md  •  Addresses, keys &amp; secrets intentionally omitted  •  Verified 2026-10-17: oMLX via Box SOCKS5 (/v1/models OK)  •  See Known unverified callout above</text>')
s.save("diagram-1-network-architecture")

# DIAGRAM 2
s=SVG(2400,1780,"2  •  Local AI Flow — Who Calls Which Model, and What Falls Back to What","OpenAI-compatible local inference on Apple Silicon, Ollama on two machines, and two SEPARATE Hermes installs with different primaries")
s.platform_strip(["macOS \u00b7 Mac mini (oMLX / Ollama host)"])
# sources
s.card(60,170,460,340,"REQUEST SOURCES",[
 "Grok Bots on the Box (17)",
 "Ian / dev tools / CLIs",
 "Hermes (Box) — coding agent",
 "Hermes (Mini) — cron + coding",
 "Studio / Scout bulk research → Hermes",
],"navy",subtitle="All requests start as tasks, not raw GPUs")
s.card(60,560,460,300,"KEY CONSTRAINT",[
 "Box: NO GPU, 15 GB shared RAM",
 "→ Never run local models on Box",
 "→ Box must CALL OUT to Mini /",
 "   Omarchy / Cloud",
 "Heavy local work belongs on",
 "Omarchy (ROCm) or Mini (MLX)",
],"rose",subtitle="The #1 routing rule")
# proxy
s.card(620,170,460,340,"BOX EGRESS: SOCKS5 PROXY",[
 "Userspace tailscaled on Box",
 "SOCKS5: localhost:1055",
 "SSH: tssh → Mini / MBP / Neo (22)",
 "oMLX via proxy: \u2713 Verified 2026-10-17",
 "SOCKS5 /v1/models returned the model list",
 "(Ornith-1.5-9B-oQ4e-mtp, bge-m3, gemma,|Qwen3-TTS)",
],"blue",icon="tailscale",subtitle="Why a proxy? No kernel TUN on shared VM")
# mini omlx
s.card(1180,150,560,430,"MAC MINI — oMLX  /v1  (TAILNET ONLY)",[
 "tailscale serve → HTTPS 443, NO Funnel",
 "OpenAI-compatible API (drop-in /v1/chat)",
 "Ornith-1.5-9B — main chat, ~17 tok/s",
 "gemma-4-e4b-it-4bit — fast / small",
 "bge-m3-mlx-8bit — embeddings (RAG)",
 "Qwen3-TTS — text-to-speech",
 "1× 9B at a time • max 2 concurrent • ~6 s cold load",
],"teal",icon="ollama",subtitle="MLX on Apple Silicon  •  unified memory")
# ollama mini + omarchy
s.card(1180,640,560,300,"MAC MINI — OLLAMA (LOCAL-ONLY)",[
 "Not exposed on tailnet — SSH in first",
 "qwen3:8b / qwen3.5:9b — local coding assist + sweeps",
 "qwen3:4b / gemma3:4b — fast tagging, classification",
 "gemma4:e4b — no assigned job yet (EXP-005 to prove)",
],"slate",icon="ollama",subtitle="Access pattern: tssh mini → ollama")
s.card(1820,640,520,300,"OMARCHY — OLLAMA + ROCm",[
 "Radeon RX 6600 XT, ROCm gfx1032 ✓",
 "Ollama: qwen3:8b — bulk local coding assist",
 "bge-m3 — bulk embeddings/RAG batches",
 "62 GB RAM = larger context / heavy builds",
 "Access via Grok Bot machine access \u2014",
 "   not a documented Box Ollama path",
 "⚠ gfx1032 is older ROCm tier — check",
 "   per-model support, not CUDA parity",
],"blue",icon="amd",subtitle="Strongest coding + local-AI machine")
# hermes boxes bottom
s.card(620,640,460,360,"HERMES ON THE BOX  v0.22.2",[
 "PRIMARY: gpt-6.1-sol via openai-codex",
 "FALLBACKS: DeepSeek-V4-Pro → MiniMax-M3",
 "Aux tasks: gpt-5.6-terra (pinned)",
 "oMLX: NOT configured here",
 "No cron / no gateway on Box Hermes",
 "Tuned by: Hermes Tuner bot",
],"purple",subtitle="SEPARATE install #1 — cloud-first")
s.card(1820,150,520,430,"HERMES ON THE MINI  v0.22.2",[
 "PRIMARY: MiniMax-M3 (cloud API)",
 "ONLY FALLBACK: local oMLX (Mini)",
 "7 total \u2014 6 active + 1 paused oMLX",
 "warm-up (Warden, never run)",
 "Oct 15: 4 jobs failed (history) \u2014 recovered",
 "Oct 16-17: all active jobs ok",
 "⚠ oMLX is NOT a login item:",
 "   after Mini reboot run `omlx start`",
],"purple",subtitle="SEPARATE install #2 — cloud → local fallback")
# annotations bottom
s.note(60,920,560,300,"TOK/S, COLD LOAD & CONCURRENCY",[
 "17 tok/s (9B, MLX) ≈ comfortable reading|speed, not datacenter throughput.",
 "~6 s cold load = first token waits for|weights into unified memory. Warm ≠ free.",
 "Max 2 concurrent: a 3rd request queues/|fails — design bots for back-off, not fan-out."])
s.note(660,1060,560,260,"QUANTIZATION, EXPLAINED",[
 "4-bit / 8-bit weights shrink a 9B model|from ~18 GB (FP16) to ~5–9 GB.",
 "That is how 9B fits an 11.3 GiB budget —|with quality loss that is task-dependent.",
 "Larger models still may not fit usefully."])
s.note(1260,1000,520,320,"EMBEDDINGS & TTS ARE SEPARATE JOBS",[
 "bge-m3 turns text → vectors for search /|RAG. It is not a chat model.",
 "Qwen3-TTS turns text → audio. Same /v1|host, different endpoint & cost profile.",
 "Do not benchmark chat tok/s on either."])
s.note(1820,1000,520,320,"OPENAI-COMPATIBLE ≠ OPENAI",[
 "oMLX speaks the OpenAI /v1 shape locally,|so tools swap base-URL, not code.",
 "Privacy / cost win, capability ceiling:|a local 9B ≠ a frontier cloud model.",
 "That gap is exactly why Hermes keeps|cloud primaries with local fallback."])
# arrows
s.arrow(520,300,620,300,"task / API call",lx=570,ly=275)
s.arrow(1080,300,1180,300,"HTTPS 443 /v1",color="#0E9A8B",marker="arrT",lx=1130,ly=275)
s.arrow(1080,420,1180,760,"SSH 22 → Ollama",lx=1010,ly=600)
s.poly([(700,510),(700,600),(2070,600),(2070,640)],"Box \u2192 Omarchy: UNVERIFIED \u2014 path/ACL not documented",dashed=True,lx=1640,ly=590)
s.poly([(1740,360),(1790,360),(1790,360),(1820,360)],"",lx=0,ly=0)
s.arrow(1740,330,1820,330,"fallback: oMLX",color="#D97706",marker="arrA",lx=1780,ly=305)
s.note(60,1480,2280,110,"KNOWN UNVERIFIED \u2014 Verified 2026-10-17; items below were NOT live-checked in this audit",[
 "Tailnet ACL details (no ACL file check)  \u2022  Omarchy specs (Ian/Atlas-verified only)|~17 tok/s + concurrency (unbenchmarked)  \u2022  oMLX login-item status"])
s.parts.append('<text x="48" y="1745" font-family="Inter,Arial" font-size="16" fill="#64748B">Sources: wiki content/infra/local-ai.md, box.md, macs.md, omarchy.md  •  Model names/speeds as documented Oct 2026  •  No API keys, tailnet IPs, or key-file contents shown  •  Verified 2026-10-17 (oMLX via SOCKS5)  •  UNVERIFIED = marked, not assumed</text>')
s.legend(60,1280,[("teal","Local MLX serving (Mini)"),("blue","GPU dev PC / proxy / egress"),("purple","Hermes agent (two separate installs)"),("rose","Constraint / do-not-do")])
s.parts.append('<text x="840" y="1305" font-family="Inter,Arial" font-size="19" font-weight="700" fill="#0F2A44">HOW TO READ PRIMARY → FALLBACK</text>')
for i,t in enumerate(["Box Hermes: cloud gpt-6.1-sol FIRST, DeepSeek/MiniMax if it fails. Local oMLX is not in its chain at all.","Mini Hermes: MiniMax-M3 FIRST, oMLX only if cloud fails. Cron therefore depends on cloud + a manually-started local server.","Bots do not pick GPUs directly — they ask Hermes / an OpenAI-compatible endpoint, and routing decides where tokens come from."]):
    s.parts.append(f'<text x="840" y="{1335+i*26}" font-family="Inter,Arial" font-size="18" fill="#475569">{t}</text>')
s.save("diagram-2-local-ai-flow")

# DIAGRAM 3
s=SVG(2400,1900,"3  •  Bot Operating Model — Lanes, Handoffs & the Atlas Gate","17 Grok Bots, each with a lane. Atlas is the portfolio gate; Warden owns runtime; Hermes is a coding agent, not a Grok Bot")
s.platform_strip(["macOS \u00b7 AIMacMini ~/projects (Foreman)"])
# Atlas center
s.card(920,170,560,260,"ATLAS — Portfolio Gate",[
 "Gatekeeper: publish / spend / send / ship ONLY",
 "Routine handoffs move file-based, no gate wait",
 "Routes work → Beacon, Scout, Ledger",
 "Receives: meaningful changes, flags,",
 "Friday Amazon, read-only project status",
],"navy",subtitle="START HERE — most work passes Atlas first")
# left column
s.card(60,170,700,240,"SIGNALS IN  (inputs to the gate)",[
 "X Bookmarks — app flags → Atlas",
 "Book Growth — Friday Amazon → Atlas",
 "Archivist — meaningful changes → Atlas",
 "Foreman — PROJECTS/ACTIVITY (read-only) → Atlas",
],"teal",subtitle="Nothing self-promotes to 'shipped'")
s.card(1640,170,700,240,"RUNTIME & QUALITY  (keep it running)",[
 "Warden — runtime owner (machines, Hermes, incidents)",
 "Improve My Bots — config/profiles; symptoms → Warden",
 "Hermes Tuner — tunes BOX Hermes; incidents ↔ Warden",
 "Atlas — runtime failures → Warden",
],"rose",subtitle="Split Oct 10, 2026: runtime ≠ config")
# middle row lanes
lanes=[
 (60,520,520,340,"BEACON — Sites","blue",["Owns Remnant Security sites","Receives routed work from Atlas","Ships only through the gate","(site detail: Beacon bot page)"]),
 (620,520,520,340,"SCOUT — Listening","teal",["Social / X listening & research","Bulk research → Hermes (CLI)","Success data ↔ Ledger","Warden gates Scout's X MCP access"]),
 (1180,520,520,340,"LEDGER — Experiments","amber",["Owns experiment numbers & IDs","Studio supplies experiment IDs","Scout success data feeds Ledger","Owns cost + EXP metrics → weekly dashboard","→ eval-driven ROUTING.md (EXP-001/003/005/008)"]),
 (1740,520,600,340,"STUDIO — Content","purple",["Content creation lane","Supplies experiment IDs → Ledger","Needs results back to iterate","(MBP proposed for video renders)"]),
]
for x,y,w,h,t,a,b in lanes: s.card(x,y,w,h,t,b,a,subtitle="LANE")
# bottom
s.card(60,960,700,360,"FOREMAN — Projects",[
 "Single root: AIMacMini:~/projects (canonical)",
 "Heavy coding → Hermes (not hand-coded by bot)",
 "File task cards (queue/) beat summary handoffs",
 "Reports PROJECTS/ACTIVITY read-only → Atlas",
 "NAS mirror is editable, never canonical",
],"blue",icon="github",subtitle="One project root to rule the fleet")
s.card(820,960,700,360,"HERMES — Coding Agent  (NOT a Grok Bot)",[
 "Two installs: Box (cloud-first) + Mini (MiniMax→oMLX)",
 "Scout bulk research & Foreman heavy coding land here",
 "Tuned by Hermes Tuner (Box install only)",
 "See Diagram 2 for primaries, fallbacks & limits",
],"purple",subtitle="Execution engine, not a lane owner")
s.card(1580,960,760,360,"OTHER LANES  (one-line ownership)",[
 "Outbound Prospecting — pitches",
 "Inbox Cleaner, Life Events, Tax Collector, Dev Diary…",
 "Each bot page in the wiki is its source of truth",
 "If a handoff is not documented, it does not happen",
],"slate",subtitle="Full roster: wiki content/bots/*.md")
# arrows
s.arrow(760,290,920,290,"flags / reports",lx=840,ly=265)
s.arrow(1640,290,1480,290,"failures →",lx=1560,ly=265)
s.poly([(1200,430),(1200,480),(320,480),(320,520)],"routes work",lx=700,ly=465)
s.poly([(1250,430),(1250,480),(880,480),(880,520)],"",lx=0,ly=0)
s.poly([(1300,430),(1300,480),(1440,480),(1440,520)],"",lx=0,ly=0)
s.poly([(1350,430),(1350,480),(2000,480),(2000,520)],"",lx=0,ly=0)
s.arrow(470,960,470,860,"status ↑",lx=520,ly=910)
s.arrow(760,1140,820,1140,"heavy coding",lx=790,ly=1115)
s.note(60,1400,720,260,"WHY A GATE? (FOR AI-ENTHUSIAST READERS)",[
 "17 autonomous agents without a gate = 17|invented priorities. Atlas makes shipping a|decision, not a side-effect of any one bot.",
 "Read-only reporting (Foreman → Atlas) keeps|status truthful: reporters cannot edit the plan."])
s.note(840,1400,720,260,"LANE vs EXECUTION ENGINE",[
 "Bots own outcomes (sites, experiments,|content). Hermes owns execution (code, bulk|research) — tuned separately from bot config.",
 "Confusing the two is how agents silently|change each other's behaviour."])
s.note(1620,1400,720,260,"HANDOFFS ARE CONTRACTS",[
 "Arrows are documented in ARCHITECTURE.md.|Undocumented handoffs should be treated as|not happening — add them to the wiki first,",
 "then to the diagram. Diagram follows docs."])
# horizontal legend in gap above notes
lx=60
s.parts.append('<text x="60" y="1362" font-family="Inter,Arial" font-size="18" font-weight="800" fill="#0F2A44">LEGEND:</text>')
for col,lab in [("navy","Gate"),("teal","Signals/Listening"),("rose","Runtime"),("purple","Execution/Content"),("amber","Experiments"),("blue","Sites/Projects")]:
    s.parts.append(f'<rect x="{lx+90}" y="1348" width="24" height="14" rx="4" fill="{COLORS[col]}"/>')
    s.parts.append(f'<text x="{lx+120}" y="1362" font-family="Inter,Arial" font-size="17" fill="#334155">{lab}</text>')
    lx+=120+len(lab)*9
# adjust legend y manually - already placed; add source
s.note(60,1685,2280,110,"KNOWN UNVERIFIED \u2014 Verified 2026-10-17; items below were NOT live-checked in this audit",[
 "Tailnet ACL details (no ACL file check)  \u2022  Omarchy specs (Ian/Atlas-verified only)|~17 tok/s + concurrency (unbenchmarked)  \u2022  oMLX login-item status (see Diagram 2)"])
s.parts.append('<text x="48" y="1845" font-family="Inter,Arial" font-size="16" fill="#64748B">Verified 2026-10-17  •  Sources: wiki content/ARCHITECTURE.md (Bot handoffs + Lanes in one line) + content/bots/*.md  •  Hermes is a CLI coding agent, not a Grok Bot  •  Shepherd retired Oct 10, 2026 per decisions/</text>')
s.save("diagram-3-bot-operating-model")

# DIAGRAM 4 — ORCHESTRATION (design 2026-10-17, no machine changes yet)
s=SVG(2400,1980,"4  •  Orchestration — Control Plane, Routing & Failover (DESIGN)","Box decides (Atlas + file queue), machines work where they are suited, every job heartbeats — design 2026-10-17, Phases 0-2")
s.platform_strip(["macOS \u00b7 Mac mini / MacBook Pro"])
# control plane top
s.card(60,160,720,370,"CONTROL PLANE — THE BOX",[
 "Atlas gate: publish / spend / send / ship ONLY",
 "File queue: /workspace/orchestration/queue/*.md",
 "Task card: type, target, tool/model, inputs,",
 "  acceptance check, fallback, heartbeat id",
 "Run log: state/*.jsonl (effective model, tokens,",
 "  cost, tok/s, duration, result, rework)",
 "Only Atlas/Ian create approved cards; any bot",
 "  may propose in queue/proposed/",
],"navy",icon="debian",subtitle="RECOMMENDED HOME  •  15 GB RAM — text/API work only, NO models/builds")
s.card(840,160,720,370,"HEALTH & OBSERVABILITY LOOP",[
 "5-min probes: oMLX /v1/models + 20-token check",
 "Per-machine health files: load, free RAM/disk,",
 "  oMLX/Ollama up, last cron success",
 "Dead-man: every job pings on success —",
 "  MISSING ping alerts (Oct-15 lesson)",
 "Warden = runtime health • Ledger = numbers",
 "Weekly dashboard → EXP evals → ROUTING.md",
],"rose",subtitle="INSTRUMENT FIRST  •  Review Recs 1 + 3")
s.card(1620,160,720,370,"CLOUD CODING  (HTTPS egress)",[
 "gpt-6.1-sol — Box Hermes PRIMARY agentic coding",
 "gpt-5.6-terra — Box Hermes aux (pinned)",
 "MiniMax-M3 — Mini Hermes PRIMARY; Box fallback #2",
 "DeepSeek-V4-Pro — Box Hermes fallback #1",
 "Claude Code / Codex — judgment vs mechanical",
 "Local 9B is NEVER the agentic-loop coder",
],"purple",subtitle="USE CASE: frontier tool-use for multi-file coding")
# workers middle
s.card(60,620,540,430,"MAC MINI — Apple + Local AI Worker",[
 "Xcode builds ONLY here (SnapDog/iOS)",
 "oMLX: Ornith-9B=chat/cron fallback (~17 tok/s)",
 "  gemma-4-e4b=fast/small • bge-m3=embed/RAG",
 "  Qwen3-TTS=speech • 1x9B, max 2 concurrent",
 "Ollama SSH-only: qwen3=assist/sweeps",
 "Hermes cron: Apple/local jobs only (Phase 1)",
 "LIMIT: 16 GB, ~11.3 GiB GPU, SPOF — shed on load",
],"teal",icon="apple",subtitle="CANONICAL ~/projects  •  :22 + :443 from Box")
s.card(640,620,540,430,"OMARCHY — Bulk / Heavy Worker",[
 "5950X 62 GB RX6600 XT ROCm gfx1032",
 "Ollama qwen3:8b = bulk local coding assist",
 "bge-m3 = bulk embeddings batches",
 "Heavy Linux + game-dev builds (GPU home)",
 "claude/codex/hermes for heavy coding",
 "Phase 1: ONE ACL port if Ian approves - - -",
 "vLLM: unsupported gfx1032 — timebox/drop",
],"blue",icon="amd",subtitle="CONDITIONAL  •  Box path UNVERIFIED today")
s.card(1220,620,540,430,"MACBOOK PRO — Video + Deputy",[
 "M4 Max — Studio video renders (async)",
 "Deputy control plane: cold-restore target",
 "  clone ~/projects from NAS/GitHub, timed <1h",
 "  becomes canonical ONLY by Ian declaration",
 "Neo: often offline — async only, never sync dep.",
 "NAS: mirror only (editable, NOT canonical)",
 "  Box has NO NAS path — by design",
],"purple",icon="apple",subtitle="RESTORE, NOT ACTIVE-ACTIVE  •  SSH 22")
s.card(1800,620,540,430,"THE BOX AS WORKER  (limited)",[
 "Cloud CLIs: claude (judgment), codex (mechanical)",
 "Box Hermes: gpt-6.1-sol → DeepSeek → MiniMax",
 "17 Grok Bot lanes: sites/books/content/etc.",
 "Small builds -j2 off-peak ONLY",
 "⛔ NO local models, NO heavy builds,",
 "⛔ NO Apple builds on Box (15 GB, no GPU)",
],"navy",icon="debian",subtitle="ORCHESTRATE + CLOUD-CLI  •  RAM >85% = shed")
# failover bottom
s.note(60,1130,720,300,"FAILOVER  (human-promoted, not split-brain)",[
 "oMLX down → launchd auto-start (Phase 1) →|queue → cloud mid-tier for cron",
 "Mini down → dead-man alert → MBP cold-restore|(Ian declares canonical; re-sync-back plan)",
 "Box down → MBP holds nightly queue/wiki copy;|re-issue from task cards (idempotent by id)"])
s.note(840,1130,720,300,"LOAD SHEDDING  (Oct-17: mini load ~956)",[
 "Mini load>8 or free RAM<1 GB → pause non-critical|cron (REPORTED skip, never silent)",
 "Bulk sweeps → omarchy Ollama; fast path →|gemma-4-e4b; cloud-primary work unaffected"])
s.note(1620,1130,720,300,"ROUTING IN ONE LINE",[
 "Judgment/multi-file → frontier cloud • Mechanical|→ codex/mid-cloud (gated) • Local 9B → embed/TTS/",
 "sweeps/fallback • Apple → mini • Heavy/game →|omarchy • Video → MBP • Cron where deps live"])
# arrows
s.arrow(400,530,320,620,"tssh SSH 22 / tasks",lx=300,ly=575)
s.arrow(900,530,900,620,"machine connector (now)",lx=900,ly=575)
s.poly([(1700,530),(1700,580),(1550,580),(1550,620)],"restore copy / async",lx=1620,ly=565)
s.arrow(2000,530,2070,620,"cloud API calls",lx=2070,ly=575)
s.poly([(1200,530),(1200,580),(700,580),(700,620)],"SOCKS5 → oMLX 443",lx=950,ly=605)
s.legend(60,1480,[("navy","Control plane / Box"),("teal","Mini local-AI worker"),("blue","Omarchy bulk/heavy (conditional)"),("purple","Video/deputy + cloud coding"),("rose","Health / failover / observability")])
s.parts.append('<text x="840" y="1505" font-family="Inter,Arial" font-size="19" font-weight="700" fill="#0F2A44">PHASES</text>')
for i,tx in enumerate(["Phase 0 (this week): file queue + run log, read-only audits, no new infra.","Phase 1 (wk 2-3): heartbeats, oMLX probe + launchd, cron moves, omarchy ACL decision.","Phase 2 (wk 4-6): MBP restore drill, EXP-001/003/005/008 → ROUTING.md, LiteLLM/llama-swap only if triggered."]):
    s.parts.append(f'<text x="840" y="{1535+i*26}" font-family="Inter,Arial" font-size="18" fill="#475569">{tx}</text>')
s.note(60,1680,2280,110,"DESIGN ONLY — NO MACHINE CHANGES YET  •  Decisions Ian must make: control-plane home, omarchy role, vLLM timebox, cron moves, dead-man service",[
 "Dashed/conditional: omarchy serving port + LiteLLM pilot (Phase 2 trigger). Known unverified: tailnet ACL, omarchy specs, ~17 tok/s (unbenchmarked)."])
s.parts.append('<text x="48" y="1885" font-family="Inter,Arial" font-size="16" fill="#64748B">Sources: /workspace/orchestration-design-2026-10-17.md + architecture-review-2026-10-17.md + wiki infra/*.md  •  Verified 2026-10-17  •  No IPs / keys / secrets shown  •  Icons: Simple Icons (see icons/) with text labels</text>')
s.save("diagram-4-orchestration")
print("patched")
