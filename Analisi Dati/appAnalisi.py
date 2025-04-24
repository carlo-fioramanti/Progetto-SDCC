from flask import Flask, request, jsonify
from confluent_kafka import Producer, KafkaException
import json
from datetime import datetime
import time




producer_config = {
    'bootstrap.servers': 'kafka:9092'
}

producer = Producer(producer_config)

app = Flask(__name__)


def notifica(fiume, sottobacino, fascia):
    topic_name = f"{fiume.replace(' ', '_').lower()}-{sottobacino.replace(' ', '_').lower()}"
    print(f"Produco su topic: {topic_name}", flush=True)  # 👈 log utile

    messaggio = {
        "fiume": fiume,
        "sottobacino": sottobacino,
        "fascia": fascia,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M')
    }

    tries = 0
    max_retries = 3
    while tries < max_retries:
        try:
            producer.produce(topic_name, json.dumps(messaggio).encode('utf-8'))
            producer.flush()
            return
        except KafkaException as e:
            if "_UNKNOWN_TOPIC" in str(e):
                print(f"❗ Topic non pronto, retry tra 1s... ({tries+1}/{max_retries})", flush=True)
                time.sleep(1)
                tries += 1
            else:
                print(f"❌ Errore Kafka: {e}", flush=True)
                break




@app.route("/analizza", methods=["POST"])
def analizza():
    payload = request.json
    dati = payload.get("dati", payload)
    da_kafka = payload.get("da_kafka", False)

    fasce = {
        "verde": 3.0,
        "gialla": 6.0,
        "arancione": 9.0,
        "rossa": 12.0
    }

    dati_fiumi = []

    for data_per_data in dati.values():
        for bacino in data_per_data["bacino"]:
            nome_bacino = bacino["nome_bacino"]
            
            for sottobacino in bacino["sottobacino"]:
                nome_sottobacino = sottobacino["nomeSottobacino"]
                valore_osservazione = float(sottobacino["osservazione"]["valore"])

                if valore_osservazione < fasce["verde"]:
                    fascia = "verde"
                elif valore_osservazione < fasce["gialla"]:
                    fascia = "gialla"
                elif valore_osservazione < fasce["arancione"]:
                    fascia = "arancione"
                    if da_kafka:
                        notifica(nome_bacino, nome_sottobacino, fascia)
                elif valore_osservazione < fasce["rossa"]:
                    fascia = "rossa"
                    if da_kafka:
                        notifica(nome_bacino, nome_sottobacino, fascia)
                else:
                    fascia = "oltre il rosso"
                    if da_kafka:
                        notifica(nome_bacino, nome_sottobacino, fascia)

                dati_fiumi.append({
                    "fiume": nome_bacino,
                    "sottobacino": nome_sottobacino,
                    "fascia": fascia
                })

    return jsonify(dati_fiumi)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
