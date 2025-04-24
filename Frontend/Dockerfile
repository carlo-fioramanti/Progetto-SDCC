FROM python:3.12

WORKDIR /app

# Installa librerie di sistema necessarie a librdkafka
RUN apt-get update && apt-get install -y \
    gcc \
    librdkafka-dev \
    && apt-get clean

COPY . .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "appFrontend.py"]


