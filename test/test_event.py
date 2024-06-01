#思路：按照测试结果，取event变化频率为5Hz，即event片段长度为200ms，即在44.1KHz采样得到的音频信号中，每8820个样本为一个event
#考虑到event之间转换的平滑处理，在event间添加2205或2940个样本的过渡带，即20Hz或15Hz，测试得到人能分辨的刺激频率在0-20Hz左右
#在每段event中，提取max,min,rms,频率等作为参数

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import Ampitude_Envelope
from scipy.signal import find_peaks

filename = r'D:\ROP-Audio-Vibration\audio\Liangzhu.wav'
waveform, sr = librosa.load(filename, sr=None) 

#对音频信号分段，每段对应一个event
segment_length = 8820
num_segments = len(waveform) // segment_length
segments = np.array_split(waveform[:num_segments * segment_length], num_segments)

# #打印每段长度
# for i, segment in enumerate(segments):
#     print("Segment", i+1, "length:", len(segment))
# print(segments[25])

#提取每一段的包络
envelopes = []
magnitudes = []
for segment in segments:
    envelope = Ampitude_Envelope.output_env(window_len=2048,hop_len=5024,bits=8,waveform=segment)
    #归一化
    max_val = np.max(waveform)
    min_val = 0
    nor_env = ((envelope - min_val) / (max_val - min_val)) * (2 ** 8 - 1)
    envelopes.append(nor_env)
    #包络详细信息
    max = np.max(nor_env)
    min = np.min(nor_env)
    mean = np.mean(nor_env)
    diff = max - min
    magnitude = [max, min, mean, diff]
    magnitudes.append(magnitude)


#提取每一段的频率信息
for i, segment in enumerate(segments):
    # 执行FFT
    fft_result = np.fft.fft(segment)
    # 计算频率
    frequencies = np.fft.fftfreq(len(segment), 1/sr)
    min_freq_distance_hz = 150
    min_peak_distance = int(min_freq_distance_hz * len(segment) / sr)
    peaks, _ = find_peaks(np.abs(fft_result)[:len(segment)//2], height=200,distance=min_peak_distance)
    # 提取大于200的峰值对应的频率
    peak_frequencies = frequencies[peaks]
    peak_amplitudes = np.abs(fft_result[peaks])
    weighted_avg_frequency = np.sum(peak_frequencies * (peak_amplitudes - 200)) / np.sum(peak_amplitudes - 200)
    #print(i)
    print(peak_frequencies)
    print(peak_amplitudes)
    print(weighted_avg_frequency)


# # 绘制振幅谱图
# plt.plot(segment, label='Waveform')
# plt.title('Waveform')
# plt.xlabel('Samples')
# plt.ylabel('Amplitude')
# plt.legend()

# plt.figure(figsize=(8, 4))
# plt.plot(frequencies[:len(segment)//2], np.abs(fft_result)[:len(segment)//2])
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Amplitude')
# plt.title('FFT Result')
# plt.grid()
# plt.show()