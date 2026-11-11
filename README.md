 # TankTrack Scheduler

A small Flask, SQLAlchemy, and React scheduling application for field-service dispatchers.

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app:create_app run --debug
```

The backend serves the production frontend from `frontend/dist`. For frontend development:

```bash
cd frontend
npm install
npm run dev
```

## Run tests

From the repository root, create and activate the virtual environment, install the
dependencies, and run the test suite:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

The suite includes unit tests for scheduling rules and API tests for job creation,
updates, recurring jobs, soft deletion, inactive technicians, and validation errors.

## Configuration and deployment

`DATABASE_URL` selects the database and defaults to SQLite. PostgreSQL URLs beginning with
`postgres://` are normalized automatically.

The application creates tables on startup and seeds sample technicians/jobs when the database
is empty. Run `flask --app app:create_app seed` to seed explicitly.

## Vercel deployment

The application is configured (`vercel.json`) to run on Vercel with Neon as the DB provider.