# Home network: physical diagram

<figure class="pro-diagram"><a href="/assets/home-network/physical.svg"><img src="/assets/home-network/physical.svg" alt="Physical layout: a 5G gateway feeds the mesh root over 1 GbE, mesh nodes link wirelessly, and the workspace node uplinks to an 8-port 2.5G switch serving the NAS and MacBook Pro at 2.5G and the Mac mini and other adapters at 1G."></a><figcaption><em>The physical layout, drawn on 2026-11-14. Line color is the speed each link negotiated; dashed lines are wireless or a port I did not confirm.</em> Select the image to open it full size.</figcaption></figure>

## The links

| From | To | Medium | Speed | How I know |
|---|---|---|---|---|
| 5G gateway | Mesh root node | Ethernet | 1 GbE | Gateway LAN ports are gigabit; read 2026-11-01 |
| Mesh root | Workspace node | Wireless backhaul | Not measured | about 8 ms from the workspace, measured 2026-11-14 |
| Mesh root | Far node | Wireless backhaul | Not measured | not measured from the workspace, measured 2026-11-14 |
| Workspace node | Switch | Ethernet, 2.5G-capable port | Not measured | Port speed not read |
| Switch | NAS | Ethernet | 2.5 Gbps | Read from the NAS itself on 2026-11-14 |
| Switch | MacBook Pro (USB-C dock) | Ethernet | 2.5 Gbps | Read from the Mac on 2026-11-14 |
| Switch | Mac mini | Ethernet | 1 Gbps | Read from the Mac on 2026-11-14; its NIC is gigabit |
| MacBook Neo | Ethernet adapter | Ethernet | 1 Gbps | Read from the Mac on 2026-11-14; I did not confirm which port it uses |
| MacBook Pro | KVM's LAN adapter | Ethernet | 1 Gbps | Read from the Mac on 2026-11-14; port not confirmed |
| Switch | omarchy | Ethernet | not measured | Read from the machine on 2026-11-14 |

## What I measured, and what I did not

On 2026-11-03 I pulled 500 MB from the NAS to the MacBook Neo, twice, and got 107 to 110 MB/s. That is the ceiling of the Neo's gigabit adapter, not the NAS. It does tell me the NAS is no longer the bottleneck, and it does not show the 2.5G path running at full speed.

On 2026-11-01, before the switch, omarchy moved 600 MB to the NAS at 2.34 Gbit/s (94 percent of 2.5G) and the MacBook Pro managed 1.92 Gbit/s, limited by its USB 2.5G dock. I have not repeated that 2.5G test since the switch went in.

## Rooms

I describe the layout by role, not by room name. The workspace is the one room with every wired machine in it. The gateway is in a different room, one wireless hop away, and the far node is a second hop beyond that. That is why latency from the workspace is not measured to its own node, about 8 ms to the root and not measured to the far node.
