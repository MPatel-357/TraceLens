from collections import Counter

from sqlalchemy.orm import Session

from app.db_models import LogRecord


def get_log_summary(db: Session):
    logs = db.query(LogRecord).all()

    total_logs = len(logs)

    level_counts = Counter(log.level for log in logs)
    service_counts = Counter(log.service for log in logs)

    error_count = level_counts.get("ERROR", 0)
    critical_count = level_counts.get("CRITICAL", 0)

    problem_count = error_count + critical_count

    problem_rate = (
        round((problem_count / total_logs) * 100, 2)
        if total_logs > 0
        else 0
    )

    return {
        "total_logs": total_logs,
        "level_counts": dict(level_counts),
        "service_counts": dict(service_counts),
        "problem_rate_percent": problem_rate
    }