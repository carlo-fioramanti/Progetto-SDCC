from flask import Flask, request, jsonify
from confluent_kafka import Producer
import json

producer_config = {
    'bootstrap.servers': 'kafka:9092'
}

producer = Producer(producer_config)

app = Flask(__name__)

def notifica(fiume, sottobacino, fascia):
    """Invia una notifica Kafka se il livello dell'acqua è in fascia arancione o rossa."""
    messaggio = {
        "fiume": fiume,
        "sottobacino": sottobacino,
        "fascia": fascia
    }
    producer.produce("allerta_fiumi", json.dumps(messaggio).encode('utf-8'))
    producer.flush()

@app.route("/analizza", methods=["POST"])
def analizza():
    dati = request.json

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
                    notifica(nome_bacino, nome_sottobacino, fascia)
                elif valore_osservazione < fasce["rossa"]:
                    fascia = "rossa"
                    notifica(nome_bacino, nome_sottobacino, fascia)
                else:
                    fascia = "oltre il rosso"

                dati_fiumi.append({
                    "fiume": nome_bacino,
                    "sottobacino": nome_sottobacino,
                    "fascia": fascia
                })

    return jsonify(dati_fiumi)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
