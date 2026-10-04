from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models_db import Prediction, db

history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
def history_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    user_predictions = (
        Prediction.query.filter_by(user_id=user_id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    return render_template("history.html", predictions=[p.to_dict() for p in user_predictions])


@history_bp.route("/api/history", methods=["GET"])
def api_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required to access prediction history."}), 401

    module_filter = request.args.get("module")
    query = Prediction.query.filter_by(user_id=user_id)
    if module_filter:
        query = query.filter_by(module=module_filter.lower())

    predictions = query.order_by(Prediction.created_at.desc()).all()
    return jsonify({"predictions": [p.to_dict() for p in predictions]}), 200


@history_bp.route("/api/history/<int:prediction_id>", methods=["DELETE"])
def api_delete_history(prediction_id: int):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required to delete history."}), 401

    pred = Prediction.query.filter_by(id=prediction_id, user_id=user_id).first()
    if not pred:
        return jsonify({"error": f"Prediction with id {prediction_id} not found."}), 404

    db.session.delete(pred)
    db.session.commit()
    return jsonify({"message": f"Prediction {prediction_id} deleted successfully."}), 200
