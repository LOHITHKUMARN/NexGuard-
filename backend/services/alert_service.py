from datetime import datetime, timezone
from backend.models import db, Device, Incident

class AlertService:
    @staticmethod
    def evaluate_device_health(device: Device, ping_result: dict):
        """
        Evaluates ping results, updates or creates incidents accordingly.
        """
        status = ping_result.get("status", "UNKNOWN")
        latency = ping_result.get("latency_ms")
        loss = ping_result.get("packet_loss_pct", 0.0)

        # 1. Device is OFFLINE
        if status == "OFFLINE":
            existing = Incident.query.filter_by(
                device_id=device.id,
                status="OPEN"
            ).filter(Incident.title.like("%Unreachable%")).first()

            if not existing:
                incident = Incident(
                    device_id=device.id,
                    title=f"CRITICAL: {device.name} Unreachable (100% Packet Loss)",
                    description=(
                        f"Device {device.name} ({device.ip_address}) in {device.location} failed ICMP reachability checks. "
                        f"100% packet loss detected. Immediate network connectivity investigation required."
                    ),
                    severity="CRITICAL",
                    status="OPEN",
                    root_cause="Link down, interface administratively shut down, or physical cabling disconnect.",
                    remediation="Verify physical cabling, check SVI / switch port status via console/SSH, inspect switch logs."
                )
                db.session.add(incident)
                db.session.commit()

        # 2. Device is DEGRADED (high packet loss or latency)
        elif status == "DEGRADED":
            existing = Incident.query.filter_by(
                device_id=device.id,
                status="OPEN"
            ).filter(Incident.title.like("%Degraded%")).first()

            if not existing:
                incident = Incident(
                    device_id=device.id,
                    title=f"WARNING: {device.name} Latency/Packet Drop Degraded",
                    description=(
                        f"Device {device.name} ({device.ip_address}) is reporting high latency ({latency}ms) "
                        f"or elevated packet loss ({loss}%). Service degradation may impact users."
                    ),
                    severity="WARNING",
                    status="OPEN",
                    root_cause="Duplex/speed mismatch, uplink saturation, or Spanning Tree topology recalculation.",
                    remediation="Check switchport error counters (CRC, collisions), inspect link utilization with Wireshark."
                )
                db.session.add(incident)
                db.session.commit()

        # 3. Device is ONLINE (Auto-resolve recovery if open unreachable alert exists)
        elif status == "ONLINE":
            open_incident = Incident.query.filter_by(
                device_id=device.id,
                status="OPEN"
            ).filter(Incident.title.like("%Unreachable%")).first()

            if open_incident:
                open_incident.status = "RESOLVED"
                open_incident.resolved_at = datetime.now(timezone.utc)
                open_incident.remediation = (
                    f"Auto-resolved: Device recovered reachability. Latency restored to {latency}ms with 0% loss."
                )
                db.session.commit()
