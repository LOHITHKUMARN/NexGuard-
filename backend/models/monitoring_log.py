from datetime import datetime, timezone
from backend.models import db

class MonitoringLog(db.Model):
    __tablename__ = "monitoring_logs"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    latency_ms = db.Column(db.Float, nullable=True)
    packet_loss_pct = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "device_name": self.device.name if self.device else "Unknown",
            "status": self.status,
            "latency_ms": round(self.latency_ms, 2) if self.latency_ms is not None else None,
            "packet_loss_pct": round(self.packet_loss_pct, 1) if self.packet_loss_pct is not None else 0.0,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
        }
