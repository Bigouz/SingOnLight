import uvicorn
from fastapi import FastAPI, Request, WebSocket, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
from contextlib import asynccontextmanager
import sqlite3
import score as score
from random import randint
from ws_manager import active_connections, broadcast

start_event = asyncio.Event()

### pour tester du code sans le raspberry PI, on peut commenter l'import de SoundSensor et LED.
#import SoundSensor as Sound
#import LED

### pour tester les messages Websockets sans raspberry PI, décommenter la ligne suivante.
import test as Sound

def gen_bdd():
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
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("winstreak", 0)) # winstreak initialisé à 0
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("rythme", -1)) # rythme custom

    stats = connect.execute('SELECT * FROM scores;')
    data_scores = stats.fetchall()
    if len(data_scores) == 0:
        for i in range(0,101,10): # initialisation des scores possibles de 0 à 100 de pas 10
            connect.execute('INSERT INTO scores (intervalleScore, occurence) VALUES (?,?);', (str(i),0)) # valeur par défaut des scores

    connect.commit()
    connect.close()
    print("Base de données initialisée.")

@asynccontextmanager # gestion du cycle de vie de l'application (onstartup/shutdown)
async def lifespan(app : FastAPI):
    print("AAAAAAAAA")
    # Code à exécuter au démarrage de l'application
    # Initialisation de la base de données SQLite
    gen_bdd()
    yield
    # Code à exécuter à l'arrêt de l'application
    if len(active_connections) > 0:
        await broadcast("Le serveur va s'arrêter. Déconnexion...")
        active_connections.clear()
    pass
    
#print(score.calculer([1,0,1,1,0,0,1],[0,1,1,1,0,0,1])) # Test de la fonction de calcul du score

templates = Jinja2Templates(directory="templates/")
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get('/')
def main(request:Request):
    #user = {'username': 'Cécile'}
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/Mode.html")
def mode(request:Request):
    return templates.TemplateResponse('Mode.html',{"request":request})

@app.get("/play_multijoueur.html")
def play_mult(request:Request) -> str:
    """ récupère les paramètres de la partie depuis la base de données et les envoie à la page play.html """
    connect = sqlite3.connect("singonlight.db")
    dureeIntervalle = connect.execute('SELECT valeur FROM parametres WHERE cle="dureeIntervalle";').fetchone()[0]
    dureePartie = connect.execute('SELECT valeur FROM parametres WHERE cle="dureePartie";').fetchone()[0]
    connect.close()

    return templates.TemplateResponse('play_multijoueur.html',{'request': request,'dureeIntervalle':dureeIntervalle, "dureePartie":dureePartie})

@app.get("/play.html")
def play(request:Request) -> str:
    """ récupère les paramètres de la partie depuis la base de données et les envoie à la page play.html """
    connect = sqlite3.connect("singonlight.db")
    dureeIntervalle = connect.execute('SELECT valeur FROM parametres WHERE cle="dureeIntervalle";').fetchone()[0]
    dureePartie = connect.execute('SELECT valeur FROM parametres WHERE cle="dureePartie";').fetchone()[0]
    winstreak = connect.execute('SELECT valeur FROM parametres WHERE cle="winstreak";').fetchone()[0]
    connect.close()

    return templates.TemplateResponse('play.html',{'request': request,'dureeIntervalle':dureeIntervalle, "dureePartie":dureePartie, "winstreak":winstreak})

@app.get("/data.html")
def data(request:Request) -> str:
    """ récupère les scores depuis la base de données et les envoie à la page data.html """
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
    """ récupère le seuil de calibration depuis la base de données et l'envoie à la page calibration.html """
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """ gère les connexions WebSocket (1) """
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        print("WebSocket disconnected:", e)
    finally:
        active_connections.remove(websocket)

@app.post("/run_play_multi")
async def run_play_multi(request:Request):
    """ appelé quand le joueur appuie sur le bouton jouer """
    body = await request.json()
    dureeIntervalle = body.get("dureeIntervalle",1)
    dureePartie = body.get("dureePartie",25)
    rythme = body.get("rythme",-1)
    print(rythme)
    save_param_jouer(dureeIntervalle, dureePartie)
    if rythme == -1:
        rythme = generation_rythme(int(dureePartie))

    global start_event
    start_event = asyncio.Event()
    sound_task = asyncio.create_task(Sound.main(start_event,rythme))
    start_event.set()

    res = await sound_task

    print(res)
    print("fin de partie")
    print("son (" + str(len(res))+"): " + str(res))
    print("led (" + str(len(rythme))+"): " + str(rythme))
    
    signal = transformation_signal_moyenne(res,dureeIntervalle)
    print(res, "=>", signal)
    pourcentage = score.calculerPourcentage(rythme, signal)
    enregistrer_score(pourcentage)
    print(str(pourcentage) + "%")
    
    return {"message":"a fini avec un score de " + str(pourcentage) + "%", "rythme": rythme, "pourcentage": pourcentage}

