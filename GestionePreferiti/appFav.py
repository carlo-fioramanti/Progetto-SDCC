from db_fav import add_to_favorites, remove_from_favorites, show_favorites
# from db_fav import show_favorites
from flask import Flask, request, jsonify
import requests
import os
import json

API_ANALISI = os.getenv("ANALISI_URL", "http://analisi-dati:5001/analizza") 
API_RACCOLTA = os.getenv("RACCOLTA_URL", "http://raccolta-dati:5005/fetch_data")

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

@app.route("/controllo_preferiti", methods=["POST"])
def controllo_preferiti():
    data =  request.json
    user_id = data.get("user_id")

    # Step 1: Ottieni i dati grezzi dai sensori dalla raccolta
    raccolta_response = requests.get(API_RACCOLTA)
    if raccolta_response.status_code != 200:
        return jsonify({"error": "Errore nel recupero dei dati dalla raccolta"}), 500
    
    dati = raccolta_response.json()

    analisi_response = requests.post(API_ANALISI, json=dati)
    if analisi_response.status_code != 200:
        return jsonify({"error": "Errore nell'analisi dei dati"}), 500

    dati_fiumi = analisi_response.json()
    # Una volta ottenuto l'id dello user, faccio la query al db per prendere la lista dei preferiti
    favorites = show_favorites(user_id, dati_fiumi)
    # return favorites
    return jsonify(favorites)

@app.route("/rimozione_preferiti", methods=["DELETE"])
def rimuovi_preferito():
    data = request.json
    user_id = data.get("user_id")
    fiume = data.get("fiume")
    sottobacino = data.get("sottobacino")

    if not user_id or not fiume or not sottobacino:
        return jsonify({"error": "Dati incompleti"}), 400

    try:
        remove_from_favorites(user_id, fiume, sottobacino)
        return jsonify({"message": f"{sottobacino} rimosso dai preferiti di {fiume}!"}), 200
    except Exception as e:
        return jsonify({"error": f"Errore durante la rimozione: {str(e)}"}), 500




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)