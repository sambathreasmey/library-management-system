# transactions/routes.py
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from extensions import db
from models import Transaction, User  # and your Customer, Bank, Game models

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

def _parse_date(s, default=None):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return default

@reports_bp.get("/report")
@jwt_required()  # require login
def report_page():
    # Prefill dropdowns (optional; adjust to your models/fields)
    users = db.session.query(User.id, User.username).order_by(User.username).all()
    # If you have models Customer, Bank, Game:
    try:
        from models import Customer, Bank, Game
        customers = db.session.query(Customer.id, Customer.name).order_by(Customer.name).all()
        banks = db.session.query(Bank.id, Bank.name).order_by(Bank.name).all()
        games = db.session.query(Game.id, Game.name).order_by(Game.name).all()
    except Exception:
        customers, banks, games = [], [], []

    return render_template(
        "transactions_report.html",
        users=users, customers=customers, banks=banks, games=games
    )

@reports_bp.get("/api/summary")
@jwt_required()
def api_summary():
    """
    Returns grouped totals by period with filters applied.

    Query params:
      start=YYYY-MM-DD, end=YYYY-MM-DD
      period=daily|weekly|monthly (default=daily)
      user_id, customer_id, bank_id, game_id, type
    """
    period = (request.args.get("period") or "daily").lower()
    start = _parse_date(request.args.get("start"), default=(datetime.utcnow() - timedelta(days=6)))
    end   = _parse_date(request.args.get("end"),   default=datetime.utcnow())
    # normalize end to inclusive end-of-day
    end = end + timedelta(days=1)

    user_id     = request.args.get("user_id") or None
    customer_id = request.args.get("customer_id") or None
    bank_id     = request.args.get("bank_id") or None
    game_id     = request.args.get("game_id") or None
    type    = request.args.get("type") or None

    # Build filters
    conds = [Transaction.created_at >= start, Transaction.created_at < end]
    if user_id:     conds.append(Transaction.user_id == user_id)
    if customer_id: conds.append(Transaction.customer_id == int(customer_id))
    if bank_id:     conds.append(Transaction.bank_id == int(bank_id))
    if game_id:     conds.append(Transaction.game_id == int(game_id))
    if type:    conds.append(Transaction.type == type)

    # MySQL-friendly group expressions
    if period == "monthly":
        # label like 2025-10
        grp_label = func.date_format(Transaction.created_at, "%Y-%m")
        order_key = func.date_format(Transaction.created_at, "%Y-%m-01")
    elif period == "weekly":
        # YEARWEEK with mode 1 (ISO weeks), label like 2025-W41
        yw = func.yearweek(Transaction.created_at, 1)
        grp_label = func.concat(func.year(Transaction.created_at), "-W", func.week(Transaction.created_at, 1))
        order_key = yw
    else:  # daily
        grp_label = func.date(Transaction.created_at)             # 'YYYY-MM-DD'
        order_key = func.date(Transaction.created_at)

    q = (
        db.session.query(
            grp_label.label("bucket"),
            func.count(Transaction.id).label("count"),
            func.sum(Transaction.amount).label("amount"),
        )
        .filter(and_(*conds))
        .group_by("bucket")
        .order_by(order_key.asc())
    )

    rows = q.all()

    # overall totals
    tq = (
        db.session.query(
            func.count(Transaction.id), func.sum(Transaction.amount)
        ).filter(and_(*conds))
    ).first()

    total_count = int(tq[0] or 0)
    total_amount = float(tq[1] or 0.0)

    data = [
        {
            "bucket": r.bucket,
            "count": int(r.count or 0),
            "amount": float(r.amount or 0.0),
        }
        for r in rows
    ]

    return jsonify({
        "period": period,
        "start": start.strftime("%Y-%m-%d"),
        "end":   (end - timedelta(days=1)).strftime("%Y-%m-%d"),
        "total_count": total_count,
        "total_amount": total_amount,
        "rows": data
    })