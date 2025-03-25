# analisi-dati/appAnalisi.py
from flask import Flask, request, jsonify

app = Flask(__name__)

# il metodo notifica viene chiamato per ogni fiume il cui livello dell'acqua sta in fascia arancione o rossa
def notifica(fiume, sottobacino, fascia):
    #qui va fatta la notifica agli utenti con il collegamento al subscriber 
    print(f"Allerta {fascia} per il sottobacino {sottobacino} del fiume {fiume}", flush=True)


@app.route("/analizza", methods=["POST"])
def analizza():
    dati = request.json

    fascia_verde = 3.0
    fascia_gialla = 6.0
    fascia_arancione = 9.0
    fascia_rossa = 12.0
    # Lista per contenere i dati_fiumi
    dati_fiumi = {
        "nome_fiume": [],
        "sottobacino": [],
        "fascia": []
    }
    
    # Itera attraverso ogni bacino
    for data_per_data in dati.values():  # Itera attraverso le date
        for bacino in data_per_data["bacino"]:
            nome_bacino = bacino["nome_bacino"]
            
            # Itera attraverso i sottobacini
            for sottobacino in bacino["sottobacino"]:
                nome_sottobacino = sottobacino["nomeSottobacino"]
                
                # Estrai i valori da colmo_previsto e osservazione
                #valore_colmo_previsto = sottobacino["colmo_previsto"]["valore"]
                valore_osservazione = float(sottobacino["osservazione"]["valore"])
                fascia = ""
                if valore_osservazione is None:
                    fascia = "valore non valido"
                elif valore_osservazione < fascia_verde:
                    fascia = "verde"
                elif valore_osservazione < fascia_gialla:
                    fascia = "gialla"
                elif valore_osservazione < fascia_arancione:
                    fascia = "arancione"
                    notifica(nome_bacino, nome_sottobacino, fascia)
                elif valore_osservazione < fascia_rossa:
                    fascia = "rossa"
                    notifica(nome_bacino, nome_sottobacino, fascia)

                # Aggiungi alla lista dei dati_fiumi
                dati_fiumi["nome_fiume"].append(nome_bacino)
                dati_fiumi["sottobacino"].append(nome_sottobacino)
                dati_fiumi["fascia"].append(fascia)
    return dati_fiumi

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
