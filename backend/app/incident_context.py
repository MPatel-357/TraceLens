from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db_models import LogRecord


def get_incident_logs(
    db: Session,
    anomaly_timestamp: str,
    window_minutes: int = 5
):
    start_time = datetime.fromisoformat(anomaly_timestamp)
    end_time = start_time + timedelta(minutes=window_minutes)

    logs = (
        db.query(LogRecord)
        .filter(
            LogRecord.timestamp >= start_time,
            LogRecord.timestamp < end_time
        )
        .order_by(LogRecord.timestamp.asc())
        .all()
    )

    return [
        {
            "timestamp": log.timestamp.isoformat(),
            "level": log.level,
            "service": log.service,
            "message": log.message
        }
        for log in logs
    ]