# Home network: addressing and names

I do not publish addresses, so this page is the plan without the numbers. It covers how things get an address, how they find each other, and how I reach them.

## Address plan

| Segment | Purpose | Subnet | Addressing |
|---|---|---|---|
| Main LAN | Every wired and wireless device | One private /24, the gateway's stock range | DHCP from the gateway. The NAS has a static address. |
| Tailscale overlay | Encrypted links between my machines | Tailscale's own shared address space | Assigned by Tailscale, stable per machine |
| IPv6 | Present on the LAN | Delegated by the cellular provider | Automatic. I do not publish prefixes. |

There is only one row of real LAN planning because there is only one LAN. Compare that with a design that has a management VLAN, a services VLAN and a guest VLAN: I have none of those, and the table above is the whole plan.

## Who gets what

| Device group | How it gets an address | Why |
|---|---|---|
| Gateway | Fixed, first address in the range | It is the router |
| NAS | Static, set in its own settings | Everything points DNS at it |
| Macs and omarchy | DHCP | They hold two or three live addresses at once (wired, Wi-Fi, sometimes a third adapter), so a single fixed address would be both fragile and arbitrary |
| Wi-Fi clients and smart-home devices | DHCP | Nothing depends on where they land |

## Names

I reach each machine three ways, in this order:

1. **A multicast DNS name on the LAN.** My SSH setup tries this first with a one-second probe. Because each Mac can hold two or three addresses, a name that follows whichever one is up beats a hardcoded address.
2. **The Tailscale address,** when the LAN probe fails, for example when I am away.
3. **The Tailscale DNS name.** I leave this off on the Macs. Tailscale's DNS setting is switched off so a Tailscale problem cannot take down ordinary lookups.

All three paths share one recorded host key per machine, so reaching a machine by a different route never produces a duplicate entry or a false "host key changed" warning.

## DNS

The NAS runs a DNS filter for the network (AdGuard Home). A small per-user LaunchAgent on each Mac chooses between three tiers and probes each one for a real answer before using it: the NAS directly when the Mac is at home, the NAS over Tailscale when it is away, and public resolvers if neither answers. Because it probes first, a Mac at home with the NAS switched off should fall through to the public resolvers. I have not tested that.

## Two honest caveats

- **The LAN-first probe has a gap.** The probe can succeed and the real connection can then fail to resolve the same name. I saw one such error on 2026-11-03 and could not reproduce it in 68 further tries. If it recurs often, a fallback that tries the Tailscale address when the name fails would close the gap.
- **omarchy's name is less stable than the Macs'.** After a reboot in October its multicast name came back with a numbered suffix because a stale record was still on the network. The Macs' LAN-first step silently stopped matching while SSH kept working over Tailscale. A DHCP reservation would be more dependable than relying on the name.
