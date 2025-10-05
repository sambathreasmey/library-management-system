from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sqlalchemy import func
from extensions import db
from models import Book, User

books_bp = Blueprint("books", __name__, url_prefix="")

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
def dashboard():
    login_required()
    total_books = db.session.scalar(db.select(func.count(Book.id))) or 0
    total_copies = db.session.scalar(db.select(func.coalesce(func.sum(Book.copies), 0))) or 0
    total_users = db.session.scalar(db.select(func.count(User.id))) or 0  # <-- NEW
    latest_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()
    return render_template(
        "dashboard.html",
        total_books=total_books,
        total_copies=total_copies,
        total_users=total_users,       # <-- NEW
        latest_books=latest_books
    )

@books_bp.get("/manage/books")
def list_books():
    login_required()
    return render_template("manage_books.html")

@books_bp.post("/manage/books/create")
@jwt_required_or_login
def create_book():
    admin_required()
    form = request.form
    title = form.get("title", "").strip()
    author = form.get("author", "").strip()
    isbn = form.get("isbn", "").strip() or None
    published_year = form.get("published_year")
    copies = form.get("copies")

    if not title or not author:
        flash("Title and Author are required.", "warning")
        return redirect(url_for("books.list_books"))

    try:
        year_val = int(published_year) if published_year else None
        copies_val = int(copies) if copies else 1
        book = Book(title=title, author=author, isbn=isbn,
                    published_year=year_val, copies=copies_val)
        db.session.add(book)
        db.session.commit()
        flash("Book created.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating book: {e}", "danger")
    return redirect(url_for("books.list_books"))

@books_bp.post("/manage/books/<int:book_id>/update")
def update_book(book_id: int):
    admin_required()
    book = Book.query.get_or_404(book_id)
    form = request.form
    book.title = form.get("title", "").strip() or book.title
    book.author = form.get("author", "").strip() or book.author
    isbn = form.get("isbn", "").strip()
    book.isbn = isbn or None
    py = form.get("published_year")
    cp = form.get("copies")

    try:
        book.published_year = int(py) if py else None
        book.copies = int(cp) if cp else book.copies
        db.session.commit()
        flash("Book updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating book: {e}", "danger")
    return redirect(url_for("books.list_books"))

@books_bp.post("/manage/books/<int:book_id>/delete")
def delete_book(book_id: int):
    admin_required()
    book = Book.query.get_or_404(book_id)
    try:
        db.session.delete(book)
        db.session.commit()
        flash("Book deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting book: {e}", "danger")
    return redirect(url_for("books.list_books"))
