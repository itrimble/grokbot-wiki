#!/usr/bin/env python3
"""Build the three home-network diagrams (SVG) in any of the supported icon families.

Standard library only. The icon files are in ../icons/<family>/ (see fetch_icons.py).

  python3 assets/home-network/src/build_home_diagrams.py                  # the site family (mdi) only
  python3 assets/home-network/src/build_home_diagrams.py --family ph      # one other family, for comparison
  python3 assets/home-network/src/build_home_diagrams.py --all            # every family, for comparison
  python3 assets/home-network/src/build_home_diagrams.py --site ph        # make ph the family the wiki pages use
  python3 assets/home-network/src/build_home_diagrams.py --list           # show the families

The site family writes physical.svg, logical.svg and relationships.svg into
assets/home-network/ (the files the wiki pages use). Any other family writes the same three
files into assets/home-network/families/<family>/ (git-ignored) so they can be compared side by side.
No addresses, MAC addresses, hostnames or account names belong in these diagrams.
"""
import argparse
import base64
import pathlib
import re
import struct
import sys
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from families import BRANDS, DRAWIO, FAMILIES  # noqa: E402

OUT = HERE.parent
ICONS = OUT / "icons"
DEFAULT = "mdi"   # also the fallback for gaps in the draw.io set
SITE = DEFAULT    # the family the wiki pages use; set with --site
ALL_FAMILIES = list(FAMILIES) + ["drawio"]

WARNINGS = []
FAMILY = DEFAULT
USED = {}      # symbol id -> symbol markup
RASTER = set() # symbol ids that are raster images


# ---------------------------------------------------------------- icons
def settings(family):
    return DRAWIO if family == "drawio" else FAMILIES[family]


def _vector_symbol(sid, text):
    match = re.search(r"<svg([^>]*)>(.*)</svg>", text, re.S)
    if not match:
        sys.exit(f"{sid}: not an SVG")
    attrs = dict(re.findall(r'([\w:-]+)="([^"]*)"', match.group(1)))
    view = attrs.get("viewBox", "0 0 24 24")
    keep = "".join(f' {k}="{v}"' for k, v in attrs.items()
                   if k not in ("xmlns", "width", "height", "viewBox"))
    return f'<symbol id="{sid}" viewBox="{view}"{keep}>{match.group(2)}</symbol>'


def _png_symbol(sid, path):
    data = path.read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    b64 = base64.b64encode(data).decode()
    return (f'<symbol id="{sid}" viewBox="0 0 {width} {height}">'
            f'<image href="data:image/png;base64,{b64}" width="{width}" height="{height}"/></symbol>')


def icon(key):
    """Return the symbol id for a meaning (router, nas...) in the current family."""
    if key in BRANDS:
        path, sid = ICONS / "simple" / f"{key}.svg", f"i-simple-{key}"
    elif key in ("switch", "macmini"):
        raster = ICONS / "drawio" / f"{key}.png"
        if FAMILY == "drawio" and raster.exists():
            path, sid = raster, f"i-drawio-{key}"
        else:
            line = "line" if settings(FAMILY)["custom"] == "line" else ""
            path = ICONS / "custom" / (f"{key}-line.svg" if line else f"{key}.svg")
            sid = f"i-custom-{key}{'-line' if line else ''}"
    else:
        raster = ICONS / "drawio" / f"{key}.png"
        if FAMILY == "drawio" and raster.exists():
            path, sid = raster, f"i-drawio-{key}"
        else:
            fam = FAMILY if FAMILY != "drawio" else DEFAULT  # draw.io has gaps: fall back to mdi
            path, sid = ICONS / fam / f"{key}.svg", f"i-{fam}-{key}"
    if sid not in USED:
        if path.suffix == ".png":
            USED[sid] = _png_symbol(sid, path)
            RASTER.add(sid)
        else:
            USED[sid] = _vector_symbol(sid, path.read_text())
    return sid


