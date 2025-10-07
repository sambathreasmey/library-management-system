# config.py
import os
from pathlib import Path
from urllib.parse import quote_plus
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env only if not in production
if os.getenv("FLASK_ENV") != "production":
    print("FLASK_ENV is set to production")
    load_dotenv(BASE_DIR / ".env")
print("FLASK_ENV ================================================")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_COOKIE_SECURE = False
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/"

    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB = os.getenv("MYSQL_DB")
    print("MYSQL_DB >>>>>>>>>>>>>>>>>>>>>> ", MYSQL_DB)

    password_encoded = quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ""
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{MYSQL_USER}:{password_encoded}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# import os
# from pathlib import Path
# from urllib.parse import quote_plus
#
# from dotenv import load_dotenv
# from datetime import timedelta
#
# BASE_DIR = Path(__file__).resolve().parent
# print(BASE_DIR)
# load_dotenv(BASE_DIR / ".env")
#
# class Config:
#     SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
#     JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
#     JWT_COOKIE_SECURE = False
#     JWT_TOKEN_LOCATION = ["cookies", "headers"]  # <- add "headers"
#     JWT_COOKIE_CSRF_PROTECT = False              # keep forms simple in dev
#     JWT_COOKIE_SAMESITE = "Lax"
#     # Token lifetimes
#     # JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
#     JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
#     # JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)
#     JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
#
#     # IMPORTANT: make sure both cookies are sent to all paths
#     JWT_ACCESS_COOKIE_PATH = "/"
#     JWT_REFRESH_COOKIE_PATH = "/"
#
#     MYSQL_USER = os.getenv("MYSQL_USER")
#     print("MYSQL_USER", MYSQL_USER)
#     MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
#     print("MYSQL_PASSWORD", MYSQL_PASSWORD)
#     MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
#     print("MYSQL_HOST", MYSQL_HOST)
#     MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")  # << default 3307
#     print("MYSQL_PORT", MYSQL_PORT)
#     MYSQL_DB = os.getenv("MYSQL_DB")
#     print("MYSQL_DB", MYSQL_DB)
#
#     password_encoded = quote_plus(MYSQL_PASSWORD)
#     SQLALCHEMY_DATABASE_URI = (
#         f"mysql+mysqlconnector://{MYSQL_USER}:{password_encoded}"
#         f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False