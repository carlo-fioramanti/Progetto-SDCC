import requests
import urllib.parse
from circuitbreaker import CircuitBreaker, CircuitBreakerError
import threading
import json
from confluent_kafka import Consumer, KafkaError 
import time
from datetime import datetime


#API url
API_URL_gestioneutente = "http://GestioneUtente:5001"
API_URL_gestionepreferiti = "http://GestionePreferiti:5004"
API_URL_raccoltadati = "http://raccolta-dati:5005/fetch_data"
API_URL_segnalazioni = "http://segnalazione-utenti:5006"



circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=Exception)

@circuit_breaker
def register_request(username, password):
    return requests.post(f"{API_URL_gestioneutente}/register", json={"username": username, "password": password})

@circuit_breaker
def register():
    try:
        username = input("Inserisci username: ")
        password = input("Inserisci password: ")
        
        # Effettua la richiesta POST per registrarsi
        response = register_request(username, password)

        # Controllo risposta
        if response.status_code == 200:
            print("Registrazione avvenuta con successo!")
        else:
            print(f"Errore nella registrazione: {response.status_code}, {response.text}")
    
    except CircuitBreakerError:
        print("Circuit Breaker attivato: il servizio non è disponibile.")
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta: {e}")
    except Exception as e:
        print(f"Errore imprevisto: {e}")

@circuit_breaker
def login_request(username, password)
    return requests.post(f"{API_URL_gestioneutente}/login", json={"username": username, "password": password})

@circuit_breaker
def login():
    try:
        username = input("Inserisci username: ")
        password = input("Inserisci password: ")
        response = login_request(username, password)

        # Verifica se il login è andato a buon fine
        if response.status_code == 200:
            print("Login eseguito con successo!") 
            return response.json()["user_id"]  
        else:
            print("Login fallito! Controlla le tue credenziali.")
            return
    except CircuitBreakerError:
        print("Circuit Breaker attivato: il servizio non è disponibile.")
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta: {e}")
    except Exception as e:
        print(f"Errore imprevisto: {e}")
    return None

@circuit_breaker
def fiumi_request():
    return requests.get(f"{API_URL_gestionepreferiti}/fiumi")

@circuit_breaker
def sottobacini_request(fiume):
    return requests.get(f"{API_URL_gestionepreferiti}/sottobacini/{fiume}")

@circuit_breaker
def gestionepreferiti_request(user_id, fiume_selezionato, sottobacino_selezionato):
    return requests.post(f"{API_URL_gestionepreferiti}/gestione_preferiti", json={
            "user_id": user_id,
            "fiume": fiume_selezionato,
            "sottobacino": sottobacino_selezionato
        })


def gestione_preferiti(user_id):
    try:
        # Recupera la lista dei fiumi
        response = fiumi_request
        if response.status_code != 200:
            print("Errore nel recupero dei fiumi.")
            return
        fiumi = response.json()

        print("\nSeleziona un fiume:")
        for idx, fiume in enumerate(fiumi):
            print(f"{idx}. {fiume}")
        scelta_fiume = int(input("Numero del fiume: "))
        fiume_selezionato = fiumi[scelta_fiume]

        # Recupera i sottobacini per il fiume selezionato
        fiume_encoded = urllib.parse.quote(fiume_selezionato)
        response = sottobacini_request(fiume_encoded)
        if response.status_code != 200:
            print("Errore nel recupero dei sottobacini.")
            return
        sottobacini = response.json()

        print("\nSeleziona un sottobacino:")
        for idx, sottobacino in enumerate(sottobacini):
            print(f"{idx}. {sottobacino}")
        scelta_sottobacino = int(input("Numero del sottobacino: "))
        sottobacino_selezionato = sottobacini[scelta_sottobacino]

        # Gestisci i preferiti
        response = gestionepreferiti_request(user_id, fiume_selezionato, sottobacino_selezionato)
        if response.status_code == 200:
            print("Preferiti gestiti correttamente!")
        else:
            print(f"Errore: {response.status_code} - {response.text}")

    except CircuitBreakerError:
        print("Circuit Breaker attivato: il servizio non è disponibile.")
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta: {e}")
    except Exception as e:
        print(f"Errore imprevisto: {e}")

