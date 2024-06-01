from phy import ser_driver
from feature import Ampitude_Envelope
import librosa
import pyaudio
import wave
from pydub import AudioSegment
import os
frame=0
def callback(in_data,frame_count,time_info,status_flags):
    data = wf.readframes(frame_count)
    global frame
    frame+=frame_count
    return (data, pyaudio.paContinue)
print("now prepare the driver init")
driver=ser_driver.Ser_driver()

driver.set_mode1(False)

driver.set_mode2(ser_driver.Mode.G,ser_driver.Mode.V,ser_driver.Mode.G,ser_driver.Mode.G)

# driver.set_voltage('FF')

driver.set_duty(False,50)

# driver.set_frequency(1000)

# driver.send()

# Analyse the audio
print('now analyse the audio')
audio='/home/linchi/rop/ROP-Audio-Vibration/audio/kick.wav'
output='/tmp/output.txt'
waveform, sample_rate = librosa.load(audio,sr=None)
Ampitude_Envelope.run(2048,1024,8,waveform,output)

#prepare to play
print('now prepare to play')
sound = AudioSegment.from_file(audio)
sound = sound+15
sound.export('/tmp/audio.wav',format='wav')
wf=wave.open('/tmp/audio.wav','rb')

pcm=[]
with open(output) as file:
    while(1):
        get=file.readline()
        get: str=get.strip()
        tmp=get.split()
        if(len(tmp)!=2):
            break
        target=tmp[0]
        pcm.append('{:02X}'.format(int(target)))

#play
print('now play')
p=pyaudio.PyAudio()
now=0
stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=wf.getnchannels(),rate=wf.getframerate(),output=True,stream_callback=callback)

while(stream.is_active()):
    tmp=frame//1024
    if(tmp>now):
        now=tmp
        if(now>=len(pcm)):
            break
        driver.set_voltage(pcm[now])
        driver.send()


#after play process
stream.stop_stream()
stream.close()
p.terminate()
os.remove('/tmp/audio.wav')
os.remove('/tmp/output.txt')

print('end')