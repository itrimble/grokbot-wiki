#!/usr/bin/env python3
"""Build the three home-network diagrams (SVG) from the icon files next to this script.

Standard library only. Run from anywhere:  python3 assets/home-network/src/build_home_diagrams.py
Outputs physical.svg, logical.svg and relationships.svg into assets/home-network/.
No addresses, MAC addresses, hostnames or account names belong in these diagrams.
"""
import pathlib
import re
import sys
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent
ICONS = OUT / "icons"
WARNINGS = []

# ---------------------------------------------------------------- icons
USED = {}  # name -> (d, fill-rule)


def icon(name):
    if name not in USED:
        text = (ICONS / f"{name}.svg").read_text()
        match = re.search(r'<path([^>]*)\sd="([^"]+)"', text)
        if not match:
            sys.exit(f"no path in {name}.svg")
        rule = "evenodd" if 'fill-rule="evenodd"' in match.group(1) else ""
        USED[name] = (match.group(2), rule)
    return name


def defs():
    out = ["<defs>"]
    for name, (d, rule) in sorted(USED.items()):
        fr = f' fill-rule="{rule}"' if rule else ""
        out.append(f'<symbol id="i-{name}" viewBox="0 0 24 24"><path{fr} d="{d}"/></symbol>')
    out.append('<marker id="a" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path class="ah" d="M0,0 L9,4.5 L0,9 z"/></marker>')
    out.append('<marker id="v" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path class="ahv" d="M0,0 L9,4.5 L0,9 z"/></marker>')
    out.append("</defs>")
    return "\n".join(out)


# ---------------------------------------------------------------- style
STYLE = """<style>
.bg{fill:#fbfaf7}.box{fill:#fff;stroke:#cfccc2;stroke-width:1.2}.grp{fill:#f3f1ea;stroke:#cfccc2;stroke-width:1.2}
.t{fill:#1d1d1b;font:13px ui-sans-serif,system-ui,sans-serif}.h{font-weight:700;font-size:14px}.m{fill:#6b6a66;font-size:12px}
.title{font-size:22px;font-weight:700}.lab{fill:#6b6a66;font:11.5px ui-sans-serif,system-ui,sans-serif}.r{text-anchor:end}.c{text-anchor:middle}
.l25{stroke:#2e8b57;stroke-width:4;fill:none}.l1{stroke:#2b6cb0;stroke-width:4;fill:none}.lx{stroke:#8a8880;stroke-width:4;fill:none}
.lw{stroke:#8a8880;stroke-width:2.5;fill:none;stroke-dasharray:7 6}.bus{stroke:#cfccc2;stroke-width:2;fill:none}
.e{stroke:#8a8880;stroke-width:2;fill:none}.ov{fill:none;stroke:#b4462b;stroke-width:2;stroke-dasharray:3 5}
.port{fill:none;stroke:#8a8880;stroke-width:1.2}.acc{fill:#b4462b}.ah{fill:#8a8880}.ahv{fill:#b4462b}.bd{fill:#8a8880}
.c-net .tb{fill:#e3ecfa}.c-net .tg{fill:#2b6cb0}
.c-pc .tb{fill:#dcf1ec}.c-pc .tg{fill:#1c8a75}
.c-st .tb{fill:#fbecd3}.c-st .tg{fill:#b86e0a}
.c-ov .tb{fill:#f9e3dc}.c-ov .tg{fill:#b4462b}
.c-cl .tb{fill:#eceae3}.c-cl .tg{fill:#5f5e59}
.c-in .tb{fill:#ece4f8}.c-in .tg{fill:#6b46c1}
@media (prefers-color-scheme:dark){
.bg{fill:#141412}.box{fill:#1d1d1b;stroke:#4a4841}.grp{fill:#1b1a18;stroke:#4a4841}.t{fill:#ecebe6}.m,.lab{fill:#9a9890}
.l25{stroke:#5fcf8f}.l1{stroke:#6aa8f0}.lx,.lw,.e{stroke:#9a9890}.bus{stroke:#4a4841}.port{stroke:#9a9890}.ov{stroke:#e07a5f}
.acc,.ahv{fill:#e07a5f}.ah,.bd{fill:#9a9890}
.c-net .tb{fill:#1b2a44}.c-net .tg{fill:#6aa8f0}
.c-pc .tb{fill:#143229}.c-pc .tg{fill:#4fd1b5}
.c-st .tb{fill:#3a2a10}.c-st .tg{fill:#f0b45a}
.c-ov .tb{fill:#3a1f18}.c-ov .tg{fill:#e07a5f}
.c-cl .tb{fill:#2a2926}.c-cl .tg{fill:#b4b2a8}
.c-in .tb{fill:#2a2140}.c-in .tg{fill:#b79cf0}
}
</style>"""