@circuit_breaker
def slc_fiumi_request():
    return requests.get(f"{API_URL_segnalazioni}/fiumi")

@circuit_breaker
def segnala_request(fiume_selezionato, sottobacino_selezionato, fascia_selezionata):
    return requests.post(f"{API_URL_segnalazioni}/segnala", json={
            "fiume": fiume_selezionato,
            "sottobacino": sottobacino_selezionato,
            "fascia": fascia_selezionata
        })

def segnala_livello_critico():
    try:
        # Recupera la lista dei fiumi
        response = slc_fiumi_request()
        if response.status_code != 200:
            print("Errore nel recupero dei fiumi.")
            return
        fiumi = response.json()

        print("\nSeleziona un fiume:")
        for idx, fiume in enumerate(fiumi):
            print(f"{idx}. {fiume}")
        scelta_fiume = int(input("Numero del fiume: "))
        fiume_selezionato = fiumi[scelta_fiume]

        # Recupera i sottobacini per il fiume selezionato
        fiume_encoded = urllib.parse.quote(fiume_selezionato)
        response = sottobacini_request(fiume_encoded)
        if response.status_code != 200:
            print("Errore nel recupero dei sottobacini.")
            return
        sottobacini = response.json()

        print("\nSeleziona un sottobacino:")
        for idx, sottobacino in enumerate(sottobacini):
            print(f"{idx}. {sottobacino}")
        scelta_sottobacino = int(input("Numero del sottobacino: "))
        sottobacino_selezionato = sottobacini[scelta_sottobacino]

        fasce = {
            "arancione": 9.0,
            "rossa": 12.0
        }   

        print("\nSeleziona una fascia di livello critico:")
        fasce_keys = list(fasce.keys())
        for idx, fascia in enumerate(fasce_keys):
            print(f"{idx}. {fascia} (>= {fasce[fascia]} metri)")
        scelta_fascia = int(input("Numero della fascia: "))
        if scelta_fascia < 0 or scelta_fascia >= len(fasce_keys):
            print("Scelta non valida.")
            return
        fascia_selezionata = fasce_keys[scelta_fascia]

        # Gestisci i preferiti
        response = segnala_request(fiume_selezionato, sottobacino_selezionato, fascia_selezionata)

        if response.status_code == 200:
            print("Segnalazione inviata correttamente!")
        else:
            print(f"Errore: {response.status_code} - {response.text}")

    except CircuitBreakerError:
        print("Circuit Breaker attivato: il servizio non è disponibile.")
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta: {e}")
    except Exception as e:
        print(f"Errore imprevisto: {e}")

@circuit_breaker
def controllapreferiti_request(user_id):
    return requests.post(f"{API_URL_gestionepreferiti}/controllo_preferiti", json={"user_id": user_id, "da_kafka": True})

def kafka_consumer_per_utente(user_id):
    # Recupera i preferiti dell'utente
    response = controllapreferiti_request(user_id)
    if response.status_code != 200:
        print("❌ Errore nel recupero dei preferiti.")
        return

    preferiti = response.json()
    topic_list = [
        f"{p['fiume'].replace(' ', '_').lower()}-{p['sottobacino'].replace(' ', '_').lower()}"
        for p in preferiti
    ]

    consumer_config = {
        'bootstrap.servers': 'kafka:9092',
        'group.id': f'frontend_{user_id}_{threading.get_ident()}',
        'auto.offset.reset': 'earliest'
    }


    consumer = Consumer(consumer_config)
    consumer.subscribe(topic_list)

    print("🟢 In ascolto delle notifiche Kafka per i preferiti...")

    notifiche_per_topic = {}
    polling_vuoti = 0
    max_polling_vuoti = 5  # ad esempio: 3 polling vuoti consecutivi = fine

    try:
        
        while polling_vuoti < max_polling_vuoti:
            msg = consumer.poll(1.0)
            if msg is None:
                polling_vuoti += 1
                continue
            
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print(f"⚠️ Topic non ancora creato: {msg.topic()}")
                else:
                    print(f"⚠️ Errore Kafka: {msg.error()}")
                continue

            data = json.loads(msg.value().decode('utf-8'))
            topic = msg.topic()
            timestamp = data.get("timestamp")

            # tiene solo l'ultima per timestamp
            esistente = notifiche_per_topic.get(topic)
            if esistente is None or esistente["timestamp"] < timestamp:
                notifiche_per_topic[topic] = data

    except KeyboardInterrupt:
        print("🛑 Interruzione consumer ricevuta.")
    finally:
        consumer.close()

    # 3. Stampo solo l'ultima per ogni topic
    print("\n📥 Notifiche più recenti per ciascun topic:")
    for topic, notifica in notifiche_per_topic.items():
        print(f"📢 Topic: {topic}")
        print(f"   Fiume: {notifica['fiume']}")
        print(f"   Sottobacino: {notifica['sottobacino']}")
        print(f"   Fascia: {notifica['fascia']}")
        print(f"   Timestamp: {notifica['timestamp']}")
        print(f"   Tipo: {notifica['tipo']}")
        print("-" * 40)


    
