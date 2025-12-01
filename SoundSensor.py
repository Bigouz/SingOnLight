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

async def main(start_event):
  await start_event.wait()
  pin = 0

  sensor = GroveSoundSensor(pin)
  taux_interpolation = 0.1
  
  connect = sqlite3.connect("singonlight.db")
  data = connect.execute("SELECT valeur FROM parametres WHERE cle = 'dureeIntervalle';")
  data = data.fetchone()[0]
  data2= connect.execute("SELECT valeur FROM parametres WHERE cle = 'dureePartie';")
  data2= data2.fetchone()[0]
  connect.close()
  print('Detecting sound...')
  L=[]
  for j in range(int(data2)):
    LED.change_state(j)
    for i in range(int(data*(1/taux_interpolation)*data2)):
        print('Sound value: {0}'.format(sensor.sound))
        L.append(sensor.sound)
        await asyncio.sleep(taux_interpolation)
  return L


async def calibrage(n):
    """
    n = durée en secondes
    Renvoie le seuil bas du son ambiant
    """
    pin = 0

    sensor = GroveSoundSensor(pin)
    taux_interpolation = 0.1

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
