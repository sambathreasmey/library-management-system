from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sqlalchemy import func, or_, asc, desc
from sqlalchemy.orm import joinedload

from extensions import db
from models import User, Customer, Game, Bank, Transaction

api_bp = Blueprint("api", __name__, url_prefix="/api")

def _parse_dt_params():
    """Parse DataTables params from request.args (GET or POST)."""
    args = request.values  # works for GET or POST
    draw   = int(args.get("draw", "1"))
    start  = int(args.get("start", "0"))
    length = int(args.get("length", "10"))
    search_value = (args.get("search[value]") or "").strip()
    # Sorting: DataTables can send multiple order[i], we’ll use the first
    order_col_index = args.get("order[0][column]")
    order_dir = args.get("order[0][dir]", "asc").lower()
    return draw, start, length, search_value, order_col_index, order_dir

def _jwt_required():
    # API endpoints: enforce JWT but keep JSON when unauthorized via your global handlers
    verify_jwt_in_request()

def _admin_required():
    _jwt_required()
    claims = get_jwt() or {}
    if not claims.get("is_admin", False):
        abort(403, description="Admins only")

@api_bp.route("/customers", methods=["GET", "POST"])
def customers_table():
    _jwt_required()

    draw, start, length, search_value, order_col_index, order_dir = _parse_dt_params()
    columns = ["id", "name", "acc_id", "created_by", "updated_by", "created_at", "updated_at"]

    base_query = db.session.query(Customer)
    total_records = db.session.scalar(db.select(func.count(Customer.id))) or 0

    if search_value:
        like = f"%{search_value}%"
        base_query = base_query.filter(
            or_(Customer.name.ilike(like), Customer.acc_id.ilike(like))
        )

    filtered_records = base_query.with_entities(func.count(Customer.id)).scalar() or 0

    # Ordering
    if order_col_index is not None and order_col_index.isdigit():
        idx = int(order_col_index)
        idx = min(max(idx, 0), len(columns) - 1)
        colname = columns[idx]
        col = getattr(Customer, colname)
        if order_dir == "desc":
            base_query = base_query.order_by(desc(col))
        else:
            base_query = base_query.order_by(asc(col))
    else:
        base_query = base_query.order_by(desc(Customer.created_at))

    # Paging
    rows = base_query.offset(start).limit(length).all()

    data = []
    for customer in rows:
        data.append({
            "id": customer.id,
            "name": customer.name,
            "acc_id": customer.acc_id,
            "created_by": customer.created_by or "",
            "updated_by": customer.updated_by or "",
            "created_at": customer.created_at.strftime("%Y-%m-%d %H:%M") if customer.created_at else "",
            "updated_at": customer.updated_at.strftime("%Y-%m-%d %H:%M") if customer.updated_at else ""
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })

@api_bp.route("/games", methods=["GET", "POST"])
def games_table():
    _jwt_required()

    draw, start, length, search_value, order_col_index, order_dir = _parse_dt_params()
    columns = ["id", "name", "created_by", "updated_by", "created_at", "updated_at"]

    base_query = db.session.query(Game)
    total_records = db.session.scalar(db.select(func.count(Game.id))) or 0

    if search_value:
        like = f"%{search_value}%"
        base_query = base_query.filter(
            Game.name.ilike(like)
        )

    filtered_records = base_query.with_entities(func.count(Game.id)).scalar() or 0

    # Ordering
    if order_col_index is not None and order_col_index.isdigit():
        idx = int(order_col_index)
        idx = min(max(idx, 0), len(columns) - 1)
        colname = columns[idx]
        col = getattr(Game, colname)
        if order_dir == "desc":
            base_query = base_query.order_by(desc(col))
        else:
            base_query = base_query.order_by(asc(col))
    else:
        base_query = base_query.order_by(desc(Game.created_at))

    # Paging
    rows = base_query.offset(start).limit(length).all()

    data = []
    for game in rows:
        data.append({
            "id": game.id,
            "name": game.name,
            "created_by": game.created_by or "",
            "updated_by": game.updated_by or "",
            "created_at": game.created_at.strftime("%Y-%m-%d %H:%M") if game.created_at else "",
            "updated_at": game.updated_at.strftime("%Y-%m-%d %H:%M") if game.updated_at else ""
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })

@api_bp.route("/banks", methods=["GET", "POST"])
def banks_table():
    _jwt_required()

    draw, start, length, search_value, order_col_index, order_dir = _parse_dt_params()
    columns = ["id", "name", "created_by", "updated_by", "created_at", "updated_at"]

    base_query = db.session.query(Bank)
    total_records = db.session.scalar(db.select(func.count(Bank.id))) or 0

    if search_value:
        like = f"%{search_value}%"
        base_query = base_query.filter(
            Bank.name.ilike(like)
        )

    filtered_records = base_query.with_entities(func.count(Bank.id)).scalar() or 0

    # Ordering
    if order_col_index is not None and order_col_index.isdigit():
        idx = int(order_col_index)
        idx = min(max(idx, 0), len(columns) - 1)
        colname = columns[idx]
        col = getattr(Bank, colname)
        if order_dir == "desc":
            base_query = base_query.order_by(desc(col))
        else:
            base_query = base_query.order_by(asc(col))
    else:
        base_query = base_query.order_by(desc(Bank.created_at))

    # Paging
    rows = base_query.offset(start).limit(length).all()

    data = []
    for bank in rows:
        data.append({
            "id": bank.id,
            "name": bank.name,
            "created_by": bank.created_by or "",
            "updated_by": bank.updated_by or "",
            "created_at": bank.created_at.strftime("%Y-%m-%d %H:%M") if bank.created_at else "",
            "updated_at": bank.updated_at.strftime("%Y-%m-%d %H:%M") if bank.updated_at else ""
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })

