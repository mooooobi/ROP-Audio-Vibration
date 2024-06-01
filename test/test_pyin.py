import librosa
import matplotlib.pyplot as plt
import numpy as np

# 加载音频文件
filename = r'D:\ROP-Audio-Vibration\audio\kick.wav'
waveform, sr = librosa.load(filename, sr=None)  # sr=None 保持原始采样率

# 绘制波形图
plt.figure(figsize=(14, 5))
plt.plot(waveform)
plt.title('Waveform of the Audio Signal')
plt.xlabel('Time (samples)')
plt.ylabel('Amplitude')
plt.show()

# 提取基频
f0, voiced_flag, voiced_probs = librosa.pyin(waveform, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

# 提取谐波频率
harmonic = librosa.effects.harmonic(waveform)

# 可视化波形和基频
plt.figure(figsize=(14, 8))

# 绘制波形
plt.subplot(3, 1, 1)
plt.plot(waveform, label='Waveform')
plt.title('Waveform')
plt.xlabel('Samples')
plt.ylabel('Amplitude')
plt.legend()

# 绘制基频
plt.subplot(3, 1, 2)
plt.plot(f0, label='F0 (Fundamental Frequency)', color='r')
plt.title('Fundamental Frequency (F0)')
plt.xlabel('Frames')
plt.ylabel('Frequency (Hz)')
plt.legend()

# 绘制谐波频率
plt.subplot(3, 1, 3)
plt.plot(harmonic, label='Harmonics')
plt.title('Harmonics')
plt.xlabel('Samples')
plt.ylabel('Amplitude')
plt.legend()

plt.tight_layout()
plt.show()