from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from backend.models import db, Device, MonitoringLog
from backend.services.ping_service import PingService
from backend.services.ssh_service import SSHService

devices_bp = Blueprint("devices_bp", __name__, url_prefix="/api/devices")

@devices_bp.route("", methods=["GET"])
def get_devices():
    vlan_filter = request.args.get("vlan", type=int)
    status_filter = request.args.get("status")

    query = Device.query
    if vlan_filter is not None:
        query = query.filter_by(vlan_id=vlan_filter)
    if status_filter:
        query = query.filter_by(status=status_filter.upper())

    devices = query.order_by(Device.id.asc()).all()
    return jsonify([d.to_dict() for d in devices]), 200

@devices_bp.route("", methods=["POST"])
def create_device():
    data = request.get_json() or {}
    name = data.get("name")
    ip = data.get("ip_address")
    device_type = data.get("device_type", "Switch")
    vendor = data.get("vendor", "Cisco")
    location = data.get("location", "Enterprise HQ")
    vlan_id = data.get("vlan_id")

    if not name or not ip:
        return jsonify({"error": "Name and IP address are required"}), 400

    existing = Device.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": f"Device '{name}' already exists"}), 409

    device = Device(
        name=name,
        ip_address=ip,
        device_type=device_type,
        vendor=vendor,
        location=location,
        vlan_id=vlan_id
    )
    db.session.add(device)
    db.session.commit()

    # Immediate initial ping
    res = PingService.ping(device.ip_address)
    device.status = res["status"]
    device.latency_ms = res["latency_ms"]
    device.packet_loss_pct = res["packet_loss_pct"]
    device.last_checked = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify(device.to_dict()), 201

@devices_bp.route("/<int:device_id>", methods=["GET"])
def get_device(device_id):
    device = Device.query.get_or_404(device_id)
    recent_logs = MonitoringLog.query.filter_by(device_id=device.id).order_by(MonitoringLog.timestamp.desc()).limit(20).all()
    data = device.to_dict()
    data["recent_logs"] = [log.to_dict() for log in recent_logs]
    return jsonify(data), 200

@devices_bp.route("/<int:device_id>", methods=["PUT"])
def update_device(device_id):
    device = Device.query.get_or_404(device_id)
    data = request.get_json() or {}

    device.name = data.get("name", device.name)
    device.ip_address = data.get("ip_address", device.ip_address)
    device.device_type = data.get("device_type", device.device_type)
    device.vendor = data.get("vendor", device.vendor)
    device.location = data.get("location", device.location)
    device.vlan_id = data.get("vlan_id", device.vlan_id)

    db.session.commit()
    return jsonify(device.to_dict()), 200

@devices_bp.route("/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    return jsonify({"message": f"Device {device.name} deleted successfully"}), 200

@devices_bp.route("/<int:device_id>/ping", methods=["POST"])
def ping_device(device_id):
    device = Device.query.get_or_404(device_id)
    res = PingService.ping(device.ip_address)
    
    device.status = res["status"]
    device.latency_ms = res["latency_ms"]
    device.packet_loss_pct = res["packet_loss_pct"]
    device.last_checked = datetime.now(timezone.utc)

    log = MonitoringLog(
        device_id=device.id,
        status=device.status,
        latency_ms=device.latency_ms,
        packet_loss_pct=device.packet_loss_pct
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "device": device.to_dict(),
        "ping_result": res
    }), 200

@devices_bp.route("/<int:device_id>/ssh", methods=["POST"])
def run_ssh_command(device_id):
    device = Device.query.get_or_404(device_id)
    data = request.get_json() or {}
    command = data.get("command", "show ip interface brief")
    
    # Check if user requests simulated or live
    force_mock = data.get("force_mock", False)

    result = SSHService.execute_command(
        ip_address=device.ip_address,
        command=command,
        device_type=device.device_type,
        force_mock=force_mock
    )
    return jsonify(result), 200
