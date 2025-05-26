# Sistema di Monitoraggio e Allerta per Bacini Fluviali

Questo repository contiene il progetto finale per il corso di Sistemi Distribuiti e Cloud Computing dell’Università degli Studi di Roma Tor Vergata (Facoltà di Ingegneria Informatica).

Il sistema consente la registrazione e l’accesso degli utenti, la visualizzazione e la gestione dei fiumi preferiti, e l’invio di notifiche in caso di livelli critici. L’architettura si basa su microservizi che comunicano via HTTP e Kafka, con integrazione di DynamoDB e S3 di AWS.

## 🛠️ Configurazione del Progetto
1. Configura l’Ambiente AWS

    Inserisci le tue credenziali AWS nel file .env:

    - AWS_ACCESS_KEY_ID=
    - AWS_SECRET_ACCESS_KEY=
    - AWS_SESSION_TOKEN=
    - AWS_REGION=

    Crea una tabella DynamoDB chiamata Favorites con chiave primaria id_user (di tipo stringa).

    Crea un bucket S3 per memorizzare i dati in cache utilizzati nell’analisi.

🚀 Come Avviare il Client

- Apri il terminale nella cartella del progetto.

- Esegui il file:

          start.py

Dopo l’accesso, l’interfaccia permette di:

- Aggiungere/Rimuovere/Visualizzare fiumi preferiti

- Segnalare situazioni critiche
        
- Ricevere notifiche in tempo reale

