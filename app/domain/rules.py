from .types import Conflict, ConflictReason, ExistingJob, TimeSlot

WORK_START = 9 * 60 # because time is saved as delta. 9 am -> 540 minutes past midnight
WORK_END = 17 * 60 # 5 pm
ALLOWED_DURATIONS = {30, 60, 90, 120}


def validate_slot(slot: TimeSlot) -> list[Conflict]:
    conflicts = []
    if slot.duration_minutes not in ALLOWED_DURATIONS:
        conflicts.append(
            Conflict(slot.date, slot.start_minute, slot.end_minute, ConflictReason.INVALID_DURATION)
        )
    if slot.date.weekday() >= 5:
        conflicts.append(
            Conflict(slot.date, slot.start_minute, slot.end_minute, ConflictReason.WEEKEND)
        )
    if slot.start_minute < WORK_START or slot.end_minute > WORK_END:
        conflicts.append(
            Conflict(slot.date, slot.start_minute, slot.end_minute, ConflictReason.OUTSIDE_HOURS)
        )
    return conflicts

def find_overlaps(slot: TimeSlot, existing: list[ExistingJob], exclude_id=None) -> list[Conflict]:
    return [
        Conflict(
            slot.date,
            slot.start_minute,
            slot.end_minute,
            ConflictReason.OVERLAP,
            job.id,
            job.customer_name,
        )
        for job in existing
        if job.id != exclude_id and slot.overlaps(job.slot)
    ]
