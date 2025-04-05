FROM python:3.12
WORKDIR /app
COPY requirementsGU.txt .
RUN pip install -r requirementsGU.txt
RUN pip install bcrypt
COPY . .
CMD ["python", "appGU.py"]
