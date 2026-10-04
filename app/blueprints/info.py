import json
from pathlib import Path
from flask import Blueprint, jsonify, render_template, current_app

info_bp = Blueprint("info", __name__)


def load_model_info():
    artifacts_dir = Path(current_app.config["ML_ARTIFACTS_DIR"])
    modules = ["disease", "yield", "recommend", "price"]
    models_metadata = {}

    for mod in modules:
        metrics_file = artifacts_dir / mod / "metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, "r", encoding="utf-8") as f:
                    models_metadata[mod] = json.load(f)
            except Exception as e:
                models_metadata[mod] = {"status": "error_loading", "error": str(e)}
        else:
            models_metadata[mod] = {
                "model_name": mod.title(),
                "status": "not_trained_yet",
                "version": "v1.0-pending",
                "metrics": {},
                "dataset": "Pending training in M1-M5",
                "last_trained": "N/A",
            }
    return models_metadata


@info_bp.route("/models", methods=["GET"])
def models_page():
    info = load_model_info()
    return render_template("model_info.html", models=info)


@info_bp.route("/api/models", methods=["GET"])
def api_models():
    info = load_model_info()
    return jsonify(info), 200