# ---------------------------------------------------------------- helpers
def width_of(text, size=12, bold=False):
    return len(text) * size * (0.58 if bold else 0.53)


def txt(x, y, s, cls="t m", **extra):
    attrs = "".join(f' {k}="{v}"' for k, v in extra.items())
    return f'<text class="{cls}" x="{x}" y="{y}"{attrs}>{escape(s)}</text>'


def fit(label, s, avail, size=12, bold=False):
    if width_of(s, size, bold) > avail:
        WARNINGS.append(f"{label}: '{s}' ~{int(width_of(s, size, bold))}px > {avail}px")


def tile(x, y, size, name, cat, glyph=None):
    glyph = glyph or int(size * 0.64)
    off = (size - glyph) / 2
    return (f'<g class="c-{cat}"><rect class="tb" x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * 0.23:.0f}"/>'
            f'<use class="tg" href="#i-{icon(name)}" x="{x + off:.1f}" y="{y + off:.1f}" width="{glyph}" height="{glyph}"/></g>')


def badge(x, y, name, size=17):
    return f'<use class="bd" href="#i-{icon(name)}" x="{x}" y="{y}" width="{size}" height="{size}"/>'


def card(x, y, w, h, ic, cat, title, subs=(), badges=(), dashed=False):
    d = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"{d}/>']
    out.append(tile(x + 12, y + 12 if h < 64 else y + (h - 44) / 2, 44, ic, cat))
    avail = w - 68 - 14 - (22 * len(badges))
    fit(title, title, avail, 14, True)
    block = 18 + 16 * len(subs)
    top = y + (h - block) / 2
    out.append(txt(x + 68, round(top + 13, 1), title, "t h"))
    for i, s in enumerate(subs):
        fit(title, s, avail)
        out.append(txt(x + 68, round(top + 31 + 16 * i, 1), s, "t m"))
    for i, b in enumerate(badges):
        out.append(badge(x + w - 26 - 22 * i, y + 10, b))
    return "\n".join(out)


def row(x, y, w, ic, cat, text, badges=()):
    out = [f'<rect class="box" x="{x}" y="{y}" width="{w}" height="42" rx="8"/>']
    out.append(tile(x + 8, y + 7, 28, ic, cat, 18))
    fit(text, text, w - 52 - 24 * len(badges), 13)
    out.append(txt(x + 46, y + 26, text, "t"))
    for i, b in enumerate(badges):
        out.append(badge(x + w - 26 - 22 * i, y + 12, b, 17))
    return "\n".join(out)


def svg(width, height, label, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">\n'
            f'<title id="t">{escape(label)}</title>\n<desc id="d">{escape(desc)}</desc>\n{STYLE}\n{defs()}\n'
            f'<rect class="bg" width="{width}" height="{height}" rx="10"/>\n{body}\n</svg>\n')


def header(title, sub):
    return txt(30, 42, title, "t title") + "\n" + txt(30, 64, sub, "lab")


def line(x1, y1, x2, y2, cls, extra=""):
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{extra}/>'


def write(name, content):
    (OUT / name).write_text(content)
    print("wrote", name, len(content), "bytes")


