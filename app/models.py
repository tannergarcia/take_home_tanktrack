from datetime import datetime, timezone

from .db import db
from .domain.types import JobStatus, TimeSlot


class Technician(db.Model):
    __tablename__ = "technicians"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    jobs = db.relationship("Job", back_populates="technician")


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey("technicians.id"), nullable=False, index=True)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    start_minute = db.Column(db.Integer, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(JobStatus), nullable=False, default=JobStatus.SCHEDULED, index=True)
    series_id = db.Column(db.String(36))
    series_index = db.Column(db.Integer)
    series_total = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
    technician = db.relationship("Technician", back_populates="jobs")
    __table_args__ = (
        db.CheckConstraint("duration_minutes IN (30, 60, 90, 120)"),
        db.CheckConstraint("start_minute >= 540 AND start_minute + duration_minutes <= 1020"),
        db.Index("ix_jobs_technician_date", "technician_id", "scheduled_date"),
    )

    @property
    def slot(self):
        return TimeSlot(self.scheduled_date, self.start_minute, self.duration_minutes)
