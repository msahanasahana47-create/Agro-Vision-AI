from flask import Blueprint, request, jsonify, render_template, session
from app.services.recommend_service import recommend_crop
from app.models_db import Prediction, db

recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.route("/recommend", methods=["GET"])
def recommend_page():
    return render_template("recommend.html")


@recommend_bp.route("/api/recommend", methods=["POST"])
def api_recommend():
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
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid numeric input: {str(e)}"}), 400

    try:
        result = recommend_crop(
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
        )

        user_id = session.get("user_id")
        if user_id:
            pred = Prediction(
                user_id=user_id,
                module="recommend",
                input_summary={
                    "N": nitrogen, "P": phosphorus, "K": potassium,
                    "temperature": temperature, "humidity": humidity,
                    "ph": ph, "rainfall": rainfall,
                },
                result=result,
                model_version="RecommendPipeline-v1.0",
            )
            db.session.add(pred)
            db.session.commit()

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500
