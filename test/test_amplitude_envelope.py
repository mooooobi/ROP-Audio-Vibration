import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

wave_path = r"D:\ROP-Audio-Vibration\audio\Liangzhu.wav"
#wave_path = r"D:\PyLearning\audio\kick.wav"
#wave_path = r"D:\PyLearning\audio\test_beat.wav"
waveform, sample_rate = librosa.load(wave_path,sr=None)

#分帧取最大值
def Amplitude_Envelope_max(waveform,frame_length,hop_length):
    if (len(waveform)-frame_length) % hop_length != 0:
        frame_num = int((len(waveform)-frame_length)/hop_length) + 1
        pad_num = frame_num*hop_length + frame_length - len(waveform)
        waveform = np.pad(waveform,(0,pad_num),mode='edge')
    frame_num = int((len(waveform)-frame_length)/hop_length)
    waveform_ae = []
    for t in range(frame_num):
        current_frame = waveform[t*hop_length:(t*hop_length + frame_length)]
        current_ae = max(current_frame)
        waveform_ae.append(current_ae)
    return np.array(waveform_ae)

#Hilbert
def MyHilbert(signal):
    n0 = len(signal)
    n = 1
    while n < len(signal):
        n *= 2
    pad_length = n - len(signal)
    signal = np.pad(signal,(0,pad_length),mode='constant')

     # 进行FFT变换
    spectrum = np.fft.fft(signal)

    # 对FFT结果进行处理
    spectrum[1:n0] *= 2
    spectrum[n0:] = 0
    spectrum[0] = 1
    spectrum[n0] = 0

    # 反向FFT变换
    hilbert = np.real(np.fft.ifft(spectrum))
    hilbert = hilbert[:n0]

    return hilbert

def AE_by_Hilbert(waveform):
    analytic_waveform = hilbert(waveform)
    waveform_ae = np.abs(analytic_waveform)
    return waveform_ae

#shannon energy
def AE_by_ShannonEnergy(waveform,window_length):
    shannon_energy = np.square(waveform) * np.log(np.square(waveform)+1e-10) * (-1)
    waveform_ae = np.convolve(shannon_energy, np.ones(window_length)/window_length, mode='valid')
    return waveform_ae

#分帧取最大值的包络生成
frame_size = 2048
hop_size = int(frame_size*0.5)
waveform_AE = Amplitude_Envelope_max(waveform=waveform,frame_length=frame_size,hop_length=hop_size)
frame_scale = np.arange(0,len(waveform_AE))
time_scale = librosa.frames_to_time(frames=frame_scale,hop_length=hop_size)

max_val = np.max(waveform_AE)
min_val = np.min(waveform_AE)
normalized_AE = ((waveform_AE - min_val)/(max_val - min_val)) * (2 ** 8 - 1)
normalized_AE_int = normalized_AE.astype(int)
binary_strings = [format(int(val), '0{}b'.format(8)) for val in normalized_AE_int]

# plt.figure(figsize=(20,10))
# librosa.display.waveshow(waveform,color = 'b')
# plt.plot(time_scale,normalized_AE_int,color = 'r')
# plt.show()

#希尔伯特变换求包络的生成
#waveform_AE = AE_by_Hilbert(waveform)

#香农能量包络生成
# window_size = 1024
# waveform_AE = AE_by_ShannonEnergy(waveform=waveform,window_length=window_size)
# waveform_AE = np.interp(np.arange(len(waveform)), np.arange(len(waveform_AE)), waveform_AE)


#打印
print(f"length:{len(waveform_AE)}\nEnvelope:{normalized_AE_int}\nsample_rate:{sample_rate}")
#输出文本
output_file_path = 'D:\ROP-Audio-Vibration\output.txt'
with open(output_file_path,'w') as file:
    #np.savetxt(file, normalized_AE_int,fmt='%d')
    for a, b in zip(normalized_AE_int, binary_strings):
        file.write(f"{a}\t{b}\n")

# time = np.arange(0,len(waveform)) / sample_rate
# plt.figure(figsize=(20,10))
# librosa.display.waveshow(waveform,color = 'b')
#plt.plot(time,waveform,color = 'b')
#plt.plot(time_scale,waveform_AE,color = 'r')
#plt.title("AE_frame_MAX")
#librosa.display.waveshow(waveform_AE,sr=sample_rate, color = 'r')
#plt.plot(time,waveform_AE,color = 'r')
#plt.title("AE by Hilbert")
#plt.show()
