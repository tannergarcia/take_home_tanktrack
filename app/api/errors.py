from flask import jsonify
from pydantic import ValidationError

from ..domain.errors import InactiveTechnician, NotFound, SchedulingConflict, ValidationFailed
from .schemas import format_time


def _conflict_detail(conflict):
    date_text = conflict.date.isoformat()
    if conflict.reason.value == "weekend":
        return f"{date_text} is not a working day (Mon to Fri)"
    if conflict.reason.value == "outside_hours":
        if conflict.start_minute < 540:
            return f"Job would start at {format_time(conflict.start_minute)}, before working hours begin at 09:00"
        return f"Job would end at {format_time(conflict.end_minute)}, after working hours end at 17:00"
    if conflict.reason.value == "invalid_duration":
        return "Duration must be 30, 60, 90, or 120 minutes"
    return (
        f"Overlaps job #{conflict.conflicting_job_id} ({conflict.conflicting_customer}) "
        f"{format_time(conflict.start_minute)}-{format_time(conflict.end_minute)}"
    )


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def pydantic_error(error):
        return jsonify({"error": {"code": "validation_error", "message": str(error)}}), 422

    @app.errorhandler(NotFound)
    def not_found(error):
        return jsonify({"error": {"code": "not_found", "message": str(error)}}), 404

    @app.errorhandler(InactiveTechnician)
    def inactive_technician(error):
        return jsonify(
            {"error": {"code": "technician_inactive", "message": str(error)}}
        ), 409

    @app.errorhandler(ValidationFailed)
    def validation(error):
        return jsonify({"error": {"code": "validation_error", "message": str(error)}}), 422

    @app.errorhandler(SchedulingConflict)
    def scheduling(error):
        conflicts = [
            {
                "date": conflict.date.isoformat(),
                "start_time": format_time(conflict.start_minute),
                "end_time": format_time(conflict.end_minute),
                "reason": conflict.reason.value,
                "occurrence": conflict.occurrence_index,
                "detail": _conflict_detail(conflict),
            }
            for conflict in error.conflicts
        ]
        return jsonify(
            {
                "error": {
                    "code": "scheduling_conflict",
                    "message": f"Cannot schedule job: {len(conflicts)} conflict(s).",
                    "conflicts": conflicts,
                }
            }
        ), 409
