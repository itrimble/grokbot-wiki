#!/usr/bin/env python3
"""Compare two facts files and list what is worth an alert.

Publishing is automatic either way. This only decides which changes also send a phone alert.

  python3 bin/home-network/changes.py OLD.json NEW.json        # prints one line per change
  exit code 0 always; the first word of each line is NOTABLE or INFO
"""
import json
import pathlib
import sys

LABEL = {"nas": "NAS", "mini": "Mac mini", "mbp": "MacBook Pro dock", "mbp_kvm": "KVM adapter", "neo": "MacBook Neo",
         "omarchy": "omarchy", "gateway": "5G gateway", "deco_root": "mesh root node",
         "deco_workspace": "workspace node", "deco_far": "far node"}


def label(name):
    return LABEL.get(name, name)


def mbps(v):
    return f"{v / 1000:g} Gbps" if v and v >= 1000 else f"{v} Mbps"


def compare(old, new):
    notes = []
    old_roles, new_roles = old.get("roles", {}), new.get("roles", {})
    for name, n in new_roles.items():
        o = old_roles.get(name)
        if o is None:
            notes.append(("NOTABLE", f"new role appeared: {label(name)}"))
            continue
        if o.get("status") == "online" and n.get("status") == "offline":
            notes.append(("NOTABLE", f"{label(name)} went offline"))
        elif o.get("status") == "offline" and n.get("status") == "online":
            notes.append(("INFO", f"{label(name)} is back online"))
        a, b = o.get("link_mbps"), n.get("link_mbps")
        if a and b and not o.get("link_stale") and not n.get("link_stale"):
            if b < a:
                notes.append(("NOTABLE", f"{label(name)} link fell from {mbps(a)} to {mbps(b)}"))
            elif b > a:
                notes.append(("INFO", f"{label(name)} link rose from {mbps(a)} to {mbps(b)}"))
        cc_a, cc_b = o.get("carrier_changes"), n.get("carrier_changes")
        up_a, up_b = o.get("uptime_s"), n.get("uptime_s")
        if None not in (cc_a, cc_b, up_a, up_b) and up_b > up_a and cc_b - cc_a >= 3:
            notes.append(("NOTABLE", f"{label(name)} link flapped {cc_b - cc_a} times since the last check"))
        e_a, e_b = o.get("errors"), n.get("errors")
        if None not in (e_a, e_b) and e_b - e_a >= 100:
            notes.append(("NOTABLE", f"{label(name)} logged {e_b - e_a} new link errors"))
    for name in old_roles:
        if name not in new_roles:
            notes.append(("NOTABLE", f"role no longer reported: {label(name)}"))
    u_a = old.get("network", {}).get("hosts_unidentified")
    u_b = new.get("network", {}).get("hosts_unidentified")
    if u_a is not None and u_b is not None and u_b - u_a >= 2:
        notes.append(("NOTABLE", f"{u_b - u_a} more unidentified devices on the LAN ({u_a} to {u_b})"))
    s_a = old.get("network", {}).get("hosts_seen")
    s_b = new.get("network", {}).get("hosts_seen")
    if s_a is not None and s_b is not None and abs(s_b - s_a) >= 5:
        notes.append(("INFO", f"devices on the LAN went from {s_a} to {s_b}"))
    return notes


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    old = json.loads(pathlib.Path(sys.argv[1]).read_text()) if pathlib.Path(sys.argv[1]).stat().st_size else {}
    new = json.loads(pathlib.Path(sys.argv[2]).read_text())
    for level, text in compare(old, new):
        print(level, text)


if __name__ == "__main__":
    main()
