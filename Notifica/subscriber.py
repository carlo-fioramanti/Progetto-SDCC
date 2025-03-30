from confluent_kafka import Consumer
import json

consumer_config = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'allerta_consumer_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(consumer_config)
consumer.subscribe(["allerta_fiumi"])

print("In ascolto su Kafka topic 'allerta_fiumi'...")

while True:
    msg = consumer.poll(1.0)
    
    if msg is None:
        continue
    if msg.error():
        print(f"Errore Kafka: {msg.error()}")
        continue

    data = json.loads(msg.value().decode('utf-8'))
    print(f"⚠️ Allerta {data['fascia']} per il fiume {data['fiume']} - Sottobacino {data['sottobacino']}")

#consumer.close()
