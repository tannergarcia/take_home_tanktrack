from datetime import timedelta

from .errors import ValidationFailed

from .types import TimeSlot


def expand_weekly(first_slot: TimeSlot, occurrences: int) -> list[TimeSlot]:
    if not isinstance(occurrences, int) or not 1 <= occurrences <= 12:
        raise ValidationFailed("recurrence_count must be between 1 and 12")
    return [
        TimeSlot(
            first_slot.date + timedelta(days=7 * index),
            first_slot.start_minute,
            first_slot.duration_minutes,
        )
        for index in range(occurrences)
    ]
