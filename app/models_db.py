from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """Application user model."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    language = db.Column(db.String(10), default="en", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    predictions = db.relationship("Prediction", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Prediction(db.Model):
    """User prediction history model."""
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    module = db.Column(db.String(20), nullable=False, index=True)  # disease, yield, recommend, price, advisor
    input_summary = db.Column(db.JSON, nullable=False)
    result = db.Column(db.JSON, nullable=False)
    model_version = db.Column(db.String(50), nullable=False, default="v1.0")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "module": self.module,
            "input_summary": self.input_summary,
            "result": self.result,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
