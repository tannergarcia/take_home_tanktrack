from datetime import date, timedelta
from .db import db
from .models import Job, Technician
from .domain.types import JobStatus


def seed_if_empty():
    if db.session.query(Technician).count():
        print("Database already has data, skipping seeding.")
        return
    technicians = [
        Technician(name=name, email=f"{name.lower().replace(' ', '.')}@tanktrack.example")
        for name in ("Fede Valverde", "Tanner Garcia", "Darwin Nunez", "Luis Suarez")
    ]
    db.session.add_all(technicians)
    db.session.flush()
    monday = date.today() - timedelta(days=date.today().weekday())
    jobs = []
    statuses = [JobStatus.SCHEDULED, JobStatus.IN_PROGRESS, JobStatus.COMPLETED]
    for index in range(20):
        day = monday + timedelta(days=(index % 10) + (7 if index >= 10 else 0))
        while day.weekday() >= 5:
            day += timedelta(days=1)
        start = 540 + (index % 4) * 120
        jobs.append(
            Job(
                customer_name=f"Customer {index + 1}",
                description="Routine field service visit",
                technician_id=technicians[index % len(technicians)].id,
                scheduled_date=day,
                start_minute=start,
                duration_minutes=60,
                status=statuses[index % len(statuses)],
            )
        )
    series_id = "seed-weekly-series"
    for index in range(8):
        jobs.append(
            Job(
                customer_name="Evergreen Industries",
                description="Weekly maintenance",
                technician_id=technicians[0].id,
                scheduled_date=monday + timedelta(days=14 + index * 7),
                start_minute=840,
                duration_minutes=60,
                status=JobStatus.SCHEDULED,
                series_id=series_id,
                series_index=index + 1,
                series_total=8,
            )
        )
    db.session.add_all(jobs)
    print(f"Seeded {len(technicians)} technicians and {len(jobs)} jobs.")
    db.session.commit()


def register_seed_command(app):
    @app.cli.command("seed")
    def seed_command():
        seed_if_empty()
