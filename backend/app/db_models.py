from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LogRecord(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )

    level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )