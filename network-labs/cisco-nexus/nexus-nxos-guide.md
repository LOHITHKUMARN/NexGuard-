# Cisco Nexus (NX-OS) Enterprise Switching & Troubleshooting Guide

## 1. Architectural Comparison: Cisco IOS vs. Cisco NX-OS

| Characteristic | Cisco IOS (Classic) | Cisco Nexus (NX-OS) |
|---|---|---|
| **Kernel Architecture** | Monolithic single-binary OS | Modular Linux microkernel with independent process restart |
| **Feature Management** | Everything active or controlled by license | Explicit feature enablement (`feature vpc`, `feature lacp`, `feature ospf`) |
| **Redundancy & STP** | Spanning Tree Protocol (blocks redundant links) | Virtual Port Channels (vPC) – active/active loop-free Layer 2 without STP port blocking |
| **Configuration Saving** | `write memory` or `copy run start` | `copy running-config startup-config` |
| **Management Plane** | Shared default routing table | Isolated VRF (`vrf member management`, `mgmt0` interface) |
| **Port Naming** | `GigabitEthernet0/1`, `FastEthernet0/1` | `Ethernet1/1`, `Ethernet1/2` |
| **Interface Mode** | Routed or switched depending on platform | Explicit `switchport` or `no switchport` on 10G/25G/100G interfaces |

---

## 2. Essential NX-OS Diagnostic Commands

### A. Feature Status Inspection
```bash
# Verify which modular features are currently running
DC-N9K-Switch01# show feature
Feature Name          Instance  State
--------------------  --------  --------
lacp                  1         enabled
vpc                   1         enabled
interface-vlan        1         enabled
sshServer             1         enabled
lldp                  1         enabled
```

### B. Interface Status and Error Diagnostics
```bash
# Compact view of all switchports, speeds, and reasons for down status
DC-N9K-Switch01# show interface brief

# Inspect physical optical transceiver details and transmit/receive optical power (dBm)
DC-N9K-Switch01# show interface Ethernet1/1 transceiver details

# Check error counters, CRC drops, and runts
DC-N9K-Switch01# show interface Ethernet1/1 counters errors
```

### C. Port-Channel and LACP Verification
```bash
# Verify bundle health and member ports
DC-N9K-Switch01# show port-channel summary
Flags:  D - Down        P - Up in port-channel (members)
        I - Individual  H - Hot-standby (LACP only)
Group Port-Type  Protocol  Member Ports
--------------------------------------------------------------------------------
1     Po1(SU)    LACP      Eth1/1(P)    Eth1/2(P)
```
*Troubleshooting Flag Tip:*
- `(SU)`: Layer 2 switchport is Up.
- `(SD)`: Switchport is Down — check physical cable or LACP timeout.
- `(I)`: Port is running individual (LACP negotiation failed).

### D. Virtual PortChannel (vPC) Health Check
```bash
# Check peer keepalive and consistency status
DC-N9K-Switch01# show vpc
vPC domain id                     : 10
Peer status                       : peer adjacency formed ok
vPC keep-alive status             : Peer is alive
Configuration consistency status  : success
vPC role                          : primary
Number of vPCs configured         : 1

# Check Type-1 vs Type-2 consistency parameters
DC-N9K-Switch01# show vpc consistency-parameters global
```

---

## 3. Data Center Failure Case Study: vPC Split-Brain Avoidance

### Symptom:
Secondary Nexus switch stops receiving heartbeat packets from primary peer switch over the management VRF.

### Root Cause Analysis (RCA):
If peer-keepalive fails while peer-link is still operational, the switches continue active forwarding. However, if peer-link fails while peer-keepalive is alive, the secondary switch disables all its vPC member ports to prevent loops and dual-active MAC flap.

### Verification Command:
```bash
DC-N9K-Switch01# show vpc role
vPC Role status
----------------------------------------------------
vPC role                        : secondary, operational secondary
Dual active detection status    : no dual-active detected
```
