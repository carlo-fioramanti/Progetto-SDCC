from datetime import datetime, time
from flask import Flask, request, jsonify
from confluent_kafka import Producer, KafkaException
import json
import requests


producer_config = {
    'bootstrap.servers': 'kafka:9092'
}

producer = Producer(producer_config)

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


@app.route("/segnala", methods=["POST"])
def segnala():
    data = request.json
    fiume = data.get("fiume")
    sottobacino = data.get("sottobacino")
    fascia = data.get("fascia")
        
        
    # Invia la notifica su Kafka
    messaggio = {
        "fiume": fiume,
        "sottobacino": sottobacino,
        "fascia": fascia,
        "timestamp": datetime.now().strftime('%Y-%m-%d'),
        "tipo": "segnalazione utente"
    }

    topic_name = f"{fiume.replace(' ', '_').lower()}-{sottobacino.replace(' ', '_').lower()}"

    tries = 0
    max_retries = 3
    while tries < max_retries:
        try:
            producer.produce(topic_name, json.dumps(messaggio).encode('utf-8'))
            producer.flush()
            return jsonify({"message": "Notifica inviata con successo"}), 200
        except KafkaException as e:
            if "_UNKNOWN_TOPIC" in str(e):
                print(f"❗ Topic non pronto, retry tra 1s... ({tries+1}/{max_retries})", flush=True)
                time.sleep(1)
                tries += 1
            else:
                print(f"❌ Errore Kafka: {e}", flush=True)
                break
            
    




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