def defs():
    out = ["<defs>"] + [USED[k] for k in sorted(USED)]
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
.port{fill:none;stroke:#8a8880;stroke-width:1.2}.acc{fill:#b4462b}.ah{fill:#8a8880}.ahv{fill:#b4462b}.bd{fill:#8a8880;color:#8a8880}
.c-net .tb{fill:#e3ecfa}.c-net .tg{fill:#2b6cb0;color:#2b6cb0}
.c-pc .tb{fill:#dcf1ec}.c-pc .tg{fill:#1c8a75;color:#1c8a75}
.c-st .tb{fill:#fbecd3}.c-st .tg{fill:#b86e0a;color:#b86e0a}
.c-ov .tb{fill:#f9e3dc}.c-ov .tg{fill:#b4462b;color:#b4462b}
.c-cl .tb{fill:#eceae3}.c-cl .tg{fill:#5f5e59;color:#5f5e59}
.c-in .tb{fill:#ece4f8}.c-in .tg{fill:#6b46c1;color:#6b46c1}
@media (prefers-color-scheme:dark){
.bg{fill:#141412}.box{fill:#1d1d1b;stroke:#4a4841}.grp{fill:#1b1a18;stroke:#4a4841}.t{fill:#ecebe6}.m,.lab{fill:#9a9890}
.l25{stroke:#5fcf8f}.l1{stroke:#6aa8f0}.lx,.lw,.e{stroke:#9a9890}.bus{stroke:#4a4841}.port{stroke:#9a9890}.ov{stroke:#e07a5f}
.acc,.ahv{fill:#e07a5f}.ah{fill:#9a9890}.bd{fill:#9a9890;color:#9a9890}
.c-net .tb{fill:#1b2a44}.c-net .tg{fill:#6aa8f0;color:#6aa8f0}
.c-pc .tb{fill:#143229}.c-pc .tg{fill:#4fd1b5;color:#4fd1b5}
.c-st .tb{fill:#3a2a10}.c-st .tg{fill:#f0b45a;color:#f0b45a}
.c-ov .tb{fill:#3a1f18}.c-ov .tg{fill:#e07a5f;color:#e07a5f}
.c-cl .tb{fill:#2a2926}.c-cl .tg{fill:#b4b2a8;color:#b4b2a8}
.c-in .tb{fill:#2a2140}.c-in .tg{fill:#b79cf0;color:#b79cf0}
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
        WARNINGS.append(f"[{FAMILY}] {label}: '{s}' ~{int(width_of(s, size, bold))}px > {avail}px")


def tile(x, y, size, key, cat, glyph=None):
    sid = icon(key)
    glyph = glyph or int(size * (0.86 if sid in RASTER else 0.64))
    off = (size - glyph) / 2
    return (f'<g class="c-{cat}"><rect class="tb" x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * 0.23:.0f}"/>'
            f'<use class="tg" href="#{sid}" x="{x + off:.1f}" y="{y + off:.1f}" width="{glyph}" height="{glyph}"/></g>')


def badge(x, y, key, size=17):
    return f'<use class="bd" href="#{icon(key)}" x="{x}" y="{y}" width="{size}" height="{size}"/>'


def card(x, y, w, h, key, cat, title, subs=(), badges=(), dashed=False):
    d = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"{d}/>']
    out.append(tile(x + 12, y + 12 if h < 64 else y + (h - 44) / 2, 44, key, cat))
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


def row(x, y, w, key, cat, text, badges=()):
    out = [f'<rect class="box" x="{x}" y="{y}" width="{w}" height="42" rx="8"/>']
    out.append(tile(x + 8, y + 7, 28, key, cat, 22 if icon(key) in RASTER else 18))
    fit(text, text, w - 52 - 24 * len(badges), 13)
    out.append(txt(x + 46, y + 26, text, "t"))
    for i, b in enumerate(badges):
        out.append(badge(x + w - 26 - 22 * i, y + 12, b, 17))
    return "\n".join(out)


def svg(width, height, label, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">\n'
            f'<title id="t">{escape(label)}</title>\n<desc id="d">{escape(desc)}</desc>\n{STYLE}\n{defs()}\n'
            f'<rect class="bg" width="{width}" height="{height}" rx="10"/>\n{body}\n</svg>\n')


def header(title, sub, width):
    out = txt(30, 42, title, "t title") + "\n" + txt(30, 64, sub, "lab")
    if FAMILY != SITE:  # make comparisons obvious
        out += "\n" + txt(width - 30, 42, "Icons: " + settings(FAMILY)["title"], "lab r")
    return out


def line(x1, y1, x2, y2, cls, extra=""):
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{extra}/>'


def write(name, content):
    folder = OUT if FAMILY == SITE else OUT / "families" / FAMILY
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(content)
    print(f"wrote {folder.relative_to(OUT.parent.parent) / name}  {len(content):,} bytes")


# ---------------------------------------------------------------- physical
def physical():
    W = 1200
    b = [header("Physical layout and link speeds",
                "As of 2026-11-03. Color is the speed each link negotiated. Dashed means wireless or not confirmed.", W)]
    b.append('<rect class="grp" x="30" y="90" width="330" height="275" rx="10"/>')
    b.append(txt(46, 112, "GATEWAY ROOM"))
    b.append(card(50, 125, 290, 76, "router", "net", "5G home-internet gateway", ["TMO-G4SE: router, NAT, DHCP"], ["g5"]))
    b.append(line(195, 201, 195, 265, "l1"))
    b.append(txt(207, 238, "1 GbE", "lab"))
    b.append(card(50, 265, 290, 76, "mesh_ap", "net", "Deco BE63: mesh root", ["the gateway plugs in here"], ["tplink"]))
    b.append('<rect class="grp" x="30" y="470" width="330" height="140" rx="10"/>')
    b.append(txt(46, 492, "FAR ROOM"))
    b.append(card(50, 505, 290, 76, "mesh_ap", "net", "Deco BE63: far node", ["Wi-Fi coverage only"], ["tplink"]))
    b.append(line(195, 341, 195, 505, "lw"))
    b.append(txt(207, 415, "wireless backhaul", "lab"))
    b.append(txt(207, 431, "6 to 11 ms from the workspace", "lab"))
    b.append('<rect class="grp" x="420" y="90" width="750" height="740" rx="10"/>')
    b.append(txt(436, 112, "WIRED WORKSPACE"))
    b.append('<rect class="box" x="450" y="120" width="300" height="125" rx="10" stroke-dasharray="5 4"/>')
    b.append(txt(466, 144, "Wi-Fi clients", "t h"))
    for i, k in enumerate(["phone", "tablet", "tv", "speaker", "smarthome"]):
        b.append(tile(466 + i * 54, 158, 42, k, "cl", 36 if icon(k) in RASTER else 26))
    b.append(txt(466, 226, "Each joins the closest Deco", "t m"))
    b.append(card(450, 265, 300, 76, "mesh_ap", "net", "Deco BE63: workspace node", ["wired anchor for the workspace"], ["tplink"]))
    b.append(line(340, 303, 450, 303, "lw"))
    b.append(txt(354, 294, "wireless", "lab"))
    b.append(txt(354, 322, "3 to 5 ms", "lab"))
    b.append(line(600, 341, 600, 400, "lx"))
    b.append(txt(588, 364, "uplink to the switch", "lab r"))
    b.append(txt(588, 380, "speed not measured", "lab r"))
    b.append(card(450, 400, 300, 104, "switch", "net", "TP-Link TL-SG108S-M2", ["8 x 2.5G, unmanaged", "loop prevention on"], ["tplink"]))
    for i in range(8):
        b.append(f'<rect class="port" x="{466 + i * 28}" y="480" width="20" height="14" rx="2"/>')
    b.append(card(450, 540, 300, 140, "tailscale", "ov", "Tailscale overlay",
                  ["Runs on every Mac, the NAS,", "omarchy, the iPhone and iPad.", "Direct on this LAN; away from", "home it goes through a relay."], dashed=True))
    b.append(line(805, 163, 805, 613, "bus", ' stroke-linecap="round"'))
    b.append(line(750, 452, 805, 452, "lx"))
    devices = [
        (125, "nas", "st", "UGREEN DXP2800 NAS", ["Intel N100, one 2.5GbE port", "static address"], [], "l25", False),
        (215, "laptop", "pc", "MacBook Pro M4 Max", ["USB-C dock at 2.5G", "Wi-Fi also on"], ["apple"], "l25", False),
        (305, "macmini", "pc", "Mac mini M4", ["built-in 1 GbE", "Wi-Fi also on"], ["apple"], "l1", False),
        (395, "laptop", "pc", "MacBook Neo", ["USB Ethernet adapter, 1G", "Wi-Fi also on"], ["apple"], "l1", True),
        (485, "tower", "pc", "omarchy (Linux PC)", ["2.5G NIC", "powered down at the moment"], ["linux"], "l25", True),
        (575, "keyboard", "cl", "TESmart KVM", ["shares keyboard and display", "1G LAN adapter to the MacBook Pro"], [], "l1", True),
    ]
    for y, k, cat, title, subs, badges, cls, dashed in devices:
        b.append(card(850, y, 300, 76, k, cat, title, subs, badges))
        extra = ' stroke-dasharray="7 6"' if dashed else ""
        b.append(line(805, y + 38, 850, y + 38, cls, extra))
    b.append('<rect class="grp" x="30" y="640" width="330" height="150" rx="10"/>')
    b.append(txt(46, 664, "Legend", "t h"))
    for i, (cls, label) in enumerate([("l25", "2.5 Gbps, negotiated"), ("l1", "1 Gbps, negotiated"),
                                      ("lx", "wired, speed not measured"), ("lw", "wireless, or port not confirmed")]):
        yy = 687 + i * 24
        b.append(line(50, yy, 105, yy, cls))
        b.append(txt(118, yy + 4, label, "t m"))
    b.append(txt(30, 808, "Wireless latencies were measured on 2026-11-01 from a wired", "lab"))
    b.append(txt(30, 824, "machine, before the switch went in. Not re-measured.", "lab"))
    write("physical.svg", svg(W, 840, "Physical layout and link speeds of the home network",
                              "A 5G gateway feeds a mesh root node over 1 GbE. Three mesh nodes link to each other wirelessly. The workspace node uplinks to an 8-port 2.5G switch. The NAS and the MacBook Pro dock connect at 2.5G, the Mac mini and other adapters at 1G.",
                              "\n".join(b)))


# ---------------------------------------------------------------- logical
def logical():
    W = 1200
    b = [header("Logical view: one flat network",
                "As of 2026-11-03. There are no VLANs. Wired, Wi-Fi, smart-home and server traffic share one broadcast domain.", W)]
    b.append(card(475, 92, 250, 64, "cloud", "in", "Internet", ["cellular, via the gateway"]))
    b.append(line(600, 156, 600, 185, "lx"))
    b.append(card(450, 185, 300, 76, "router", "net", "5G home-internet gateway", ["router, NAT, DHCP, MTU 1420"], ["g5"]))
    b.append(line(600, 261, 600, 300, "lx"))
    b.append('<rect class="grp" x="30" y="300" width="1140" height="400" rx="12"/>')
    b.append(txt(50, 322, "ONE FLAT PRIVATE NETWORK (a single /24)"))
    cols = [
        (50, "mesh_ap", "net", "Wi-Fi mesh", "3 x Deco BE63 in access-point mode", [
            ("phone", "cl", "Phones and tablets", []),
            ("tv", "cl", "TVs and AV receivers", []),
            ("smarthome", "cl", "Smart-home devices", []),
            ("speaker", "cl", "Voice assistants and speakers", []),
            ("laptop", "cl", "Laptops when they are off the wire", [])]),
        (425, "switch", "net", "Wired workspace", "behind the 2.5G switch", [
            ("laptop", "pc", "MacBook Pro M4 Max", ["apple"]),
            ("macmini", "pc", "Mac mini M4", ["apple"]),
            ("laptop", "pc", "MacBook Neo", ["apple"]),
            ("tower", "pc", "omarchy (powered down)", ["linux"]),
            ("keyboard", "cl", "TESmart KVM", [])]),
        (800, "nas", "st", "Services on the NAS", "UGREEN DXP2800, static address", [
            ("share", "st", "File shares (SMB, NFS)", []),
            ("backup", "st", "Time Machine backups for the Macs", []),
            ("adguard", "st", "DNS filtering for the whole LAN", []),
            ("plex", "st", "Media server and helpers", ["docker"]),
            ("tailscale", "ov", "Tailscale (runs in a container)", ["docker"])]),
    ]
    for x, k, cat, title, sub, rows in cols:
        b.append(tile(x, 336, 40, k, cat))
        b.append(txt(x + 52, 354, title, "t h"))
        b.append(txt(x + 52, 372, sub, "t m"))
        for i, (rk, rcat, rtext, rb) in enumerate(rows):
            b.append(row(x, 392 + i * 50, 350, rk, rcat, rtext, rb))
    b.append(txt(50, 688, "No segmentation between these groups.", "lab"))
    for x in (225, 600, 975):
        b.append(line(x, 700, x, 730, "ov"))
    b.append('<rect class="grp" x="30" y="730" width="1140" height="100" rx="12" stroke-dasharray="3 5"/>')
    b.append(tile(50, 752, 48, "tailscale", "ov"))
    b.append(txt(114, 768, "Tailscale overlay", "t h acc"))
    b.append(txt(114, 788, "Encrypted peer-to-peer links on top of the LAN. They reach the Macs, the NAS, omarchy, an iPhone and an iPad from anywhere.", "t m"))
    b.append(txt(114, 806, "Peers on the same LAN connect directly. An automation VM outside the house joins the same overlay and can only dial out.", "t m"))
    write("logical.svg", svg(W, 850, "Logical view of the home network: one flat network",
                             "The internet reaches a 5G gateway. Behind it is one flat private network holding the Wi-Fi mesh and its clients, the wired workspace, and the services on the NAS. A Tailscale overlay runs on top.",
                             "\n".join(b)))


# ---------------------------------------------------------------- relationships
def relationships():
    W = 1200
    b = [header("Who depends on whom",
                "As of 2026-11-03. Solid arrows are services on the LAN. Dashed arrows travel over the Tailscale overlay.", W)]
    b.append(card(475, 95, 250, 76, "router", "net", "5G gateway", ["DHCP, NAT, the internet"], ["g5"]))
    b.append(card(50, 235, 280, 90, "nas", "st", "NAS", ["DNS filtering, file shares,", "backups, media, Tailscale"]))
    b.append(card(460, 235, 280, 90, "laptop", "pc", "The Macs", ["mini, MacBook Pro, Neo", "use the NAS when at home"], ["apple"]))
    b.append(card(870, 235, 280, 90, "tower", "pc", "omarchy", ["Linux workstation,", "powered down at the moment"], ["linux"]))
    b.append(card(680, 430, 230, 76, "keyboard", "cl", "TESmart KVM", ["shares keyboard", "and display"]))
    b.append(card(150, 430, 260, 76, "phone", "cl", "iPhone and iPad", ["remote access via Tailscale"]))
    b.append(card(940, 430, 230, 76, "server", "ov", "Automation VM", ["outside the house"]))
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
    b.append(line(100, 325, 100, 600, "ov"))
    b.append(line(280, 506, 280, 598, "ov", ' marker-end="url(#v)"'))
    b.append(line(520, 325, 520, 600, "ov"))
    b.append(line(925, 325, 925, 600, "ov"))
    b.append(line(1055, 506, 1055, 598, "ov", ' marker-end="url(#v)"'))
    b.append(txt(1067, 556, "dials out only", "lab"))
    b.append('<rect class="grp" x="30" y="600" width="1140" height="110" rx="12" stroke-dasharray="3 5"/>')
    b.append(tile(50, 625, 48, "tailscale", "ov"))
    b.append(txt(114, 645, "Tailscale overlay", "t h acc"))
    b.append(txt(114, 666, "Lets the Macs, the NAS and omarchy reach each other from anywhere. On the LAN they connect directly.", "t m"))
    b.append(txt(114, 686, "My access rules let the automation VM dial out and let nothing dial in.", "t m"))
    write("relationships.svg", svg(W, 740, "Who depends on whom in the home network",
                                   "The gateway hands out addresses and internet to the NAS, the Macs and omarchy. The NAS provides DNS filtering, files and backups to the Macs. The KVM shares a keyboard and display with the Macs. A Tailscale overlay joins the Macs, NAS, omarchy, phones and an outbound-only automation VM.",
                                   "\n".join(b)))


def build(family):
    global FAMILY
    FAMILY = family
    for diagram in (physical, logical, relationships):
        USED.clear()
        RASTER.clear()
        diagram()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--family", default=None, choices=ALL_FAMILIES, help="build one family")
    parser.add_argument("--site", default=DEFAULT, choices=ALL_FAMILIES, help="family the wiki pages use (default mdi)")
    parser.add_argument("--all", action="store_true", help="build every family")
    parser.add_argument("--list", action="store_true", help="list the families and exit")
    args = parser.parse_args()
    if args.list:
        for name in ALL_FAMILIES:
            s = settings(name)
            mark = " (site default)" if name == DEFAULT else ""
            print(f"{name:18} {s['title']}  [{s['license']}]{mark}")
        return
    global SITE
    SITE = args.site
    for family in (ALL_FAMILIES if args.all else [args.family or SITE]):
        build(family)
    if WARNINGS:
        print("TEXT MAY OVERFLOW (estimates, check the render):")
        for w in WARNINGS:
            print("  ", w)
    else:
        print("text-fit check: no overflow predicted")


if __name__ == "__main__":
    main()
