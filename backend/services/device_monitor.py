import time
import threading
from datetime import datetime, timezone
from backend.models import db, Device, MonitoringLog
from backend.services.ping_service import PingService
from backend.services.alert_service import AlertService

class DeviceMonitor:
    _thread = None
    _running = False

    @staticmethod
    def check_all(app):
        """Runs a complete monitoring cycle across all registered devices."""
        with app.app_context():
            devices = Device.query.all()
            for device in devices:
                ping_res = PingService.ping(device.ip_address)
                device.status = ping_res["status"]
                device.latency_ms = ping_res["latency_ms"]
                device.packet_loss_pct = ping_res["packet_loss_pct"]
                device.last_checked = datetime.now(timezone.utc)

                # Append history log
                log = MonitoringLog(
                    device_id=device.id,
                    status=device.status,
                    latency_ms=device.latency_ms,
                    packet_loss_pct=device.packet_loss_pct
                )
                db.session.add(log)

                # Evaluate for alerts / incidents
                AlertService.evaluate_device_health(device, ping_res)

            db.session.commit()

    @classmethod
    def start_background_polling(cls, app, interval_seconds=30):
        """Starts background thread to poll devices at regular intervals."""
        if cls._running:
            return

        cls._running = True

        def _poll_worker():
            # Initial slight delay before first cycle to allow DB init
            time.sleep(2)
            while cls._running:
                try:
                    cls.check_all(app)
                except Exception as e:
                    print(f"[DeviceMonitor Error]: {e}")
                time.sleep(interval_seconds)

        cls._thread = threading.Thread(target=_poll_worker, daemon=True)
        cls._thread.start()

    @classmethod
    def stop_background_polling(cls):
        cls._running = False
