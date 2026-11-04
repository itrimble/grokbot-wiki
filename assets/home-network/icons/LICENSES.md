# Icons used in the home-network diagrams

Fetched 2026-11-03 through the Iconify API (https://api.iconify.design), which serves
each set under its upstream license. Every icon in a diagram is paired with a text
label, so the diagrams read correctly without the icons.

| Files | Set | Author | License |
|---|---|---|---|
| `mdi-*.svg` | Material Design Icons | Pictogrammers, https://github.com/Templarian/MaterialDesign | Apache-2.0, https://github.com/Templarian/MaterialDesign/blob/master/LICENSE |
| `simple-*.svg` | Simple Icons (v16.36.0 as reported by Iconify) | Simple Icons Collaborators, https://github.com/simple-icons/simple-icons | CC0-1.0, https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md |
| `custom-*.svg` | Drawn for this wiki (network switch, Mac mini) | This repo | CC0-1.0 |

Brand glyphs in `simple-*.svg` (Apple, Linux, Tailscale, Docker, Plex, AdGuard, TP-Link)
are trademarks of their owners. They appear only to name the product the label already
names, and are not an endorsement.

Not used: the draw.io `clip_art` raster icons (https://github.com/jgraph/drawio). They were
compared and set aside because they are 128 px glossy rasters in mixed styles.

Rebuild the diagrams with `python3 assets/home-network/src/build_home_diagrams.py`
(standard library only).
