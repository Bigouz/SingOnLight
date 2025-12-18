import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
from contextlib import asynccontextmanager
import sqlite3
import score as score
from random import randint
from ws_manager import active_connections, broadcast


### pour tester du code sans le raspberry PI, on peut commenter l'import de SoundSensor et LED (dans SoundSensor).
import SoundSensor as Sound

### pour tester les messages Websockets sans raspberry PI, décommenter la ligne suivante.
#import test as Sound

def gen_bdd():
    """fonction qui génère les tables de la base de données si les tables n'existent pas."""
    connect = sqlite3.connect('singonlight.db')
    connect.execute('CREATE TABLE IF NOT EXISTS parametres (cle TEXT PRIMARY KEY,valeur INTEGER);') # utilisé afin d'obtenir le seuil de calibration
    connect.execute('CREATE TABLE IF NOT EXISTS histoire (cle INTEGER PRIMARY KEY,rythme TEXT,intervalle DOUBLE);') # utilisé afin d'obtenir les rythmes du mode histoire
    connect.execute('CREATE TABLE IF NOT EXISTS scores (intervalleScore TEXT PRIMARY KEY, occurence INTEGER);') # utilisé afin d'obtenir les scores des parties jouées
    connect.execute('CREATE TABLE IF NOT EXISTS rythme (id INTEGER PRIMARY KEY AUTOINCREMENT, rythme CHAR(120));') # itlisé afin d'obtenir les rythmes créés par les utilisateurs
    everything = connect.execute('SELECT * FROM parametres;')
    data = everything.fetchall()
    print(len(data))
    if len(data) == 0:
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("seuil",50)) # valeur par défaut du seuil de calibration
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("dureeIntervalle", 1)) # durée d'une intervalle
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("dureePartie", 25)) # durée de la partie en intervalles
        connect.execute('INSERT INTO parametres (cle,valeur) VALUES (?,?);', ("winstreak", 0)) # winstreak initialisé à 0
        connect.execute('INSERT INTO rythme (rythme) VALUES (?);', ("2")) # rythme custom

    
        """
        Les rythmes du mode histoire
        Légende : 
        {temps}b = faire du bruit durant {temps} seconde(s)
        {temps}s = silence durant {temps} seconde(s)
        """
    
    if len(connect.execute("SELECT * FROM histoire;").fetchall()) == 0:
        """
        Niveaux facile : Comprendre les bases du jeu
        Condition victoire : 50%
        """
        
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (1, "11010",1.0)) # rythme histoire 1
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (2, "11101",0.6)) # rythme histoire 2
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (3, "0110010101",0.8)) # rythme histoire 3
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (4, "11101011",0.8)) # rythme histoire 4
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (5, "101001011",0.7)) # rythme histoire 5

        """
        Niveaux Intermediaire : Savoir gérer le changement de rythme 
        Condition victoire : 60%
        """
        
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (6, "011110001011011111",0.6))
        # rythme histoire 6 [0.6s,2.4b,1.8s,0.6b,0.6s,1.2b,0.6s,3.0b]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (7, "101010101111011101001",0.5))
        # rythme histoire 7 [0.5b,0.5s,0.5b,0.5s,0.5b,0.5s,0.5b,0.5s,2.0b,0.5s,1.5b,0.5s,0.5b,1.0s,0.5b]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (8, "10111101010101001010100011111101",0.4))
        # rythme histoire 8 [0.4b,0.4s,1.6b,0.4s,0.4b,0.4s,0.4b,0.4s,0.4b,0.4s,0.4b,0.8s,0.4b,0.4s,0.4b,0.4s,0.4b,1.2s,2.4b,0.4s,0.4b]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (9, "11010110110101101110101101101100100011111",0.3))
        # rythme histoire 9 [0.6b,0.3s,0.3b,0.3s,0.6b,0.3s,0.6b,0.3s,0.3b,0.3s,0.6b,0.3s,0.9b,0.3s,0.3b,0.3s,0.6b,0.3s,0.6b,0.3s,0.6b,0.6s,0.3b,0.9s,1.5b]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (10, "1011011011110010010011000000101111111110110101",0.3))
        # rythme histoire 10 [0.3b,0.3s,0.6b,0.3s,0.6b,0.3s,1.2b,0.6s,0.3b,0.6s,0.3b,0.6s,0.6b,1.8s,0.3b,0.3s,2.7b,0.3s,0.6b,0.3s,0.3b,0.3s,0.3b]

        """
        Niveaux Difficile : Savoir gérer le changement d'intervalle
        Condition victoire : 60%
        """
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (11, "1111100001111111000000000011110000111111111111111111111111111111000111001100111001111001100011",0.1))
        # rythme histoire 11 [0.5b,0.4s,0.7b,1.0s,0.4b,0.4s,3.0b,0.3s,0.3b,0.2s,0.2b,0.2s,0.3b,0.2s,0.4b,0.2s,0.2b,0.3s,0.2b]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (12, "111000011111000000111111100000000000000000000111111100011100111100000111000011000001111100111000110011100111",0.1))
        # rythme histoire 12 [0.3b,0.4s,0.5b,0.6s,0.7b,2.0s,0.7b,0.3s,0.3b,0.2s,0.4b,0.5s,0.3b,0.4s,0.2b,0.5s,0.5b,0.2s,0.3b,0.3s,0.2b,0.2s,0.3b,0.2s,0.3b]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (13, "11111111110000111000001111001110011110011100000111100011100110000011100000110011001100011100001100111100000000001111110011100000111001110001111111100001110011000111111001110001111110",0.1))
        # rythme histoire 13 [1.0b,0.4s,0.3b,0.5s,0.4b,0.2s,0.3b,0.2s,0.4b,0.2s,0.3b,0.5s,0.4b,0.3s,0.3b,0.2s,0.2b,0.5s,0.3b,0.5s,0.2b,0.2s,0.2b,0.2s,0.2b,0.3s,0.3b,0.4s,0.2b,0.2s,0.4b,1.0s,0.6b,0.2s,0.3b,0.5s,0.3b,0.2s,0.3b,0.3s,0.8b,0.4s,0.2b,0.2s,0.2b,0.3s,0.2b,0.2s,0.2b,0.3s,0.5b,0.1s]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (14, "11100110011000110011111111110011110001110011111000001110011100111001110000000000000001111100011001110000000110111100111000000000011110000",0.1))
        # rythme histoire 14 [0.3b,0.2s,0.2b,0.2s,0.2b,0.3s,0.2b,0.2s,1.0b,0.2s,0.4b,0.3s,0.3b,0.2s,0.5b,0.5s,0.3b,0.2s,0.3b,0.2s,0.3b,0.2s,0.3b,1.5s,0.5b,0.3s,0.2b,0.2s,0.3b,0.7s,0.2b,0.1s,0.4b,0.2s,0.3b,1.0s,0.4b,0.4s]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (15, "1111111111110000000000000001100110111110110110000111111100111000111101110000001101101100011111000000110011100000011011111001110011001111000110011100111",0.1))
        # rythme histoire 15 [1.2b,1.5s,0.2b,0.2s,0.2b,0.1s,0.5b,0.1s,0.2b,0.1s,0.2b,0.4s,0.7b,0.2s,0.3b,0.3s,0.4b,0.1s,0.3b,0.6s,0.2b,0.1s,0.2b,0.1s,0.2b,0.3s,0.5b,0.6s,0.2b,0.2s,0.3b,0.6s,0.2b,0.1s,0.5b,0.2s,0.3b,0.2s,0.2b,0.2s,0.4b,0.3s,0.2b,0.2s,0.3b,0.2s,0.3b]

                

        """
        Mode Impossible : Bonne chance
        Condition victoire : 70%
        """
        
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (16, "11111110111011000011110111000010000010000001000010011010101100101010110001101000101011011001001010111101011000110111",0.1))
        # rythme histoire 16 [0.7b,0.1s,0.3b,0.1s,0.2b,0.4s,0.4b,0.1s,0.3b,0.4s,0.1b,0.5s,0.1b,0.6s,0.1b,0.4s,0.1b,0.2s,0.2b,0.1s,0.1b,0.1s,0.1b,0.1s,0.2b,0.2s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.2b,0.3s,0.2b,0.1s,0.1b,0.3s,0.1b,0.1s,0.1b,0.1s,0.2b,0.1s,0.2b,0.2s,0.1b,0.2s,0.1b,0.1s,0.1b,0.1s,0.4b,0.1s,0.1b,0.1s,0.2b,0.3s,0.2b,0.1s,0.3b]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (17, "1010100101000100100001110010010111110011111110011111110011111110010101001100010011100010011000111110100011111000111111011111001111110111110011111011111111000",0.1))
        # rythme histoire 17 [1.2b,0.2s,0.1b,0.2s,0.1b,0.1s,0.5b,0.2s,0.7b,0.2s,0.7b,0.2s,0.7b,0.2s,0.1b,0.1s,0.1b,0.1s,0.1b,0.2s,0.2b,0.3s,0.1b,0.2s,0.3b,0.3s,0.1b,0.2s,0.2b,0.3s,0.5b,0.1s,0.1b,0.3s,0.5b,0.3s,0.6b,0.1s,0.5b,0.2s,0.6b,0.1s,0.5b,0.2s,0.5b,0.1s,0.8b,0.3s]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (18, "110100010101000100110001110010011001000111000111010111000100111001011111000111100011111000111000100100001000100010101010101010101010101010001100100110000",0.1))
        # rythme histoire 18 [0.2b,0.1s,0.1b,0.3s,0.1b,0.1s,0.1b,0.1s,0.1b,0.3s,0.1b,0.2s,0.2b,0.3s,0.3b,0.2s,0.1b,0.2s,0.2b,0.2s,0.1b,0.3s,0.3b,0.3s,0.3b,0.1s,0.1b,0.1s,0.3b,0.3s,0.1b,0.2s,0.3b,0.2s,0.1b,0.1s,0.5b,0.3s,0.4b,0.3s,0.5b,0.3s,0.3b,0.3s,0.1b,0.2s,0.1b,0.4s,0.1b,0.3s,0.1b,0.3s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.3s,0.2b,0.2s,0.1b,0.2s,0.2b,0.4s]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (19, "01101101101111100111001100111000110000011001010101010101010110110111001001111100111100000001110011000110011000011001110011000011111101101110000010101001111010011000000011100110100110010000",0.1))
        # rythme histoire 19 [0.1s,0.2b,0.1s,0.2b,0.1s,0.2b,0.1s,0.5b,0.2s,0.3b,0.2s,0.2b,0.2s,0.3b,0.3s,0.2b,0.5s,0.2b,0.2s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.2b,0.1s,0.2b,0.1s,0.3b,0.2s,0.1b,0.2s,0.5b,0.2s,0.4b,0.7s,0.3b,0.2s,0.2b,0.3s,0.2b,0.2s,0.2b,0.4s,0.2b,0.2s,0.3b,0.2s,0.2b,0.4s,0.6b,0.1s,0.2b,0.1s,0.3b,0.5s,0.1b,0.1s,0.1b,0.1s,0.1b,0.2s,0.4b,0.1s,0.1b,0.2s,0.2b,0.7s,0.3b,0.2s,0.2b,0.1s,0.1b,0.2s,0.2b,0.2s,0.1b,0.4s]
        connect.execute('INSERT INTO histoire (cle,rythme,intervalle) VALUES (?,?,?);', (20, "011010111011101011110011111101101110110101010101010101000001100111110110011101101111100111111111111111111111111111100000000000000000011111000011111110000000111110000000000000000110011001110110011110011011100000110011101100111011011011011000010101100111100101011100111001010100101100101010010100101101100101101",0.1))
        # rythme histoire 20 [0.1s,0.2b,0.1s,0.1b,0.1s,0.3b,0.1s,0.3b,0.1s,0.1b,0.1s,0.4b,0.2s,0.6b,0.1s,0.2b,0.1s,0.3b,0.1s,0.2b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.1s,0.1b,0.5s,0.2b,0.2s,0.5b,0.1s,0.2b,0.2s,0.3b,0.1s,0.2b,0.1s,0.5b,0.2s,2.8b,1.8s,0.5b,0.4s,0.7b,0.7s,0.5b,1.6s,0.2b,0.2s,0.2b,0.2s,0.3b,0.1s,0.2b,0.2s,0.4b,0.2s,0.2b,0.1s,0.3b,0.5s,0.2b,0.2s,0.3b,0.1s,0.2b,0.2s,0.3b,0.1s,0.2b,0.1s,0.2b,0.1s,0.2b,0.1s,0.2b,0.4s,0.1b,0.1s,0.1b,0.1s,0.2b,0.2s,0.4b,0.2s,0.1b,0.1s,0.1b,0.1s,0.3b,0.2s,0.3b,0.2s,0.1b,0.1s,0.1b,0.1s,0.1b,0.2s,0.1b,0.1s,0.2b,0.2s,0.1b,0.1s,0.1b,0.1s,0.1b,0.2s,0.1b,0.1s,0.1b,0.2s,0.1b,0.1s,0.2b,0.1s,0.2b,0.2s,0.1b,0.1s,0.2b,0.1s,0.1b]
    
        
    stats = connect.execute('SELECT * FROM scores;')
    data_scores = stats.fetchall()
    if len(data_scores) == 0:
        for i in range(0,101,10): # initialisation des scores possibles de 0 à 100 de pas 10
            connect.execute('INSERT INTO scores (intervalleScore, occurence) VALUES (?,?);', (str(i),0)) # valeur par défaut des scores

    connect.commit()
    connect.close()
    print("Base de données initialisée.")