# ---------------------------------------------------------------- physical
def physical():
    b = [header("Physical layout and link speeds",
                "As of 2026-11-03. Color is the speed each link negotiated. Dashed means wireless or not confirmed.")]
    # gateway room
    b.append('<rect class="grp" x="30" y="90" width="330" height="275" rx="10"/>')
    b.append(txt(46, 112, "GATEWAY ROOM"))
    b.append(card(50, 125, 290, 76, "mdi-router-wireless", "net", "5G home-internet gateway", ["TMO-G4SE: router, NAT, DHCP"], ["mdi-signal-5g"]))
    b.append(line(195, 201, 195, 265, "l1"))
    b.append(txt(207, 238, "1 GbE", "lab"))
    b.append(card(50, 265, 290, 76, "mdi-access-point-network", "net", "Deco BE63: mesh root", ["the gateway plugs in here"], ["simple-tplink"]))
    # far room
    b.append('<rect class="grp" x="30" y="470" width="330" height="140" rx="10"/>')
    b.append(txt(46, 492, "FAR ROOM"))
    b.append(card(50, 505, 290, 76, "mdi-access-point-network", "net", "Deco BE63: far node", ["Wi-Fi coverage only"], ["simple-tplink"]))
    b.append(line(195, 341, 195, 505, "lw"))
    b.append(txt(207, 415, "wireless backhaul", "lab"))
    b.append(txt(207, 431, "6 to 11 ms from the workspace", "lab"))
    # workspace group
    b.append('<rect class="grp" x="420" y="90" width="750" height="740" rx="10"/>')
    b.append(txt(436, 112, "WIRED WORKSPACE"))
    # wi-fi clients
    b.append('<rect class="box" x="450" y="120" width="300" height="125" rx="10" stroke-dasharray="5 4"/>')
    b.append(txt(466, 144, "Wi-Fi clients", "t h"))
    for i, n in enumerate(["mdi-cellphone", "mdi-tablet", "mdi-television", "mdi-speaker", "mdi-home-automation"]):
        b.append(tile(466 + i * 54, 158, 42, n, "cl", 26))
    b.append(txt(466, 226, "Each joins the closest Deco", "t m"))
    # workspace node
    b.append(card(450, 265, 300, 76, "mdi-access-point-network", "net", "Deco BE63: workspace node", ["wired anchor for the workspace"], ["simple-tplink"]))
    b.append(line(340, 303, 450, 303, "lw"))
    b.append(txt(354, 294, "wireless", "lab"))
    b.append(txt(354, 322, "3 to 5 ms", "lab"))
    # uplink + switch
    b.append(line(600, 341, 600, 400, "lx"))
    b.append(txt(588, 364, "uplink to the switch", "lab r"))
    b.append(txt(588, 380, "speed not measured", "lab r"))
    b.append(card(450, 400, 300, 104, "custom-switch", "net", "TP-Link TL-SG108S-M2", ["8 x 2.5G, unmanaged", "loop prevention on"], ["simple-tplink"]))
    for i in range(8):
        b.append(f'<rect class="port" x="{466 + i * 28}" y="480" width="20" height="14" rx="2"/>')
    # tailscale
    b.append(card(450, 540, 300, 140, "simple-tailscale", "ov", "Tailscale overlay",
                  ["Runs on every Mac, the NAS,", "omarchy, the iPhone and iPad.", "Direct on this LAN; away from", "home it goes through a relay."], dashed=True))
    # bus + devices
    b.append(line(805, 163, 805, 613, "bus", ' stroke-linecap="round"'))
    b.append(line(750, 452, 805, 452, "lx"))
    devices = [
        (125, "mdi-nas", "st", "UGREEN DXP2800 NAS", ["Intel N100, one 2.5GbE port", "static address"], [], "l25", False),
        (215, "mdi-laptop", "pc", "MacBook Pro M4 Max", ["USB-C dock at 2.5G", "Wi-Fi also on"], ["simple-apple"], "l25", False),
        (305, "custom-mac-mini", "pc", "Mac mini M4", ["built-in 1 GbE", "Wi-Fi also on"], ["simple-apple"], "l1", False),
        (395, "mdi-laptop", "pc", "MacBook Neo", ["USB Ethernet adapter, 1G", "Wi-Fi also on"], ["simple-apple"], "l1", True),
        (485, "mdi-desktop-tower", "pc", "omarchy (Linux PC)", ["2.5G NIC", "powered down at the moment"], ["simple-linux"], "l25", True),
        (575, "mdi-keyboard", "cl", "TESmart KVM", ["shares keyboard and display", "1G LAN adapter to the MacBook Pro"], [], "l1", True),
    ]
    for y, ic, cat, title, subs, badges, cls, dashed in devices:
        b.append(card(850, y, 300, 76, ic, cat, title, subs, badges))
        extra = ' stroke-dasharray="7 6"' if dashed else ""
        b.append(line(805, y + 38, 850, y + 38, cls, extra))
    # legend
    b.append('<rect class="grp" x="30" y="640" width="330" height="150" rx="10"/>')
    b.append(txt(46, 664, "Legend", "t h"))
    for i, (cls, label, dashed) in enumerate([("l25", "2.5 Gbps, negotiated", False), ("l1", "1 Gbps, negotiated", False),
                                              ("lx", "wired, speed not measured", False), ("lw", "wireless, or port not confirmed", False)]):
        yy = 687 + i * 24
        b.append(line(50, yy, 105, yy, cls))
        b.append(txt(118, yy + 4, label, "t m"))
    b.append(txt(30, 808, "Wireless latencies were measured on 2026-11-01 from a wired", "lab"))
    b.append(txt(30, 824, "machine, before the switch went in. Not re-measured.", "lab"))
    write("physical.svg", svg(1200, 840, "Physical layout and link speeds of the home network",
                              "A 5G gateway feeds a mesh root node over 1 GbE. Three mesh nodes link to each other wirelessly. The workspace node uplinks to an 8-port 2.5G switch. The NAS and the MacBook Pro dock connect at 2.5G, the Mac mini and other adapters at 1G.",
                              "\n".join(b)))


