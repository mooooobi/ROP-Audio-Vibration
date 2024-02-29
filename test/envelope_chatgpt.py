import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import librosa
import librosa.display

def calculate_envelope(signal, fs):
    # 使用希尔伯特变换来获取包络
    analytic_signal = scipy.signal.hilbert(signal)
    amplitude_envelope = np.abs(analytic_signal)

    # 对包络进行低通滤波以平滑结果
    cutoff_frequency = 10.0  # 设置低通滤波器的截止频率
    nyquist = 0.5 * fs
    normalized_cutoff = cutoff_frequency / nyquist
    b, a = scipy.signal.butter(1, normalized_cutoff, btype='low')
    smoothed_envelope = scipy.signal.filtfilt(b, a, amplitude_envelope)

    return amplitude_envelope

# 读取音频文件
wave_path = r"D:\PyLearning\audio\kick.wav"
audio_signal, fs = librosa.load(wave_path,sr=None)


# # 计算音频信号的包络
# envelope = calculate_envelope(audio_signal, fs)

# # 绘制原始音频信号和包络
time = np.arange(0, len(audio_signal)) / fs

# plt.figure(figsize=(10, 6))
# # plt.plot(time, audio_signal, color = 'b')
# # plt.plot(time, envelope, color='r')
# librosa.display.waveshow(audio_signal,sr=fs, color = 'b')
# librosa.display.waveshow(envelope,sr=fs, color = 'r')

# plt.tight_layout()
# plt.show()


def calculate_shannon_energy(signal, window_size):
    squared_signal = (-1) * np.log(np.square(signal)+1e-10) * np.square(signal)
    energy = np.convolve(squared_signal, np.ones(window_size)/window_size, mode='valid')
    return energy

# 计算香农能量包络
window_size = 1024  # 调整窗口大小以满足你的需求
shannon_energy = calculate_shannon_energy(audio_signal, window_size)

# 插值以匹配原始信号的长度
shannon_energy = np.interp(np.arange(len(audio_signal)), np.arange(len(shannon_energy)), shannon_energy)

print(f"length:{len(shannon_energy)}\nEnvelope:{shannon_energy}")

# 绘制原始音频信号和香农能量包络
plt.figure(figsize=(10, 6))


plt.plot(time, audio_signal, color = 'b')

plt.plot(time, shannon_energy, color='r')

plt.tight_layout()
plt.show()