gen_bdd()
@asynccontextmanager # gestion du cycle de vie de l'application (onstartup/shutdown)
async def lifespan(app : FastAPI):
    """ code executé au lancement du serveur local"""
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
    """ envoi de la page principale (index.html) """
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/Mode.html")
def mode(request:Request):
    """ envoi de la page mode de jeu"""
    return templates.TemplateResponse('Mode.html',{"request":request})

@app.get("/histoire.html")
def histoire(request:Request):
    """ envoi de la page du mode histoire"""
    return templates.TemplateResponse('histoire.html',{"request":request})

@app.get("/play_multijoueur.html")
def play_mult(request:Request) -> str:
    """ récupère les paramètres de la partie depuis la base de données et les envoie à la page play_multijoueur.html """
    connect = sqlite3.connect("singonlight.db")
    dureeIntervalle = connect.execute('SELECT valeur FROM parametres WHERE cle="dureeIntervalle";').fetchone()[0]
    dureePartie = connect.execute('SELECT valeur FROM parametres WHERE cle="dureePartie";').fetchone()[0]
    connect.close()

    return templates.TemplateResponse('play_multijoueur.html',{'request': request,'dureeIntervalle':dureeIntervalle, "dureePartie":dureePartie})

@app.get("/play.html")
def play(request:Request) -> str:
    """ récupère les paramètres de la partie depuis la base de données et les envoie à la page play.html en tant que valeur par defaut"""
    connect = sqlite3.connect("singonlight.db")
    dureeIntervalle = connect.execute('SELECT valeur FROM parametres WHERE cle="dureeIntervalle";').fetchone()[0]
    dureePartie = connect.execute('SELECT valeur FROM parametres WHERE cle="dureePartie";').fetchone()[0]
    winstreak = connect.execute('SELECT valeur FROM parametres WHERE cle="winstreak";').fetchone()[0]
    rythme = connect.execute('SELECT rythme FROM rythme WHERE id=1;').fetchone()[0]
    connect.close()
    longueur_rythme = len(str(rythme)) if rythme != -1 else 0
    return templates.TemplateResponse('play.html',{'request': request,'dureeIntervalle':dureeIntervalle, "dureePartie":dureePartie, "winstreak":winstreak, "rythme":longueur_rythme})

