# NexGuard Enterprise Troubleshooting Log

Standardized ITIL-compliant Incident and Root Cause Analysis (RCA) records for the NexGuard enterprise network topology.

| Incident ID | Target Asset | Dept / VLAN | Symptom | Diagnostic Commands | Root Cause Analysis (RCA) | Corrective Action | MTTR | Status |
|:---:|:---|:---|:---|:---|:---|:---|:---:|:---:|
| **INC-101** | `HR-PC-02` | HR (VLAN 10) | Host receives IP in wrong subnet `192.168.40.15` | `ipconfig /all`, `show vlan brief` | Switchport Fa0/2 mistakenly tagged to VLAN 40 | Reassigned Fa0/2 to `switchport access vlan 10` | 8 min | **RESOLVED** |
| **INC-102** | `Fin-Switch-01` | Finance (VLAN 20) | Cannot access DC Database server `192.168.50.20` | `show interfaces trunk` | Trunk uplink allowed-vlan list omitted VLAN 20 | Added `switchport trunk allowed vlan add 20` | 12 min | **RESOLVED** |
| **INC-103** | `Core-Router-01` | Support (VLAN 40) | Gateway ping timeout from all support hosts | `show ip interface brief` | Sub-interface `Gi0/0.40` protocol down due to missing 802.1Q tag | Configured `encapsulation dot1Q 40` and `no shutdown` | 15 min | **RESOLVED** |
| **INC-104** | `IT-Admin-Host` | IT (VLAN 30) | Host falls back to APIPA `169.254.x.x` | `show ip dhcp binding` | Core router missing `ip helper-address 192.168.50.5` on Gi0/0.30 | Configured DHCP relay helper address on sub-interface | 10 min | **RESOLVED** |
| **INC-105** | `Fin-FileServer` | Finance (VLAN 20) | High packet loss (25%) & slow transfer | `show interfaces Fa0/15` | Duplex mismatch: server Full Duplex, switchport Auto (Half) | Standardized switchport to `speed 100` and `duplex full` | 14 min | **RESOLVED** |
| **INC-106** | `Support-Host-01` | Support (VLAN 40) | Hostnames fail to resolve (`NXDOMAIN`) | `nslookup`, `show ip dhcp pool` | DHCP pool pushing public DNS `8.8.8.8` ahead of DC DNS `192.168.50.5` | Reordered DNS entries in router DHCP pool definition | 7 min | **RESOLVED** |
| **INC-107** | `HR-Switch-01` | HR (VLAN 10) | Port goes down instantly when hub connected | `show interfaces status err-disabled` | Spanning Tree BPDU Guard tripped by unauthorized bridge | Removed unauthorized hub; bounced port (`shut` / `no shut`) | 5 min | **RESOLVED** |
| **INC-108** | `Dist-Switch-01` | Campus Backbone | 99% CPU load, network-wide broadcast storm | `show spanning-tree detail`, Wireshark | Loop created between two access ports without STP protection | Removed loop cable, enabled global BPDU Guard and Loopguard | 18 min | **RESOLVED** |

---

### Key Takeaways for Technical Support Specialists:
1. **Always verify Layer 1 and 2 before Layer 3**: Check cable, interface status (`show ip int brief`), and VLAN allocation (`show vlan brief`) before debugging IP routing.
2. **Trunking hygiene**: Always use the `add` keyword when modifying allowed VLAN lists on trunks (`switchport trunk allowed vlan add <id>`) to avoid overwriting existing allowed VLANs.
3. **Cisco IOS vs. NX-OS**: In NX-OS, remember that features must be explicitly activated (`feature vpc`, `feature lacp`) and interfaces belong to VRF management by default for out-of-band control.
