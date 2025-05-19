FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir confluent_kafka

CMD ["python3", "appGestionePreferiti.py"]
