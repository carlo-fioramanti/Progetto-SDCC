FROM python:3.9
WORKDIR /app
COPY requirementsGU.txt .
RUN pip install -r requirementsGU.txt
COPY . .
CMD ["python", "appGU.py"]
