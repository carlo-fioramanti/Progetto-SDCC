import time
import requests
import os
from flask import Flask
from datetime import timedelta

API_REGIONE = "https://allertameteo.regione.emilia-romagna.it/datiTempoReale-prevPiog-portlet/get-bollettino-monitoraggio"  
API_ANALISI = os.getenv("ANALISI_URL", "http://analisi-dati:5001/analizza")  # nome del servizio docker

app = Flask(__name__)

@app.route("/fetch_data", methods=["GET"])
def fetch_data():
    try:
        response = requests.get(API_REGIONE)
        response.raise_for_status()
        return response.json()
        #print("Dati ricevuti:", response.json())
    except Exception as e:
        print("Errore:", e)
        return None
    
def invia_a_analisi(dati):
    try:
        response = requests.post(API_ANALISI, json=dati)
        print("Risposta da analisi-dati:", response.json())
    except Exception as e:
        print("Errore nell'invio a analisi-dati:", e)
    
def main():
    while True:
        dati = fetch_data()
        if dati:
            invia_a_analisi(dati)
        # Crea un oggetto timedelta di 12 ore
        attesa = timedelta(hours=12)

        # Converte in secondi e passalo a sleep
        time.sleep(attesa.total_seconds())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
