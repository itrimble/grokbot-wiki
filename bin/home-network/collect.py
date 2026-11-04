#!/usr/bin/env python3
"""Read-only probes of the home network -> facts/home-network.json.

Standard library only. Nothing here changes anything on any machine: it pings, reads
interface state over SSH and reads `tailscale status`. The output holds roles, link
speeds, online/offline, counts and RTTs. It never holds an address, a MAC address, a
hostname or an account name; those live only in the private targets file, which is
never committed (see targets.example.json).

  python3 bin/home-network/collect.py                       # uses ~/.config/home-network/targets.json
  python3 bin/home-network/collect.py --targets T --out F    # explicit paths
  python3 bin/home-network/collect.py --dry-run              # print the facts, write nothing
"""
import argparse
import concurrent.futures as cf
import datetime
import json
import pathlib
import platform
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_TARGETS = pathlib.Path.home() / ".config" / "home-network" / "targets.json"
DEFAULT_OUT = REPO / "facts" / "home-network.json"
IS_MAC = platform.system() == "Darwin"
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "-o", "ServerAliveInterval=5"]


def run(cmd, timeout=45):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return done.returncode, done.stdout
    except (subprocess.TimeoutExpired, OSError):
        return 255, ""


# ---------------------------------------------------------------- ping
def ping(host, count=5):
    """Return (reachable, avg_rtt_ms or None, loss_percent)."""
    wait = ["-t", "6"] if IS_MAC else ["-W", "2"]
    code, out = run(["ping", "-c", str(count), "-i", "0.3", *wait, host], timeout=30)
    loss = re.search(r"([\d.]+)% packet loss", out)
    rtt = re.search(r"=\s*[\d.]+/([\d.]+)/[\d.]+", out)
    loss_pct = float(loss.group(1)) if loss else 100.0
    return loss_pct < 100.0, (round(float(rtt.group(1)), 1) if rtt else None), loss_pct


# ---------------------------------------------------------------- link state
def media_mbps(text):
    """Parse '1000baseT', '2500Base-T', '10Gbase-T' from an ifconfig media line."""
    m = re.search(r"\((\d+)([Gg]?)[Bb]ase", text)
    if not m:
        return None
    value = int(m.group(1))
    return value * 1000 if m.group(2) else value


def parse_mac_ifconfig(text, iface=None, mac=None):
    """Find one interface block in `ifconfig -a` output by name or by MAC and read its link."""
    blocks = re.split(r"(?m)^(?=\S+:)", text)
    for block in blocks:
        name = block.split(":", 1)[0].strip()
        ether = re.search(r"\sether\s+([0-9a-f:]{11,17})", block, re.I)
        if (iface and name == iface) or (mac and ether and ether.group(1).lower() == mac.lower()):
            media = re.search(r"media:.*", block)
            active = "status: active" in block
            return {"link_mbps": media_mbps(media.group(0)) if media and active else None,
                    "carrier": active}
    return None


def read_sysfs(iface):
    """Remote shell snippet for Linux: print the interface counters, one per line."""
    base = f"/sys/class/net/{iface}"
    names = ["operstate", "speed", "carrier_changes"]
    stats = ["rx_errors", "tx_errors", "rx_crc_errors"]
    cmd = " ; ".join([f"cat {base}/{n} 2>/dev/null || echo -" for n in names] +
                     [f"cat {base}/statistics/{s} 2>/dev/null || echo -" for s in stats] +
                     ["cut -d' ' -f1 /proc/uptime"])
    return cmd


def to_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def probe_link(spec):
    """Link facts for one role from its ssh/self + iface or mac settings."""
    target = spec.get("ssh")
    os_kind = spec.get("os", "mac")
    if os_kind == "linux":
        code, out = run((SSH + [target, read_sysfs(spec["iface"])]) if target != "self" else ["sh", "-c", read_sysfs(spec["iface"])])
        lines = out.strip().splitlines()
        if code != 0 or len(lines) < 7:
            return None
        state, speed, changes, rx, tx, crc, up = lines[:7]
        return {"link_mbps": to_int(speed) if state == "up" else None, "carrier": state == "up",
                "carrier_changes": to_int(changes),
                "errors": sum(v for v in (to_int(rx), to_int(tx), to_int(crc)) if v is not None),
                "uptime_s": to_int(up)}
    cmd = ["ifconfig", "-a"] if target == "self" else SSH + [target, "ifconfig -a"]
    code, out = run(cmd)
    if code != 0:
        return None
    return parse_mac_ifconfig(out, spec.get("iface"), spec.get("mac"))