@app.get("/play_histoire.html")
def play_histoire(request:Request) -> str:
    """ page play_histoire """
    connect = sqlite3.connect("singonlight.db")
    rythme = connect.execute('SELECT rythme FROM histoire WHERE cle=1;').fetchone()[0]
    connect.close()
    return templates.TemplateResponse('play_histoire.html',{'request': request, 'rythme' : rythme})

@app.get("/data.html")
def data(request:Request) -> str:
    """ récupère les scores depuis la base de données et les envoie à la page data.html pour les afficher dans le graphique"""
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
    """ récupère le seuil de calibration depuis la base de données et l'envoie à la page calibration.html pour l'affichage de la valeur par defaut pour la calibration manuelle"""
    connect = sqlite3.connect('singonlight.db')
    seuil = connect.execute('SELECT valeur FROM parametres WHERE cle="seuil";').fetchone()[0]
    connect.close()
    return templates.TemplateResponse('calibration.html',{'request': request, 'seuil':int(seuil)})

def save_calibration(seuil: int):
    """ sauvegarde le seuil dans la base de données"""
    connect = sqlite3.connect('singonlight.db')
    connect.execute('UPDATE parametres set valeur=(?) WHERE cle="seuil";', (seuil,))
    connect.commit()
    connect.close()


@app.post("/run-calibrate") # récupération du seuil de calibration depuis la page calibration.html afin de le sauvegarder dans la base de donnée
async def run_calibrate(request:Request):
    """ récupère le seuil depuis le site et le sauvegarde dans la bdd"""
    body = await request.json()
    seuil = body.get("seuil", 50)
    result = save_calibration(int(seuil))
    return "Calibration sauvegardée."

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """ gère les connexions WebSockets pour l'affichage du texte pour la calibration automatique"""
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
    """ appelé quand le joueur appuie sur le bouton jouer dans le mode multijoueur"""
    body = await request.json()
    dureeIntervalle = body.get("dureeIntervalle",1)
    dureePartie = body.get("dureePartie",25)
    rythme = body.get("rythme",-1)
    print(rythme)
    save_param_jouer(dureeIntervalle, dureePartie)
    if rythme == -1:
        rythme = generation_rythme(int(dureePartie))

    res = await Sound.main(None,rythme)

    print(res)
    print("fin de partie")
    print("son (" + str(len(res))+"): " + str(res))
    print("led (" + str(len(rythme))+"): " + str(rythme))
    
    signal = transformation_signal_moyenne(res,dureeIntervalle)
    print(res, "=>", signal)
    pourcentage = score.calculerPourcentage(rythme, signal)
    enregistrer_score(pourcentage)
    print(str(pourcentage) + "%")
    
    # le "Joueur 1" / "Joueur 2" est affiché en javascript
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
    """ sauvegarde des paramètres dans la BDD pour que l'utilisateur ne doive pas le rentrer a chaque fois"""
    connect = sqlite3.connect('singonlight.db')
    connect.execute('UPDATE parametres set valeur=(?) WHERE cle="dureeIntervalle";', (dureeIntervalle,))
    connect.execute('UPDATE parametres set valeur=(?) WHERE cle="dureePartie";', (dureePartie,))
    connect.commit()
    connect.close()



