from datetime import datetime

from pydantic import BaseModel, Field


class RawLog(BaseModel):
    raw: str = Field(
        ...,
        min_length=1,
        description="A raw application log line"
    )


class LogEvent(BaseModel):
    id: int | None = None
    timestamp: datetime
    level: str
    service: str
    message: str

    model_config = {
        "from_attributes": True
    }