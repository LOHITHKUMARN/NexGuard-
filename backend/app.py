import os
from flask import Flask, render_template
from backend.config import Config
from backend.models import db, Device, Incident, MonitoringLog
from backend.routes.devices import devices_bp
from backend.routes.monitoring import monitoring_bp
from backend.routes.incidents import incidents_bp
from backend.routes.reports import reports_bp
from backend.services.device_monitor import DeviceMonitor

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder=config_class.TEMPLATE_FOLDER,
        static_folder=config_class.STATIC_FOLDER
    )
    app.config.from_object(config_class)

    # Ensure database directory exists
    os.makedirs(os.path.dirname(config_class.DB_PATH), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(devices_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(reports_bp)

    # HTML Page Routes
    @app.route("/")
    def dashboard_page():
        return render_template("dashboard.html", active_page="dashboard")

    @app.route("/devices")
    def devices_page():
        return render_template("devices.html", active_page="devices")

    @app.route("/monitoring")
    def monitoring_page():
        return render_template("monitoring.html", active_page="monitoring")

    @app.route("/incidents")
    def incidents_page():
        return render_template("incidents.html", active_page="incidents")

    @app.route("/reports")
    def reports_page():
        return render_template("reports.html", active_page="reports")

    # Initialize DB schema and seed baseline data
    with app.app_context():
        db.create_all()
        seed_database(app)

    return app

def seed_database(app):
    """Populates baseline simulated enterprise network topology."""
    if Device.query.count() > 0:
        return

    sample_devices = [
        # Core & Distribution
        {"name": "Core-Router-01", "ip_address": "192.168.1.1", "device_type": "Router", "vendor": "Cisco IOS (2911)", "location": "Enterprise Core DC", "vlan_id": None},
        {"name": "Dist-Switch-01", "ip_address": "192.168.1.2", "device_type": "Switch", "vendor": "Cisco IOS (3560)", "location": "Campus MDF - Rack 1", "vlan_id": None},

        # HR Department (VLAN 10)
        {"name": "HR-Switch-01", "ip_address": "192.168.10.2", "device_type": "Switch", "vendor": "Cisco IOS (2960)", "location": "HR Floor 2 - IDF 1", "vlan_id": 10},
        {"name": "HR-Workstation-01", "ip_address": "192.168.10.10", "device_type": "Workstation", "vendor": "Dell OptiPlex", "location": "HR Dept Desk 101", "vlan_id": 10},

        # Finance Department (VLAN 20)
        {"name": "Fin-Switch-01", "ip_address": "192.168.20.2", "device_type": "Switch", "vendor": "Cisco IOS (2960)", "location": "Finance Floor 3 - IDF 2", "vlan_id": 20},
        {"name": "Fin-Workstation-01", "ip_address": "192.168.20.10", "device_type": "Workstation", "vendor": "HP EliteDesk", "location": "Finance Desk 204", "vlan_id": 20},

        # IT Department (VLAN 30)
        {"name": "IT-Switch-01", "ip_address": "192.168.30.2", "device_type": "Switch", "vendor": "Cisco IOS (2960)", "location": "IT Operations Room", "vlan_id": 30},
        {"name": "IT-Admin-Host", "ip_address": "192.168.30.10", "device_type": "Workstation", "vendor": "Lenovo ThinkCentre", "location": "NOC Engineer Station", "vlan_id": 30},

        # Customer Support (VLAN 40)
        {"name": "Support-Switch-01", "ip_address": "192.168.40.2", "device_type": "Switch", "vendor": "Cisco IOS (2960)", "location": "Support Floor 1 - IDF 3", "vlan_id": 40},
        {"name": "Support-Host-01", "ip_address": "192.168.40.10", "device_type": "Workstation", "vendor": "Dell OptiPlex", "location": "Support Bay A - Desk 3", "vlan_id": 40},

        # Data Center & Nexus (VLAN 50)
        {"name": "Nexus-DC-N9K", "ip_address": "192.168.50.2", "device_type": "Nexus", "vendor": "Cisco NX-OS (9300)", "location": "Data Center Server Rack A1", "vlan_id": 50},
        {"name": "DC-Web-Server", "ip_address": "192.168.50.10", "device_type": "Server", "vendor": "Cisco UCS / Ubuntu", "location": "Data Center Blade 1", "vlan_id": 50},
        {"name": "DC-DB-Server", "ip_address": "192.168.50.20", "device_type": "Server", "vendor": "Dell PowerEdge / RHEL", "location": "Data Center Blade 2", "vlan_id": 50},
        {"name": "DC-DNS-DHCP", "ip_address": "192.168.50.5", "device_type": "Server", "vendor": "Cisco Infrastructure / Linux", "location": "Data Center Blade 3", "vlan_id": 50},
    ]

    for d in sample_devices:
        device = Device(**d)
        db.session.add(device)
    db.session.commit()

    # Pre-populate sample troubleshooting incidents for interview demonstration
    dev_support = Device.query.filter_by(name="Support-Host-01").first()
    if dev_support:
        dev_support.status = "OFFLINE"
        dev_support.packet_loss_pct = 100.0
        incident1 = Incident(
            device_id=dev_support.id,
            title="CRITICAL: Support-Host-01 Unreachable (VLAN Mismatch)",
            description="Workstation in Customer Support unable to receive DHCP lease or ping gateway 192.168.40.1.",
            severity="CRITICAL",
            status="OPEN",
            root_cause="Access switchport FastEthernet0/11 incorrectly assigned to VLAN 1 instead of VLAN 40.",
            remediation="Execute 'switchport access vlan 40' on Support-Switch-01 FastEthernet0/11 and renew IP."
        )
        db.session.add(incident1)

    dev_db = Device.query.filter_by(name="DC-DB-Server").first()
    if dev_db:
        dev_db.status = "DEGRADED"
        dev_db.latency_ms = 112.4
        dev_db.packet_loss_pct = 15.0
        incident2 = Incident(
            device_id=dev_db.id,
            title="WARNING: DC-DB-Server High Latency & Packet Drop",
            description="Intermittent TCP latency spikes noticed when queries originate from VLAN 20 (Finance).",
            severity="WARNING",
            status="ACKNOWLEDGED",
            root_cause="Port-Channel 1 link speed negotiation flapping between 10G and 1G due to optical transceiver mismatch.",
            remediation="Standardized transceiver SFP+ module on Nexus Eth1/2 and re-enabled LACP member."
        )
        db.session.add(incident2)

    db.session.commit()

    # Initial telemetry collection across all devices
    from backend.services.device_monitor import DeviceMonitor
    DeviceMonitor.check_all(app)

app = create_app()

if __name__ == "__main__":
    DeviceMonitor.start_background_polling(app, interval_seconds=Config.MONITOR_INTERVAL_SECONDS)
    app.run(host="127.0.0.1", port=5000, debug=True)
