import time
import requests

API_URL = "https://allertameteo.regione.emilia-romagna.it/datiTempoReale-prevPiog-portlet/get-bollettino-monitoraggio"  

def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        print("Dati ricevuti:", response.json())
    except Exception as e:
        print("Errore:", e)

def main():
    while True:
        fetch_data()
        time.sleep(3600)  # ogni ora

if __name__ == "__main__":
    main()