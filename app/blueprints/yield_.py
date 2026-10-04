from flask import Blueprint, request, jsonify, render_template, session
from app.services.yield_service import predict_yield
from app.models_db import Prediction, db

yield_bp = Blueprint("yield_", __name__)


@yield_bp.route("/yield", methods=["GET"])
def yield_page():
    return render_template("yield.html")


@yield_bp.route("/api/yield", methods=["POST"])
def api_yield():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"error": "No input payload provided."}), 400

    try:
        crop = data.get("crop", "").strip()
        rainfall = float(data.get("rainfall"))
        temperature = float(data.get("temperature"))
        humidity = float(data.get("humidity"))
        soil_ph = float(data.get("soil_ph"))
        nitrogen = float(data.get("nitrogen"))
        phosphorus = float(data.get("phosphorus"))
        potassium = float(data.get("potassium"))
        area = float(data.get("area"))
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid numeric input: {str(e)}"}), 400

    try:
        result = predict_yield(
            crop=crop,
            rainfall=rainfall,
            temperature=temperature,
            humidity=humidity,
            soil_ph=soil_ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            area=area,
        )

        user_id = session.get("user_id")
        if user_id:
            pred = Prediction(
                user_id=user_id,
                module="yield",
                input_summary={
                    "crop": crop, "rainfall": rainfall, "temperature": temperature,
                    "humidity": humidity, "soil_ph": soil_ph, "N": nitrogen,
                    "P": phosphorus, "K": potassium, "area": area,
                },
                result=result,
                model_version="YieldPipeline-v1.0",
            )
            db.session.add(pred)
            db.session.commit()

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500
