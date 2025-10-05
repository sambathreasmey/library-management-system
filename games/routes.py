from functools import wraps

from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from extensions import db
from models import Game

games_bp = Blueprint("games", __name__, url_prefix="")

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

@games_bp.get("/manage/games")
def list_games():
    login_required()
    return render_template("manage_games.html")

@games_bp.post("/manage/games/create")
@jwt_required_or_login
def create_game():
    login_required()
    user_id = get_jwt_identity()
    username = get_jwt().get("username")
    form = request.form
    name = form.get("name", "")

    if not name:
        flash("Game name are required.", "warning")
        return redirect(url_for("games.list_games"))

    try:
        game = Game(name=name, user_id=user_id,
                    created_by=username, updated_by=username)
        db.session.add(game)
        db.session.commit()
        flash("Game created.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating game: {e}", "danger")
    return redirect(url_for("games.list_games"))

@games_bp.post("/manage/games/<int:game_id>/update")
def update_game(game_id: int):
    admin_required()
    game = Game.query.get_or_404(game_id)
    form = request.form
    game.name = form.get("name", "").strip() or game.name

    try:
        db.session.commit()
        flash("Game updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating game: {e}", "danger")
    return redirect(url_for("games.list_games"))

@games_bp.post("/manage/games/<int:game_id>/delete")
def delete_game(game_id: int):
    admin_required()
    game = Game.query.get_or_404(game_id)
    try:
        db.session.delete(game)
        db.session.commit()
        flash("Game deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting game: {e}", "danger")
    return redirect(url_for("games.list_games"))