import pytest

from app import create_app
from app.config import Config
from app.db import db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SEED_ON_START = False


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
