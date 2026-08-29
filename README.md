# Task 4 - Secure Local API Configuration

A RESTful API built using Python Flask featuring JWT authentication, role-based access control (RBAC), HTTPS encryption, and request logging.

## Security Overview
- **HTTPS Enforcement**: Secured with self-signed SSL certificates (`cert.pem`, `key.pem`).
- **JWT Authentication**: Secured endpoints require a valid Bearer token.
- **RBAC**: Supports `admin` and `user` roles.
- **Audit Logging**: Captures request timestamp, client IP, method, endpoint, and status codes into `app_requests.log`.

## How to Run
1. Run application: `python app.py`
2. Local Endpoint: `https://127.0.0.1:5000`

## Endpoints
- `POST /login` -> Public login (`{"username": "admin", "password": "admin123"}`)
- `GET /devices` -> Retrieve devices (User/Admin)
- `POST /devices` -> Add device (Admin only)
- `DELETE /devices/<id>` -> Delete device (Admin only)
- `GET /logs` -> View log entries (Admin only)