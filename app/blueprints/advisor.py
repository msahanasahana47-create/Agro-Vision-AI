from flask import Blueprint, request, jsonify, render_template, session
from app.services.advisor_service import run_cross_module_advisor
from app.models_db import Prediction, db

advisor_bp = Blueprint("advisor", __name__)


@advisor_bp.route("/advisor", methods=["GET"])
def advisor_page():
    return render_template("advisor.html")


@advisor_bp.route("/api/advisor", methods=["POST"])
def api_advisor():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"error": "No input payload provided."}), 400

    try:
        nitrogen = float(data.get("nitrogen"))
        phosphorus = float(data.get("phosphorus"))
        potassium = float(data.get("potassium"))
        temperature = float(data.get("temperature"))
        humidity = float(data.get("humidity"))
        ph = float(data.get("ph"))
        rainfall = float(data.get("rainfall"))
        area = float(data.get("area"))
        has_disease_risk = str(data.get("has_disease_risk", "false")).lower() in ["true", "1", "yes"]
        disease_name = data.get("disease_name")
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid numeric input: {str(e)}"}), 400

    try:
        result = run_cross_module_advisor(
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            area=area,
            has_disease_risk=has_disease_risk,
            disease_name=disease_name,
        )

        user_id = session.get("user_id")
        if user_id:
            pred = Prediction(
                user_id=user_id,
                module="advisor",
                input_summary={
                    "N": nitrogen, "P": phosphorus, "K": potassium,
                    "temperature": temperature, "humidity": humidity,
                    "ph": ph, "rainfall": rainfall, "area": area,
                    "has_disease_risk": has_disease_risk,
                },
                result=result,
                model_version="AdvisorCrossModule-v1.0",
            )
            db.session.add(pred)
            db.session.commit()

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500
