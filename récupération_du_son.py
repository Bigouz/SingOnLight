#Aidé en parti par l'ia

import grovepi
import numpy as np
import time
import SoundSensor.py as sound

# definition du décibel minimal a dépasser
def recuperation son (n) : 
  n # durée en seconde définit par l'utilisateur dans les paramètre
  l = []
  start = time.time()
  while time.time() - start<n:
    l.append(sound.main())
  return l

"""
CHUNK = 1000 #Definition de la taille de l'échantillon audio
FORMAT = pyaudio.paInt16
CHANNELS = 1 # 1 pour mono et 2 pour stéréo
RATE = 44100

#Ouverture du capteur son

p = pyaudio.PyAudio()
son = p.open(format = FORMAT,
             channels = CHANNELS,
             rate = RATE,
             input = True,
             frame_per_buffer = CHUNK)

#Lire le son
try:
  While True:
  donee = son.read(CHUNK) # lire le morceau du son
  audio_donee = np.frombuffer(donee, dtype = np.int16) # Convertir en nombres utilisables
  volume = np.sqrt(np.mean(audio_data**2)) # Calculer le volume

  #afficher le volume
  print(f"Volume : {volume}")
  
  # détécter si quelqu'un parle
  if volume > 1000:
    print("ça parle")

except KeyboardInterrupt:
  print("arret du programme")
  son.stop_stream()
  son.close()
  p.terminate()
  """

