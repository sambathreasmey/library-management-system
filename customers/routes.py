from functools import wraps

from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from extensions import db
from models import Customer

customers_bp = Blueprint("customers", __name__, url_prefix="")

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

@customers_bp.get("/manage/customers")
def list_customers():
    login_required()
    return render_template("manage_customers.html")

@customers_bp.post("/manage/customers/create")
@jwt_required_or_login
def create_customer():
    login_required()
    user_id = get_jwt_identity()
    username = get_jwt().get("username")
    form = request.form
    name = form.get("name", "")
    acc_id = form.get("acc_id", "").strip()

    if not name or not acc_id:
        flash("Customer name and Account Id are required.", "warning")
        return redirect(url_for("customers.list_customers"))

    try:
        customer = Customer(name=name, acc_id=acc_id, user_id=user_id,
                    created_by=username, updated_by=username)
        db.session.add(customer)
        db.session.commit()
        flash("Customer created.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating book: {e}", "danger")
    return redirect(url_for("customers.list_customers"))

@customers_bp.post("/manage/customers/<int:customer_id>/update")
def update_customer(customer_id: int):
    admin_required()
    customer = Customer.query.get_or_404(customer_id)
    form = request.form
    customer.name = form.get("name", "").strip() or customer.name
    customer.acc_id = form.get("acc_id", "").strip() or customer.acc_id

    try:
        db.session.commit()
        flash("Customer updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating customer: {e}", "danger")
    return redirect(url_for("customers.list_customers"))

@customers_bp.post("/manage/customers/<int:customer_id>/delete")
def delete_customer(customer_id: int):
    admin_required()
    customer = Customer.query.get_or_404(customer_id)
    try:
        db.session.delete(customer)
        db.session.commit()
        flash("Customer deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting customer: {e}", "danger")
    return redirect(url_for("customers.list_customers"))