@app.post("/run_play")
async def run_play(request:Request):
    """ appelé quand le joueur appuie sur le bouton jouer en mode solo, prend le rythme personnalisé si le bouton est coché, sinon il est généré"""
    body = await request.json()
    dureeIntervalle = body.get("dureeIntervalle",1)
    dureePartie = body.get("dureePartie",25)
    isRythme = body.get("isRythme",0)
    if isRythme == 0:
        rythme = generation_rythme(int(dureePartie))
    else:
        connect = sqlite3.connect('singonlight.db')
        rythme = connect.execute("SELECT rythme FROM rythme WHERE id=1;").fetchone()[0]
        connect.close()
        rythme = [int(e) for e in rythme]
    print(rythme)
    save_param_jouer(dureeIntervalle, dureePartie)

    res = await Sound.main(None, rythme)

    print(res)
    print("fin de partie")
    print("son (" + str(len(res))+"): " + str(res))
    print("led (" + str(len(rythme))+"): " + str(rythme))
    
    signal = transformation_signal_moyenne(res,dureeIntervalle)
    print(res, "=>", signal)
    pourcentage = score.calculerPourcentage(rythme, signal)
    enregistrer_score(pourcentage)
    print(str(pourcentage) + "%")

    w=get_winstreak()
    if pourcentage >= 50:
        if isRythme == 0:
            w = increment_winstreak()
        return {"message":"Vous avez gagné avec un score de " + str(pourcentage) + "%", "winstreak": w}
    if isRythme == 0:
        w = reset_winstreak()
    return {"message": "Vous avez perdu avec un score de " + str(pourcentage) + "%", "winstreak": w}


