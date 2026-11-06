from datetime import datetime, timezone
from backend.models import db

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # Router, Switch, Nexus, Server, Workstation
    vendor = db.Column(db.String(50), default="Cisco")
    location = db.Column(db.String(100), default="Enterprise HQ")
    vlan_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default="UNKNOWN")  # ONLINE, OFFLINE, DEGRADED, UNKNOWN
    latency_ms = db.Column(db.Float, nullable=True, default=None)
    packet_loss_pct = db.Column(db.Float, default=0.0)
    last_checked = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    logs = db.relationship("MonitoringLog", backref="device", lazy=True, cascade="all, delete-orphan")
    incidents = db.relationship("Incident", backref="device", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ip_address": self.ip_address,
            "device_type": self.device_type,
            "vendor": self.vendor,
            "location": self.location,
            "vlan_id": self.vlan_id,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 2) if self.latency_ms is not None else None,
            "packet_loss_pct": round(self.packet_loss_pct, 1) if self.packet_loss_pct is not None else 0.0,
            "last_checked": self.last_checked.strftime("%Y-%m-%d %H:%M:%S") if self.last_checked else "Never",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }
