from datetime import datetime, timezone
from backend.models import db

class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default="WARNING")  # CRITICAL, WARNING, INFO
    status = db.Column(db.String(20), default="OPEN")        # OPEN, ACKNOWLEDGED, RESOLVED
    root_cause = db.Column(db.Text, nullable=True)
    remediation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "device_name": self.device.name if self.device else "Unknown Device",
            "device_ip": self.device.ip_address if self.device else "Unknown IP",
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "root_cause": self.root_cause,
            "remediation": self.remediation,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "resolved_at": self.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if self.resolved_at else None,
        }
