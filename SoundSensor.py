import math
import time
from grove.adc import ADC
import sqlite3

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

def main():
  from grove.helper import SlotHelper
  sh = SlotHelper(SlotHelper.ADC)
  pin = 0

  sensor = GroveSoundSensor(pin)
  taux_interpolation = 0.1
  
  connect = sqlite3.connect("singonlight.db")
  data = connect.execute("SELECT dureeIntervalle FROM parametres;")
  data = data.fetchone()
  data2= connect.execute("SELECT dureePartie FROM parametres;")
  data2= data2.fetchone()
  connect.close()
  print('Detecting sound...')
  L=[]
  for i in range(int(data*taux_interpolation*data2)):
      print('Sound value: {0}'.format(sensor.sound))
      L.append(sensor.sound)
      time.sleep(taux_interpolation)
  return L

if __name__ == '__main__':
    main()
