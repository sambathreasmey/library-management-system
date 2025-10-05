from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from datetime import timedelta
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.get("/login")
def login_page():
    return render_template("login.html", hide_chrome=True)

@auth_bp.post("/login")
def login_submit():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        flash("Invalid username or password", "danger")
        return redirect(url_for("auth.login_page"))

    # identity must be a STRING
    identity = str(user.id)
    base_claims = {"username": user.username, "is_admin": bool(user.is_admin)}

    access_token = create_access_token(identity=identity, additional_claims=base_claims)
    refresh_token = create_refresh_token(identity=identity, additional_claims=base_claims)

    resp = make_response(redirect(url_for("books.dashboard")))
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    flash(f"Welcome back, {user.username}!", "success")
    return resp

@auth_bp.post("/logout")
def logout():
    resp = redirect(url_for("auth.login_page"))
    unset_jwt_cookies(resp)  # clears BOTH access & refresh cookies
    return resp

# Optional: JSON login for API tools; returns token AND sets cookies.
@auth_bp.post("/login-json")
def login_submit_json():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad credentials"}), 401

    identity = str(user.id)
    base_claims = {"username": user.username, "is_admin": bool(user.is_admin)}
    access_token  = create_access_token(identity=identity, additional_claims=base_claims)
    refresh_token = create_refresh_token(identity=identity, additional_claims=base_claims)

    resp = jsonify({"access_token": access_token})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp

@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_access_token():
    identity = get_jwt_identity()
    claims = get_jwt()
    new_access = create_access_token(
        identity=identity,
        additional_claims={
            "username": claims.get("username", ""),
            "is_admin": bool(claims.get("is_admin", False)),
        },
    )
    resp = jsonify({"access_token": new_access})
    set_access_cookies(resp, new_access)
    return resp

@auth_bp.get("/refresh-silent")
@jwt_required(refresh=True)
def refresh_silent():
    identity = get_jwt_identity()
    claims = get_jwt()
    next_url = request.args.get("next") or url_for("books.dashboard")
    new_access = create_access_token(
        identity=identity,
        additional_claims={
            "username": claims.get("username", ""),
            "is_admin": bool(claims.get("is_admin", False)),
        },
    )
    resp = redirect(next_url)
    set_access_cookies(resp, new_access)
    return resp
