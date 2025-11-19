import math
import time
from grove.adc import ADC

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

  print('Detecting sound...')
  while True:
      print('Sound value: {0}'.format(sensor.sound))
      time.sleep(.3)

if __name__ == '__main__':
    main()
