from backend.services.ssh_service import SSHService

def test_cisco_ios_ssh_simulation():
    res = SSHService.execute_command("192.168.10.2", "show ip interface brief", device_type="cisco_ios", force_mock=True)
    assert res["success"] is True
    assert "GigabitEthernet0/0" in res["output"]

def test_cisco_nexus_ssh_simulation():
    res = SSHService.execute_command("192.168.50.2", "show version", device_type="cisco_nxos", force_mock=True)
    assert res["success"] is True
    assert "Nexus" in res["output"] or "NX-OS" in res["output"]

def test_cisco_nexus_vpc_command():
    res = SSHService.execute_command("192.168.50.2", "show vpc", device_type="cisco_nxos", force_mock=True)
    assert res["success"] is True
    assert "vPC domain" in res["output"]
