import os
import logging
from pathlib import Path
from flask import Flask, jsonify, render_template, session
from config import config_by_name
from app.extensions import db, csrf
from app.blueprints import (
    auth_bp,
    disease_bp,
    yield_bp,
    recommend_bp,
    price_bp,
    advisor_bp,
    history_bp,
    info_bp,
)
from app.services import (
    init_disease_model,
    init_yield_model,
    init_recommend_model,
    init_price_models,
)

logger = logging.getLogger("agrovision")


def create_app(config_name: str = None) -> Flask:
    """Flask Application Factory."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    # Exempt API endpoints from standard form CSRF checks for programmatic JSON clients
    csrf.exempt(disease_bp)
    csrf.exempt(yield_bp)
    csrf.exempt(recommend_bp)
    csrf.exempt(price_bp)
    csrf.exempt(advisor_bp)
    csrf.exempt(auth_bp)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(yield_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(price_bp)
    app.register_blueprint(advisor_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(info_bp)

    # Load ML artifacts once at startup
    artifacts_dir = Path(app.config["ML_ARTIFACTS_DIR"])
    logger.info("Initializing ML model artifacts at startup from %s...", artifacts_dir)
    init_disease_model(artifacts_dir)
    init_yield_model(artifacts_dir)
    init_recommend_model(artifacts_dir)
    init_price_models(artifacts_dir)
    logger.info("All ML model initializers executed.")

    # Base & health routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy",
            "service": "agro-vision-ai",
            "version": "1.0.0",
        }), 200

    # Global context processor for i18n and session user
    @app.context_processor
    def inject_user_context():
        return {
            "current_user_id": session.get("user_id"),
            "current_user_name": session.get("user_name"),
            "current_language": session.get("language", "en"),
        }

    # Friendly error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="The requested page could not be found."), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({"error": "File size exceeds the 5 MB limit. Please upload a smaller image."}), 413

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("error.html", code=500, message="An internal server error occurred. Please try again later."), 500

    with app.app_context():
        db.create_all()

    return app
