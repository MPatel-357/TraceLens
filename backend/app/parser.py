from datetime import datetime

from app.models import LogEvent


VALID_LEVELS = {"DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"}


def parse_log_line(raw: str) -> LogEvent:
    parts = raw.strip().split(maxsplit=4)

    if len(parts) < 5:
        raise ValueError(
            "Invalid log format. Expected: "
            "YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE"
        )

    date_part, time_part, level, service, message = parts

    level = level.upper()

    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid log level '{level}'. "
            f"Expected one of: {', '.join(sorted(VALID_LEVELS))}"
        )

    try:
        timestamp = datetime.strptime(
            f"{date_part} {time_part}",
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError as exc:
        raise ValueError(
            "Invalid timestamp. Expected YYYY-MM-DD HH:MM:SS"
        ) from exc

    return LogEvent(
        timestamp=timestamp,
        level=level,
        service=service,
        message=message
    )