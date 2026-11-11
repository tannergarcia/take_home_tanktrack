from dataclasses import dataclass
from datetime import date
from enum import Enum


class JobStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ConflictReason(str, Enum):
    OUTSIDE_HOURS = "outside_hours"
    WEEKEND = "weekend"
    OVERLAP = "overlap"
    INVALID_DURATION = "invalid_duration"


@dataclass(frozen=True)
class TimeSlot:
    date: date
    start_minute: int
    duration_minutes: int

    @property
    def end_minute(self):
        return self.start_minute + self.duration_minutes

    def overlaps(self, other: TimeSlot) -> bool:
        return (
            self.date == other.date
            and self.start_minute < other.end_minute
            and other.start_minute < self.end_minute
        )


@dataclass(frozen=True)
class ExistingJob:
    id: int
    customer_name: str
    slot: TimeSlot


@dataclass(frozen=True)
class Conflict:
    date: date
    start_minute: int
    end_minute: int
    reason: ConflictReason
    conflicting_job_id: int | None = None
    conflicting_customer: str | None = None
    occurrence_index: int | None = None
