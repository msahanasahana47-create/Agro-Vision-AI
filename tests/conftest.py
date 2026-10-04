import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app import create_app
from app.extensions import db
from app.models_db import User, Prediction


@pytest.fixture
def app():
    """Create test application instance with in-memory database."""
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()


@pytest.fixture
def auth_user(app):
    """Create a persistent test user."""
    with app.app_context():
        user = User(name="Test Farmer", email="farmer@example.com", language="en")
        user.set_password("Secret123!")
        db.session.add(user)
        db.session.commit()
        return user.to_dict()
