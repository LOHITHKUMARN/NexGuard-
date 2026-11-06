from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from backend.models import db, Incident, Device

incidents_bp = Blueprint("incidents_bp", __name__, url_prefix="/api/incidents")

@incidents_bp.route("", methods=["GET"])
def get_incidents():
    status = request.args.get("status")
    severity = request.args.get("severity")

    query = Incident.query
    if status:
        query = query.filter_by(status=status.upper())
    if severity:
        query = query.filter_by(severity=severity.upper())

    incidents = query.order_by(Incident.created_at.desc()).all()
    return jsonify([inc.to_dict() for inc in incidents]), 200

@incidents_bp.route("", methods=["POST"])
def create_incident():
    data = request.get_json() or {}
    device_id = data.get("device_id")
    title = data.get("title")
    description = data.get("description")
    severity = data.get("severity", "WARNING").upper()
    root_cause = data.get("root_cause")
    remediation = data.get("remediation")

    if not device_id or not title:
        return jsonify({"error": "Device ID and title are required"}), 400

    incident = Incident(
        device_id=device_id,
        title=title,
        description=description,
        severity=severity,
        status="OPEN",
        root_cause=root_cause,
        remediation=remediation
    )
    db.session.add(incident)
    db.session.commit()
    return jsonify(incident.to_dict()), 201

@incidents_bp.route("/<int:incident_id>/status", methods=["PUT"])
def update_incident_status(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json() or {}
    new_status = data.get("status", "").upper()
    root_cause = data.get("root_cause")
    remediation = data.get("remediation")

    if new_status not in ["OPEN", "ACKNOWLEDGED", "RESOLVED"]:
        return jsonify({"error": "Status must be OPEN, ACKNOWLEDGED, or RESOLVED"}), 400

    incident.status = new_status
    if root_cause:
        incident.root_cause = root_cause
    if remediation:
        incident.remediation = remediation

    if new_status == "RESOLVED" and not incident.resolved_at:
        incident.resolved_at = datetime.now(timezone.utc)

    db.session.commit()
    return jsonify(incident.to_dict()), 200
