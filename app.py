import datetime
import logging
from functools import wraps
from flask import Flask, jsonify, request
import jwt

app = Flask(__name__)

SECRET_KEY = "my_super_secret_jwt_key"
app.config["SECRET_KEY"] = SECRET_KEY

# Set up dedicated logger for request tracking
logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("app_requests.log")
formatter = logging.Formatter("%(asctime)s | %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Automatically log every incoming HTTP request and response status
@app.after_request
def log_request_info(response):
    log_msg = f"IP: {request.remote_addr} | Method: {request.method} | Path: {request.path} | Status: {response.status_code}"
    logger.info(log_msg)
    return response

# In-Memory Database Resource
devices_db = {
    1: {"id": 1, "name": "Router-A", "status": "active"},
    2: {"id": 2, "name": "Switch-B", "status": "inactive"}
}

# Role-Based Token Authentication Decorator
def token_required(required_role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "Authorization token is missing"}), 401
            
            try:
                if token.startswith("Bearer "):
                    token = token.split(" ")[1]
                data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            except Exception as e:
                return jsonify({"error": f"Invalid or expired token: {str(e)}"}), 401

            if required_role and data.get("role") != required_role:
                return jsonify({"error": "Forbidden: Insufficient privileges"}), 403

            return f(data, *args, **kwargs)
        return decorated
    return decorator

# --- ENDPOINTS ---

@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json() or {}
    username = auth.get("username")
    password = auth.get("password")

    if username == "admin" and password == "admin123":
        role = "admin"
    elif username == "user" and password == "user123":
        role = "user"
    else:
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({"token": token})

@app.route("/devices", methods=["GET"])
@token_required()
def get_devices(current_user):
    return jsonify(list(devices_db.values()))

@app.route("/devices", methods=["POST"])
@token_required(required_role="admin")
def create_device(current_user):
    data = request.get_json() or {}
    new_id = max(devices_db.keys(), default=0) + 1
    new_device = {
        "id": new_id,
        "name": data.get("name", f"Device-{new_id}"),
        "status": data.get("status", "active")
    }
    devices_db[new_id] = new_device
    return jsonify(new_device), 201

@app.route("/devices/<int:device_id>", methods=["DELETE"])
@token_required(required_role="admin")
def delete_device(current_user, device_id):
    if device_id in devices_db:
        del devices_db[device_id]
        return jsonify({"message": f"Device {device_id} deleted successfully"})
    return jsonify({"error": "Device not found"}), 404

@app.route("/logs", methods=["GET"])
@token_required(required_role="admin")
def get_logs(current_user):
    try:
        with open("app_requests.log", "r") as f:
            logs = f.readlines()
        return jsonify({"logs": [line.strip() for line in logs[-30:]]})
    except FileNotFoundError:
        return jsonify({"logs": []})

if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'), host="127.0.0.1", port=5000)