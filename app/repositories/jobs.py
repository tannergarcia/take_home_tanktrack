from sqlalchemy import select

from ..models import Job

from datetime import date


class JobRepository:
    def __init__(self, session):
        self.session = session

    def get(self, job_id: int) -> Job | None:
        query = select(Job).where(Job.id == job_id, Job.deleted.is_(False))
        return self.session.scalar(query)

    def list(self, filters=None) -> list[Job]:
        filters = filters or {}
        query = select(Job).where(Job.deleted.is_(False))
        if filters.get("date"):
            query = query.where(Job.scheduled_date == filters["date"])
        if filters.get("date_from"):
            query = query.where(Job.scheduled_date >= filters["date_from"])
        if filters.get("date_to"):
            query = query.where(Job.scheduled_date <= filters["date_to"])
        if filters.get("technician_id"):
            query = query.where(Job.technician_id == filters["technician_id"])
        if filters.get("status"):
            query = query.where(Job.status == filters["status"])
        return list(self.session.scalars(query.order_by(Job.scheduled_date, Job.start_minute)).all())

    def list_for_technician_on_dates(self, technician_id: int, dates: list[date]) -> list[Job]:
        query = select(Job).where(
            Job.technician_id == technician_id,
            Job.scheduled_date.in_(dates),
            Job.deleted.is_(False),
        )
        return list(self.session.scalars(query).all())

    def add(self, job: Job) -> Job:
        self.session.add(job)
        return job

    def add_many(self, jobs: list[Job]) -> list[Job]:
        self.session.add_all(jobs)
        return jobs

    def delete(self, job: Job) -> None:
        job.deleted = True
