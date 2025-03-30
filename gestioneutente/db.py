import boto3
import os
import uuid
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv

load_dotenv()

# Ottieni le credenziali dalle variabili d'ambiente
import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_session_token = os.environ['AWS_SESSION_TOKEN']
aws_region = os.environ['AWS_REGION']
dynamodb_table = os.environ['DYNAMODB_TABLE']


try:

    dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token = aws_session_token,
    region_name=aws_region
    )
    table = dynamodb.Table(dynamodb_table)
except (NoCredentialsError, PartialCredentialsError):
    print("Errore: Credenziali AWS mancanti o incomplete. Configurare con `aws configure`.")

def create_user(username, password):
    """ Registra un nuovo utente nel database """
    user_id = str(uuid.uuid4())  # Genera un ID univoco
    item = {
        "user_id": user_id,
        "username": username,
        "password": password,  # ⚠️ Da hashare!
    }
    print(f"Salvataggio in tabella {dynamodb_table}: {item}")
    table.put_item(Item=item)
    return user_id

def get_user(username):
    """ Recupera un utente per nome utente """
    response = table.scan(
        FilterExpression="username = :u",
        ExpressionAttributeValues={":u": username},
    )
    users = response.get("Items", [])
    return users[0] if users else None
