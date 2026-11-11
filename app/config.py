import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///tanktrack.db").replace(
        "postgres://", "postgresql://", 1
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEED_ON_START = os.getenv("SEED_ON_START", "true").lower() == "true"
