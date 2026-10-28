import os
import time
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash

app = Flask(__name__)

def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "database"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "AppPass123!"),
        connection_timeout=5,
    )

def wait_for_db():
    for attempt in range(30):
        try:
            conn = connect_db()
            conn.close()
            print("Database is ready.", flush=True)
            return
        except Error as exc:
            print(f"Waiting for database ({attempt + 1}/30): {exc}", flush=True)
            time.sleep(2)
    raise RuntimeError("Database did not become ready in time")

@app.get("/health")
def health():
    return jsonify(status="ok", service="login")

@app.post("/api/login/")
def login():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    if not username or not password:
        return jsonify(message="Nom d'utilisateur et mot de passe requis."), 400
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify(message="Identifiants invalides."), 401
        return jsonify(message=f"Connexion réussie. Bienvenue {username} !"), 200
    except Error as exc:
        app.logger.exception("Erreur MySQL")
        return jsonify(message="Erreur lors de la connexion à la base de données."), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    wait_for_db()
    app.run(host="0.0.0.0", port=5000)
