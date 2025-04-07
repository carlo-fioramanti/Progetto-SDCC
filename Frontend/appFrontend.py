import requests

API_URL = "http://gestioneutente:5001"

def register():

    username = input("Inserisci username: ")
    password = input("Inserisci password: ")
    response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})


def login():
    username = input("Inserisci username: ")
    password = input("Inserisci password: ")
    response = requests.post(f"{API_URL_gestioneuntente}/login", json={"username": username, "password": password})

    # Verifica se il login è andato a buon fine
    if response.status_code == 200:
        print(response.json()) 
        return response.json()["user_id"]  
    else:
        print("Login fallito! Controlla le tue credenziali.")
        return


def gestione_preferiti(user_id):
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

    response = requests.post(f"{API_URL_gestionepreferiti}/gestione_preferiti", json={
        "user_id": user_id,
        "fiume": fiume_selezionato,
        "sottobacino": sottobacino_selezionato
    })

    if response.status_code == 200:
        print("Preferiti gestiti correttamente!")
    else:
        print(f"Errore: {response.status_code} - {response.text}")

def controllo_preferiti(user_id):
    response = requests.post(f"{API_URL_gestionepreferiti}/controllo_preferiti", json = {"user_id": user_id})
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
                        while True:
                            print("\n--- Schermata Gestione Preferiti ---")
                            print("0. Aggiungi Preferiti")
                            print("1. Controlla Preferiti")
                            print("2. Torna Alla Schermata Principale")
                            choice = input("Scegli un'opzione: ")
                            if choice == "0":
                                gestione_preferiti(user_id)
                            elif choice == "1":
                                controllo_preferiti(user_id)
                            elif choice == "1":
                                print("Ritorno alla schermata principale")
                                break
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
