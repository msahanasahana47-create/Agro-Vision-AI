from flask import Blueprint, request, jsonify, render_template, session
from app.services.price_service import forecast_price, SUPPORTED_CROPS
from app.models_db import Prediction, db

price_bp = Blueprint("price", __name__)


@price_bp.route("/price", methods=["GET"])
def price_page():
    return render_template("price.html", supported_crops=[c.title() for c in SUPPORTED_CROPS])


@price_bp.route("/api/price", methods=["POST"])
def api_price():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data or "crop" not in data:
        return jsonify({"error": "Field 'crop' is required."}), 400

    crop = data.get("crop", "").strip()
    if not crop:
        return jsonify({"error": "Crop name cannot be empty."}), 400

    try:
        result = forecast_price(crop)

        user_id = session.get("user_id")
        if user_id:
            pred = Prediction(
                user_id=user_id,
                module="price",
                input_summary={"crop": crop},
                result=result,
                model_version="PriceLSTM-v1.0",
            )
            db.session.add(pred)
            db.session.commit()

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500
