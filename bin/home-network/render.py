#!/usr/bin/env python3
"""facts/home-network.json + templates/home-network/*.md -> pages/home-network/*.md and the SVG diagrams.

Standard library only. Edit the templates, never the generated pages. The diagrams come from
assets/home-network/src/build_home_diagrams.py, which reads the same facts file.

  python3 bin/home-network/render.py            # render everything
  python3 bin/home-network/render.py --check    # render to memory, exit 1 if anything would change
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
FACTS = REPO / "facts" / "home-network.json"
TEMPLATES = REPO / "templates" / "home-network"
PAGES = REPO / "pages" / "home-network"
GENERATOR = REPO / "assets" / "home-network" / "src" / "build_home_diagrams.py"

LONG = {10000: "10 Gbps", 5000: "5 Gbps", 2500: "2.5 Gbps", 1000: "1 Gbps", 100: "100 Mbps", 10: "10 Mbps"}
SHORT = {10000: "10G", 5000: "5G", 2500: "2.5G", 1000: "1G", 100: "100M", 10: "10M"}
WORDS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()


def ms(value):
    if value is None:
        return "not measured"
    return "under 1 ms" if value < 1 else f"about {round(value)} ms"


def context(facts):
    roles = facts.get("roles", {})

    def speed(name, default):
        return roles.get(name, {}).get("link_mbps", default)

    def long(name, default=None):
        v = speed(name, default)
        return LONG.get(v, f"{v} Mbps") if v else "not measured"

    def short(name, default=None):
        v = speed(name, default)
        return SHORT.get(v, f"{v}M") if v else "unknown-speed"

    offline = roles.get("omarchy", {}).get("status") == "offline"
    net = facts.get("network", {})
    unidentified = net.get("hosts_unidentified")
    date = facts.get("collected_date", "")
    ctx = {
        "as_of": date,
        "nas_speed": long("nas"), "nas_speed_short": short("nas"),
        "mbp_speed": long("mbp"), "mbp_speed_short": short("mbp"),
        "mini_speed": long("mini"), "mini_speed_short": short("mini"),
        "neo_speed": long("neo"), "neo_speed_short": short("neo"),
        "kvm_speed": long("mbp_kvm"), "kvm_speed_short": short("mbp_kvm"),
        "omarchy_speed_short": short("omarchy"),
        "omarchy_state": "Powered down at the moment." if offline else "Online.",
        "omarchy_speed_cell": (long("omarchy") + (" when last measured" if offline else "")),
        "omarchy_how_cell": "It is powered down now" if offline else f"Read from the machine on {date}",
        "rtt_workspace": ms(roles.get("deco_workspace", {}).get("rtt_ms")),
        "rtt_root": ms(roles.get("deco_root", {}).get("rtt_ms")),
        "rtt_far": ms(roles.get("deco_far", {}).get("rtt_ms")),
        "hosts_seen": str(net.get("hosts_seen", "an unknown number of")),
        "unidentified_words": (WORDS[unidentified] if isinstance(unidentified, int) and unidentified < len(WORDS)
                               else str(unidentified if unidentified is not None else "an unknown number"))
        if unidentified is not None else "an unknown number",
    }
    return ctx


def render_text(text, ctx, name):
    missing = sorted({m for m in re.findall(r"\{\{(\w+)\}\}", text) if m not in ctx})
    if missing:
        sys.exit(f"{name}: unknown placeholder(s) {missing}")
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: ctx[m.group(1)], text)
    if "{{" in out:
        sys.exit(f"{name}: a placeholder is left in the output")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--facts", default=str(FACTS))
    args = ap.parse_args()

    facts = json.loads(pathlib.Path(args.facts).read_text())
    ctx = context(facts)
    changed = []
    PAGES.mkdir(parents=True, exist_ok=True)
    for template in sorted(TEMPLATES.glob("*.md")):
        out = render_text(template.read_text(), ctx, template.name)
        target = PAGES / template.name
        if not target.exists() or target.read_text() != out:
            changed.append(str(target.relative_to(REPO)))
            if not args.check:
                target.write_text(out)
    if args.check:
        print("would change:" if changed else "pages are current", *changed)
        sys.exit(1 if changed else 0)
    before = {p: p.read_bytes() for p in (REPO / "assets" / "home-network").glob("*.svg")}
    done = subprocess.run([sys.executable, str(GENERATOR), "--facts", args.facts], capture_output=True, text=True)
    if done.returncode != 0:
        sys.exit("diagram generator failed:\n" + done.stderr)
    for p, old in before.items():
        if p.read_bytes() != old:
            changed.append(str(p.relative_to(REPO)))
    print("changed:" if changed else "nothing changed", *changed)


if __name__ == "__main__":
    main()
