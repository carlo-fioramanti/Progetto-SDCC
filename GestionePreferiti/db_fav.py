import boto3
import os
import uuid
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os


aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_session_token = os.environ['AWS_SESSION_TOKEN']
aws_region = os.environ['AWS_REGION']



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


def add_to_favorites(user_id, fiume, sottobacino):
    try:
        response = table.get_item(Key={'id_user': user_id})
        if 'Item' in response:
            # Se l'utente ha già dei preferiti, aggiungi il nuovo fiume e sottobacino
            user_favorites = response['Item']
            if 'preferiti' not in user_favorites:
                user_favorites['preferiti'] = []
        else:
            # Se l'utente non ha ancora preferiti, crea una nuova lista
            user_favorites = {'id_user': user_id, 'preferiti': []}
        
        print(fiume, flush=True)
        print(sottobacino, flush=True)
        # Aggiungi il nuovo preferito
        user_favorites['preferiti'].append({'fiume': fiume, 'sottobacino': sottobacino})
        
        # Salva o aggiorna la tabella Favorites
        table.put_item(Item=user_favorites)
        return {"message": f"{sottobacino} aggiunto ai preferiti del fiume {fiume}!"}

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

def remove_from_favorites(user_id, fiume, sottobacino):
    response = table.get_item(Key={'id_user': user_id})
    if 'Item' not in response:
        raise Exception("Utente non trovato.")

    user_data = response['Item']
    preferiti = user_data.get('preferiti', [])

    # Rimuovi con confronto "robusto"
    nuovi_preferiti = []
    rimosso = False
    for p in preferiti:
        if p['fiume'].strip().lower() == fiume.strip().lower() and p['sottobacino'].strip().lower() == sottobacino.strip().lower():
            rimosso = True
            continue  # salta questo elemento
        nuovi_preferiti.append(p)

    if not rimosso:
        raise Exception("Preferito non trovato.")

    # Aggiorna la lista nel DB
    user_data['preferiti'] = nuovi_preferiti
    table.put_item(Item=user_data)

