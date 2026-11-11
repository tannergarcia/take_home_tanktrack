from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from ..db import db
from ..repositories.jobs import JobRepository
from ..repositories.technicians import TechnicianRepository
from ..services.job_service import JobService
from .schemas import JobInput, JobPatch, format_time

jobs_bp = Blueprint("jobs", __name__)


def service():
    return JobService(JobRepository(db.session), TechnicianRepository(db.session), db.session)


def serialize(job):
    return {
        "id": job.id,
        "customer_name": job.customer_name,
        "description": job.description,
        "technician_id": job.technician_id,
        "technician_name": job.technician.name,
        "scheduled_date": job.scheduled_date.isoformat(),
        "start_time": format_time(job.start_minute),
        "end_time": format_time(job.start_minute + job.duration_minutes),
        "duration_minutes": job.duration_minutes,
        "status": job.status.value,
        "deleted": job.deleted,
        "series_id": job.series_id,
        "series_index": job.series_index,
        "series_total": job.series_total,
    }


@jobs_bp.get("/jobs")
def list_jobs():
    filters = {key: request.args.get(key) for key in ("date", "date_from", "date_to", "status")}
    technician = request.args.get("technician_id")
    if technician:
        try:
            filters["technician_id"] = int(technician)
        except ValueError:
            return jsonify(
                {"error": {"code": "validation_error", "message": "technician_id must be an integer"}}
            ), 422
    return jsonify([serialize(job) for job in service().list_jobs(filters)])


@jobs_bp.get("/jobs/<int:job_id>")
def get_job(job_id: int):
    return jsonify(serialize(service().get_job(job_id)))


@jobs_bp.post("/jobs")
def create_job():
    data = JobInput.model_validate(request.get_json(silent=True) or {})
    jobs = service().create_recurring_jobs(data.to_service_data(), data.recurrence_count)
    return jsonify([serialize(job) for job in jobs]), 201


@jobs_bp.patch("/jobs/<int:job_id>")
def update_job(job_id: int):
    data = JobPatch.model_validate(request.get_json(silent=True) or {})
    return jsonify(serialize(service().update_job(job_id, data.to_service_data())))


@jobs_bp.delete("/jobs/<int:job_id>")
def delete_job(job_id: int):
    service().delete_job(job_id)
    return "", 204
