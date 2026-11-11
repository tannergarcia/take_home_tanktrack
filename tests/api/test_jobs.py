from datetime import date

from app.db import db
from app.models import Job, Technician


def test_create_and_filter_job(client, app):
    with app.app_context():
        db.session.add(Technician(name="Dana"))
        db.session.commit()
        technician_id = Technician.query.one().id
    response = client.post("/api/jobs", json={
        "customer_name": "Acme", "description": "Inspection", "technician_id": technician_id,
        "scheduled_date": "2026-11-09", "start_time": "09:00", "duration_minutes": 60,
    })
    assert response.status_code == 201
    assert response.get_json()[0]["end_time"] == "10:00"
    assert client.get("/api/jobs?status=scheduled").status_code == 200


def test_conflict_returns_structured_error(client, app):
    with app.app_context():
        db.session.add(Technician(name="Dana"))
        db.session.commit()
        technician_id = Technician.query.one().id
    payload = {"customer_name": "Acme", "description": "Inspection", "technician_id": technician_id, "scheduled_date": "2026-11-09", "start_time": "09:00", "duration_minutes": 60}
    assert client.post("/api/jobs", json=payload).status_code == 201
    conflict = client.post("/api/jobs", json={**payload, "customer_name": "Other"})
    assert conflict.status_code == 409
    assert conflict.get_json()["error"]["code"] == "scheduling_conflict"


def test_recurring_conflict_is_atomic(client, app):
    with app.app_context():
        db.session.add(Technician(name="Dana"))
        db.session.commit()
        technician_id = Technician.query.one().id
    existing = {
        "customer_name": "Existing", "description": "Busy", "technician_id": technician_id,
        "scheduled_date": "2026-11-16", "start_time": "09:00", "duration_minutes": 60,
    }
    assert client.post("/api/jobs", json=existing).status_code == 201
    series = {**existing, "customer_name": "Series", "start_time": "09:30", "recurrence_count": 3}
    response = client.post("/api/jobs", json=series)
    assert response.status_code == 409
    assert response.get_json()["error"]["conflicts"][0]["date"] == "2026-11-16"
    assert client.get("/api/jobs").get_json() and len(client.get("/api/jobs").get_json()) == 1


def test_delete_soft_deletes_and_frees_time_slot(client, app):
    with app.app_context():
        db.session.add(Technician(name="Dana"))
        db.session.commit()
        technician_id = Technician.query.one().id
    payload = {
        "customer_name": "Acme", "description": "Inspection", "technician_id": technician_id,
        "scheduled_date": "2026-11-09", "start_time": "09:00", "duration_minutes": 60,
    }
    created = client.post("/api/jobs", json=payload).get_json()[0]
    assert client.delete(f"/api/jobs/{created['id']}").status_code == 204
    assert client.get("/api/jobs").get_json() == []
    assert client.get(f"/api/jobs/{created['id']}").status_code == 404

    replacement = client.post("/api/jobs", json={**payload, "customer_name": "Replacement"})
    assert replacement.status_code == 201
    with app.app_context():
        deleted = db.session.get(Job, created["id"])
        assert deleted.deleted is True


def test_inactive_technician_cannot_be_scheduled(client, app):
    with app.app_context():
        technician = Technician(name="Dana", is_active=False)
        db.session.add(technician)
        db.session.commit()
        technician_id = technician.id
    payload = {
        "customer_name": "Acme", "description": "Inspection", "technician_id": technician_id,
        "scheduled_date": "2026-11-09", "start_time": "09:00", "duration_minutes": 60,
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "technician_inactive"


def test_technician_status_endpoints(client, app):
    with app.app_context():
        technician = Technician(name="Dana", is_active=True)
        db.session.add(technician)
        db.session.commit()
        technician_id = technician.id
    response = client.post(f"/api/technicians/{technician_id}/deactivate")
    assert response.status_code == 200
    assert response.get_json()["is_active"] is False
    response = client.patch(f"/api/technicians/{technician_id}", json={"is_active": True})
    assert response.status_code == 200
    assert response.get_json()["is_active"] is True
    response = client.post(f"/api/technicians/{technician_id}/activate")
    assert response.status_code == 200
    assert response.get_json()["is_active"] is True
