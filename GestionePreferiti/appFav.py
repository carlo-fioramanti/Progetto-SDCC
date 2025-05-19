from db_fav import add_to_favorites, show_favorites, remove_from_favorites, is_already_favorite
from flask import Flask, request, jsonify
import requests
import os
import json
import time
import boto3
from circuitbreaker import CircuitBreaker, CircuitBreakerError

#Configuriamo il bucket s3
s3_client = boto3.client('s3')
bucket_name = 'cacheapisdcc'

circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=Exception)
app = Flask(__name__)

API_ANALISI = os.getenv("ANALISI_URL", "http://analisi_dati:5001/analizza") 
API_RACCOLTA = os.getenv("RACCOLTA_URL", "http://raccolta_dati:5005/fetch_data")

def save_to_cache(dati):
    cache_key = "cache.json"

    if isinstance(dati, str):  
        dati = json.loads(dati)
    cache_data = {
        'data': dati,
        'timestamp': int(time.time())  # Timestamp corrente
    }
    s3_client.put_object(
        Bucket=bucket_name,
        Key=cache_key,
        Body=json.dumps(cache_data),
        ContentType='application/json'
    )
    print(f"Cache aggiornata", flush=True)

@app.route("/cache", methods=["GET"])
def get_from_cache():
    cache_key = "cache.json"  
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=cache_key)
        response_body = response['Body'].read()
        if not response_body:
            print("Il file è vuoto.", flush=True)
            return None 
        print(f"Contenuto grezzo della risposta: {response_body}", flush=True)
        cache_data = json.loads(response_body.decode('utf-8'))      
        

        # Verifichiamo se la cache è recente (5 minuti di validità)
        current_time = int(time.time())
        if current_time - cache_data['timestamp'] < 43.200:  # 12 ore
            print("Cache trovata e ancora valida.", flush=True)
            return cache_data['data']  # Restituisci tutti i dati nella cache
        else:
            print("La cache è scaduta.", flush=True)
            return None
    except s3_client.exceptions.NoSuchKey:
        print("Nessuna cache trovata.", flush=True)
        return None

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

    # Controllo che tutti i dati necessari siano forniti
    if not user_id or not fiume or not sottobacino:
        return jsonify({"error": "Dati incompleti"}), 400

    # Verifico che il fiume e il sottobacino esistano nel file fiumi_sottobacini
    if fiume not in fiumi_sottobacini:
        return jsonify({"error": f"Fiume '{fiume}' non trovato"}), 404
    
    if sottobacino not in fiumi_sottobacini[fiume]:
        return jsonify({"error": f"Sottobacino '{sottobacino}' non trovato nel fiume {fiume}"}), 404

    try:
        result = is_already_favorite(user_id, fiume, sottobacino)
        if result == 1:
            return jsonify({"status": 1, "message": f"Il fiume {fiume} e il sottobacino {sottobacino} sono già nei preferiti!"}), 200
        # Aggiungo il nuovo preferito
        add_to_favorites(user_id, fiume, sottobacino)
        return jsonify({"message": f"{sottobacino} aggiunto ai preferiti di {fiume}!"}), 200
    except CircuitBreakerError:
        return jsonify({"error": "Circuit Breaker attivato, il servizio non è disponibile."}), 503
    except Exception as e:
        return jsonify({"error": f"Errore durante l'aggiunta ai preferiti: {str(e)}"}), 500

@circuit_breaker
def raccolta_request():
    return requests.get(API_RACCOLTA)

@circuit_breaker
def analisi_request(payload):
    return requests.post(API_ANALISI, json=payload)

@app.route("/controllo_preferiti", methods=["POST"])
def controllo_preferiti():
    try:    
        data = request.json
        user_id = data.get("user_id")
        da_kafka = data.get("da_kafka", False)

        #Controlliamo la cache S3
        cached_data = get_from_cache()
        
        if cached_data:
            print("cache non vuota", flush=True)
            # Se la cache è valida, ritorniamo i dati dalla cache
            payload = {"dati": cached_data, "da_kafka": da_kafka}
        else:
            print("cache vuota", flush=True)
            # Se la cache è scaduta o non esiste, si fa richiesta all'API
            raccolta_response = raccolta_request()
            dati = raccolta_response.json()
            #Salva i dati nella cache S3
            save_to_cache(dati)
            payload = {"dati": dati, "da_kafka": da_kafka}
        

        # Analizziamo i dati
        analisi_response = analisi_request(payload)
        if analisi_response.status_code != 200:
            return jsonify({"error": "Errore nell'analisi dei dati"}), 500

        dati_fiumi = analisi_response.json()
        
        # Una volta ottenuto l'id dello user, faccio la query al db per prendere la lista dei preferiti
        favorites = show_favorites(user_id, dati_fiumi)

        return jsonify(favorites)
    except CircuitBreakerError:
        return jsonify({"error": "Circuit Breaker attivato, il servizio non è disponibile."}), 503
    except Exception as e:
        return jsonify({"error": f"Errore durante l'aggiunta ai preferiti: {str(e)}"}), 500
    
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