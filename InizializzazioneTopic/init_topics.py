# init_topics.py
import json
from confluent_kafka.admin import AdminClient, NewTopic

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
FILENAME = "fiumi_sottobacini.json"

def crea_topic(nome):
    admin_client = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
    topic = NewTopic(nome, num_partitions=1, replication_factor=1)
    futures = admin_client.create_topics([topic])
    for topic_name, future in futures.items():
        try:
            future.result()
            print(f"✅ Creato topic: {topic_name}")
        except Exception as e:
            print(f"⚠️ Errore (o già esistente) per topic {topic_name}: {e}")

def main():
    with open(FILENAME, "r") as file:
        fiumi_sottobacini = json.load(file)

    for fiume, sottobacini in fiumi_sottobacini.items():
        for sottobacino in sottobacini:
            topic = f"{fiume.replace(' ', '_').lower()}-{sottobacino.replace(' ', '_').lower()}"
            crea_topic(topic)

if __name__ == "__main__":
    main()
