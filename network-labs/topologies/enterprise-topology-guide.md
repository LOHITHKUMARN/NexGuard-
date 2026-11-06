# NexGuard Enterprise Topology & Implementation Guide

## 1. Network Topology Blueprint

The NexGuard simulated network model follows a hierarchical enterprise campus architecture:
- **Core / WAN Routing Layer**: Cisco 2911 / 4321 Integrated Services Router performing Router-on-a-Stick inter-VLAN routing and acting as DHCP server.
- **Distribution Layer**: Cisco Catalyst 3560 Layer 3 Switch managing 802.1Q trunk aggregation.
- **Access Layer**: Two Cisco Catalyst 2960 switches isolating client traffic per department.
- **Data Center Fabric**: Cisco Nexus 9300 series switch running NX-OS with LACP Port-Channels and high-throughput server links.

```
                         +--------------------------+
                         |      Core-Router-01      |
                         | (Cisco 2911 / 4321 ISR)  |
                         |     Sub-ifs: .10-.50     |
                         +------------+-------------+
                                      | Gi0/0 (802.1Q Trunk)
                                      |
                         +------------+-------------+
                         |      Dist-Switch-01      |
                         |  (Cisco Catalyst 3560)   |
                         +---+----------+--------+--+
                             |          |        |
           Gi0/2 (Trunk)     |          | Gi0/3  | Po1 (LACP Eth1/1-2)
     +-----------------------+          | (Trunk)|
     |                                  |        +-------------------+
+----+-------------------+   +----------+-------------+   +----------+-------------+
|    HR-Fin-Switch-01    |   |    IT-Supp-Switch-01   |   |     Nexus-DC-N9K       |
| (Cisco Catalyst 2960)  |   |  (Cisco Catalyst 2960) |   | (Cisco Nexus 9300)     |
+----+--------------+----+   +----+--------------+----+   +----+---------+---------+
     | Fa0/1        | Fa0/11      | Fa0/1        | Fa0/11      | Eth1/3  | Eth1/4  | Eth1/5
     |              |             |              |             |         |         |
[HR-PC-01]     [Fin-PC-01]    [IT-Admin]    [Supp-PC-01]   [Web-Svr]  [DB-Svr]  [DNS-DHCP]
  VLAN 10        VLAN 20        VLAN 30        VLAN 40       VLAN 50   VLAN 50   VLAN 50
```

---

## 2. Cabling & Port Allocation Matrix

| Origin Device | Origin Port | Destination Device | Destination Port | Cable Type | Mode / VLAN |
|---|---|---|---|---|---|
| Core-Router-01 | Gi0/0 | Dist-Switch-01 | Gi0/1 | Copper Straight-Through | 802.1Q Trunk (10-50) |
| Dist-Switch-01 | Gi0/2 | HR-Fin-Switch-01 | Gi0/24 | Copper Straight-Through | 802.1Q Trunk (10, 20) |
| Dist-Switch-01 | Gi0/3 | IT-Supp-Switch-01 | Gi0/24 | Copper Straight-Through | 802.1Q Trunk (30, 40) |
| Dist-Switch-01 | Gi0/4 | Nexus-DC-N9K | Eth1/1 | Fiber / Twinax | LACP Port-Channel 1 |
| Dist-Switch-01 | Gi0/5 | Nexus-DC-N9K | Eth1/2 | Fiber / Twinax | LACP Port-Channel 1 |
| HR-Fin-Switch-01 | Fa0/1 | HR-Workstation-01 | FastEthernet0 | Copper Straight-Through | Access VLAN 10 |
| HR-Fin-Switch-01 | Fa0/11 | Fin-Workstation-01 | FastEthernet0 | Copper Straight-Through | Access VLAN 20 |
| IT-Supp-Switch-01 | Fa0/1 | IT-Admin-Host | FastEthernet0 | Copper Straight-Through | Access VLAN 30 |
| IT-Supp-Switch-01 | Fa0/11 | Support-Host-01 | FastEthernet0 | Copper Straight-Through | Access VLAN 40 |
| Nexus-DC-N9K | Eth1/3 | DC-Web-Server | Eth0 | 10G SFP+ Direct Attach | Access VLAN 50 |
| Nexus-DC-N9K | Eth1/4 | DC-DB-Server | Eth0 | 10G SFP+ Direct Attach | Access VLAN 50 |
| Nexus-DC-N9K | Eth1/5 | DC-DNS-DHCP | Eth0 | 10G SFP+ Direct Attach | Access VLAN 50 |

---

## 3. Step-by-Step Packet Tracer Build Checklist

1. **Place Devices**:
   - 1x Router `2911`
   - 1x Multi-layer Switch `3560-24PS`
   - 2x Switches `2960-24TT`
   - 1x Switch `2960` or Server representing Data Center Nexus Fabric
   - 5x End Devices (PCs / Servers)
2. **Apply Configurations**:
   - Paste `network-labs/cisco-ios/core-router.cfg` into the router CLI.
   - Paste `network-labs/cisco-ios/dist-switch.cfg` into the 3560 switch CLI.
   - Paste `network-labs/cisco-ios/access-switches.cfg` into the two access switches.
3. **Verify DHCP Addressing**:
   - Set each PC's IP Configuration to **DHCP**.
   - Verify `HR-PC-01` receives `192.168.10.x/24` with default gateway `192.168.10.1`.
   - Verify `Fin-PC-01` receives `192.168.20.x/24` with default gateway `192.168.20.1`.
4. **Inter-VLAN Connectivity Test**:
   - Open Command Prompt on `HR-PC-01` and ping `192.168.20.10` (Finance PC).
   - Expected Result: 4/4 ICMP Echo replies received (`Reply from 192.168.20.10: bytes=32 time=2ms TTL=127`).
