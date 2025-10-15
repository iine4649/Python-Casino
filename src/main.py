from flask import Flask, render_template, request, jsonify
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "userdata.json"
ASSETS_DIR = BASE_DIR / "assets"

app = Flask(__name__, template_folder=str(ASSETS_DIR), static_folder=str(ASSETS_DIR))

# Security baseline
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-in-prod"),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_ENABLED=True,
)

# HTTPS-related headers & policies (dev: will not actually provide TLS, use reverse-proxy in prod)
Talisman(app, force_https=False, strict_transport_security=True)

# CSRF and bcrypt
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)


def load_users():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("{}", encoding="utf-8")
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return {}


def save_users(users: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


@app.route("/")
def login():
    return render_template("secure_login.html")


@app.route("/sign-up")
def sign_up():
    return render_template("secure_sign_up.html")

@app.route("/lobby")
def lobby():
    return render_template("lobby.html")
    
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")






@app.route("/health")
def health():
    return {"status": "ok"}


@app.post("/api/sign-up")
@csrf.exempt  # If using forms without CSRF token; for production, include token in your form
def api_sign_up():
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password") or ""
    password_confirm = data.get("password_confirm") or data.get("password2") or ""

    if not user_id or not password:
        return jsonify({"ok": False, "error": "Missing user_id or password"}), 400
    if password != password_confirm:
        return jsonify({"ok": False, "error": "Passwords do not match"}), 400

    users = load_users()
    if user_id in users:
        return jsonify({"ok": False, "error": "User already exists"}), 409

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    users[user_id] = {"password_hash": hashed}
    save_users(users)
    return jsonify({"ok": True}), 201


@app.post("/api/sign-in")
@csrf.exempt  # If using forms without CSRF token; for production, include token in your form
def api_sign_in():
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = (data.get("user_id") or "").strip()
    password = data.get("password") or ""

    users = load_users()
    user = users.get(user_id)
    if not user:
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    if not bcrypt.check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
