import pytest
from backend.services.ping_service import PingService

def test_ping_simulation_online():
    res = PingService.ping("192.168.10.1")
    assert res["status"] == "ONLINE"
    assert res["latency_ms"] is not None
    assert res["latency_ms"] > 0
    assert res["packet_loss_pct"] == 0.0

def test_ping_simulation_offline():
    res = PingService.ping("192.168.40.10")
    assert res["status"] == "OFFLINE"
    assert res["latency_ms"] is None
    assert res["packet_loss_pct"] == 100.0

def test_ping_simulation_degraded():
    res = PingService.ping("192.168.50.20")
    assert res["status"] in ["ONLINE", "DEGRADED"]
    assert res["latency_ms"] is not None
