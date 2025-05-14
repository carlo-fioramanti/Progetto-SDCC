from confluent_kafka import Consumer, KafkaError
import requests
import json
import time
import os
from circuitbreaker import CircuitBreaker, CircuitBreakerError
from flask import Flask, request, jsonify 

API_URL_gestionepreferiti = "http://gestione_preferiti:5004"
app = Flask(__name__)

circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=Exception)

@circuit_breaker
def preferiti_request(user_id):
    return requests.post(f"{API_URL_gestionepreferiti}/controllo_preferiti", json={"user_id": user_id, "da_kafka": True})

@app.route("/notifiche", methods=["POST"])
def pull_notifiche():
    try:
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id mancante"}), 400
        # Recupera i preferiti dell'utente
        response = preferiti_request(user_id)
        if response.status_code != 200:
            print("❌ Errore nel recupero dei preferiti.")
            return
        preferiti = response.json()
        topic_list = [
            f"{p['fiume'].replace(' ', '_').lower()}-{p['sottobacino'].replace(' ', '_').lower()}"
            for p in preferiti
        ]
    except CircuitBreakerError:
        return jsonify({"error": "Circuit Breaker attivato, il servizio di registrazione non è disponibile."}), 503
    except Exception as e:
        return jsonify({"error": f"Errore durante la registrazione: {str(e)}"}), 500


    consumer_config = {
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'notifica-service',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(consumer_config)
    #controllo se la subscription ha funzionato per tutti i topic in topic_list e printo i topic non creati
    for topic in topic_list:
        try:
            consumer.subscribe([topic])
        except KafkaError as e:
            if e.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                print(f"⚠️ Topic non ancora creato: {topic}")
            else:
                print(f"⚠️ Errore Kafka: {e}")

    #consumer.subscribe(topic_list)

    print("🟢 In ascolto delle notifiche Kafka per i preferiti...")

    notifiche_per_topic = {}
    polling_vuoti = 0
    max_polling_vuoti = 5  # ad esempio: 5 polling vuoti consecutivi = fine

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
        print(notifiche_per_topic, flush=True)
        return notifiche_per_topic
    except KeyboardInterrupt:
        print("🛑 Interruzione consumer ricevuta.")
    finally:
        consumer.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007)
