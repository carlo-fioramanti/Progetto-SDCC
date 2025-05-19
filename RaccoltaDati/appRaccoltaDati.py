import time
import requests
import os
from flask import Flask
from datetime import timedelta
from circuitbreaker import CircuitBreaker, CircuitBreakerError

circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=Exception)


API_REGIONE = "https://allertameteo.regione.emilia-romagna.it/datiTempoReale-prevPiog-portlet/get-bollettino-monitoraggio"  
API_ANALISI = os.getenv("ANALISI_URL", "http://analisi_dati:5001/analizza")  # nome del servizio docker


app = Flask(__name__)

@circuit_breaker
def api_request():
    return requests.get(API_REGIONE)


@app.route("/fetch_data", methods=["GET"])
def fetch_data():
    try:
        response = api_request()
        response.raise_for_status()  
        return response.json()
    except CircuitBreakerError:
        return jsonify({"error": "Circuit Breaker attivato, il servizio non è disponibile."}), 503
    except Exception as e:
        print("Errore:", e)
        return None

@circuit_breaker
def analisi_request(dati):
    return requests.post(API_ANALISI, json=dati)

# Funzione per inviare i dati all'analisi
def invia_a_analisi(dati):
    try:
        response = analisi_request(dati)
        print("Risposta da analisi-dati:", response.json())
    except CircuitBreakerError:
        return jsonify({"error": "Circuit Breaker attivato, il servizio non è disponibile."}), 503
    except Exception as e:
        print("Errore nell'invio a analisi-dati:", e)


def main():
    print("avvio raccolTA dati", flush=True)
    while True:
        try:
            dati = fetch_data()
            if dati:
                invia_a_analisi(dati)
            # Crea un oggetto timedelta di 12 ore
            attesa = timedelta(hours=12)

            time.sleep(attesa.total_seconds())

        except CircuitBreakerError:
            print("Circuit Breaker attivato: un servizio non è disponibile.")
            time.sleep(60)  # Attende 60 secondi prima di ritentare 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
