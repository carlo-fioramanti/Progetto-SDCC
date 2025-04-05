FROM python:3.12
WORKDIR /app
COPY requirementsFrontend.txt .
RUN pip install -r requirementsFrontend.txt
COPY . .
CMD ["python", "appFrontend.py"]

