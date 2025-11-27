from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import datetime
import os
import hashlib
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# MySQL connection config (update with your own DB credentials)
"""db_config = {
    "host": "localhost",
    "user": "root",           # your MySQL username
    "password": "Sanjana@0806",   # your MySQL password
    "database": "student_portal"
}"""

db_config = {
    "host": "mysql",
    "user": "root",           # your MySQL username
    "password": "Root@123",   # your MySQL password
    "database": "student_portal"
}

LOG_FILE = "logs/login_attempts.json"

def get_db_connection():
    """Create and return a new DB connection"""
    return mysql.connector.connect(**db_config)

def get_client_info(request):
    """Extract client information from request"""
    return {
        "ip_address": request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        "user_agent": request.headers.get('User-Agent', ''),
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    }

def log_login_attempt(username, success, client_info, failure_reason=None):
    """Log login attempt to JSON file"""
    log_entry = {
        "username": username,
        "timestamp": client_info["timestamp"],
        "ip_address": client_info["ip_address"],
        "user_agent": client_info["user_agent"],
        "success": success,
        "failure_reason": failure_reason,
        "session_id": hashlib.md5(f"{username}{client_info['timestamp']}".encode()).hexdigest()[:8]
    }
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Append to log file
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    
    logs.append(log_entry)
    
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    
    print(f"Logged: {username} - {'SUCCESS' if success else 'FAILED'} - {client_info['ip_address']}")

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    client_info = get_client_info(request)
    
    if not username or not password:
        log_login_attempt(username, False, client_info, "Missing credentials")
        return jsonify({"success": False, "message": "Username and password required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT password_hash FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and check_password_hash(result["password_hash"], password):
        log_login_attempt(username, True, client_info)
        return jsonify({"success": True, "message": "Login successful"})
    else:
        failure_reason = "User not found" if not result else "Invalid credentials"
        log_login_attempt(username, False, client_info, failure_reason)
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/api/logs')
def get_logs():
    """Endpoint to view current logs (for debugging)"""
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
        return jsonify(logs)
    except FileNotFoundError:
        return jsonify([])
    
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

"""from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import datetime
import os
import hashlib

app = Flask(__name__)
CORS(app)

# Mock student database
STUDENTS = {
    "ST001": "password123",
    "ST002": "mypassword",
    "ST003": "student123",
    "admin": "admin123"
}

LOG_FILE = "logs/login_attempts.json"

def get_client_info(request):
    return {
        "ip_address": request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        "user_agent": request.headers.get('User-Agent', ''),
        #"timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    }

def log_login_attempt(username, success, client_info, failure_reason=None):
    log_entry = {
        "username": username,
        "timestamp": client_info["timestamp"],
        "ip_address": client_info["ip_address"],
        "user_agent": client_info["user_agent"],
        "success": success,
        "failure_reason": failure_reason,
        "session_id": hashlib.md5(f"{username}{client_info['timestamp']}".encode()).hexdigest()[:8]
    }
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Append to log file
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    
    logs.append(log_entry)
    
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    
    print(f"Logged: {username} - {'SUCCESS' if success else 'FAILED'} - {client_info['ip_address']}")

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    client_info = get_client_info(request)
    
    if not username or not password:
        log_login_attempt(username, False, client_info, "Missing credentials")
        return jsonify({"success": False, "message": "Username and password required"}), 400
    
    if username in STUDENTS and STUDENTS[username] == password:
        log_login_attempt(username, True, client_info)
        return jsonify({"success": True, "message": "Login successful"})
    else:
        failure_reason = "Invalid credentials"
        if username not in STUDENTS:
            failure_reason = "User not found"
        log_login_attempt(username, False, client_info, failure_reason)
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/api/logs')
def get_logs():try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
        return jsonify(logs)
    except FileNotFoundError:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)"""