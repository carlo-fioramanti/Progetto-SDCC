import requests
import urllib.parse
from circuitbreaker import CircuitBreaker, CircuitBreakerError


API_URL_gestioneutente = "http://gestioneutente:5001"
API_URL_gestionepreferiti = "http://GestionePreferiti:5004"

circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=Exception)

@circuit_breaker
def register():
    try:
        username = input("Inserisci username: ")
        password = input("Inserisci password: ")
        
        # Effettua la richiesta POST per registrarsi
        response = requests.post(f"{API_URL_gestioneuntente}/register", json={"username": username, "password": password})

        # Gestisci la risposta
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
def login():
    username = input("Inserisci username: ")
    password = input("Inserisci password: ")
    response = requests.post(f"{API_URL_gestioneutente}/login", json={"username": username, "password": password})

    # Verifica se il login è andato a buon fine
    if response.status_code == 200:
        print(response.json()) 
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
def gestione_preferiti(user_id):
    try:
        # Recupera la lista dei fiumi
        response = requests.get(f"{API_URL_gestionepreferiti}/fiumi")
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
        response = requests.get(f"{API_URL_gestionepreferiti}/sottobacini/{fiume_encoded}")
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
        response = requests.post(f"{API_URL_gestionepreferiti}/gestione_preferiti", json={
            "user_id": user_id,
            "fiume": fiume_selezionato,
            "sottobacino": sottobacino_selezionato
        })

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


def main():
    while True:
        print("\n1. Registrati\n2. Login\n3. Esci")
        choice = input("Scegli un'opzione: ")
        if choice == "1":
            register()
        elif choice == "2":
            user_id = login()
            if user_id:
                while True:
                    print("\n--- Schermata principale ---")
                    print("0. Gestione Preferiti")
                    print("1. Esci")
                    choice = input("Scegli un'opzione: ")

                    if choice == "0":
                        gestione_preferiti(user_id)
                    elif choice == "1":
                        print("Arrivederci!")
                        break
                    else:
                        print("Scelta non valida!")
            elif choice == "3":
                break
            else:
                print("Scelta non valida!") 

if __name__ == "__main__":
    main()