@circuit_breaker
def preferiti_request(user_id):
    return requests.post(f"{API_URL_gestionepreferiti}/controllo_preferiti", json = {"user_id": user_id})

def controllo_preferiti(user_id):
    response = preferiti_request(user_id)
    if response.status_code != 200:
        print(response)
        print("Errore nel recupero dei preferiti.")
        return
    preferiti = response.json()
    print("\n Fiumi preferiti:")
    for idx, pref in enumerate(preferiti):
        fiume = pref.get("fiume", "")
        sottobacino = pref.get("sottobacino", "")
        fascia_allerta = pref.get("allerta", "")
        print(f"{idx}. Fiume: {fiume}, Sottobacino: {sottobacino}, Allerta: {fascia_allerta}")

@circuit_breaker
def rimozione_request(user_id, fiume, sottobacino):
    return requests.delete(
        f"{API_URL_gestionepreferiti}/rimozione_preferiti",
        json={"user_id": user_id, "fiume": fiume, "sottobacino": sottobacino}
    )

def rimozione_preferiti(user_id):
    response = preferiti_request(user_id)
    if response.status_code != 200:
        print("Errore nel recupero dei preferiti.")
        return
    preferiti = response.json()
    print("\nFiumi preferiti:")
    for idx, pref in enumerate(preferiti):
        print(f"{idx}. Fiume: {pref['fiume']} | Sottobacino: {pref['sottobacino']}")

    try:
        num_fiume = int(input("Seleziona il numero del fiume da rimuovere: "))
        if num_fiume < 0 or num_fiume >= len(preferiti):
            print("Numero selezionato non valido")
            return
    except ValueError:
        print("Input non valido. Inserisci un numero.")
        return

    fiume_da_rimuovere = preferiti[num_fiume]["fiume"]
    sottobacino_da_rimuovere = preferiti[num_fiume]["sottobacino"]

    response = rimozione_request(user_id, fiume_da_rimuovere, sottobacino_da_rimuovere)

    if response.status_code == 200:
        print("✅ Preferito rimosso correttamente.")
    else:
        print(f"Errore nella rimozione: {response.text}")

def main():
    while True:
        print("\n1. Registrati\n2. Login\n3. Esci")
        choice = input("Scegli un'opzione: ")
        if choice == "1":
            register()
        elif choice == "2":
            user_id = login()
            if user_id:
                threading.Thread(target=kafka_consumer_per_utente, args=(user_id,), daemon=True).start()
                print("Caricamento delle notifiche in corso:")
                time.sleep(35)
                while True:
                    print("\n--- Menu ---")
                    print("0. Aggiungi Preferiti")
                    print("1. Controlla Preferiti")
                    print("2. Rimuovi Preferiti")
                    print("3. Segnala fiume")
                    print("4. Esci")
                    scelta = input("Scegli un'opzione: ")
                    if scelta == "0":
                        gestione_preferiti(user_id)
                    elif scelta == "1":
                        controllo_preferiti(user_id)
                    elif scelta == "2":
                        rimozione_preferiti(user_id)
                    elif scelta == "3":
                        segnala_livello_critico()
                    elif scelta == "4":
                        print("Logout effettuato.")
                        break
                    else:
                        print("Scelta non valida!")
        elif choice == "3":
            print("Arrivederci!")
            break
        else:
            print("Scelta non valida!")



if __name__ == "__main__":
    main()
