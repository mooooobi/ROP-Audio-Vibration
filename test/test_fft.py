import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# 加载音频文件
filename = r'D:\ROP-Audio-Vibration\audio\kick.wav'
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