@api_bp.route("/transactions", methods=["GET", "POST"])
def transactions_table():
    _jwt_required()

    draw, start, length, search_value, order_col_index, order_dir = _parse_dt_params()
    columns = ["id", "amount", "created_by", "updated_by", "created_at", "updated_at"]

    base_query = db.session.query(Transaction).options(
        joinedload(Transaction.customer),
        joinedload(Transaction.bank),
        joinedload(Transaction.game)
    )
    total_records = db.session.scalar(db.select(func.count(Transaction.id))) or 0

    if search_value:
        like = f"%{search_value}%"
        base_query = base_query.filter(
            Transaction.name.ilike(like)
        )

    filtered_records = base_query.with_entities(func.count(Transaction.id)).scalar() or 0

    # Ordering
    if order_col_index is not None and order_col_index.isdigit():
        idx = int(order_col_index)
        idx = min(max(idx, 0), len(columns) - 1)
        colname = columns[idx]
        col = getattr(Transaction, colname)
        if order_dir == "desc":
            base_query = base_query.order_by(desc(col))
        else:
            base_query = base_query.order_by(asc(col))
    else:
        base_query = base_query.order_by(desc(Transaction.created_at))

    # Paging
    rows = base_query.offset(start).limit(length).all()

    data = []
    for transaction in rows:
        data.append({
            "id": transaction.id,
            "amount": transaction.amount,
            "bank_stor": transaction.bank_stor,
            "customer_id": transaction.customer_id,
            "customer_name": transaction.customer.name if transaction.customer else "",
            "bank_id": transaction.bank_id,
            "bank_name": transaction.bank.name if transaction.bank else "",
            "game_id": transaction.game_id,
            "game_name": transaction.game.name if transaction.game else "",
            "currency": transaction.currency,
            "type": transaction.type,
            "created_by": transaction.created_by or "",
            "updated_by": transaction.updated_by or "",
            "created_at": transaction.created_at.strftime("%Y-%m-%d %H:%M") if transaction.created_at else "",
            "updated_at": transaction.updated_at.strftime("%Y-%m-%d %H:%M") if transaction.updated_at else ""
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })

@api_bp.route("/booking", methods=["GET", "POST"])
def books_table():
    _jwt_required()

    draw, start, length, search_value, order_col_index, order_dir = _parse_dt_params()

    # Column mapping (MUST match columns config on client)
    columns = ["id", "title", "author", "isbn", "published_year", "copies", "created_at"]

    base_query = db.session.query(Book)
    total_records = db.session.scalar(db.select(func.count(Book.id))) or 0

    # Searching
    if search_value:
        like = f"%{search_value}%"
        base_query = base_query.filter(
            or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like))
        )

    filtered_records = base_query.with_entities(func.count(Book.id)).scalar() or 0

    # Ordering
    if order_col_index is not None and order_col_index.isdigit():
        idx = int(order_col_index)
        idx = min(max(idx, 0), len(columns)-1)
        colname = columns[idx]
        col = getattr(Book, colname)
        if order_dir == "desc":
            base_query = base_query.order_by(desc(col))
        else:
            base_query = base_query.order_by(asc(col))
    else:
        base_query = base_query.order_by(desc(Book.created_at))

    # Paging
    rows = base_query.offset(start).limit(length).all()

    data = []
    for b in rows:
        data.append({
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "isbn": b.isbn or "",
            "published_year": b.published_year or "",
            "copies": b.copies,
            "created_at": b.created_at.strftime("%Y-%m-%d %H:%M") if b.created_at else ""
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })

@api_bp.route("/users", methods=["GET", "POST"])
def users_table():
    _admin_required()  # only admins can see users table

    draw, start, length, search_value, order_col_index, order_dir = _parse_dt_params()

    columns = ["id", "fullname", "username", "is_admin", "created_at", "updated_at"]

    base_query = db.session.query(User)
    total_records = db.session.scalar(db.select(func.count(User.id))) or 0

    if search_value:
        like = f"%{search_value}%"
        base_query = base_query.filter(User.username.ilike(like))

    filtered_records = base_query.with_entities(func.count(User.id)).scalar() or 0

    if order_col_index is not None and order_col_index.isdigit():
        idx = int(order_col_index)
        idx = min(max(idx, 0), len(columns)-1)
        colname = columns[idx]
        col = getattr(User, colname)
        if order_dir == "desc":
            base_query = base_query.order_by(desc(col))
        else:
            base_query = base_query.order_by(asc(col))
    else:
        base_query = base_query.order_by(desc(User.created_at))

    rows = base_query.offset(start).limit(length).all()

    data = []
    for u in rows:
        data.append({
            "id": u.id,
            "fullname": u.fullname,
            "username": u.username,
            "is_admin": bool(u.is_admin),
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S %p") if u.created_at else "",
            "updated_at": u.updated_at.strftime("%Y-%m-%d %H:%M:%S %p") if u.updated_at else ""
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })
