from functools import wraps

from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from extensions import db
from models import Bank

banks_bp = Blueprint("banks", __name__, url_prefix="")

def jwt_required_or_login(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()  # checks cookies/headers per your config
        except Exception:
            return redirect(url_for("auth.login_page"))
        return fn(*args, **kwargs)
    return wrapper

def login_required():
    # raises if invalid; returns None otherwise
    verify_jwt_in_request(optional=False)

def admin_required():
    login_required()
    claims = get_jwt()
    if not claims.get("is_admin", False):
        from flask import abort
        abort(403, description="Admins only")

@banks_bp.get("/manage/banks")
def list_banks():
    login_required()
    return render_template("manage_banks.html")

@banks_bp.post("/manage/banks/create")
@jwt_required_or_login
def create_bank():
    login_required()
    user_id = get_jwt_identity()
    username = get_jwt().get("username")
    form = request.form
    name = form.get("name", "")

    if not name:
        flash("Bank name are required.", "warning")
        return redirect(url_for("banks.list_banks"))

    try:
        bank = Bank(name=name, user_id=user_id,
                    created_by=username, updated_by=username)
        db.session.add(bank)
        db.session.commit()
        flash("Bank created.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating bank: {e}", "danger")
    return redirect(url_for("banks.list_banks"))

@banks_bp.post("/manage/banks/<int:bank_id>/update")
def update_bank(bank_id: int):
    admin_required()
    bank = Bank.query.get_or_404(bank_id)
    form = request.form
    bank.name = form.get("name", "").strip() or bank.name

    try:
        db.session.commit()
        flash("Bank updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating bank: {e}", "danger")
    return redirect(url_for("banks.list_banks"))

@banks_bp.post("/manage/banks/<int:bank_id>/delete")
def delete_bank(bank_id: int):
    admin_required()
    bank = Bank.query.get_or_404(bank_id)
    try:
        db.session.delete(bank)
        db.session.commit()
        flash("Bank deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting bank: {e}", "danger")
    return redirect(url_for("banks.list_banks"))