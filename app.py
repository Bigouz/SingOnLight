import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
from contextlib import asynccontextmanager
import sqlite3
import score as score
import time
from random import randint
import SoundSensor as Sound
import LED

@asynccontextmanager # gestion du cycle de vie de l'application (onstartup/shutdown)
async def lifespan(app : FastAPI):
    # Code à exécuter au démarrage de l'application
    # Initialisation de la base de données SQLite
    connect = sqlite3.connect('singonlight.db')
    connect.execute('CREATE TABLE IF NOT EXISTS parametres (cle TEXT PRIMARY KEY,valeur INTEGER);') # utilisé afin d'obtenir le seuil de calibration
    connect.execute('CREATE TABLE IF NOT EXISTS scores (intervalleScore TEXT PRIMARY KEY, occurence INTEGER);') # utilisé afin d'obtenir les scores des parties jouées
    everything = connect.execute('SELECT * FROM parametres;')
    data = everything.fetchall()
    print(len(data))
    if len(data) == 0:
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("seuil",50)) # valeur par défaut du seuil de calibration
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("dureeIntervalle", 1)) # durée d'une intervalle
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("dureePartie", 25)) # durée de la partie en intervalles

    stats = connect.execute('SELECT * FROM scores;')
    data_scores = stats.fetchall()
    if len(data_scores) == 0:
        for i in range(0,101,10): # initialisation des scores possibles de 0 à 100 de pas 10
            connect.execute('INSERT INTO scores (intervalleScore, occurence) VALUES (?,?);', (str(i),0)) # valeur par défaut des scores

    connect.commit()
    connect.close()
    print("Base de données initialisée.")
    yield
    # Code à exécuter à l'arrêt de l'application
    pass

#print(score.calculer([1,0,1,1,0,0,1],[0,1,1,1,0,0,1])) # Test de la fonction de calcul du score

templates = Jinja2Templates(directory="templates/")
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get('/')
def main(request:Request):
    #user = {'username': 'Cécile'}
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/play.html")
def play(request:Request) -> str:
    connect = sqlite3.connect("singonlight.db")
    dureeIntervalle = connect.execute('SELECT valeur FROM parametres WHERE cle="dureeIntervalle";').fetchone()[0]
    dureePartie = connect.execute('SELECT valeur FROM parametres WHERE cle="dureePartie";').fetchone()[0]
    connect.close()

    return templates.TemplateResponse('play.html',{'request': request,'dureeIntervalle':dureeIntervalle, "dureePartie":dureePartie})

@app.get("/data.html")
def data(request:Request) -> str:
    connect = sqlite3.connect('singonlight.db')
    scores = connect.execute('SELECT * FROM scores;').fetchall()
    connect.close()
    s = []
    for score in scores:
        if score[0] == "100":
            s.append([score[0]+"%", score[1]])
        else:
            s.append([score[0] + "-" + str(int(score[0])+9) + "%", score[1]])
    return templates.TemplateResponse('data.html',{'request': request, 'scores':s})

@app.get("/calibration.html")
def calibration(request:Request) -> str:
    connect = sqlite3.connect('singonlight.db')
    seuil = connect.execute('SELECT valeur FROM parametres WHERE cle="seuil";').fetchone()[0]
    connect.close()
    return templates.TemplateResponse('calibration.html',{'request': request, 'seuil':int(seuil)})

def save_calibration(seuil: int):
    connect = sqlite3.connect('singonlight.db')
    connect.execute('UPDATE parametres set valeur=(?) WHERE cle="seuil";', (seuil,))
    connect.commit()
    connect.close()


@app.post("/run-calibrate") # récupération du seuil de calibration depuis la page calibration.html afin de le sauvegarder dans la base de donnée
async def run_calibrate(request:Request):
    body = await request.json()
    seuil = body.get("seuil", 50)
    result = save_calibration(int(seuil))
    return "Calibration sauvegardée."

def save_param_jouer(dureeIntervalle:int, dureePartie:int):
    connect = sqlite3.connect('singonlight.db')
    connect.execute('UPDATE parametres set valeur=(?) WHERE cle="dureeIntervalle";', (dureeIntervalle,))
    connect.execute('UPDATE parametres set valeur=(?) WHERE cle="dureePartie";', (dureePartie,))
    connect.commit()
    connect.close()

@app.post("/run_play")
async def run_play(request:Request):
    """ appelé quand le joueur appuie sur le bouton jouer """
    body = await request.json()
    dureeIntervalle = body.get("dureeIntervalle",1)
    dureePartie = body.get("dureePartie",25)
    #dureeTotale = dureeIntervalle*dureePartie
    save_param_jouer(dureeIntervalle, dureePartie)
    
    rythme = generation_rythme(int(dureePartie))
    res = Sound.run() # resultat du capteur son (liste de volumes)
    LED.run(rythme) # allume la led selon le rythme
    print("fin de partie")
    ### appeler les fonctions pour transformer 
    ### la liste en liste de 0 et 1 ici
    
    pourcentage = score.calculer_pourcentage(rythme, res)
    enregistrer_score(pourcentage)
    
    ### afficher le pourcentage de réussite ici
    
    """for i in range(dureeTotale):
        time.sleep(60)
        dureeTotale-=1
        """ ### A MODIFIER POUR VISUALISER LE TEMPS QUI S'ECOULE (TESTS)

    return f"La partie a démarrée." # \n Temps restant de la partie: {dureePartie} \n Temps restant de l'intervalle: {dureeIntervalle} \n Temps total restant: {dureeTotale}


@app.post("/reset_data")
async def reset_data(request:Request):
    connect = sqlite3.connect('singonlight.db')
    for i in range(0,101,10):
        connect.execute('UPDATE scores set occurence=0 WHERE intervalleScore=?;', (str(i),))
    connect.commit()
    connect.close()
    return {"status":"Les données ont bien été réinitialisées."}

def generation_rythme(longueur) -> list: 
    """ Génère un rythme dit "aléatoire" de longueur longueur, composé de 1 et de 0."""
    signal=[]
    for i in range(longueur):
        signal.append(randint(0, 1))
    return signal

def transformer_signal_audio(signal_audio, seuil):
    """Transforme un signal audio en une liste binaire en fonction d'un seuil donné."""
    pass  # Implémentation à venir

# a appeler en fin de partie
def enregistrer_score(score_obtenu):
    """Enregistre le score obtenu dans la base de données.
    Args:
        score_obtenu (int): Le score obtenu par le joueur (entre 0 et 100).
    """
    intervalle = (score_obtenu // 10) * 10  # Déterminer l'intervalle de score (0-10, 11-20, ..., 91-100)
    connect = sqlite3.connect('singonlight.db')
    # Récupérer l'occurence actuelle pour le score_obtenu
    occurence_actuelle = connect.execute('SELECT occurence FROM scores WHERE intervalleScore=?;', (str(intervalle),)).fetchone()[0]
    # Incrémenter l'occurence
    nouvelle_occurence = occurence_actuelle + 1
    # Mettre à jour la base de données
    connect.execute('UPDATE scores SET occurence=? WHERE intervalleScore=?;', (nouvelle_occurence, str(intervalle)))
    connect.commit()
    connect.close()


if __name__ == "__main__":
    uvicorn.run(app) # lancement du serveur HTTP + WSGI avec les options de debug
