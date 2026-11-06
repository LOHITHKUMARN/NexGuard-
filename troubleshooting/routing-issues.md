# NexGuard Troubleshooting: Routing & DHCP Relay Issues

## Scenario 3: Inter-VLAN Sub-Interface Missing 802.1Q Tag

### Problem Overview
Users in Customer Support (VLAN 40) report a total network blackout. They cannot ping external websites or reach the centralized servers in VLAN 50.

### Symptoms
- Workstations have static IP `192.168.40.10/24`.
- Pinging gateway `192.168.40.1` yields `Request timed out`.

### Diagnostic Commands & Analysis
1. **Inspect Sub-Interfaces on Core Router**:
   ```bash
   Core-Router-01# show ip interface brief | include GigabitEthernet0/0
   GigabitEthernet0/0     unassigned      YES unset  up                    up
   GigabitEthernet0/0.10  192.168.10.1    YES manual up                    up
   GigabitEthernet0/0.20  192.168.20.1    YES manual up                    up
   GigabitEthernet0/0.30  192.168.30.1    YES manual up                    up
   GigabitEthernet0/0.40  192.168.40.1    YES manual up                    down   <-- Line protocol down!
   GigabitEthernet0/0.50  192.168.50.1    YES manual up                    up
   ```

2. **Inspect Sub-Interface Configuration**:
   ```bash
   Core-Router-01# show running-config interface GigabitEthernet0/0.40
   Building configuration...
   interface GigabitEthernet0/0.40
    description Customer Support Gateway
    ip address 192.168.40.1 255.255.255.0
   end
   ```
   *Notice: The `encapsulation dot1Q 40` command is missing! Without encapsulation, Cisco IOS cannot map incoming tagged 802.1Q frames to this Layer 3 sub-interface.*

### Root Cause Analysis (RCA)
The sub-interface was created and assigned an IP address without defining the 802.1Q encapsulation tag. Cisco IOS requires the encapsulation command to be entered before routing tagged frames; without it, line protocol remains down.

### Corrective Action
```bash
Core-Router-01# configure terminal
Core-Router-01(config)# interface GigabitEthernet0/0.40
Core-Router-01(config-subif)# encapsulation dot1Q 40
Core-Router-01(config-subif)# ip address 192.168.40.1 255.255.255.0
Core-Router-01(config-subif)# no shutdown
Core-Router-01(config-subif)# end
Core-Router-01# copy running-config startup-config
```

### Verification
```bash
Core-Router-01# show ip interface brief | include 0/0.40
GigabitEthernet0/0.40  192.168.40.1    YES manual up                    up
```
Workstations in VLAN 40 immediately resume successful pings to `192.168.40.1` and `192.168.50.10`.

---

## Scenario 4: DHCP Relay Agent Failure (`ip helper-address`)

### Problem Overview
Workstations in VLAN 30 (IT Support) are failing to obtain dynamic IP addresses from the central DHCP server located at `192.168.50.5` in the Data Center.

### Symptoms
- Workstations fall back to Microsoft APIPA addresses (`169.254.120.45`).
- Static IP assignment works properly, indicating Layer 2 connectivity is sound.

### Diagnostic Steps
1. **Analyze DHCP Broadcast Forwarding**:
   - Workstation broadcasts a `DHCPDISCOVER` packet (`255.255.255.255`).
   - Routers by default drop broadcast packets unless configured to forward them as unicast UDP to a designated server.
2. **Inspect Core Gateway Sub-Interface**:
   ```bash
   Core-Router-01# show running-config interface GigabitEthernet 0/0.30
   interface GigabitEthernet0/0.30
    encapsulation dot1Q 30
    ip address 192.168.30.1 255.255.255.0
    ! Missing ip helper-address!
   end
   ```

### Corrective Action
```bash
Core-Router-01# configure terminal
Core-Router-01(config)# interface GigabitEthernet 0/0.30
Core-Router-01(config-subif)# ip helper-address 192.168.50.5
Core-Router-01(config-subif)# end
```

### Verification
Run `ipconfig /renew` on the IT workstation:
Client receives `192.168.30.12`, Default Gateway: `192.168.30.1`, DNS Server: `192.168.50.5`.