# ---------------------------------------------------------------- logical
def logical():
    b = [header("Logical view: one flat network",
                "As of 2026-11-03. There are no VLANs. Wired, Wi-Fi, smart-home and server traffic share one broadcast domain.")]
    b.append(card(475, 92, 250, 64, "mdi-cloud", "in", "Internet", ["cellular, via the gateway"]))
    b.append(line(600, 156, 600, 185, "lx"))
    b.append(card(450, 185, 300, 76, "mdi-router-wireless", "net", "5G home-internet gateway", ["router, NAT, DHCP, MTU 1420"], ["mdi-signal-5g"]))
    b.append(line(600, 261, 600, 300, "lx"))
    b.append('<rect class="grp" x="30" y="300" width="1140" height="400" rx="12"/>')
    b.append(txt(50, 322, "ONE FLAT PRIVATE NETWORK (a single /24)"))
    cols = [
        (50, "mdi-access-point-network", "net", "Wi-Fi mesh", "3 x Deco BE63 in access-point mode", [
            ("mdi-cellphone", "cl", "Phones and tablets", []),
            ("mdi-television", "cl", "TVs and AV receivers", []),
            ("mdi-home-automation", "cl", "Smart-home devices", []),
            ("mdi-speaker", "cl", "Voice assistants and speakers", []),
            ("mdi-laptop", "cl", "Laptops when they are off the wire", [])]),
        (425, "custom-switch", "net", "Wired workspace", "behind the 2.5G switch", [
            ("mdi-laptop", "pc", "MacBook Pro M4 Max", ["simple-apple"]),
            ("custom-mac-mini", "pc", "Mac mini M4", ["simple-apple"]),
            ("mdi-laptop", "pc", "MacBook Neo", ["simple-apple"]),
            ("mdi-desktop-tower", "pc", "omarchy (powered down)", ["simple-linux"]),
            ("mdi-keyboard", "cl", "TESmart KVM", [])]),
        (800, "mdi-nas", "st", "Services on the NAS", "UGREEN DXP2800, static address", [
            ("mdi-folder-network", "st", "File shares (SMB, NFS)", []),
            ("mdi-backup-restore", "st", "Time Machine backups for the Macs", []),
            ("simple-adguard", "st", "DNS filtering for the whole LAN", []),
            ("simple-plex", "st", "Media server and helpers", ["simple-docker"]),
            ("simple-tailscale", "ov", "Tailscale (runs in a container)", ["simple-docker"])]),
    ]
    for x, ic, cat, title, sub, rows in cols:
        b.append(tile(x, 336, 40, ic, cat))
        b.append(txt(x + 52, 354, title, "t h"))
        b.append(txt(x + 52, 372, sub, "t m"))
        for i, (ric, rcat, rtext, rb) in enumerate(rows):
            b.append(row(x, 392 + i * 50, 350, ric, rcat, rtext, rb))
    b.append(txt(50, 688, "No segmentation between these groups.", "lab"))
    for x in (225, 600, 975):
        b.append(line(x, 700, x, 730, "ov"))
    b.append('<rect class="grp" x="30" y="730" width="1140" height="100" rx="12" stroke-dasharray="3 5"/>')
    b.append(tile(50, 752, 48, "simple-tailscale", "ov"))
    b.append(txt(114, 768, "Tailscale overlay", "t h acc"))
    b.append(txt(114, 788, "Encrypted peer-to-peer links on top of the LAN. They reach the Macs, the NAS, omarchy, an iPhone and an iPad from anywhere.", "t m"))
    b.append(txt(114, 806, "Peers on the same LAN connect directly. An automation VM outside the house joins the same overlay and can only dial out.", "t m"))
    write("logical.svg", svg(1200, 850, "Logical view of the home network: one flat network",
                             "The internet reaches a 5G gateway. Behind it is one flat private network holding the Wi-Fi mesh and its clients, the wired workspace, and the services on the NAS. A Tailscale overlay runs on top.",
                             "\n".join(b)))


