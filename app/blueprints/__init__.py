from app.blueprints.auth import auth_bp
from app.blueprints.disease import disease_bp
from app.blueprints.yield_ import yield_bp
from app.blueprints.recommend import recommend_bp
from app.blueprints.price import price_bp
from app.blueprints.advisor import advisor_bp
from app.blueprints.history import history_bp
from app.blueprints.info import info_bp

__all__ = [
    "auth_bp",
    "disease_bp",
    "yield_bp",
    "recommend_bp",
    "price_bp",
    "advisor_bp",
    "history_bp",
    "info_bp",
]
