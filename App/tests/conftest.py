import os
from wsgi import app as cli_app
import pytest
import os
from wsgi import app as cli_app
from App.main import create_app
from App.database import db

# Ensure persistent test.db has all tables before any tests run
@pytest.fixture(scope="session", autouse=True)
def ensure_test_db_tables():
    db_uri = cli_app.config["SQLALCHEMY_DATABASE_URI"]
    # Only run for file-based SQLite DB
    if db_uri.startswith("sqlite:///test.db"):
        with cli_app.app_context():
            db.create_all()


@pytest.fixture
def app():
    """
    Create and configure a new app instance for each test.
    Uses an in-memory SQLite database.
    """
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def empty_db(app):
    """
    Ensures database is clean before each test.
    """
    # DB is already created in app fixture
    yield
    # Optional: clear data between tests
    db.session.remove()
    db.drop_all()
    db.create_all()


@pytest.fixture
def client(app):
    """
    Flask test client for route testing.
    """
    return app.test_client()