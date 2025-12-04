import os, time, sys, traceback
import sqlite3
from functools import wraps
from flask import session, redirect, url_for 

def get_db():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

def email_is_allowed(email):
    db = get_db()
    row = db.execute("SELECT * FROM allowed_emails WHERE email=?", (email,)).fetchone()
    return row is not None

def username_exists(username):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    return row is not None

def create_user(username, email):
    db = get_db()
    db.execute("INSERT INTO users(username, email) VALUES(?, ?)", (username, email))
    db.commit()

# ---------------------------
# Login protection decorator
# ---------------------------

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth"))
        return f(*args, **kwargs)
    return wrapper
