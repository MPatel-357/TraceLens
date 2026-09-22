import pytest

from app.parser import parse_log_line


def test_parse_valid_log():
    log = parse_log_line(
        "2026-09-22 14:30:00 ERROR PaymentService Database connection timeout"
    )

    assert log.level == "ERROR"
    assert log.service == "PaymentService"
    assert log.message == "Database connection timeout"
    assert log.timestamp.year == 2026


def test_level_is_normalized():
    log = parse_log_line(
        "2026-09-22 14:30:00 error PaymentService Request failed"
    )

    assert log.level == "ERROR"


def test_invalid_level():
    with pytest.raises(ValueError):
        parse_log_line(
            "2026-09-22 14:30:00 BANANA PaymentService Something happened"
        )


def test_invalid_timestamp():
    with pytest.raises(ValueError):
        parse_log_line(
            "not-a-date 14:30:00 ERROR PaymentService Something happened"
        )


def test_invalid_format():
    with pytest.raises(ValueError):
        parse_log_line("this is not a valid log")