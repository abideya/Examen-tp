import os
import time
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

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
    return jsonify(status="ok", service="signup")

@app.post("/api/signup/")
def signup():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    if len(username) < 3 or len(password) < 8:
        return jsonify(message="Le nom doit contenir au moins 3 caractères et le mot de passe au moins 8."), 400
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, generate_password_hash(password)),
        )
        conn.commit()
        cursor.close()
        return jsonify(message="Compte créé avec succès. Vous pouvez vous connecter."), 201
    except mysql.connector.IntegrityError:
        return jsonify(message="Ce nom d'utilisateur existe déjà."), 409
    except Error:
        app.logger.exception("Erreur MySQL")
        return jsonify(message="Erreur lors de la création du compte."), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    wait_for_db()
    app.run(host="0.0.0.0", port=5000)
