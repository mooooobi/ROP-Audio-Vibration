import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# 加载音频文件
filename = r'D:\ROP-Audio-Vibration\sample_noise\20240828_103746.mp3'
#filename = r'D:\ROP-Audio-Vibration\noise.wav'
#filename = r'D:\ROP-Audio-Vibration\output_noise.wav'
filename = r'D:\ROP-Audio-Vibration\audio\alone.mp3'
waveform, sr = librosa.load(filename, sr=None)

# 执行FFT
fft_result = np.fft.fft(waveform)
# 计算频率
frequencies = np.fft.fftfreq(len(waveform), 1/sr)
    
# 绘制振幅谱图
plt.figure(figsize=(8, 4))
plt.plot(frequencies[:len(waveform)//2], np.abs(fft_result)[:len(waveform)//2])
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('FFT Result')
plt.grid()
plt.show()

