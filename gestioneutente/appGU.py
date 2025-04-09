from flask import Flask, request, jsonify
from db import create_user, get_user
import bcrypt
from circuitbreaker import CircuitBreaker, CircuitBreakerError

app = Flask(__name__)

circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=Exception)

def hash_password(password: str) -> str:
    # Genera un salt e hash
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Salvo l'hash come stringa nel DB


def check_password(plain_password: str, hashed_password_from_db: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_from_db.encode('utf-8'))


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_password = hash_password(data["password"])  # Assumendo che tu abbia una funzione hash_password
    try:
        user_id = create_user(data["username"], hashed_password)
        return jsonify({"message": "User registered", "user_id": user_id})
    except CircuitBreakerError:
        return jsonify({"error": "Circuit Breaker attivato, il servizio di registrazione non è disponibile."}), 503
    except Exception as e:
        return jsonify({"error": f"Errore durante la registrazione: {str(e)}"}), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    try:
        user = get_user(data["username"])
    except CircuitBreakerError:
        return jsonify({"error": "Circuit Breaker attivato, il servizio di login non è disponibile."}), 503
    except Exception as e:
        return jsonify({"error": f"Errore durante il recupero dell'utente: {str(e)}"}), 500

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not check_password(data["password"], user["password"]):  # Assumendo che tu abbia una funzione check_password
        return jsonify({"error": "Invalid credentials"}), 403
    
    return jsonify({"message": "Login successful", "user_id": user["user_id"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
