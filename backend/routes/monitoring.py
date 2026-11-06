from flask import Blueprint, jsonify, request, current_app
from backend.models import db, Device, Incident, MonitoringLog
from backend.services.device_monitor import DeviceMonitor
from backend.services.network_scanner import NetworkScanner

monitoring_bp = Blueprint("monitoring_bp", __name__, url_prefix="/api/monitoring")

@monitoring_bp.route("/status", methods=["GET"])
def get_monitoring_status():
    devices = Device.query.all()
    total = len(devices)
    online = sum(1 for d in devices if d.status == "ONLINE")
    offline = sum(1 for d in devices if d.status == "OFFLINE")
    degraded = sum(1 for d in devices if d.status == "DEGRADED")
    unknown = sum(1 for d in devices if d.status == "UNKNOWN")

    active_incidents = Incident.query.filter(Incident.status.in_(["OPEN", "ACKNOWLEDGED"])).count()
    
    online_latencies = [d.latency_ms for d in devices if d.latency_ms is not None and d.status in ["ONLINE", "DEGRADED"]]
    avg_latency = round(sum(online_latencies) / len(online_latencies), 2) if online_latencies else 0.0

    return jsonify({
        "total_devices": total,
        "online_devices": online,
        "offline_devices": offline,
        "degraded_devices": degraded,
        "unknown_devices": unknown,
        "active_incidents": active_incidents,
        "average_latency_ms": avg_latency,
        "network_health_pct": round((online / total * 100), 1) if total > 0 else 100.0
    }), 200

@monitoring_bp.route("/telemetry", methods=["GET"])
def get_telemetry():
    """Returns recent log trends across devices for live Chart.js rendering."""
    devices = Device.query.all()
    labels = [d.name for d in devices]
    latencies = [d.latency_ms if d.latency_ms is not None else 0 for d in devices]
    packet_losses = [d.packet_loss_pct for d in devices]
    statuses = [d.status for d in devices]

    return jsonify({
        "labels": labels,
        "latencies": latencies,
        "packet_losses": packet_losses,
        "statuses": statuses
    }), 200

@monitoring_bp.route("/poll-now", methods=["POST"])
def poll_all_now():
    DeviceMonitor.check_all(current_app._get_current_object())
    return jsonify({"message": "Poll cycle completed across all devices"}), 200

@monitoring_bp.route("/scan", methods=["POST"])
def scan_network():
    data = request.get_json() or {}
    cidr = data.get("cidr", "192.168.10.0/28")
    result = NetworkScanner.scan_subnet(cidr)
    return jsonify(result), 200
