from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

users_bp = Blueprint("users", __name__, url_prefix="/manage/users")

def admin_required():
    verify_jwt_in_request()
    claims = get_jwt() or {}
    if not claims.get("is_admin", False):
        abort(403, description="Admins only")

@users_bp.get("/")
def list_users():
    admin_required()
    # no query needed — DataTables will call /api/users
    return render_template("manage_users.html")

@users_bp.post("/create")
def create_user():
    admin_required()
    fullname = request.form.get("fullname") or ""
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    is_admin = request.form.get("is_admin") == "on"

    if not username or not password:
        flash("Username and password are required.", "warning")
        return redirect(url_for("users.list_users"))

    if User.query.filter_by(username=username).first():
        flash("Username already exists.", "danger")
        return redirect(url_for("users.list_users"))

    u = User(fullname=fullname, username=username, is_admin=is_admin)
    u.set_password(password)
    db.session.add(u)
    try:
        db.session.commit()
        flash("User created.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("users.list_users"))

@users_bp.post("/<int:user_id>/password")
def change_password(user_id: int):
    admin_required()
    user = User.query.get_or_404(user_id)
    new_pw = request.form.get("new_password") or ""
    if not new_pw:
        flash("New password required.", "warning")
        return redirect(url_for("users.list_users"))
    user.password_hash = generate_password_hash(new_pw)
    user.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        flash("Password updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("users.list_users"))

@users_bp.post("/<int:user_id>/toggle-admin")
def toggle_admin(user_id: int):
    admin_required()
    user = User.query.get_or_404(user_id)
    # prevent removing *your own* admin accidentally (optional safeguard)
    # You can remove this block if you don't want the safeguard.
    from flask_jwt_extended import get_jwt_identity
    if str(user.id) == str(get_jwt_identity()):
        flash("You cannot change your own admin role.", "warning")
        return redirect(url_for("users.list_users"))

    user.is_admin = not bool(user.is_admin)
    user.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        flash("Admin flag toggled.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("users.list_users"))

@users_bp.post("/<int:user_id>/delete")
def delete_user(user_id: int):
    admin_required()
    user = User.query.get_or_404(user_id)
    # Optional: prevent deleting yourself
    from flask_jwt_extended import get_jwt_identity
    if str(user.id) == str(get_jwt_identity()):
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for("users.list_users"))

    try:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for("users.list_users"))
