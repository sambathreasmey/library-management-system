# config.py
import os
from pathlib import Path
from urllib.parse import quote_plus
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# 1. Try loading production .env from parent dir first
prod_env_path = BASE_DIR.parent / ".env"
local_env_path = BASE_DIR / ".env"
if prod_env_path.exists():
    print(f"Attempting to load production .env from: {prod_env_path}")
    load_dotenv(dotenv_path=prod_env_path, override=False)
else:
    print(f"Loading local .env from: {local_env_path}")
    load_dotenv(dotenv_path=local_env_path, override=True)

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

    password_encoded = quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ""
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{MYSQL_USER}:{password_encoded}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 280,
        "pool_timeout": 30
    }
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FS_CACHE_DIR = os.path.expanduser('~/flask_cache')
    CACHE_TYPE = 'simple'          # use 'simple' if only 1 worker 'filesystem' if only 2 worker
    CACHE_DIR = FS_CACHE_DIR
    CACHE_DEFAULT_TIMEOUT = 180
    CACHE_THRESHOLD = 5000
    
    JINJA_CACHE_DIR = os.path.expanduser('~/jinja_cache')
    JINJA_BYTECODE_PATTERN = '%s.cache'
