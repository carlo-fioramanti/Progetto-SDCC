FROM python:3.12

WORKDIR /app

COPY appRaccolta.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt




CMD ["python", "appRaccolta.py"]
