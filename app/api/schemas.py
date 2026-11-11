from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..domain.types import JobStatus


def parse_time(value: str) -> int:
    """Parses a HH:MM formatted string into minutes since midnight. Raises ValueError if the format is invalid."""
    if not isinstance(value, str) or len(value) != 5 or value[2] != ":":
        raise ValueError("start_time must use HH:MM format")
    try:
        hour, minute = (int(part) for part in value.split(":"))
    except ValueError as exc:
        raise ValueError("start_time must use HH:MM format") from exc
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("start_time must use HH:MM format")
    return hour * 60 + minute


def format_time(minutes: int) -> str:
    """Formats minutes since midnight into a HH:MM formatted string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


class JobInput(BaseModel):
    customer_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    technician_id: int
    scheduled_date: date
    start_time: str
    duration_minutes: int
    status: JobStatus = JobStatus.SCHEDULED
    recurrence_count: int = Field(default=1, ge=1, le=12)

    @field_validator("start_time")
    @classmethod
    def valid_time(cls, value):
        parse_time(value)
        return value

    def to_service_data(self):
        data = self.model_dump()
        data["start_minute"] = parse_time(data.pop("start_time"))
        return data


class JobPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_name: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    technician_id: int | None = None
    scheduled_date: date | None = None
    start_time: str | None = None
    duration_minutes: int | None = None
    status: JobStatus | None = None

    @field_validator("start_time")
    @classmethod
    def valid_time(cls, value):
        if value is not None:
            parse_time(value)
        return value

    def to_service_data(self):
        data = {key: value for key, value in self.model_dump(exclude_unset=True).items() if value is not None}
        if "start_time" in data:
            data["start_minute"] = parse_time(data.pop("start_time"))
        return data
