import os
import uuid
from flask import Blueprint, request, jsonify, render_template, current_app, session
from werkzeug.utils import secure_filename
from app.services.disease_service import predict_disease
from app.models_db import Prediction, db

disease_bp = Blueprint("disease", __name__)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@disease_bp.route("/disease", methods=["GET"])
def disease_page():
    return render_template("disease.html")


@disease_bp.route("/api/disease", methods=["POST"])
def api_disease():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided in request."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No image selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file format. Allowed formats: PNG, JPG, JPEG."}), 415

    # Enforce safe unique filename
    ext = file.filename.rsplit(".", 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    if not safe_name.endswith(f".{ext}"):
        safe_name = f"{safe_name}.{ext}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, safe_name)
    file.save(save_path)

    try:
        threshold = current_app.config.get("DISEASE_CONFIDENCE_THRESHOLD", 0.60)
        result = predict_disease(save_path, threshold=threshold)

        # Record prediction if user is authenticated
        user_id = session.get("user_id")
        if user_id:
            pred = Prediction(
                user_id=user_id,
                module="disease",
                input_summary={"filename": safe_name},
                result=result,
                model_version="MobileNetV2-v1.0",
            )
            db.session.add(pred)
            db.session.commit()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
