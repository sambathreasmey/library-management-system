from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sqlalchemy import func, or_, asc, desc
from extensions import db
from models import Book, User

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

@api_bp.route("/books", methods=["GET", "POST"])
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
