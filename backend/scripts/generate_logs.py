import random
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.db_models import LogRecord


SERVICES = [
    "AuthService",
    "PaymentService",
    "DatabaseService",
    "OrderService",
    "UserService",
]

NORMAL_MESSAGES = {
    "INFO": [
        "Request completed successfully",
        "User authenticated successfully",
        "Database query completed",
        "Response returned successfully",
    ],
    "WARN": [
        "Request latency elevated",
        "Connection pool usage elevated",
        "Retry attempt initiated",
    ],
}

ERROR_MESSAGES = [
    "Database connection timeout",
    "Payment processing failed",
    "Service unavailable",
    "Request timed out",
]


def generate_logs(count=1000):
    db = SessionLocal()

    start_time = datetime.now() - timedelta(hours=24)

    try:
        records = []

        for i in range(count):
            timestamp = start_time + timedelta(
                seconds=i * random.randint(20, 60)
            )

            roll = random.random()

            if roll < 0.90:
                level = "INFO"
            elif roll < 0.98:
                level = "WARN"
            else:
                level = "ERROR"

            service = random.choice(SERVICES)

            if level == "ERROR":
                message = random.choice(ERROR_MESSAGES)
            else:
                message = random.choice(NORMAL_MESSAGES[level])

            records.append(
                LogRecord(
                    timestamp=timestamp,
                    level=level,
                    service=service,
                    message=message,
                )
            )

        # Inject an obvious incident:
        incident_start = datetime.now() - timedelta(hours=1)

        for i in range(40):
            records.append(
                LogRecord(
                    timestamp=incident_start + timedelta(seconds=i * 10),
                    level="ERROR",
                    service="PaymentService",
                    message="Database connection timeout",
                )
            )

        db.add_all(records)
        db.commit()

        print(f"Generated {len(records)} logs.")

    finally:
        db.close()


if __name__ == "__main__":
    generate_logs()