@app.get("/creation_rythme.html")
def creation_rythme(request:Request) -> str:
    """ récupère les paramètres de la partie depuis la base de données et les envoie à la page creation_rythme.html """
    connect = sqlite3.connect("singonlight.db")
    rythme = connect.execute('SELECT rythme FROM rythme WHERE id=1;').fetchone()[0]
    dureePartie = connect.execute('SELECT valeur FROM parametres WHERE cle="dureePartie";').fetchone()[0]

    connect.close()
    if rythme == "2": # "2" car "-1" ne marche pas
        return templates.TemplateResponse('creation_rythme.html',{'request': request, "dureePartie":dureePartie, "rythme":[]})
    
    rythme = str(rythme)
    return templates.TemplateResponse('creation_rythme.html',{'request': request, "dureePartie":dureePartie, "rythme":rythme})


@app.post("/run_creation_rythme") 
async def run_creation_rythme(request:Request):
    """ appelé quand le bouton créer est appuyé. sauvegarde le rythme dans la BDD"""
    body = await request.json()
    rythme = body.get("rythme", "2")
    if rythme == "2":
        return "Aucun rythme reçu."
    connect = sqlite3.connect('singonlight.db')


    connect.execute('UPDATE rythme set rythme=? WHERE id=1;', (str(rythme),))
    connect.commit()
    connect.close()
    return "rythme sauvegardé."


