from flask import Flask, render_template, request, session, redirect, url_for, make_response, send_from_directory
from flask import flash
from datetime import datetime, timedelta
from openpyxl import load_workbook
import pandas as pd
import os, time, sys, traceback, re, pwd
import sqlite3
from functools import wraps
from dateutil.relativedelta import relativedelta
from functions import (debug_log, load_excel_file, calculate_average_age, calculate_indiv_age, excel_table)
from functions_login import get_db, email_is_allowed, username_exists, create_user, login_required, email_already_registered
from config import SERVER_START_TIME,  GROUP_PASSWORD, EXCEL_FILE_PATH, SHARED_FOLDER, DEBUG_ENABLED

app = Flask(__name__, template_folder='templates')
app.secret_key = 'Golf3001'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

last_file_check = 0
last_modified_time = 0
cached_datetime_dict = {}
cached_string_dict = {}

@app.route('/')
def index():
    debug_log("Index route accessed")
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():

    if request.method == "POST":
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()

        print(f"DEBUG: Email entered: {email}")
        print(f"DEBUG: Username entered: {username}")
    
        if not username:
            flash("Benutzername falsch oder fehlend", "error")
            return redirect(url_for('auth'))

        if not email_is_allowed(email):
            flash("Email Adresse unbekannt", "error")
            return redirect(url_for('auth'))
    
        email_registered = email_already_registered(email)
        username_exists_check = username_exists(username)
        
        print(f"DEBUG: Email already registered? {email_registered}")
        print(f"DEBUG: Username exists? {username_exists_check}")
        
        if email_registered:        
            if not username_exists_check:
                print("DEBUG: Should flash 'falscher Benutzername'")
                flash("Falscher Benutzername", "error")
            else:
                print("DEBUG: Should flash 'Benutzername schon registriert'")
                flash("Benutzername schon registriert, jetzt einloggen", "error")
            return redirect(url_for('auth'))

        try:
            create_user(username, email)
            flash("Registrierung erfolgreich", "success")    
            return redirect(url_for('auth'))
        except Exception as e:
            print(f"Benutzer kann nicht registriert werden: {e}")
            flash("Benutzer kann nicht registriert werden", "error")
            return redirect(url_for('auth'))

    return render_template('auth.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if not username_exists(username):
            flash("Benutzername unbekannt", "error")
            return redirect(url_for('auth'))

        if password != GROUP_PASSWORD:
            flash("Passwort falsch", "error")
            return redirect(url_for('auth'))

        session["logged_in"] = True
        session["username"] = username
        return redirect(url_for('private'))
    
    return render_template('auth.html')

@app.route('/private')
def private():
    if not session.get("logged_in"):
        flash("Bitte zuerst einloggen", "error")
        return redirect(url_for('auth'))
    return render_template('private.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/test_1')
def test_1():
    return render_template('test_1.html')

@app.route('/members_corner')
@login_required
def members_corner():
    return redirect(url_for('auth'))

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    return f"ERROR: {str(e)}", 500

@app.route('/program')
def program():
    debug_log("Program route accessed")
    return render_template('program.html')

@app.route('/special', methods=['GET', 'POST'])
def special():
    debug_log(f"/special route accessed with method: {request.method}")
    
    # Always reset caching variables to force reload
    global last_file_check, last_modified_time
    last_file_check = 0
    last_modified_time = 0

    if request.method == 'POST':
        try:
            name = request.form['name']
            debug_log(f"Form submitted with name: {name}")

            # Reload data from Excel to ensure we have the latest
            members_dict_datetime, members_dict_string = load_excel_file(force_reload=True)

            if name in members_dict_datetime:
                birthdate = members_dict_datetime[name]
                session['result_2'] = calculate_indiv_age(birthdate)
                session['input_name'] = name
                session.pop('error_message', None)  # Clear any previous error
                debug_log(f"Found birthdate for {name}: {birthdate}")

            else:
                session['error_message'] = "Name ungueltig"
                session.pop('result_2', None)  # Clear any previous result
                session['input_name'] = name
                debug_log(f"Invalid name: {name}")

        except Exception as e:
            debug_log(f"Error in /special POST: {e}")
            traceback.print_exc()
            session['error_message'] = f"An error occurred: {str(e)}"
            session.pop('result_2', None)  # Clear any previous result

        return redirect(url_for('special'))

    # Handle GET request
    if request.method == 'GET':
        debug_log("Processing GET request for /special")

        # Initialize result variables
        result_1 = "Error calculating average age"
        result_2 = None
        result_3 = "Error loading table"
        error_message = None
        input_name = None

        # Always reload data for each page load
        try:
            # Calculate average age
            debug_log("About to calculate average age")
            result_1 = calculate_average_age()
            debug_log(f"Calculated average age: {result_1}")
        except Exception as e:
            debug_log(f"Error calculating average age: {e}")
            traceback.print_exc()
            result_1 = f"Error calculating age: {str(e)}"

        # Get session data
        result_2 = session.get('result_2')
        error_message = session.get('error_message')
        input_name = session.get('input_name')
        
        debug_log(f"Session data - result_2: {result_2}, error_message: {error_message}, input_name: {input_name}")
        
        try:
            debug_log("About to generate Excel table")
            result_3 = excel_table()
            debug_log("Successfully generated Excel table")
        except Exception as e:
            debug_log(f"Error generating table: {e}")
            traceback.print_exc()
            result_3 = f"Error loading table: {str(e)}"

        # Clear session variables after rendering
        session.pop('result_2', None)
        session.pop('error_message', None)
        session.pop('input_name', None)

        debug_log("Rendering special.html template with results")
        return render_template(
            'special.html',
            result_1=result_1,
            result_2=result_2,
            result_3=result_3,
            error_message=error_message,
            input_name=input_name
        )

@app.route('/gallery')
def gallery():
    debug_log("Gallery route accessed")
    folder = app.static_folder
    
    images = []
    for f in os.listdir(folder):
        if f.startswith("Folie") and f.lower().endswith(".jpg"):
            images.append((f))

     # Sort numerically: Folie1, Folie2, Folie10 (not alphabetically)
    images.sort(key=lambda x: int(x.replace("Folie", "").replace(".jpg", "")))

    return render_template('gallery.html', images=images)
    
@app.route('/debug')
def debug_route():
    """A route to test function execution directly"""
    debug_log("Debug route accessed")
    
    output = []
    
    try:
        output.append("Testing load_excel_file()...")
        members_dict_datetime, members_dict_string = load_excel_file(force_reload=True)
        output.append(f"✓ load_excel_file() SUCCESS! Loaded {len(members_dict_datetime)} members")
        
        output.append("\nTesting calculate_average_age()...")
        avg_age = calculate_average_age()
        output.append(f"✓ calculate_average_age() SUCCESS! Average age: {avg_age}")
        
        output.append("\nTesting excel_table()...")
        table = excel_table()
        table_len = len(table) if table else 0
        output.append(f"✓ excel_table() SUCCESS! Generated table of {table_len} characters")
        
        return "<h1>Debug Tests</h1><pre>" + "\n".join(output) + "</pre>"
    except Exception as e:
        output.append(f"✗ ERROR: {str(e)}")
        return "<h1>Debug Tests Failed</h1><pre>" + "\n".join(output) + "</pre>"

@app.route('/shared_files/<path:filename>')
def shared_files(filename):
    """Serve files from the SHARED_FOLDER directory."""
    debug_log(f"Attempting to serve shared file: {filename}")
    return send_from_directory('/mnt/pg_web_data/slide_show', filename, as_attachment=False)

@app.route('/refresh_data')
def refresh_data():
    """Force refresh all cached data"""
    debug_log("refresh_data route accessed")
    try:
        global last_file_check, last_modified_time, cached_datetime_dict, cached_string_dict
        # Reset all caching variables
        last_file_check = 0
        last_modified_time = 0
        cached_datetime_dict = {}
        cached_string_dict = {}
        
        # Try to reload the data
        members_dict_datetime, members_dict_string = load_excel_file(force_reload=True)
        
        return f"Data refreshed successfully. Loaded {len(members_dict_datetime)} members. <a href='/special'>Go to special page</a>"
    except Exception as e:
        debug_log(f"Error refreshing data: {e}")
        traceback.print_exc()
        return f"Error refreshing data: {str(e)}"

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Add a route to check file modification time
@app.route('/check_excel_update')
def check_excel_update():
    """Check if the Excel file has been updated."""
    debug_log("check_excel_update route accessed")
    try:
        if os.path.exists(EXCEL_FILE_PATH):
            mod_time = os.path.getmtime(EXCEL_FILE_PATH)
            mod_time_str = datetime.fromtimestamp(mod_time).strftime('%d.%m.%Y')

            # Reset any caching
            global last_file_check, last_modified_time
            last_file_check = 0
            last_modified_time = 0

            return f"Excel file last modified: {mod_time_str}"
        else:
            return f"Excel file not found at {EXCEL_FILE_PATH}"
    except Exception as e:
        debug_log(f"Error checking file: {e}")
        traceback.print_exc()
        return f"Error checking file: {str(e)}"

@app.context_processor
def utility_processor():
    return {
            'version': str(time.time()),
            'timestamp': SERVER_START_TIME
    }

if __name__ == '__main__':
    debug_log("Starting Flask application...")
    debug_log(f"Excel file path: {EXCEL_FILE_PATH}")

    # Check if file exists and is accessible
    if os.path.exists(EXCEL_FILE_PATH):
        mod_time = os.path.getmtime(EXCEL_FILE_PATH)
        debug_log(f"Excel file found! Last modified: {datetime.fromtimestamp(mod_time).strftime('%d.%m.%Y')}")
        
        # Try to load the Excel file during startup
        try:
            debug_log("Testing Excel file loading during startup...")
            members_dict_datetime, members_dict_string = load_excel_file(force_reload=True)
            debug_log(f"Successfully loaded {len(members_dict_datetime)} members during startup")
        except Exception as e:
            debug_log(f"Error pre-loading Excel file during startup: {e}")
            traceback.print_exc()
    else:
        debug_log(f"WARNING: Excel file not found at: {EXCEL_FILE_PATH}")
        debug_log("Available files in shared folder:")
        try:
            files = os.listdir(SHARED_FOLDER)
            for file in files:
                debug_log(f"  - {file}")
        except Exception as e:
            debug_log(f"Error listing shared folder: {e}")
            traceback.print_exc()

    # Create static folder if it doesn't exist
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if not os.path.exists(static_folder):
        debug_log(f"Creating missing static folder at: {static_folder}")
        os.makedirs(static_folder)

    # Create script.js in static folder if it doesn't exist
    script_js_path = os.path.join(static_folder, 'script.js')
    if not os.path.exists(script_js_path):
        debug_log(f"Creating missing script.js file at: {script_js_path}")
        with open(script_js_path, 'w') as f:
            f.write('''// script.js - Required for the special.html page

// Function to force a refresh of the page with a cache-busting parameter
function refreshData() {
    // Add a timestamp to prevent caching
    const timestamp = new Date().getTime();
    window.location.href = '/special?t=' + timestamp;
}

// Function to check if Excel file has been updated
function checkExcelUpdate() {
    fetch('/check_excel_update')
        .then(response => response.text())
        .then(data => {
            alert(data);
        })
        .catch(error => {
            console.error('Error checking Excel update:', error);
        });
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add any page initialization code here
    console.log('Script loaded successfully');
});''')

    debug_log("Adding new debug route at /debug")
    debug_log("Starting Flask web server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
