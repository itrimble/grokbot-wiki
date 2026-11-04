# Home-network pages that update themselves

The home-network section of the wiki is generated from facts read off the network each night.
Nothing on it is typed by hand except the template text.

```
~/.config/home-network/targets.json   PRIVATE (addresses, MACs, aliases). Never committed.
        |  collect.py   read-only: ping, ifconfig/sysfs over ssh, tailscale status
        v
facts/home-network.json               roles, link speeds, online/offline, counts. No addresses.
        |  render.py    templates/home-network/*.md + assets/home-network/src/build_home_diagrams.py
        v
pages/home-network/*.md  +  assets/home-network/{physical,logical,relationships}.svg
        |  validate.py  the gate: no addresses, hostnames, secrets or banned words; valid XML; sane facts
        v
git commit + push (main)  ->  the box pulls and deploys at its next rebuild
        |  changes.py   notable change? (link fell, device offline, flapping, new unknown devices)
        v
ntfy alert after the fact
```

Publishing is fully automatic. A run that fails the validator commits nothing, restores the
working tree and alerts the phone. `watchdog.sh` alerts if there has been no success for 36 hours.

## Where it runs

On the Mac mini, nightly at 05:40, from a private clone at `~/wiki-facts/grokbot-wiki` (outside the
synced `~/projects` tree, like the product diary). Install with `bash bin/home-network/install-on-mini.sh`.
The wiki box deploys; it must `git pull` before it builds or it will overwrite this section.

## Editing

- Change wording or layout: edit `templates/home-network/*.md` or `assets/home-network/src/`, never `pages/`.
- Add a device: add a role to the private targets file and to `build_home_diagrams.py` and the templates.
- Test without committing: `NIGHTLY_DRY=1 bash bin/home-network/nightly.sh`.
- Facts only, nothing written: `/usr/bin/python3 bin/home-network/collect.py --dry-run`.

## Notes

- Use Apple's `/usr/bin/python3` for the collector. On the machine this was built on, Homebrew's Python,
  `bash -c`, node and perl all read an empty ARP table while Apple's Python read all of it.
- The collector and everything else is standard library only and must stay compatible with Python 3.9.
- `NOTABLE` changes (a link falling, a device going offline, link flapping, new unidentified devices)
  still publish. They also send an alert so a person looks.

## The Architecture page

Its detailed diagrams used to be fixed pictures with hard-coded text. They now rebuild on every deploy:

```
deploy.sh  ->  git pull --ff-only  ->  sync-content.sh (docs from the box)
           ->  bin/fleet_facts.py   facts/fleet.json   (bot counts and names, read from content/README.md)
           ->  assets/diagrams-pro/src/build_diagrams.py   (uses the facts; needs cairosvg for the PNGs)
           ->  build.mjs            (writes the note under the diagrams from what was actually built)
```

- Bot counts come from the docs. Bots the docs list but the diagram does not draw are named on the card
  automatically. The set of drawn bots is `DRAWN` in `build_diagrams.py`: update it when you draw another bot.
- If the diagrams could not be regenerated, or the docs disagree with themselves, the page says so instead
  of showing stale numbers quietly.
- Statements such as "verified 2026-10-17" about live checks stay manual on purpose. Nothing generates a
  claim that something was verified.
