import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "nexguard-enterprise-secret-key-2026")
    
    # SQLite Database configuration
    DB_PATH = BASE_DIR / "database" / "nexguard.db"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ping Engine settings
    PING_TIMEOUT_SECONDS = float(os.getenv("PING_TIMEOUT_SECONDS", "2.0"))
    PING_COUNT = int(os.getenv("PING_COUNT", "2"))
    MONITOR_INTERVAL_SECONDS = int(os.getenv("PING_INTERVAL_SECONDS", "30"))

    # Alert Thresholds
    LATENCY_THRESHOLD_WARNING_MS = 80.0
    LATENCY_THRESHOLD_CRITICAL_MS = 200.0
    PACKET_LOSS_CRITICAL_PCT = 25.0

    # Cisco SSH Automation settings
    CISCO_USERNAME = os.getenv("CISCO_USERNAME", "admin")
    CISCO_PASSWORD = os.getenv("CISCO_PASSWORD", "cisco123")
    CISCO_ENABLE_SECRET = os.getenv("CISCO_ENABLE_SECRET", "cisco123")
    CISCO_PORT = int(os.getenv("CISCO_PORT", "22"))

    # Frontend paths
    TEMPLATE_FOLDER = str(BASE_DIR / "frontend" / "templates")
    STATIC_FOLDER = str(BASE_DIR / "frontend" / "static")
