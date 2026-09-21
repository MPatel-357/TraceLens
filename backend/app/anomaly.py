from collections import defaultdict

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from app.db_models import LogRecord


def detect_anomalies(db: Session):
    logs = (
        db.query(LogRecord)
        .order_by(LogRecord.timestamp.asc())
        .all()
    )

    if len(logs) < 20:
        return []

    buckets = defaultdict(
        lambda: {
            "total": 0,
            "errors": 0,
            "warnings": 0
        }
    )

    for log in logs:
        bucket_time = log.timestamp.replace(
            minute=(log.timestamp.minute // 5) * 5,
            second=0,
            microsecond=0
        )

        bucket = buckets[bucket_time]

        bucket["total"] += 1

        if log.level in {"ERROR", "CRITICAL"}:
            bucket["errors"] += 1

        elif log.level == "WARN":
            bucket["warnings"] += 1

    timestamps = sorted(buckets.keys())

    features = []

    for timestamp in timestamps:
        bucket = buckets[timestamp]

        error_rate = (
            bucket["errors"] / bucket["total"]
            if bucket["total"]
            else 0
        )

        features.append([
            bucket["total"],
            bucket["errors"],
            bucket["warnings"],
            error_rate,
        ])

    if len(features) < 5:
        return []

    X = np.array(features)

    model = IsolationForest(
        contamination=0.08,
        random_state=42
    )

    predictions = model.fit_predict(X)
    scores = model.decision_function(X)

    anomalies = []

    for timestamp, prediction, score, feature in zip(
        timestamps,
        predictions,
        scores,
        features
    ):
        if prediction == -1:
            anomalies.append({
                "timestamp": timestamp.isoformat(),
                "total_logs": int(feature[0]),
                "errors": int(feature[1]),
                "warnings": int(feature[2]),
                "error_rate": round(float(feature[3]), 3),
                "anomaly_score": round(float(score), 4),
            })

    return sorted(
        anomalies,
        key=lambda item: item["anomaly_score"]
    )