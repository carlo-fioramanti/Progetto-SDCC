FROM python:3.12

WORKDIR /app

COPY requirements.txt .
COPY appAnalisiDati.py .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install confluent-kafka

COPY . .

CMD ["python3", "appAnalisiDati.py"]