niveau_histoire = 1
@app.post("/run_play_histoire")
async def run_play_histoire():
    """ appelé quand le joueur lance une partie en mode histoire """
    global niveau_histoire
    connect = sqlite3.connect('singonlight.db')
    dureeIntervalle = connect.execute("SELECT intervalle FROM histoire WHERE cle=" + str(niveau_histoire) + ";").fetchone()[0]
    rythme = connect.execute("SELECT rythme FROM histoire WHERE cle=" + str(niveau_histoire) + ";").fetchone()[0]
    rythme = [int(e) for e in rythme]
    dureePartie = len(rythme)
    print(rythme)
    res = await Sound.main(None, rythme, dureeIntervalle)
    print(niveau_histoire)
    print(dureePartie)

    print(res)
    print("fin de partie")
    print("son (" + str(len(res))+"): " + str(res))
    print("led (" + str(len(rythme))+"): " + str(rythme))
    
    print(dureeIntervalle)
    signal = transformation_signal_moyenne(res,dureeIntervalle)
    print(res, "=>", signal)
    pourcentage = score.calculerPourcentage(rythme, signal)
    enregistrer_score(pourcentage)
    print(str(pourcentage) + "%")

    cond_victoire = 50
    if niveau_histoire > 5 :
        cond_victoire = 60
    if niveau_histoire > 15 :
        cond_victoire = 70
    if pourcentage >= cond_victoire:
        niveau_histoire += 1
        if niveau_histoire > 20:
            niveau_histoire = 1
            return {"message":"<script>apparition()></script>", "niveau": niveau_histoire, "etat":"fini"}
        return {"message":"Vous avez gagné avec un score de " + str(pourcentage) + "%", "niveau": niveau_histoire, "etat": "gagné"}
    niveau_histoire = 1
    return {"message": "Vous avez perdu avec un score de " + str(pourcentage) + "%", "niveau": niveau_histoire, "etat":"perdu"}