def role_facts(spec, previous):
    ok = False
    rtt = None
    if spec.get("ping"):
        ok, rtt, _ = ping(spec["ping"])
    link = probe_link(spec) if (spec.get("ssh") and spec.get("iface") or spec.get("mac")) else None
    facts = {"status": "online" if (ok or link is not None) else "offline"}
    if rtt is not None:
        facts["rtt_ms"] = rtt
    if link:
        facts.update({k: v for k, v in link.items() if v is not None})
        facts.pop("carrier", None)
    if facts["status"] == "offline" and previous and previous.get("link_mbps"):
        facts["link_mbps"] = previous["link_mbps"]   # last known, so the page can say "2.5G NIC, powered down"
        facts["link_stale"] = True
    return facts


# ---------------------------------------------------------------- network counts
def sweep(prefix):
    """Ping every address once, then count complete ARP entries. Returns the set of MACs seen."""
    def one(i):
        flags = ["-t", "1"] if IS_MAC else ["-W", "1"]
        run(["ping", "-c", "1", *flags, f"{prefix}.{i}"], timeout=6)
    with cf.ThreadPoolExecutor(max_workers=64) as pool:
        list(pool.map(one, range(1, 255)))
    code, out = run(["arp", "-an"])
    macs = set()
    for m in re.finditer(rf"\(({re.escape(prefix)}\.\d+)\) at ([0-9a-f:]+)", out, re.I):
        parts = m.group(2).lower().split(":")
        if len(parts) == 6 and m.group(2).lower() != "ff:ff:ff:ff:ff:ff":
            macs.add(":".join(p.zfill(2) for p in parts))
    return macs


def tailscale_counts(binary):
    code, out = run([binary, "status", "--json"], timeout=30)
    if code != 0:
        return None
    try:
        data = json.loads(out)
    except ValueError:
        return None
    peers = list((data.get("Peer") or {}).values())
    return {"peers_total": len(peers), "peers_online": sum(1 for p in peers if p.get("Online"))}


# ---------------------------------------------------------------- main
FORBIDDEN = [r"\b\d{1,3}(?:\.\d{1,3}){3}\b", r"(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}", r"\.local\b", r"\.ts\.net", r"/Users/"]


def check_clean(text):
    for pat in FORBIDDEN:
        hit = re.search(pat, text, re.I)
        if hit:
            sys.exit(f"refusing to write facts: found {hit.group(0)!r} (pattern {pat})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--targets", default=str(DEFAULT_TARGETS))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = json.loads(pathlib.Path(args.targets).read_text())
    out_path = pathlib.Path(args.out)
    previous = {}
    if out_path.exists():
        try:
            previous = json.loads(out_path.read_text())
        except ValueError:
            pass
    prev_roles = previous.get("roles", {})

    roles = {}
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {name: pool.submit(role_facts, spec, prev_roles.get(name)) for name, spec in targets["roles"].items()}
        for name, fut in futures.items():
            roles[name] = fut.result()

    seen = sweep(targets["sweep_prefix"]) if targets.get("sweep_prefix") else set()
    identified = {m.lower() for m in targets.get("identified_macs", [])}
    network = {}
    if seen:
        network = {"hosts_seen": len(seen), "hosts_unidentified": len(seen - identified)}
    ts = tailscale_counts(targets.get("tailscale", "tailscale"))

    now = datetime.datetime.now(datetime.timezone.utc)
    facts = {"schema": 1,
             "collected_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
             "collected_date": datetime.datetime.now().strftime("%Y-%m-%d"),
             "network": network or previous.get("network", {}),
             "tailscale": ts or previous.get("tailscale", {}),
             "roles": roles}
    text = json.dumps(facts, indent=2, sort_keys=True) + "\n"
    check_clean(text)
    if args.dry_run:
        print(text)
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text)
    print(f"wrote {out_path} ({len(roles)} roles)")


if __name__ == "__main__":
    main()
