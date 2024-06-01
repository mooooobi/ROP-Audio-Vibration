from phy import ser_driver
from feature import event
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

event.run(audio,output)

#prepare to play
print('now prepare to play')
sound = AudioSegment.from_file(audio)
sound = sound+15
sound.export('/tmp/audio.wav',format='wav')
wf=wave.open('/tmp/audio.wav','rb')

lut={0:(0,0),1:(5,5),2:(5,10),3:(5,15),4:(5,25),5:(5,30),6:(5,40),7:(5,50),8:(10,5),9:(10,10),10:(10,20),11:(10,30),12:(10,40),13:(10,50),14:(20,5),15:(20,10),16:(20,15),17:(20,25),18:(20,40),19:(30,5),20:(30,25),21:(30,45),22:(40,10),23:(40,25),24:(40,40),25:(40,50)}
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