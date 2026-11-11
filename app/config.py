import os

# Neon's Vercel integration exposes the pooled connection string under these names.
_DATABASE_URL_ENV_VARS = ("DATABASE_URL", "POSTGRES_URL")


def _default_database_uri():
    # Vercel's deployment filesystem is read-only; only /tmp is writable.
    if os.getenv("VERCEL"):
        return "sqlite:////tmp/tanktrack.db"
    return "sqlite:///tanktrack.db"


def _normalize_postgres_uri(uri):
    # SQLAlchemy needs an explicit dialect+driver; route Postgres URLs to psycopg (v3).
    for prefix in ("postgres://", "postgresql://"):
        if uri.startswith(prefix):
            return "postgresql+psycopg://" + uri[len(prefix):]
    return uri


def _database_uri():
    for name in _DATABASE_URL_ENV_VARS:
        value = os.getenv(name)
        if value:
            return _normalize_postgres_uri(value)
    return _default_database_uri()


def _engine_options(uri):
    if not uri.startswith("postgresql"):
        return {}
    # Neon suspends idle compute and closes idle connections, so validate pooled
    # connections before use and recycle them before the server drops them.
    return {"pool_pre_ping": True, "pool_recycle": 300, "pool_size": 5, "max_overflow": 5}


class Config:
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEED_ON_START = os.getenv("SEED_ON_START", "true").lower() == "true"