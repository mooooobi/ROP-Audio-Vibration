import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

# 读取txt文件并提取幅值 (逗号分隔)
def read_amplitude_from_txt(file_path):
    with open(file_path, 'r') as f:
        data = f.read().strip()  # 读取所有内容
        amplitudes = np.array([int(x) for x in data.split(',')])  # 按逗号分隔并转换为整数
    return amplitudes

# 生成单个500 Hz的方波段，指定持续时间和振幅
def generate_square_wave_segment(amplitude, freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    square_wave = np.sign(np.sin(2 * np.pi * freq * t)) * (amplitude / 255)  # 振幅归一化到0-1之间
    return square_wave

# 拼接所有方波段
def concatenate_square_wave_segments(amplitudes, freq, segment_duration, sample_rate):
    wave = np.array([])
    for amplitude in amplitudes:
        segment = generate_square_wave_segment(amplitude, freq, segment_duration, sample_rate)
        wave = np.concatenate((wave, segment))
    return wave

# 保存为WAV文件
def save_wavefile(filename, sample_rate, data):
    # 将数据缩放到-32767到32767之间，并转换为16位整数
    data = np.int16(data * 32767)
    wavfile.write(filename, sample_rate, data)

# 主流程
file_path = r'D:\ROP-Audio-Vibration\new_algorithm\output_v2.txt'  # txt文件路径
sample_rate = 16000  # 采样率
wave_freq = 20  # 方波频率
event_freq = 5
segment_duration = 1/event_freq  # 每段方波持续时间，秒

# 读取幅值
amplitudes = read_amplitude_from_txt(file_path)

# 生成拼接后的方波
concatenated_wave = concatenate_square_wave_segments(amplitudes, wave_freq, segment_duration, sample_rate)

# 保存音频文件
save_wavefile(r'D:\ROP-Audio-Vibration\new_algorithm\output_square_wave.wav', sample_rate, concatenated_wave)

# 可视化生成的波形
plt.plot(concatenated_wave[44100:88200])

plt.show()
