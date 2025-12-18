### BRANCHER EN A0
### https://wiki.seeedstudio.com/Grove-Sound_Sensor/
from grove.adc import ADC
import sqlite3
import asyncio
from ws_manager import broadcast
import LED

__all__ = ['GroveSensorSound']

class GroveSoundSensor(object):

    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def sound(self):
        value = self.adc.read(self.channel)
        return value

Grove = GroveSoundSensor

async def main(start_event, rythme, dureeIntervalleHist=None):
  """ fonction qui lance la partie, allume la LED, capte le son, renvoie la liste des volumes sonores. """
  pin = 0

  sensor = GroveSoundSensor(pin)
  taux_interpolation = 0.1
  
  if dureeIntervalleHist == None: # si la partie n'est pas en mode histoire
    connect = sqlite3.connect("singonlight.db")
    data = connect.execute("SELECT valeur FROM parametres WHERE cle = 'dureeIntervalle';")
    data = data.fetchone()[0]
    connect.close()
  else: # si la partie est en mode histoire, alors la durée de l'intervalle est celle du paramètre
    data = dureeIntervalleHist  
  data2= len(rythme)
  print(data2)
  print('Detecting sound...')
  L=[]
  # boucle de jeu
  for j in range(int(data2)): 
    LED.change_state(rythme,j) # change l'etat de la LED en fonction du rythme a l'indice j
    for i in range(round(data*(1/taux_interpolation))):
        print('Sound value: {0}'.format(sensor.sound))
        L.append(sensor.sound)
        await asyncio.sleep(taux_interpolation)
  LED.change_state([0],0) # eteint la led 
  return L


async def calibrage(n):
    """
    appelé quand l'utilisateur appuie sur le bouton calibration automatique
    n = durée en secondes
    Renvoie le seuil bas du son ambiant
    """
    pin = 0

    sensor = GroveSoundSensor(pin)
    taux_interpolation = 0.1

    # broadcast fait apparaître le message sur le site via un websocket
    await broadcast("Veuillez ne pas faire de bruit durant le calibrage du son ambiant")
    print("Veuillez ne pas faire de bruit durant le calibrage du son ambiant")
    await asyncio.sleep(5)
    for i in range(3,0,-1):
        await broadcast("Le calibrage commence dans " + str(i) + " secondes")
        print("Le calibrage commence dans ",i," secondes")
        await asyncio.sleep(1)
    await broadcast("Calibrage du son ambiant en cours... Veuillez rester silencieux.")
    print("Silence")
    L = []
    for _ in range(int(n*(1/taux_interpolation))):
        L.append(sensor.sound)
        await asyncio.sleep(taux_interpolation)
    S = (sum(x**2 for x in L)/len(L))**0.5 # Calcul du Seuil bas
    await broadcast("Calibrage du son ambiant terminé. (" + str(S) + ")")
    print("Calibrage du son ambiant terminé")
    return S



if __name__ == '__main__':
    asyncio.run(main())
