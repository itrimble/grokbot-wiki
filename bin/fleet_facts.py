#!/usr/bin/env python3
"""Read the bot roster from the synced docs and write facts/fleet.json.

Standard library only. Runs during the deploy, after bin/sync-content.sh has filled content/.
The Architecture diagrams read this file, so the bot counts and names on them come from the docs
every time the site is built instead of being typed into the diagram script.

Sources, in order of trust:
  content/README.md   "## Bots (28 profiles: 27 active, 1 retired)" and the table under it
  content/bots/*.md   one page per bot
  content/ARCHITECTURE.md   the mermaid node "27 active Grok Bots" (used only as a cross-check)

  python3 bin/fleet_facts.py            # writes facts/fleet.json
  python3 bin/fleet_facts.py --print    # print, write nothing
"""
import datetime
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CONTENT = REPO / "content"
OUT = REPO / "facts" / "fleet.json"


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def main():
    readme = read(CONTENT / "README.md")
    arch = read(CONTENT / "ARCHITECTURE.md")
    problems = []

    heading = re.search(r"##\s+Bots\s*\((\d+)\s+profiles?:\s*(\d+)\s+active(?:,\s*(\d+)\s+retired)?\)", readme)
    total = active = retired = None
    if heading:
        total, active = int(heading.group(1)), int(heading.group(2))
        retired = int(heading.group(3) or 0)
    else:
        problems.append("README heading with the bot counts was not found")

    # The table: "| [Name](bots/x.md) (RETIRED) | role |". Names, in the docs' own order.
    names_active, names_retired = [], []
    for m in re.finditer(r"^\|\s*\[([^\]]+)\]\(bots/[^)]+\.md\)\s*(\(RETIRED\))?", readme, re.M):
        (names_retired if m.group(2) else names_active).append(m.group(1).strip())

    pages = sorted(p.stem for p in (CONTENT / "bots").glob("*.md")) if (CONTENT / "bots").is_dir() else []

    if heading and len(names_active) + len(names_retired) != total:
        problems.append(f"README says {total} profiles but its table lists {len(names_active) + len(names_retired)}")
    if heading and len(names_active) != active:
        problems.append(f"README says {active} active but its table lists {len(names_active)}")
    if pages and total is not None and len(pages) != total:
        problems.append(f"README says {total} profiles but content/bots has {len(pages)} pages")
    mermaid = re.search(r'"(\d+)\s+active\s+Grok\s+Bots"', arch)
    if mermaid and active is not None and int(mermaid.group(1)) != active:
        problems.append(f"ARCHITECTURE.md says {mermaid.group(1)} active bots but README says {active}")

    facts = {
        "schema": 1,
        "generated_date": datetime.date.today().isoformat(),
        "bots_total": total,
        "bots_active": active,
        "bots_retired": retired,
        "names_active": names_active,
        "names_retired": names_retired,
        "source": "content/README.md",
        "consistency_problems": problems,
    }
    text = json.dumps(facts, indent=2) + "\n"
    if "--print" in sys.argv:
        print(text)
        return
    if total is None:
        sys.exit("fleet facts: could not read the bot counts; leaving any existing facts/fleet.json untouched")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"fleet facts: {active} active of {total} profiles ({len(names_active)} named)" +
          (f"; {len(problems)} docs inconsistency(ies)" if problems else ""))


if __name__ == "__main__":
    main()
