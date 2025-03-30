# Usa Python come base
FROM python:3.12

WORKDIR /app

COPY subscriber.py .
COPY requirements.txt .

# Installa le dipendenze
RUN pip install confluent-kafka

# Comando di default (sovrascritto da docker-compose)
CMD ["python3", "subscriber.py"]
