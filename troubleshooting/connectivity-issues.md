# NexGuard Troubleshooting: Physical Layer & Connectivity Issues

## Scenario 5: Duplex & Speed Auto-Negotiation Mismatch

### Problem
Users connecting to the Finance File Server report abysmal file transfer speeds (less than 100 KB/s) and frequent session timeouts.

### Diagnostics & Symptoms
1. **Ping Test Result**:
   - Round-trip ping shows 25% packet drop and erratic latency (varying from 1ms to 240ms).
2. **Switchport Statistics**:
   ```bash
   HR-Fin-Switch-01# show interfaces FastEthernet 0/15
   FastEthernet0/15 is up, line protocol is up (connected)
     Hardware is Fast Ethernet, address is 0019.e845.820f
     Full-duplex, 100Mb/s, media type is 100BaseTX
     Input flow-control is unsupported, output flow-control is unsupported
     523821 packets input, 41298492 bytes, 0 no buffer
     Received 2124 broadcasts (0 multicasts)
     0 runts, 0 giants, 0 throttles
     8429 input errors, 8102 CRC, 0 frame, 0 overrun, 0 ignored
     14920 late collisions, 4390 deferred   <-- High late collisions & CRC errors!
   ```

### Root Cause Analysis (RCA)
The server interface was manually hardcoded to **100 Mbps / Full Duplex**, while the switchport was left at the default **Auto/Auto**. When an auto-negotiating port fails to detect partner parameters, IEEE 802.3 standards dictate falling back to Half Duplex at 100 Mbps. The resulting duplex mismatch causes collisions whenever both sides transmit simultaneously.

### Corrective Action
Align both endpoints to either standard auto-negotiation or explicitly configure full duplex:
```bash
HR-Fin-Switch-01# configure terminal
HR-Fin-Switch-01(config)# interface FastEthernet 0/15
HR-Fin-Switch-01(config-if)# speed 100
HR-Fin-Switch-01(config-if)# duplex full
HR-Fin-Switch-01(config-if)# end
```

### Verification
Clear interface counters and monitor:
```bash
HR-Fin-Switch-01# clear counters FastEthernet 0/15
HR-Fin-Switch-01# show interfaces FastEthernet 0/15 | include collision
     0 collisions, 0 late collisions
```
Packet loss drops to 0%, file transfer speed restored to wire speed (12 MB/s).

---

## Scenario 6: Internal DNS Server Resolution Failure

### Problem
Customer support agents can open internal web tools by raw IP address (`http://192.168.50.10:8080`), but entering the hostname `http://crm.nexguard.enterprise.local` results in `DNS_PROBE_FINISHED_NXDOMAIN`.

### Diagnostics
```cmd
C:\> nslookup crm.nexguard.enterprise.local
*** DNS request timed out.
    timeout was 2 seconds.
Server:  UnKnown
Address:  8.8.8.8
```
*Notice: The client is querying public Google DNS `8.8.8.8` instead of internal DC DNS server `192.168.50.5`!*

### Root Cause Analysis (RCA)
The DHCP scope `POOL_SUPPORT_VLAN40` on the Core Router had `dns-server 8.8.8.8` configured first, bypassing the internal enterprise DNS resolver which holds records for `nexguard.enterprise.local`.

### Corrective Action
```bash
Core-Router-01# configure terminal
Core-Router-01(config)# ip dhcp pool POOL_SUPPORT_VLAN40
Core-Router-01(dhcp-config)# dns-server 192.168.50.5 8.8.8.8
Core-Router-01(dhcp-config)# end
```

---

## Scenario 7: Switchport Error-Disabled (BPDU Guard Triggered)

### Problem
Port `FastEthernet 0/5` abruptly went dark when an employee plugged in an unmanaged switch under their desk.

### Diagnostics
```bash
HR-Fin-Switch-01# show interfaces status err-disabled
Port      Name               Status       Reason               Err-disabled Vlans
Fa0/5     Workstation Desk   err-disabled bpduguard
```

### Root Cause Analysis (RCA)
`spanning-tree bpduguard enable` is active on all edge access ports. When the unmanaged switch sent BPDU packets, the switch protected the enterprise topology by immediately shutting down the port to prevent spanning-tree loops.

### Corrective Action
Remove unauthorized hardware, then reset the port:
```bash
HR-Fin-Switch-01# configure terminal
HR-Fin-Switch-01(config)# interface FastEthernet 0/5
HR-Fin-Switch-01(config-if)# shutdown
HR-Fin-Switch-01(config-if)# no shutdown
HR-Fin-Switch-01(config-if)# end
```

---

## Scenario 8: Broadcast Storm & STP Loop Detection

### Problem
Network CPU spikes to 99%, switch link lights flash in unison, and users across all VLANs lose responsiveness.

### Diagnostics
1. **Wireshark Packet Analysis**:
   - Capture shows thousands of duplicate ARP Broadcast packets (`Who has 192.168.10.1? Tell 192.168.10.10`) per second with decreasing TTL.
2. **Switch Diagnostic**:
   ```bash
   Dist-Switch-01# show spanning-tree detail | include changes
     Number of topology changes 1894 last occurred 00:00:03 ago
   ```

### Root Cause Analysis (RCA)
A looped patch cable connected two access ports together without PortFast BPDU protection, causing an infinite Layer 2 broadcast amplification storm.

### Corrective Action
1. Identify flapping MAC address:
   ```bash
   Dist-Switch-01# show mac address-table notification
   ```
2. Unplug the redundant loop cable.
3. Enable `spanning-tree loopguard default` and `spanning-tree portfast bpduguard default` across all access switches.
