import pytest
from backend.app import create_app
from backend.models import db, Device

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_monitoring_status_endpoint(client):
    res = client.get("/api/monitoring/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "total_devices" in data
    assert "online_devices" in data
    assert "active_incidents" in data

def test_devices_list_endpoint(client):
    res = client.get("/api/devices")
    assert res.status_code == 200
    devices = res.get_json()
    assert len(devices) > 0
    assert any(d["name"] == "Core-Router-01" for d in devices)

def test_incidents_endpoint(client):
    res = client.get("/api/incidents")
    assert res.status_code == 200
    incidents = res.get_json()
    assert len(incidents) > 0

def test_reports_summary_endpoint(client):
    res = client.get("/api/reports/summary")
    assert res.status_code == 200
    report = res.get_json()
    assert "overall_sla_uptime_pct" in report
    assert "vlan_breakdown" in report
