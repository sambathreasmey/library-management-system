from flask import Flask, redirect, url_for, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from config import Config
from extensions import db, jwt
from models import User
import os
from jinja2 import FileSystemBytecodeCache

def create_app():
    cache_dir = '/tmp/jinja_cache'
    os.makedirs(cache_dir, exist_ok=True)  # ✅ creates if missing

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.jinja_env.bytecode_cache = FileSystemBytecodeCache(cache_dir, '%s.cache')
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    @app.context_processor
    def inject_claims():
        # Defaults for anonymous users
        ctx = {
            "is_admin": False,
            "current_user_id": None,
            "username": None,
            "token_expiry": None,
        }
        try:
            # ✅ Only read identity/claims if a JWT is present; won't raise for anonymous
            verify_jwt_in_request(optional=True)
            claims = get_jwt() or {}
            ctx["current_user_id"] = get_jwt_identity()
            ctx["is_admin"] = bool(claims.get("is_admin", False))
            # We stored username in additional_claims at login
            ctx["username"] = claims.get("username")
            # Keep the exp so your timer still works
            if "exp" in claims:
                ctx["token_expiry"] = claims["exp"]
        except Exception:
            # No valid token: leave defaults
            pass

        return ctx

    @jwt.unauthorized_loader
    def _unauthorized(msg):
        wants_json = request.path.startswith("/api") or request.accept_mimetypes.best == "application/json"
        if wants_json:
            return {"msg": msg}, 401
        return redirect(url_for("auth.login_page"))

    @jwt.invalid_token_loader
    def _invalid(msg):
        wants_json = request.path.startswith("/api") or request.accept_mimetypes.best == "application/json"
        if wants_json:
            return {"msg": msg}, 401
        return redirect(url_for("auth.login_page"))

    @jwt.expired_token_loader
    def _expired(jwt_header, jwt_payload):
        # Always try silent refresh when ACCESS token is expired
        if jwt_payload.get("type") == "access":
            nxt = request.full_path if request.query_string else request.path
            return redirect(url_for("auth.refresh_silent", next=nxt))
        # If the REFRESH itself expired -> go to login
        wants_json = request.path.startswith("/api") or request.accept_mimetypes.best == "application/json"
        if wants_json:
            return {"msg": "Session expired. Please log in again."}, 401
        return redirect(url_for("auth.login_page"))

    @jwt.revoked_token_loader
    def _revoked(jwt_header, jwt_payload):
        wants_json = request.path.startswith("/api") or request.accept_mimetypes.best == "application/json"
        if wants_json:
            return {"msg": "Token has been revoked"}, 401
        return redirect(url_for("auth.login_page"))

    # Blueprints
    from auth.routes import auth_bp
    from booking.routes import books_bp
    from users.routes import users_bp
    from api.routes import api_bp
    from customers.routes import customers_bp
    from games.routes import games_bp
    from banks.routes import banks_bp
    from transactions.routes import transactions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(banks_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return redirect(url_for("booking.dashboard"))

    # Initialize DB & seed an admin user (only if empty)
    with app.app_context():
        db.create_all()
        if not User.query.first():
            User.create_admin_if_missing()

    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=False, port=5000)
