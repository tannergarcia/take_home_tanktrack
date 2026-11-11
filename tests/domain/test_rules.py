from datetime import date

import pytest

from app.domain.recurrence import expand_weekly
from app.domain.rules import find_overlaps, validate_slot
from app.domain.types import ConflictReason, ExistingJob, TimeSlot


@pytest.mark.parametrize("duration", [30, 60, 90, 120])
def test_allowed_durations(duration):
    assert not validate_slot(TimeSlot(date(2026, 11, 9), 540, duration))

@pytest.mark.parametrize("duration", [0, 10, 15, 180])
def test_rejected_durations(duration):
    assert any(c.reason == ConflictReason.INVALID_DURATION for c in validate_slot(TimeSlot(date(2026, 11, 9), 540, duration)))

@pytest.mark.parametrize("start,duration", [(510, 30), (990, 60), (1019, 30), (1200, 30)])
def test_hours_rejected(start, duration):
    assert any(c.reason == ConflictReason.OUTSIDE_HOURS for c in validate_slot(TimeSlot(date(2026, 11, 9), start, duration)))


def test_weekend_rejected():
    assert any(c.reason == ConflictReason.WEEKEND for c in validate_slot(TimeSlot(date(2026, 11, 14), 540, 30)))


def test_back_to_back_allowed_and_overlap_rejected():
    existing = [ExistingJob(1, "Acme", TimeSlot(date(2026, 11, 9), 540, 60))]
    assert not find_overlaps(TimeSlot(date(2026, 11, 9), 600, 60), existing)
    assert find_overlaps(TimeSlot(date(2026, 11, 9), 599, 60), existing)


def test_weekly_expansion():
    slots = expand_weekly(TimeSlot(date(2026, 11, 9), 600, 60), 12)
    assert len(slots) == 12
    assert slots[-1].date == date(2027, 1, 25)
