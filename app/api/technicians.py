from flask import Blueprint, jsonify, request
from pydantic import BaseModel

from ..db import db
from ..repositories.technicians import TechnicianRepository
from ..domain.errors import NotFound


technicians_bp = Blueprint("technicians", __name__)


@technicians_bp.get("/technicians")
def list_technicians():
    return jsonify(
        [
            {
                "id": technician.id,
                "name": technician.name,
                "email": technician.email,
                "is_active": technician.is_active,
            }
            for technician in TechnicianRepository(db.session).list()
        ]
    )


class TechnicianStatus(BaseModel):
    is_active: bool


def _update_status(technician_id: int, is_active: bool):
    technician = TechnicianRepository(db.session).get(technician_id)
    if not technician:
        raise NotFound("Technician not found")
    technician.is_active = is_active
    db.session.commit()
    return jsonify(
        {
            "id": technician.id,
            "name": technician.name,
            "email": technician.email,
            "is_active": technician.is_active,
        }
    )


@technicians_bp.patch("/technicians/<int:technician_id>")
def update_technician_status(technician_id: int):
    data = TechnicianStatus.model_validate(request.get_json(silent=True) or {})
    return _update_status(technician_id, data.is_active)


@technicians_bp.post("/technicians/<int:technician_id>/activate")
def activate_technician(technician_id: int):
    return _update_status(technician_id, True)


@technicians_bp.post("/technicians/<int:technician_id>/deactivate")
def deactivate_technician(technician_id: int):
    return _update_status(technician_id, False)