@app.post("/run-auto-calibrate")
async def run_auto_calibrate(request:Request):
    """ appelé quand l'utilisateur appuie sur le bouton de calibration automatique """
    n=10

    seuil = asyncio.create_task(Sound.calibrage(n))
    result = await seuil
    if result < 30:
        result = 30
    elif result > 750:
        result = 750
    print("Nouveau seuil calibré :", result)
    save_calibration(int(result))
    return "La calibration automatique est terminée."

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
    save_param_jouer(dureeIntervalle, dureePartie)
    rythme = generation_rythme(int(dureePartie))

    global start_event
    start_event = asyncio.Event()
    sound_task = asyncio.create_task(Sound.main(start_event,rythme))
    start_event.set()

    res = await sound_task

    print(res)
    print("fin de partie")
    print("son (" + str(len(res))+"): " + str(res))
    print("led (" + str(len(rythme))+"): " + str(rythme))
    
    signal = transformation_signal_moyenne(res,dureeIntervalle)
    print(res, "=>", signal)
    pourcentage = score.calculerPourcentage(rythme, signal)
    enregistrer_score(pourcentage)
    print(str(pourcentage) + "%")
    
    if pourcentage >= 50:
        w = increment_winstreak()
        return {"message":"Vous avez gagné avec un score de " + str(pourcentage) + "%", "winstreak": w}
    w = reset_winstreak()
    return {"message": "Vous avez perdu avec un score de " + str(pourcentage) + "%", "winstreak": w}

@app.post("/run_creation_rythme") 
async def run_creation_rythme(request:Request):
    body = await request.json()
    rythme = body.get("rythme", -1)
    if rythme == -1:
        return "Aucun rythme reçu."
    connect = sqlite3.connect('singonlight.db')

    # il faut trasformer le rythme en chaîne de caractères pour le stocker dans la BDD ici


    connect.execute('UPDATE parametres set valeur=? WHERE cle="rythme";', (str(rythme),))
    connect.commit()
    connect.close()
    return "rythme sauvegardé."

@app.post("/run_play_rythme")
async def run_play_rythme(request:Request):
    """ appelé quand le joueur appuie sur le bouton jouer avec ton rythme"""
    connect = sqlite3.connect('singonlight.db')
    body = await request.json()
    dureeIntervalle = body.get("dureeIntervalle",1)
    dureePartie = body.get("dureePartie",25)
    save_param_jouer(dureeIntervalle, dureePartie)
    rythme = connect.execute("SELECT value FROM parametres WHERE cle='rythme';").fetchone()[0]
    if rythme == -1:
        return("Tu n'as pas crée de rythme")
    else:
        global start_event
        start_event = asyncio.Event()
        sound_task = asyncio.create_task(Sound.main(start_event,rythme))
        start_event.set()

        res = await sound_task

        print(res)
        print("fin de partie")
        print("son (" + str(len(res))+"): " + str(res))
        print("led (" + str(len(rythme))+"): " + str(rythme))
            
        signal = transformation_signal_moyenne(res,dureeIntervalle)
        print(res, "=>", signal)
        pourcentage = score.calculerPourcentage(rythme, signal)
        enregistrer_score(pourcentage)
        print(str(pourcentage) + "%")

        if pourcentage >= 50:
            w = increment_winstreak()
            return {"message":"Vous avez gagné avec un score de " + str(pourcentage) + "%", "winstreak": w}
        w = reset_winstreak()
        return {"message": "Vous avez perdu avec un score de " + str(pourcentage) + "%", "winstreak": w}

def reset_winstreak():
    connect = sqlite3.connect('singonlight.db')
    connect.execute('UPDATE parametres set valeur=0 WHERE cle="winstreak";')
    connect.commit()
    connect.close()
    return 0

def increment_winstreak():
    connect = sqlite3.connect('singonlight.db')
    current_winstreak = connect.execute('SELECT valeur FROM parametres WHERE cle="winstreak";').fetchone()[0]
    new_winstreak = current_winstreak + 1
    connect.execute('UPDATE parametres set valeur=? WHERE cle="winstreak";', (new_winstreak,))
    connect.commit()
    connect.close()
    return new_winstreak

def transformation_signal_moyenne(signal,dureeIntervalle):
    connect = sqlite3.connect("singonlight.db")
    seuil = connect.execute("SELECT valeur FROM parametres WHERE cle='seuil';").fetchone()[0]
    print("seuil :",seuil)
    connect.close()
    
    signal_bin = [1 if signal[i] >= seuil else 0 for i in range(len(signal))]
    taux = 0.1
    signal_compr = []
    n = int(dureeIntervalle/taux)
    for i in range(0,len(signal_bin),n):
        signal_compr.append(sum(signal_bin[i:i+n])/n)
    signal_fin = []
    for s in signal_compr:
        if s >= 0.5:
            signal_fin.append(1)
        else:
            signal_fin.append(0)
    return signal_fin

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

# a appeler en fin de partie
def enregistrer_score(score_obtenu):
    """
    Enregistre le score obtenu dans la base de données.
    Args:
        score_obtenu (int): Le score obtenu par le joueur (entre 0 et 100).
    """
    intervalle = int((score_obtenu // 10) * 10)  # Déterminer l'intervalle de score (0-10, 11-20, ..., 91-100)
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
