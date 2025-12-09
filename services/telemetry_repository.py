from models.system_telemetry import SystemTelemetry
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class TelemetryRepository:
    @staticmethod
    def get_metrics(db: Session, metric: str, start: datetime, end: datetime):
        return db.query(SystemTelemetry).filter(
            SystemTelemetry.metric == metric,
            SystemTelemetry.timestamp >= start,
            SystemTelemetry.timestamp <= end
        ).order_by(SystemTelemetry.timestamp.asc()).all()

    @staticmethod
    def get_latest(db: Session, metric: str):
        return db.query(SystemTelemetry).filter_by(metric=metric).order_by(SystemTelemetry.timestamp.desc()).first()

    @staticmethod
    def add(db: Session, metric: str, value: int, timestamp: datetime, meta: dict = None):
        entry = SystemTelemetry(
            metric=metric,
            value=value,
            timestamp=timestamp,
            meta=meta or {}
        )
        db.add(entry)
        db.commit()
        return entry
