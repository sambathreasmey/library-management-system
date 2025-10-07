from functools import wraps

from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from extensions import db
from models import Transaction

transactions_bp = Blueprint("transactions", __name__, url_prefix="")

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

@transactions_bp.get("/manage/transactions")
def list_transactions():
    login_required()
    return render_template("manage_transactions.html")

@transactions_bp.post("/manage/transactions/create")
@jwt_required_or_login
def create_transaction():
    login_required()
    user_id = get_jwt_identity()
    username = get_jwt().get("username")
    form = request.form
    amount = form.get("amount", 0)
    bank_stor = form.get("bank_stor", "")
    currency = form.get("currency", "USD")
    type = form.get("type", 1)
    customer_id = form.get("customer_id", "")
    bank_id = form.get("bank_id", "")
    game_id = form.get("game_id", "")

    if not amount or not bank_stor or not currency or not type or not customer_id or not bank_id or not game_id or not user_id:
        flash("Transaction amount, bank_stor , currency, customer, bank, game or type are required.", "warning")
        return redirect(url_for("booking.booking"))

    try:
        transaction = Transaction(amount=amount, currency=currency, bank_stor=bank_stor, type=type, user_id=user_id,
                    created_by=username, updated_by=username, customer_id=customer_id, bank_id=bank_id, game_id=game_id)
        db.session.add(transaction)
        db.session.commit()
        flash("Transaction created.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating transaction: {e}", "danger")
    return redirect(url_for("booking.booking"))

@transactions_bp.post("/manage/transactions/<int:transaction_id>/update")
def update_transaction(transaction_id: int):
    admin_required()
    transaction = Transaction.query.get_or_404(transaction_id)
    form = request.form
    transaction.amount = form.get("amount", 0) or transaction.amount
    transaction.bank_stor = form.get("bank_stor", "") or transaction.bank_stor
    transaction.currency = form.get("currency", "") or transaction.currency
    transaction.type = form.get("type", 0) or transaction.type

    try:
        db.session.commit()
        flash("Transaction updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating transaction: {e}", "danger")
    return redirect(url_for("transactions.list_transactions"))

@transactions_bp.post("/manage/transactions/<int:transaction_id>/delete")
def delete_transaction(transaction_id: int):
    admin_required()
    transaction = Transaction.query.get_or_404(transaction_id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash("Transaction deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting transaction: {e}", "danger")
    return redirect(url_for("transactions.list_transactions"))