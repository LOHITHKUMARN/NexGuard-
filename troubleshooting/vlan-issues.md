# NexGuard Troubleshooting: VLAN & Trunking Issues

## Scenario 1: Access Port Assigned to Incorrect VLAN

### Problem Overview
A newly deployed workstation in the Human Resources department (`HR-PC-02`, intended for VLAN 10) is unable to communicate with other HR peers or reach the enterprise server farm (`192.168.50.10`).

### Symptoms
- Workstation reports "No Internet / Unidentified Network".
- Unable to ping the default gateway `192.168.10.1`.
- IP configuration reveals either an APIPA address (`169.254.x.x`) or an IP from an unrelated subnet (`192.168.40.15`).

### Diagnostic Investigation (Step-by-Step)
1. **Verify Client IP Configuration**:
   ```cmd
   C:\> ipconfig /all
   IPv4 Address: 192.168.40.15
   Subnet Mask:  255.255.255.0
   Default Gateway: 192.168.40.1
   ```
   *Finding: The client received an IP in the Customer Support subnet (VLAN 40) rather than HR (VLAN 10).*

2. **Inspect Switchport Assignment on Access Switch**:
   ```bash
   HR-Fin-Switch-01# show vlan brief

   VLAN Name                             Status    Ports
   ---- -------------------------------- --------- -------------------------------
   1    default                          active    Fa0/2 - Fa0/10
   10   HR                               active    Fa0/1
   20   Finance                          active    Fa0/11 - Fa0/20
   40   Customer_Support                 active    Fa0/2   <-- Port Fa0/2 in VLAN 40!
   ```

3. **Check Interface Running Configuration**:
   ```bash
   HR-Fin-Switch-01# show running-config interface FastEthernet 0/2
   Building configuration...
   interface FastEthernet0/2
    switchport mode access
    switchport access vlan 40
   end
   ```

### Root Cause Analysis (RCA)
During provisioning, switchport `FastEthernet 0/2` was erroneously assigned to VLAN 40 (`Customer_Support`) instead of VLAN 10 (`HR`). As a result, DHCP discover broadcasts were processed by the VLAN 40 scope, isolating the HR workstation from its departmental resources.

### Corrective Action
```bash
HR-Fin-Switch-01# configure terminal
HR-Fin-Switch-01(config)# interface FastEthernet 0/2
HR-Fin-Switch-01(config-if)# description HR-PC-02 Workstation
HR-Fin-Switch-01(config-if)# switchport access vlan 10
HR-Fin-Switch-01(config-if)# spanning-tree portfast
HR-Fin-Switch-01(config-if)# end
HR-Fin-Switch-01# copy running-config startup-config
```

### Verification & Closure
1. Force DHCP renewal on workstation:
   ```cmd
   C:\> ipconfig /release
   C:\> ipconfig /renew
   IPv4 Address: 192.168.10.15
   Default Gateway: 192.168.10.1
   ```
2. Ping default gateway:
   ```cmd
   C:\> ping 192.168.10.1
   Reply from 192.168.10.1: bytes=32 time=1ms TTL=255 (0% loss)
   ```
3. Verified ticket resolved.

---

## Scenario 2: Trunk Allowed-List Dropping Inter-Switch VLAN Traffic

### Problem Overview
Employees in the Finance department (VLAN 20) are unable to access the ERP Database server (`192.168.50.20`) in the Data Center, while HR (VLAN 10) users can access it without issue.

### Symptoms
- Workstation in Finance has correct IP `192.168.20.15` and can ping its local default gateway `192.168.20.1`.
- Cannot reach any hosts on VLAN 50 or other departments.

### Diagnostic Investigation
1. **Check Trunk Status on Campus Distribution Switch**:
   ```bash
   Dist-Switch-01# show interfaces trunk
   Port        Mode             Encapsulation  Status        Native vlan
   Gi0/2       on               802.1q         trunking      1

   Port        Vlans allowed on trunk
   Gi0/2       10,99            <-- VLAN 20 is MISSING from allowed list!
   ```

### Root Cause Analysis (RCA)
An engineer updated the trunk allowed list using `switchport trunk allowed vlan 10,99` rather than using the `add` keyword, inadvertently pruning VLAN 20 traffic from the distribution uplink.

### Corrective Action
```bash
Dist-Switch-01# configure terminal
Dist-Switch-01(config)# interface GigabitEthernet 0/2
Dist-Switch-01(config-if)# switchport trunk allowed vlan add 20
Dist-Switch-01(config-if)# end
Dist-Switch-01# copy running-config startup-config
```

### Verification
```bash
Dist-Switch-01# show interfaces trunk | include Gi0/2
Gi0/2       10,20,99
```
Ping from Finance Workstation to Database server `192.168.50.20`: 0% packet loss.
