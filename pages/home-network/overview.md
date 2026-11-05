# Home network: overview

This is the network in my house, drawn the way I wish other people had documented theirs. It is one flat private network behind a 5G gateway, with three Wi-Fi mesh nodes, a small 2.5G switch where my computers sit, and a NAS that does more work than anything else on it. I last checked the details on 2026-11-05. A script reads the machines every night, so the speeds, statuses and counts on this page update themselves. Anything marked as not measured was not read.

I left out addresses, MAC addresses, serial numbers, hostnames and account names on purpose. The relationships are the point.

## The short version

- **One network.** Every device shares a single private /24 with the gateway. I do not run VLANs.
- **The internet is cellular.** A T-Mobile 5G home-internet gateway is the router. Its LAN ports are gigabit, so the internet side tops out near 1 Gbit/s, and its MTU is 1420.
- **Wi-Fi is three TP-Link Deco BE63 nodes** in access-point mode, linked to each other wirelessly in a chain.
- **The wired computers sit behind a TP-Link TL-SG108S-M2**, an 8-port 2.5G unmanaged switch I installed on 2026-11-03. It plugs into the Deco in my workspace.
- **The NAS is the busiest machine.** A UGREEN DXP2800 serves files, takes backups, filters DNS for the whole LAN, runs a media server and carries Tailscale.
- **Tailscale sits on top.** It lets the Macs, the NAS and the phones reach each other from anywhere.

## Where to go next

| Page | What it answers |
|---|---|
| [Logical diagram](home-network/logical-diagram.md) | What the groups are and how traffic flows between them |
| [Physical diagram](home-network/physical-diagram.md) | Which cable or radio links what, and at what speed |
| [Addressing and names](home-network/addressing-and-names.md) | How devices get addresses and how I reach them |
| [Relationships and failures](home-network/relationships-and-failures.md) | Who depends on whom, and what breaks when a piece fails |
| [The switch and the 100 Mb/s NAS](home-network/lessons-2026-11-03.md) | What went wrong on install day and what I measured |

## Everything on the network

| Device | What it does | How it connects | Relationship |
|---|---|---|---|
| 5G home-internet gateway (T-Mobile TMO-G4SE) | Router, NAT and DHCP. The only way out to the internet. | Cellular on the WAN side; two 1 GbE LAN ports | Everything depends on it. It plugs into the mesh root node. |
| Deco BE63, root node | Mesh root, in the gateway room | 1 GbE to the gateway; wireless to the next node | Carries all traffic between the mesh and the gateway |
| Deco BE63, workspace node | Wired anchor for the workspace | Wireless backhaul to the root; wired uplink to the switch | One wireless hop from the gateway |
| Deco BE63, far node | Wi-Fi coverage for the far end of the house | Wireless backhaul only | Two wireless hops from the workspace |
| TP-Link TL-SG108S-M2 | 8-port 2.5G unmanaged switch with loop prevention switched on | Uplink to the workspace node | Joins the NAS, the Mac mini and the MacBook Pro dock |
| UGREEN DXP2800 NAS | Files, Time Machine backups, DNS filtering, media server, Tailscale container. Intel N100, 8 GB, one 2.5GbE port. | 2.5G through the switch; static address | The Macs lean on it for files, backups and DNS when at home |
| Mac mini M4 | Always-on host for scheduled jobs and builds | Built-in NIC at 1G through the switch; Wi-Fi also on | Uses the NAS for DNS and backups |
| MacBook Pro M4 Max | My main machine | USB-C dock at 2.5G through the switch; Wi-Fi also on; a third 1G adapter on the KVM | Same dependencies as the mini |
| MacBook Neo | Second laptop | USB Ethernet adapter at 1G, plus Wi-Fi | Same dependencies as the mini |
| omarchy | Linux workstation | unknown-speed NIC and Wi-Fi. Online. | Reaches the rest over the LAN or Tailscale |
| TESmart KVM | Shares one keyboard and display between computers | The MacBook Pro sees a 1G USB LAN adapter through it | Needs no network to do its main job |
| Tailscale overlay | Encrypted peer-to-peer links between the Macs, the NAS, omarchy, an iPhone and an iPad | Runs over the LAN or the internet | Direct on the LAN, relayed when I am away |
| Automation VM | A sandboxed VM outside the house that joins the overlay | Outbound only | My access rules let it dial out and let nothing dial in |
| Smart-home devices, TVs, AV receivers, voice assistants, other appliances | Wi-Fi clients | Whichever Deco is closest | Need the gateway for addresses and the internet, the NAS for DNS |
| Phones and tablets | Wi-Fi clients, many with randomised hardware addresses | Whichever Deco is closest | Same as above |

## What I have not identified

The nightly sweep of the LAN on 2026-11-05 saw 36 devices and could not name eight of them. Some give only a generic hostname. I would rather list that gap here than guess. Wi-Fi clients that use randomised hardware addresses and sleep a lot are also easy to miss in a sweep, so treat the client list as a floor.

I also did not record which switch port each device uses. The switch is unmanaged, so the ports only show in the lights on its front.

## Credits

The device icons in the diagrams are Material Design Icons (Apache-2.0) and Simple Icons (CC0). I drew the network switch and Mac mini glyphs myself. Brand marks belong to their owners and appear only next to a text label. The full list is in `assets/home-network/icons/LICENSES.md` in the wiki repo.
