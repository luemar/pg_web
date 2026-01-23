import os, logging, sys
import sqlite3
from functools import wraps
from flask import session, redirect, url_for 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = "/var/www/pg_web/app.db"
CAM_TOKEN = "452710"

def get_db():
    conn = sqlite3.connect(
        DB_PATH, 
        timeout=10, 
        isolation_level=None, 
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=DELETE;")
    return conn

def email_is_allowed(email):
    db = get_db()
    try: 
        row = db.execute(
            "SELECT * FROM allowed_emails WHERE email=?",
            (email,)).fetchone()
        return row is not None
    finally:
        db.close()

def username_exists(username):
    db = get_db()
    try: 
        row = db.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)).fetchone()
        return row is not None
    finally:
        db.close()

def create_user(username, email):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users(username, email) VALUES(?, ?)",
            (username, email))
        db.commit()
    finally:
        db.close()

def email_already_registered(email):
    db = get_db()
    try:
        row = db.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)).fetchone()
        return row is not None
    finally:
        db.close()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth"))
        return f(*args, **kwargs)
    return wrapper

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if token != CAM_TOKEN:
            return jsonify({"error": "nicht autorisiert"}), 401
        return f(*args, **kwargs)
    return decorated
