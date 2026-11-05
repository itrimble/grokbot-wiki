"""Icon families the home-network diagrams can be drawn with.

Each diagram asks for icons by meaning (router, nas, laptop...). A family maps those
meanings to icon names in one icon set. Brand glyphs always come from Simple Icons, and
the network switch and Mac mini are drawn glyphs because no set has them.

Add a family: add an entry here, run fetch_icons.py, then build_home_diagrams.py --family NAME.
"""

# Meanings the diagrams use, in the order the name lists below follow.
KEYS = ["router", "mesh_ap", "cloud", "nas", "laptop", "tower", "phone", "tablet", "tv",
        "speaker", "smarthome", "keyboard", "share", "backup", "g5", "server"]

# Brand glyphs (Simple Icons, CC0). The same in every family.
BRANDS = ["apple", "linux", "tailscale", "docker", "plex", "adguard", "tplink"]

# name -> settings.  prefix is the Iconify set prefix.  custom is the style of the drawn
# switch and Mac mini glyphs ("fill" or "line") so they sit well beside that family.
FAMILIES = {
    "mdi": dict(
        title="Material Design Icons", prefix="mdi", custom="fill",
        license="Apache-2.0", author="Pictogrammers", url="https://github.com/Templarian/MaterialDesign",
        names=["router-wireless", "access-point-network", "cloud", "nas", "laptop", "desktop-tower", "cellphone",
               "tablet", "television", "speaker", "home-automation", "keyboard", "folder-network",
               "backup-restore", "signal-5g", "server"]),
    "ph": dict(
        title="Phosphor", prefix="ph", custom="line",
        license="MIT", author="Phosphor Icons", url="https://github.com/phosphor-icons/core",
        names=["network", "wifi-high", "cloud", "hard-drives", "laptop", "desktop-tower", "device-mobile",
               "device-tablet", "television", "speaker-hifi", "house-line", "keyboard", "share-network",
               "clock-counter-clockwise", "cell-signal-full", "database"]),
    "tabler": dict(
        title="Tabler Icons", prefix="tabler", custom="line",
        license="MIT", author="Paweł Kuna", url="https://github.com/tabler/tabler-icons",
        names=["router", "access-point", "cloud", "server-2", "device-laptop", "device-desktop", "device-mobile",
               "device-tablet", "device-tv", "device-speaker", "smart-home", "keyboard", "folder-share", "history",
               "signal-5g", "server"]),
    "lucide": dict(
        title="Lucide", prefix="lucide", custom="line",
        license="ISC", author="Lucide Contributors", url="https://github.com/lucide-icons/lucide",
        names=["router", "wifi", "cloud", "server-nas", "laptop", "pc-case", "smartphone", "tablet", "tv", "speaker",
               "house-wifi", "keyboard", "folder-symlink", "cloud-backup", "signal-high", "server"]),
    "fluent": dict(
        title="Fluent UI System Icons", prefix="fluent", custom="line",
        license="MIT", author="Microsoft Corporation", url="https://github.com/microsoft/fluentui-system-icons",
        names=["router-24-regular", "wifi-1-24-regular", "cloud-24-regular", "hard-drive-24-regular",
               "laptop-24-regular", "desktop-tower-24-regular", "phone-24-regular", "tablet-24-regular",
               "tv-24-regular", "speaker-2-24-regular", "home-24-regular", "keyboard-24-regular",
               "folder-link-24-regular", "cloud-backup-24-regular", "cellular-5g-24-regular", "server-24-regular"]),
    "material-symbols": dict(
        title="Material Symbols (outlined)", prefix="material-symbols", custom="line",
        license="Apache-2.0", author="Google", url="https://github.com/google/material-design-icons",
        names=["router-outline", "wifi", "cloud-outline", "dns-outline", "laptop-mac-outline",
               "desktop-windows-outline", "smartphone-outline", "tablet-outline", "tv-outline", "speaker-outline",
               "home-iot-device-outline", "keyboard-outline", "folder-shared-outline", "backup-outline", "5g",
               "storage-outline"]),
    "carbon": dict(
        title="Carbon", prefix="carbon", custom="line",
        license="Apache-2.0", author="IBM", url="https://github.com/carbon-design-system/carbon/tree/main/packages/icons",
        names=["router", "router-wifi", "cloud", "storage-pool", "laptop", "bare-metal-server", "mobile", "tablet",
               "screen", "volume-up", "home", "keyboard", "folder-shared", "data-backup", "cell-tower",
               "server-dns"]),
}

# draw.io clip art (raster PNG, 128 px). Only some meanings exist; the rest fall back to mdi.
# Files live in icons/drawio/<key>.png. See icons/LICENSES.md for the provenance caveat.
DRAWIO = dict(
    title="draw.io clip art (raster)", custom="fill", raster=True,
    license="Apache-2.0 (repository); no separate notice for clip_art, provenance unverified",
    author="JGraph", url="https://github.com/jgraph/drawio",
    files={"router": "Wireless_Router", "mesh_ap": "Repeater", "cloud": "Cloud", "nas": "Harddrive",
           "laptop": "MacBook", "tower": "Monitor_Tower", "phone": "iPhone", "tablet": "iPad",
           "g5": "Signal_tower_on", "server": "Server", "switch": "Switch"},
    source_dir="networking|computers|telecommunication",
)
