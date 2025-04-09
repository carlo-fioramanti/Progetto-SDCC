import boto3
import os
import uuid
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os
from circuitbreaker import CircuitBreaker, CircuitBreakerError  # Importa il Circuit Breaker


aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_session_token = os.environ['AWS_SESSION_TOKEN']
aws_region = os.environ['AWS_REGION']

circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=Exception)

try:

    dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token = aws_session_token,
    region_name=aws_region
    )
    table = dynamodb.Table('Favorites')
except (NoCredentialsError, PartialCredentialsError):
    print("Errore: Credenziali AWS mancanti o incomplete. Configurare con `aws configure`.")


@circuit_breaker
def add_to_favorites(user_id, fiume, sottobacino):
    try:
        # Recupero l'elemento dall'ID utente
        response = table.get_item(Key={'id_user': user_id})
        
        if 'Item' in response:
            # Se l'utente ha già dei preferiti, aggiungo il nuovo fiume e sottobacino
            user_favorites = response['Item']
            if 'preferiti' not in user_favorites:
                user_favorites['preferiti'] = []
        else:
            # Se l'utente non ha ancora preferiti, creo una nuova lista
            user_favorites = {'id_user': user_id, 'preferiti': []}
        
        # Aggiungo il nuovo preferito
        user_favorites['preferiti'].append({'fiume': fiume, 'sottobacino': sottobacino})
        
        # Salvo o aggiorno la tabella Favorites
        table.put_item(Item=user_favorites)
        return {"message": f"{sottobacino} aggiunto ai preferiti del fiume {fiume}!"}

    except CircuitBreakerError:
        return {"error": "Circuit Breaker attivato, il servizio DynamoDB non è disponibile."}
    except Exception as e:
        print(f"Errore durante l'aggiunta ai preferiti: {e}")
        return {"error": f"Errore durante l'aggiunta ai preferiti: {str(e)}"}
    
def show_favorites(user_id, dati_fiumi):
    response = table.get_item(Key={'id_user': user_id})
    preferiti = response['Item']['preferiti']

    favorites = []
    for p in preferiti:
        fiume = p['fiume']
        sottobacino = p['sottobacino']

        fascia_allerta = "non disponibile"

        for entry in dati_fiumi:
            if entry["fiume"] == fiume and entry["sottobacino"] == sottobacino:
                fascia_allerta = entry["fascia"]
                break

        favorites.append({
            "fiume": fiume,
            "sottobacino": sottobacino,
            "allerta": fascia_allerta
        })

    return favorites
