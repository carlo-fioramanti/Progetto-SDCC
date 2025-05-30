import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os
from circuitbreaker import CircuitBreaker  


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

    except Exception as e:
        print(f"Errore durante l'aggiunta ai preferiti: {e}")
        return {"error": f"Errore durante l'aggiunta ai preferiti: {str(e)}"}
    

    
    
@circuit_breaker    
def show_favorites(user_id, dati_fiumi):
    try:
        response = table.get_item(Key={'id_user': user_id})
        preferiti = response['Item']['preferiti']

        favorites = []
        for p in preferiti:
            fiume = p['fiume']['S'] if isinstance(p['fiume'], dict) else p['fiume']
            sottobacino = p['sottobacino']['S'] if isinstance(p['sottobacino'], dict) else p['sottobacino']
            fascia_allerta = "non disponibile"

            for entry in dati_fiumi:
                if entry["fiume"]== fiume and entry["sottobacino"] == sottobacino:
                    fascia_allerta = entry["fascia"]
                    break

            favorites.append({
                "fiume": fiume,
                "sottobacino": sottobacino,
                "allerta": fascia_allerta
            })
    
        return favorites

    except Exception as e:
        print(f"Errore durante l'aggiunta ai preferiti: {e}")
        return {"error": f"Errore durante l'aggiunta ai preferiti: {str(e)}"}

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


@circuit_breaker
def is_already_favorite(user_id, fiume, sottobacino):
    try:
        response = table.get_item(Key={'id_user': user_id})
        if 'Item' not in response:
            return 0  # Nessun preferito ancora

        preferiti = response['Item'].get('preferiti', [])

        f_input = fiume.strip().lower()
        s_input = sottobacino.strip().lower()

        print(f"Verifica se il preferito {f_input} - {s_input} è già presente nei preferiti.", flush=True)

        for p in preferiti:
            f = p.get('fiume', "").get("S", "") if isinstance(p.get('fiume'), dict) else p.get('fiume', "")
            s = p.get('sottobacino', "").get("S", "") if isinstance(p.get('sottobacino'), dict) else p.get('sottobacino', "")

            print(f"Confronto: fiume = {f.strip().lower()} con {f_input}, sottobacino = {s.strip().lower()} con {s_input}", flush=True)

            if f.strip().lower() == f_input and s.strip().lower() == s_input:
                return 1

        return 0
    except Exception as e:
        print(f"Errore durante il controllo dei preferiti: {e}")
        
