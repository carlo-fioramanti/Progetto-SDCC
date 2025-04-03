from db_fav import add_to_favorites
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

def carica_fiumi_sottobacini():
    try:
        with open("fiumi_sottobacini.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Errore: il file 'fiumi_sottobacini.json' non è stato trovato.")
        return {}
    except json.JSONDecodeError:
        print("Errore: il file JSON non è valido.")
        return {}

fiumi_sottobacini = carica_fiumi_sottobacini()

@app.route("/fiumi", methods=["GET"])
def get_fiumi():
    return jsonify(list(fiumi_sottobacini.keys())), 200

@app.route("/sottobacini/<fiume>", methods=["GET"])
def get_sottobacini(fiume):
    if fiume not in fiumi_sottobacini:
        return jsonify({"error": "Fiume non trovato"}), 404
    return jsonify(fiumi_sottobacini[fiume]), 200

@app.route("/gestione_preferiti", methods=["POST"])
def gestione_preferiti():
    data = request.json
    user_id = data.get("user_id")
    fiume = data.get("fiume")
    sottobacino = data.get("sottobacino")

    # Controlla che tutti i dati necessari siano forniti
    if not user_id or not fiume or not sottobacino:
        return jsonify({"error": "Dati incompleti"}), 400

    # Verifica che il fiume e il sottobacino esistano nel file fiumi_sottobacini
    if fiume not in fiumi_sottobacini:
        return jsonify({"error": f"Fiume '{fiume}' non trovato"}), 404
    
    if sottobacino not in fiumi_sottobacini[fiume]:
        return jsonify({"error": f"Sottobacino '{sottobacino}' non trovato nel fiume {fiume}"}), 404

    try:
        # Aggiungi il fiume e il sottobacino ai preferiti dell'utente
        add_to_favorites(user_id, fiume, sottobacino)
        return jsonify({"message": f"{sottobacino} aggiunto ai preferiti di {fiume}!"}), 200
    except Exception as e:
        return jsonify({"error": f"Errore durante l'aggiunta ai preferiti: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)