from app.models_db import User, Prediction
from app.extensions import db


def test_user_password_hashing(app):
    """Test user password hashing and verification."""
    with app.app_context():
        user = User(name="Ramesh", email="ramesh@example.com")
        user.set_password("MyStrongPass99")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "MyStrongPass99"
        assert user.check_password("MyStrongPass99") is True
        assert user.check_password("WrongPassword") is False


def test_prediction_creation_and_cascade(app):
    """Test prediction persistence and cascade deletion."""
    with app.app_context():
        user = User(name="Sita", email="sita@example.com")
        user.set_password("Pass1234")
        db.session.add(user)
        db.session.commit()

        pred = Prediction(
            user_id=user.id,
            module="yield",
            input_summary={"crop": "rice", "area": 2.5},
            result={"predicted_yield": 8.75},
            model_version="v1.0",
        )
        db.session.add(pred)
        db.session.commit()

        assert pred.id is not None
        assert len(user.predictions) == 1

        db.session.delete(user)
        db.session.commit()

        remaining_pred = Prediction.query.filter_by(id=pred.id).first()
        assert remaining_pred is None
