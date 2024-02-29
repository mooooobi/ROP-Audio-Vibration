import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT, channels=CHANNEL, rate=RATE,\
                input=True,frames_per_buffer=CHUNK)

while True:
    data = stream.read(CHUNK,exception_on_overflow=False)
    data = np.frombuffer(data, dtype=np.int16)
    print(data)