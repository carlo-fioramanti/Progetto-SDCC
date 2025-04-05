from flask import Flask, request, jsonify
from db import create_user, get_user
import bcrypt

app = Flask(__name__)


def hash_password(password: str) -> str:
    # Genera un salt e hash
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Salvo l'hash come stringa nel DB


def check_password(plain_password: str, hashed_password_from_db: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_from_db.encode('utf-8'))


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_password = hash_password(data["password"])
    user_id = create_user(data["username"], hashed_password)
    return jsonify({"message": "User registered", "user_id": user_id})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = get_user(data["username"])

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not check_password(data["password"], user["password"]):
        return jsonify({"error": "Invalid credentials"}), 403
    
    return jsonify({"message": "Login successful", "user_id": user["user_id"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
