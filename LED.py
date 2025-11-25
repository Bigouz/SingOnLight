### BRANCHER SUT LE PORT 12 DU BASE HAT
### https://wiki.seeedstudio.com/Grove-Red_LED/
from grove.gpio import GPIO
import sqlite3
import asyncio

class GroveLed(GPIO):
    def __init__(self,pin):
        super(GroveLed, self).__init__(pin, GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(0)


Grove = GroveLed
pin=12
connect = sqlite3.connect("singonlight.db")
dureeIntervalle = connect.execute("SELECT valeur FROM parametres WHERE cle = 'dureeIntervalle';").fetchone()[0]
connect.close()

async def main(schema_aleatoire:list[int]):
    """utiliser LED.run() a la place car c'edt une fonction async. """
    import time

    led = GroveLed(pin)

    for i in range(len(schema_aleatoire)):
        if schema_aleatoire[i] == 1:
            led.on()
        elif schema_aleatoire[i] == 0:
            led.off()
        
        await asyncio.sleep(dureeIntervalle)
    return schema_aleatoire

def run(schema_aleatoire:list[int]):
    """a utiliser pour executer main()"""
    asyncio.run(main(schema_aleatoire))

if __name__ == '__main__':
    asyncio.run(main())

