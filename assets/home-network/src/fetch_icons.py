#!/usr/bin/env python3
"""Download the icon files every family needs into assets/home-network/icons/.

Standard library only. Uses curl for the HTTP request. Each downloaded file is checked:
it must be a plain SVG built from drawing elements only, with no scripts or links.
Files land in icons/<family>/<meaning>.svg, so the build never needs the network.

  python3 assets/home-network/src/fetch_icons.py            # every family and the brands
  python3 assets/home-network/src/fetch_icons.py ph tabler  # only those families
"""
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from families import BRANDS, FAMILIES, KEYS  # noqa: E402

ICONS = HERE.parent / "icons"
ALLOWED = {"svg", "path", "g", "rect", "circle", "line", "polyline", "polygon", "ellipse"}


def fetch(prefix, name):
    """One request, paced, with a few retries and growing pauses if the API pushes back."""
    url = f"https://api.iconify.design/{prefix}/{name}.svg"
    for attempt in range(4):
        time.sleep(0.5 + attempt * 2)
        done = subprocess.run(["curl", "-s", "-m", "25", "-f", url], capture_output=True, text=True)
        if done.returncode == 0 and done.stdout.strip():
            return done.stdout
    return None


def safe(svg):
    tags = {t.lower() for t in re.findall(r"<\s*([a-zA-Z]+)", svg)}
    bad_attr = re.search(r"\son\w+\s*=|href\s*=|<script", svg, re.I)
    return tags <= ALLOWED and not bad_attr and "viewBox" in svg


def main(wanted):
    problems = []
    targets = [(fam, spec["prefix"], dict(zip(KEYS, spec["names"]))) for fam, spec in FAMILIES.items()
               if not wanted or fam in wanted]
    if not wanted or "simple" in wanted:
        targets.append(("simple", "simple-icons", {b: b for b in BRANDS}))
    for fam, prefix, mapping in targets:
        (ICONS / fam).mkdir(parents=True, exist_ok=True)
        for key, name in mapping.items():
            if (ICONS / fam / f"{key}.svg").exists():
                continue  # already downloaded; delete the file to fetch it again
            svg = fetch(prefix, name)
            if not svg or not safe(svg):
                problems.append(f"{fam}/{key} ({prefix}:{name})")
                continue
            (ICONS / fam / f"{key}.svg").write_text(svg)
        print(f"{fam}: {len(mapping)} icons requested")
    if problems:
        print("PROBLEMS (not saved):", ", ".join(problems))
        sys.exit(1)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
