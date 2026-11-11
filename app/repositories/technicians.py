from sqlalchemy import select

from ..models import Technician


class TechnicianRepository:
    def __init__(self, session):
        self.session = session

    def get(self, technician_id):
        return self.session.get(Technician, technician_id)

    def list(self):
        return list(self.session.scalars(select(Technician).order_by(Technician.name)).all())
