# Icons used in the home-network diagrams

Fetched 2026-11-03 through the Iconify API (https://api.iconify.design), which serves each
set under its upstream license. Every icon in a diagram is paired with a text label, so the
diagrams read correctly without the icons. Files are in `icons/<family>/<meaning>.svg`
(`router.svg`, `nas.svg`, `laptop.svg`...), so a build never needs the network.

## Families the diagrams can be drawn with

| Folder | Set | Author | License |
|---|---|---|---|
| `mdi/` (site default) | Material Design Icons | Pictogrammers, https://github.com/Templarian/MaterialDesign | Apache-2.0, https://github.com/Templarian/MaterialDesign/blob/master/LICENSE |
| `ph/` | Phosphor | Phosphor Icons, https://github.com/phosphor-icons/core | MIT, https://github.com/phosphor-icons/core/blob/main/LICENSE |
| `tabler/` | Tabler Icons | Paweł Kuna, https://github.com/tabler/tabler-icons | MIT, https://github.com/tabler/tabler-icons/blob/master/LICENSE |
| `lucide/` | Lucide | Lucide Contributors, https://github.com/lucide-icons/lucide | ISC, https://github.com/lucide-icons/lucide/blob/main/LICENSE |
| `fluent/` | Fluent UI System Icons | Microsoft Corporation, https://github.com/microsoft/fluentui-system-icons | MIT, https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE |
| `material-symbols/` | Material Symbols (outlined) | Google, https://github.com/google/material-design-icons | Apache-2.0, https://github.com/google/material-design-icons/blob/master/LICENSE |
| `carbon/` | Carbon | IBM, https://github.com/carbon-design-system/carbon/tree/main/packages/icons | Apache-2.0 (Iconify gives no license URL; see the Carbon repository) |
| `drawio/` | draw.io clip art (128 px raster) | JGraph, https://github.com/jgraph/drawio | Repository is Apache-2.0. I found no separate notice for the `clip_art` folder, so where that artwork came from is unverified. |

The licenses above are the ones Iconify reports for each set. Check each set's own license
file before relying on this note for anything beyond these diagrams.

Other files:

| Folder | What | License |
|---|---|---|
| `simple/` | Brand glyphs for Apple, Linux, Tailscale, Docker, Plex, AdGuard and TP-Link, from Simple Icons (v16.36.0 as reported by Iconify), https://github.com/simple-icons/simple-icons | CC0-1.0 |
| `custom/` | Network switch and Mac mini, drawn for this wiki in a filled and a line style | CC0-1.0 |

Brand glyphs are trademarks of their owners. They appear only to name the product the label
already names, and are not an endorsement.

The draw.io set has gaps (no TV, speaker, keyboard, share, backup or smart-home icon), so
those fall back to the Material Design Icons.

## Commands

```sh
python3 assets/home-network/src/fetch_icons.py                       # download or refresh the icon files
python3 assets/home-network/src/build_home_diagrams.py --list        # show the families
python3 assets/home-network/src/build_home_diagrams.py --all         # render every family to compare them
python3 assets/home-network/src/build_home_diagrams.py --site ph     # make Phosphor the family the wiki uses
```

Comparison renders go to `assets/home-network/families/<family>/` and are git-ignored. To add a
family, add an entry to `src/families.py`, run `fetch_icons.py`, then build it.
