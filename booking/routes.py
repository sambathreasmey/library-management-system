from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sqlalchemy import func
from extensions import db
from models import User, Transaction, Customer, Bank, Game

books_bp = Blueprint("booking", __name__, url_prefix="")

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

@books_bp.get("/dashboard")
@cache.cached(timeout=120, key_prefix='dashboard_html_v1')
def dashboard():
    login_required()
    total_customers = db.session.scalar(db.select(func.count(Customer.id))) or 0
    total_booked = db.session.scalar(db.select(func.coalesce(func.count(Transaction.id), 0))) or 0
    total_users = db.session.scalar(db.select(func.count(User.id))) or 0
    latest_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    return render_template(
        "dashboard.html",
        total_customers=total_customers,
        total_booked=total_booked,
        total_users=total_users,
        latest_transactions=latest_transactions
    )

@books_bp.get("/manage/booking")
def booking():
    login_required()
    banks = Bank.query.all()
    customers = Customer.query.all()
    games = Game.query.all()
    return render_template("booking.html", banks=banks, customers=customers, games=games)
