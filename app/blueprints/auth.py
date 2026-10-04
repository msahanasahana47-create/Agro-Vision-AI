from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from app.models_db import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form if request.form else request.get_json(silent=True) or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        language = data.get("language", "en")

        if not name or not email or not password:
            if request.is_json:
                return jsonify({"error": "Name, email, and password are required."}), 400
            flash("All fields are required.", "danger")
            return render_template("register.html"), 400

        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({"error": "An account with this email already exists."}), 409
            flash("An account with this email already exists.", "warning")
            return render_template("register.html"), 409

        user = User(name=name, email=email, language=language)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["user_name"] = user.name
        session["language"] = user.language

        wants_json = request.is_json or request.accept_mimetypes.accept_json
        if wants_json:
            return jsonify({"message": "Registration successful", "user": user.to_dict()}), 201
        flash("Registration successful! Welcome to Agro-Vision AI.", "success")
        return redirect(url_for("advisor.advisor_page"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form if request.form else request.get_json(silent=True) or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            if request.is_json:
                return jsonify({"error": "Invalid email or password."}), 401
            flash("Invalid email or password.", "danger")
            return render_template("login.html"), 401

        session["user_id"] = user.id
        session["user_name"] = user.name
        session["language"] = user.language

        if request.is_json:
            return jsonify({"message": "Login successful", "user": user.to_dict()}), 200
        flash("Welcome back!", "success")
        return redirect(url_for("advisor.advisor_page"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    if request.is_json:
        return jsonify({"message": "Logged out successfully"}), 200
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
