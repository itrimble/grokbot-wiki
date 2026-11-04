#!/usr/bin/env python3
"""The gate every automatic update must pass before it is committed. Exit 1 on any problem.

Standard library only. Checks the generated pages, the diagrams and the facts file against the
same rules the product diary uses for its public posts (internal addresses, hostnames, secrets,
banned words), plus structure: valid XML, no leftover placeholders, working internal links,
sane facts and size limits.

  python3 bin/home-network/validate.py
"""
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).resolve().parents[2]
PAGES = sorted((REPO / "pages" / "home-network").glob("*.md"))
SVGS = sorted((REPO / "assets" / "home-network").glob("*.svg"))
FACTS = REPO / "facts" / "home-network.json"
problems = []

INTERNAL = [
    (r"\b192\.168\.\d{1,3}\.\d{1,3}\b", "internal IP"), (r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "internal IP"),
    (r"\b172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b", "internal IP"),
    (r"\b100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b", "Tailscale IP"),
    (r"\b[\w-]+\.local\b", "mDNS hostname"), (r"[\w-]+\.ts\.net", "tailnet hostname"), (r"\.lan\b", "LAN hostname"),
    (r"/Volumes/", "local NAS path"), (r"/Users/[a-z]+/", "home directory path"),
    (r"(?<![0-9a-f:])(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}(?![0-9a-f:])", "MAC address"),
]
SECRETS = [
    (r"\b(sk|rk)-[A-Za-z0-9_-]{16,}", "API-key-shaped string"), (r"\bgh[pousr]_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"), (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key block"),
    (r"\beyJ[A-Za-z0-9_-]{20,}\.", "JWT"), (r"\btskey-", "Tailscale auth key"),
]
BANNED_WORDS = ["delv(?:e|es|ed|ing)", "leverag(?:e|es|ed|ing)", "robust(?:ly|ness)?", "seamless(?:ly)?",
                "elevat(?:e|es|ed|ing|ion)", "unlock(?:s|ed|ing)?", "empower(?:s|ed|ing|ment)?", "game[- ]chang(?:er|ing)",
                "cutting[- ]edge", "best[- ]in[- ]class", "journey(?:s)?", "landscape(?:s)?", "testament", "tapestr(?:y|ies)",
                "realm(?:s)?", "underscor(?:e|es|ed|ing)", "pivotal(?:ly)?", "crucial(?:ly)?", "vital(?:ly)?", "notably",
                "moreover", "furthermore"]
BANNED_PHRASES = [r"it'?s not just .{1,40}?,? it'?s", r"in today'?s fast[- ]paced", r"stands as a testament", r"^overall,"]
ALLOWED_SPEEDS = {10, 100, 1000, 2500, 5000, 10000}


def bad(where, what):
    problems.append(f"{where}: {what}")


def scan_text(path, text, svg=False):
    for pat, why in INTERNAL + SECRETS:
        for m in re.finditer(pat, text, re.I if "MAC" in why else 0):
            if svg and why == "MAC address":
                continue
            bad(path.name, f"{why} {m.group(0)[:40]!r}")
    # long hex runs: skip SVG path data and base64 images, where digits are not hex strings
    if not svg:
        for m in re.finditer(r"\b[A-Fa-f0-9]{40,}\b", text):
            bad(path.name, f"long hex string {m.group(0)[:20]!r}")
    if svg:
        for m in re.finditer(r"<(?:text|title|desc)[^>]*>([^<]*)", text):
            if re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", m.group(1)):
                bad(path.name, f"address-like text {m.group(1)[:40]!r}")
    else:
        for word in BANNED_WORDS:
            hit = re.search(rf"\b{word}\b", text, re.I)
            if hit:
                bad(path.name, f"banned word {hit.group(0)!r}")
        for pat in BANNED_PHRASES:
            if re.search(pat, text, re.I | re.M):
                bad(path.name, f"banned phrase /{pat}/")
    if ("{{" in text or "}}" in text) and not svg:
        bad(path.name, "placeholder left in output")


def check_pages():
    if not PAGES:
        bad("pages", "no generated pages found")
    names = {p.stem for p in PAGES}
    for page in PAGES:
        text = page.read_text()
        scan_text(page, text)
        if len(text) > 60_000:
            bad(page.name, f"page is {len(text)} bytes, over the 60000 limit")
        if not re.match(r"# .+", text):
            bad(page.name, "does not start with a heading")
        for para in re.split(r"\n\s*\n", text):
            if para.lstrip().startswith("|"):
                continue
            if para.count("—") > 1:
                bad(page.name, "more than one em dash in a paragraph")
        for target in re.findall(r"\]\(home-network/([\w-]+)\.md\)", text):
            if target not in names:
                bad(page.name, f"link to missing page {target}")
        for asset in re.findall(r'(?:src|href)="(/assets/home-network/[^"]+)"', text):
            if not (REPO / asset.lstrip("/")).exists():
                bad(page.name, f"missing asset {asset}")


def check_svgs():
    if len(SVGS) != 3:
        bad("assets", f"expected 3 diagrams, found {len(SVGS)}")
    for svg in SVGS:
        text = svg.read_text()
        try:
            ET.fromstring(text)
        except ET.ParseError as exc:
            bad(svg.name, f"not valid XML: {exc}")
            continue
        scan_text(svg, text, svg=True)
        if len(text) > 400_000:
            bad(svg.name, f"diagram is {len(text)} bytes, over the 400000 limit")


def check_facts():
    try:
        facts = json.loads(FACTS.read_text())
    except (OSError, ValueError) as exc:
        bad("facts", f"cannot read facts file: {exc}")
        return
    if facts.get("schema") != 1:
        bad("facts", "schema is not 1")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(facts.get("collected_date", ""))):
        bad("facts", "collected_date is not YYYY-MM-DD")
    if not facts.get("roles"):
        bad("facts", "no roles")
    for name, role in facts.get("roles", {}).items():
        if role.get("status") not in ("online", "offline"):
            bad("facts", f"{name}: status must be online or offline")
        speed = role.get("link_mbps")
        if speed is not None and speed not in ALLOWED_SPEEDS:
            bad("facts", f"{name}: link_mbps {speed} is not a standard Ethernet speed")
        rtt = role.get("rtt_ms")
        if rtt is not None and not (0 <= rtt <= 2000):
            bad("facts", f"{name}: rtt_ms {rtt} out of range")
    scan_text(FACTS, FACTS.read_text())


def main():
    check_pages()
    check_svgs()
    check_facts()
    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"validation passed: {len(PAGES)} pages, {len(SVGS)} diagrams, facts file")


if __name__ == "__main__":
    main()
