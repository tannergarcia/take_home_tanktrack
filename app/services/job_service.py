from uuid import uuid4

from ..domain.errors import InactiveTechnician, NotFound, SchedulingConflict
from ..domain.recurrence import expand_weekly
from ..domain.rules import find_overlaps, validate_slot
from ..domain.types import ExistingJob, JobStatus, TimeSlot
from ..models import Job


class JobService:
    def __init__(self, job_repo, tech_repo, session):
        self.jobs = job_repo
        self.techs = tech_repo
        self.session = session

    def _technician(self, technician_id: int):
        technician = self.techs.get(technician_id)
        if not technician:
            raise NotFound("Technician not found")
        return technician

    def _active_technician(self, technician_id: int):
        technician = self._technician(technician_id)
        if not technician.is_active:
            raise InactiveTechnician(technician_id)
        return technician

    def _existing(self, technician_id: int, dates: list) -> list[ExistingJob]:
        return [
            ExistingJob(job.id, job.customer_name, job.slot)
            for job in self.jobs.list_for_technician_on_dates(technician_id, dates)
        ]

    def create_job(self, data: dict) -> Job:
        return self.create_recurring_jobs(data, data.get("recurrence_count", 1))[0]

    def create_recurring_jobs(self, data: dict, occurrences: int) -> list[Job]:
        technician_id = data["technician_id"]
        self._active_technician(technician_id)
        first = TimeSlot(data["scheduled_date"], data["start_minute"], data["duration_minutes"])
        slots = expand_weekly(first, occurrences)
        conflicts = []
        for index, slot in enumerate(slots, 1): # check for business logic conflicts for each occurrence
            conflicts.extend(
                type(conflict)(
                    conflict.date, conflict.start_minute, conflict.end_minute,
                    conflict.reason, conflict.conflicting_job_id,
                    conflict.conflicting_customer, index
                )
                for conflict in validate_slot(slot)
            )
        existing = self._existing(technician_id, [slot.date for slot in slots]) 
        for index, slot in enumerate(slots, 1): # now check for conflicts with this technician's schedule
            conflicts.extend(
                type(conflict)(
                    conflict.date, conflict.start_minute, conflict.end_minute,
                    conflict.reason, conflict.conflicting_job_id,
                    conflict.conflicting_customer, index
                )
                for conflict in find_overlaps(slot, existing)
            )
        if conflicts:
            raise SchedulingConflict(conflicts)
        series_id = str(uuid4()) if len(slots) > 1 else None
        jobs = [
            Job(
                customer_name=data["customer_name"],
                description=data["description"],
                technician_id=technician_id,
                scheduled_date=slot.date,
                start_minute=slot.start_minute,
                duration_minutes=slot.duration_minutes,
                status=data.get("status", JobStatus.SCHEDULED),
                series_id=series_id,
                series_index=index if series_id else None,
                series_total=len(slots) if series_id else None,
            )
            for index, slot in enumerate(slots, 1)
        ]
        self.jobs.add_many(jobs)
        self.session.commit()
        return jobs

    def update_job(self, job_id: int, patch: dict) -> Job:
        job = self.jobs.get(job_id)
        if not job:
            raise NotFound("Job not found")
        scheduling_fields = {"technician_id", "scheduled_date", "start_minute", "duration_minutes"}
        changed = any(key in patch and getattr(job, key) != value for key, value in patch.items() if key in scheduling_fields)
        if changed:
            technician_id = patch.get("technician_id", job.technician_id)
            self._active_technician(technician_id)
            slot = TimeSlot(
                patch.get("scheduled_date", job.scheduled_date),
                patch.get("start_minute", job.start_minute),
                patch.get("duration_minutes", job.duration_minutes),
            )
            conflicts = validate_slot(slot)
            existing = self._existing(technician_id, [slot.date])
            conflicts.extend(find_overlaps(slot, existing, exclude_id=job.id))
            if conflicts:
                raise SchedulingConflict(conflicts)
        for key, value in patch.items():
            if key not in {"series_id", "series_index", "series_total", "recurrence_count"}:
                setattr(job, key, value)
        self.session.commit()
        return job

    def delete_job(self, job_id: int) -> None:
        """Performs a soft delete of a job"""
        job = self.jobs.get(job_id)
        if not job:
            raise NotFound("Job not found")
        self.jobs.delete(job)
        self.session.commit()

    def get_job(self, job_id: int) -> Job:
        job = self.jobs.get(job_id)
        if not job:
            raise NotFound("Job not found")
        return job

    def list_jobs(self, filters: dict | None = None) -> list[Job]:
        return self.jobs.list(filters)
