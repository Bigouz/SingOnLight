### BRANCHER EN A0
### https://wiki.seeedstudio.com/Grove-Sound_Sensor/
import time
from grove.adc import ADC
import sqlite3
import asyncio

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

async def main():
  """ utiliser run() a la place car async"""
  from grove.helper import SlotHelper
  sh = SlotHelper(SlotHelper.ADC)
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
  for i in range(int(data*(1/taux_interpolation)*data2)):
      print('Sound value: {0}'.format(sensor.sound))
      L.append(sensor.sound)
      await asyncio.sleep(taux_interpolation)
  return L

def run():
  """ a utiliser pour executer main"""
  return asyncio.run(main())

if __name__ == '__main__':
    main()
