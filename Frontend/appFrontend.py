import requests

API_URL = "http://gestioneutente:5001"

def register():

    username = input("Inserisci username: ")
    password = input("Inserisci password: ")
    response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})


def login():
    username = input("Inserisci username: ")
    password = input("Inserisci password: ")
    response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    print(response.json())

def main():
    while True:
        print("\n1. Registrati\n2. Login\n3. Esci")
        choice = input("Scegli un'opzione: ")
        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            break
        else:
            print("Scelta non valida!")

if __name__ == "__main__":
    main()
