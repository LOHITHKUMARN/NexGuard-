from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from backend.models.device import Device
from backend.models.incident import Incident
from backend.models.monitoring_log import MonitoringLog

__all__ = ["db", "Device", "Incident", "MonitoringLog"]
