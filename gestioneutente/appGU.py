from flask import Flask, request, jsonify
from db import create_user, get_user

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user_id = create_user(data["username"], data["password"])
    return jsonify({"message": "User registered", "user_id": user_id})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = get_user(data["username"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user["password"] != data["password"]:
        return jsonify({"error": "Invalid credentials"}), 403
    
    return jsonify({"message": "Login successful", "user_id": user["user_id"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