def reset_winstreak():
    """ réinitialise le winsteak (nombre de victoires d'affilé)"""
    connect = sqlite3.connect('singonlight.db')
    connect.execute('UPDATE parametres set valeur=0 WHERE cle="winstreak";')
    connect.commit()
    connect.close()
    return 0
def get_winstreak():
    """ récupère le winstreak depuis la BDD"""
    connect = sqlite3.connect('singonlight.db')
    current_winstreak = connect.execute('SELECT valeur FROM parametres WHERE cle="winstreak";').fetchone()[0]
    connect.close()
    return current_winstreak
    
    
def increment_winstreak():
    """ incrémente le winstreak de 1 """
    connect = sqlite3.connect('singonlight.db')
    current_winstreak = connect.execute('SELECT valeur FROM parametres WHERE cle="winstreak";').fetchone()[0]
    new_winstreak = current_winstreak + 1
    connect.execute('UPDATE parametres set valeur=? WHERE cle="winstreak";', (new_winstreak,))
    connect.commit()
    connect.close()
    return new_winstreak

def transformation_signal_moyenne(signal,dureeIntervalle):
    """ transforme le signal du capteur sonore selon la moyenne """
    connect = sqlite3.connect("singonlight.db")
    seuil = connect.execute("SELECT valeur FROM parametres WHERE cle='seuil';").fetchone()[0]
    print("seuil :",seuil)
    connect.close()
    
    signal_bin = [1 if signal[i] >= seuil else 0 for i in range(len(signal))] # si la valeur du capteur > seuil, alors cela append 1, 0 sinon
    taux = 0.1
    signal_compr = []
    n = round(dureeIntervalle/taux) # temps d'une intervalle en secondes 
    print(n)

    for i in range(0,len(signal_bin),n):
        signal_compr.append(sum(signal_bin[i:i+n])/n) # calcule la moyenne des n éléments (0 ou 1), puis des n éléments suivants
    signal_fin = []
    for s in signal_compr:
        if s >= 0.5: # si il y a un bruit pendant la majorité de l'intervalle, alors il y a un bruit pendant l'intervalle
            signal_fin.append(1)
        else:
            signal_fin.append(0)
    return signal_fin

@app.post("/reset_data")
async def reset_data(request:Request):
    """ appelé quand l'utilisateur appuye sur le bouton effacer les données sur la page data.html
        réinitialise les données de parties dans la BDD. """
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
    # Récuperation de l'occurence actuelle pour le score_obtenu
    occurence_actuelle = connect.execute('SELECT occurence FROM scores WHERE intervalleScore=?;', (str(intervalle),)).fetchone()[0]
    # Incrémentation de l'occurence
    nouvelle_occurence = occurence_actuelle + 1
    # Mise à jour la base de données
    connect.execute('UPDATE scores SET occurence=? WHERE intervalleScore=?;', (nouvelle_occurence, str(intervalle)))
    connect.commit()
    connect.close()

if __name__ == "__main__":
    uvicorn.run(app) # lancement du serveur HTTP + WSGI
