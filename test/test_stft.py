import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

# 读取音频文件
audio_path = r'D:\ROP-Audio-Vibration\audio\faded.mp3'
y, sr = librosa.load(audio_path, sr=16000)

# 设置 STFT 参数
n_fft = 3200
hop_length = 3200
win_length = 3200

# 计算 STFT
D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length, win_length=win_length)

# 将幅度谱转换为功率谱
power_spectrogram = np.abs(D) ** 2

# 设定频率范围 (例如 500 Hz 到 1000 Hz)
freq_min = 7000
freq_max = 8000

# 计算对应的频率 bin
freqs = np.fft.fftfreq(n_fft, 1/sr)
freq_indices = np.where((freqs >= freq_min) & (freqs <= freq_max))[0]

# 计算每一帧在设定频率范围内的功率
frame_power = np.sum(power_spectrogram[freq_indices, :], axis=0)

# 设置参考功率（可以根据实际情况选择）
reference_power = np.max(frame_power)

# 计算声强（以dB为单位）
frame_db = 10 * np.log10(frame_power / reference_power + 1e-10)  # +1e-10防止log(0)

# 打印每一帧的声强（以dB为单位）到输出文件
output_file = r'D:\ROP-Audio-Vibration\test\output_stft.txt'
with open(output_file, 'w') as f:
    for i, db in enumerate(frame_db):
        f.write(f'Frame {i}: Sound Intensity = {db:.2f} dB\n')

print(f'Sound intensity values saved to {output_file}')

# 可视化声强随时间变化
plt.figure(figsize=(10, 4))
plt.plot(frame_db)
plt.xlabel('Frame')
plt.ylabel('Sound Intensity (dB)')
plt.title(f'Sound Intensity in frequency range {freq_min}-{freq_max} Hz')
plt.show()