# ---------------------------------------------------------------- relationships
def relationships():
    b = [header("Who depends on whom",
                "As of 2026-11-03. Solid arrows are services on the LAN. Dashed arrows travel over the Tailscale overlay.")]
    b.append(card(475, 95, 250, 76, "mdi-router-wireless", "net", "5G gateway", ["DHCP, NAT, the internet"], ["mdi-signal-5g"]))
    b.append(card(50, 235, 280, 90, "mdi-nas", "st", "NAS", ["DNS filtering, file shares,", "backups, media, Tailscale"]))
    b.append(card(460, 235, 280, 90, "mdi-laptop", "pc", "The Macs", ["mini, MacBook Pro, Neo", "use the NAS when at home"], ["simple-apple"]))
    b.append(card(870, 235, 280, 90, "mdi-desktop-tower", "pc", "omarchy", ["Linux workstation,", "powered down at the moment"], ["simple-linux"]))
    b.append(card(680, 430, 230, 76, "mdi-keyboard", "cl", "TESmart KVM", ["shares keyboard", "and display"]))
    b.append(card(150, 430, 260, 76, "mdi-cellphone", "cl", "iPhone and iPad", ["remote access via Tailscale"]))
    b.append(card(940, 430, 230, 76, "mdi-server", "ov", "Automation VM", ["outside the house"]))
    # lan edges
    b.append(line(540, 171, 240, 233, "e", ' marker-end="url(#a)"'))
    b.append(txt(262, 202, "DHCP, NAT", "lab"))
    b.append(line(600, 171, 600, 233, "e", ' marker-end="url(#a)"'))
    b.append(txt(612, 208, "DHCP, NAT", "lab"))
    b.append(line(660, 171, 960, 233, "e", ' marker-end="url(#a)"'))
    b.append(txt(792, 194, "DHCP, NAT", "lab"))
    b.append(line(330, 262, 458, 262, "e", ' marker-end="url(#a)"'))
    b.append(txt(338, 254, "DNS filtering", "lab"))
    b.append(line(460, 298, 332, 298, "e", ' marker-end="url(#a)"'))
    b.append(txt(346, 316, "files, backups", "lab"))
    b.append(line(700, 325, 700, 428, "e", ' marker-end="url(#a)"'))
    b.append(txt(712, 382, "keyboard, display", "lab"))
    # overlay edges
    b.append(line(100, 325, 100, 600, "ov"))
    b.append(line(280, 506, 280, 598, "ov", ' marker-end="url(#v)"'))
    b.append(line(520, 325, 520, 600, "ov"))
    b.append(line(925, 325, 925, 600, "ov"))
    b.append(line(1055, 506, 1055, 598, "ov", ' marker-end="url(#v)"'))
    b.append(txt(1067, 556, "dials out only", "lab"))
    b.append('<rect class="grp" x="30" y="600" width="1140" height="110" rx="12" stroke-dasharray="3 5"/>')
    b.append(tile(50, 625, 48, "simple-tailscale", "ov"))
    b.append(txt(114, 645, "Tailscale overlay", "t h acc"))
    b.append(txt(114, 666, "Lets the Macs, the NAS and omarchy reach each other from anywhere. On the LAN they connect directly.", "t m"))
    b.append(txt(114, 686, "My access rules let the automation VM dial out and let nothing dial in.", "t m"))
    write("relationships.svg", svg(1200, 740, "Who depends on whom in the home network",
                                   "The gateway hands out addresses and internet to the NAS, the Macs and omarchy. The NAS provides DNS filtering, files and backups to the Macs. The KVM shares a keyboard and display with the Macs. A Tailscale overlay joins the Macs, NAS, omarchy, phones and an outbound-only automation VM.",
                                   "\n".join(b)))


if __name__ == "__main__":
    for build in (physical, logical, relationships):
        USED.clear()
        build()
    if WARNINGS:
        print("TEXT MAY OVERFLOW:")
        for w in WARNINGS:
            print("  ", w)
    else:
        print("text-fit check: no overflow predicted")
