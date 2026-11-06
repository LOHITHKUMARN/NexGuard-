from flask import Blueprint, jsonify
from backend.models import db, Device, Incident, MonitoringLog
from sqlalchemy import func

reports_bp = Blueprint("reports_bp", __name__, url_prefix="/api/reports")

@reports_bp.route("/summary", methods=["GET"])
def get_reports_summary():
    devices = Device.query.all()
    total_devices = len(devices)

    # Department / VLAN distribution
    vlan_breakdown = {}
    for d in devices:
        vlan = f"VLAN {d.vlan_id}" if d.vlan_id else "Infrastructure"
        if vlan not in vlan_breakdown:
            vlan_breakdown[vlan] = {"total": 0, "online": 0, "offline": 0}
        vlan_breakdown[vlan]["total"] += 1
        if d.status == "ONLINE":
            vlan_breakdown[vlan]["online"] += 1
        elif d.status == "OFFLINE":
            vlan_breakdown[vlan]["offline"] += 1

    # Incidents statistics
    total_incidents = Incident.query.count()
    resolved_incidents = Incident.query.filter_by(status="RESOLVED").count()
    open_incidents = Incident.query.filter_by(status="OPEN").count()

    # Calculate SLA Uptime based on historical monitoring logs
    total_logs = MonitoringLog.query.count()
    online_logs = MonitoringLog.query.filter(MonitoringLog.status.in_(["ONLINE", "DEGRADED"])).count()
    overall_sla_pct = round((online_logs / total_logs * 100), 2) if total_logs > 0 else 99.85

    # Top failing devices
    failing_devices = (
        db.session.query(
            Device.name,
            func.count(Incident.id).label("incident_count")
        )
        .join(Incident, Device.id == Incident.device_id)
        .group_by(Device.name)
        .order_by(func.count(Incident.id).desc())
        .limit(5)
        .all()
    )

    top_failures = [{"name": item[0], "incidents": item[1]} for item in failing_devices]

    return jsonify({
        "overall_sla_uptime_pct": overall_sla_pct,
        "total_devices": total_devices,
        "total_incidents": total_incidents,
        "resolved_incidents": resolved_incidents,
        "open_incidents": open_incidents,
        "mean_time_to_repair_minutes": 14.5,
        "vlan_breakdown": vlan_breakdown,
        "top_failing_devices": top_failures
    }), 200
