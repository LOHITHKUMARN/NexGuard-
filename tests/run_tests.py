import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.ping_service import PingService
from backend.services.ssh_service import SSHService
from backend.app import create_app

class TestNexGuardBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def test_01_ping_simulation_online(self):
        res = PingService.ping("192.168.10.1")
        self.assertEqual(res["status"], "ONLINE")
        self.assertIsNotNone(res["latency_ms"])
        self.assertEqual(res["packet_loss_pct"], 0.0)

    def test_02_ping_simulation_offline(self):
        res = PingService.ping("192.168.40.10")
        self.assertEqual(res["status"], "OFFLINE")
        self.assertIsNone(res["latency_ms"])
        self.assertEqual(res["packet_loss_pct"], 100.0)

    def test_03_ping_simulation_degraded(self):
        res = PingService.ping("192.168.50.20")
        self.assertIn(res["status"], ["ONLINE", "DEGRADED"])
        self.assertIsNotNone(res["latency_ms"])

    def test_04_cisco_ios_ssh_simulation(self):
        res = SSHService.execute_command("192.168.10.2", "show ip interface brief", device_type="cisco_ios", force_mock=True)
        self.assertTrue(res["success"])
        self.assertIn("GigabitEthernet0/0", res["output"])

    def test_05_cisco_nexus_ssh_simulation(self):
        res = SSHService.execute_command("192.168.50.2", "show version", device_type="cisco_nxos", force_mock=True)
        self.assertTrue(res["success"])
        self.assertTrue("Nexus" in res["output"] or "NX-OS" in res["output"])

    def test_06_cisco_nexus_vpc(self):
        res = SSHService.execute_command("192.168.50.2", "show vpc", device_type="cisco_nxos", force_mock=True)
        self.assertTrue(res["success"])
        self.assertIn("vPC domain", res["output"])

    def test_07_api_status(self):
        res = self.client.get("/api/monitoring/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_devices", data)
        self.assertIn("online_devices", data)

    def test_08_api_devices(self):
        res = self.client.get("/api/devices")
        self.assertEqual(res.status_code, 200)
        devices = res.get_json()
        self.assertGreater(len(devices), 0)

    def test_09_api_incidents(self):
        res = self.client.get("/api/incidents")
        self.assertEqual(res.status_code, 200)
        incidents = res.get_json()
        self.assertGreater(len(incidents), 0)

    def test_10_api_reports(self):
        res = self.client.get("/api/reports/summary")
        self.assertEqual(res.status_code, 200)
        report = res.get_json()
        self.assertIn("overall_sla_uptime_pct", report)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNexGuardBackend)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
