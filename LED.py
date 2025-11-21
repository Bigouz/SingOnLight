### BRANCHER SUT LE PORT 12 DU BASE HAT
### https://wiki.seeedstudio.com/Grove-Red_LED/
from grove.gpio import GPIO

class GroveLed(GPIO):
    def __init__(self,pin):
        super(GroveLed, self).__init__(pin, GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(0)


Grove = GroveLed
pin=12
taux_interpolation = 0.1

def main(schema_aleatoire:list[int]):
    import time

    led = GroveLed(pin)

    for i in range(len(schema_aleatoire)):
        if schema_aleatoire[i] == 1:
            led.on()
        elif schema_aleatoire[i] == 0:
            led.off()
        time.sleep(taux_interpolation)
    return schema_aleatoire


if __name__ == '__main__':
    main()

