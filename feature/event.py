#思路：按照测试结果，取event变化频率为5Hz，即event片段长度为200ms，即在44.1KHz采样得到的音频信号中，每8820个样本为一个event
#考虑到event之间转换的平滑处理，在event间添加2205或2940个样本的过渡带，即20Hz或15Hz，测试得到人能分辨的刺激频率在0-20Hz左右
#在每段event中，提取max,min,rms,频率等作为参数

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import Ampitude_Envelope
from scipy.signal import find_peaks

segment_length = 8820
height = 200
window_len = 2048
hop_len = 1024
bits = 8

def seg_env_gen(waveform):
    #分段
    num_segments = len(waveform) // segment_length
    segments = np.array_split(waveform[:num_segments * segment_length], num_segments)

    envelopes = []
    magnitudes = []
    for segment in segments:
        envelope = Ampitude_Envelope.output_env(window_len=window_len,hop_len=hop_len,bits=bits,waveform=segment)

        #归一化
        max_val = np.max(waveform)
        min_val = 0
        nor_env = ((envelope - min_val) / (max_val - min_val)) * (2 ** bits - 1)
        envelopes.append(nor_env)

        #包络详细信息
        max = np.max(nor_env)
        min = np.min(nor_env)
        mean = np.mean(nor_env)
        diff = max - min
        magnitude = [max, min, mean, diff]
        magnitudes.append(magnitude)

    return envelopes, magnitudes, num_segments

def seg_freq_gen(waveform, sr):
    #分段
    num_segments = len(waveform) // segment_length
    segments = np.array_split(waveform[:num_segments * segment_length], num_segments)

    seg_avg_freqs = []
    for i, segment in enumerate(segments):

        # 执行FFT
        fft_result = np.fft.fft(segment)
        # 计算频率
        frequencies = np.fft.fftfreq(len(segment), 1/sr)

        #提取平均峰值频率
        min_freq_distance_hz = 150
        min_peak_distance = int(min_freq_distance_hz * len(segment) / sr)

        peaks, _ = find_peaks(np.abs(fft_result)[:len(segment)//2], height=height,distance=min_peak_distance)

        if len(peaks) == 0:
            peak_frequencies = np.array([0])
            peak_amplitudes = np.array([0])
            weighted_avg_frequency = 0
        else:
            peak_frequencies = frequencies[peaks]
            peak_amplitudes = np.abs(fft_result[peaks])
            weighted_avg_frequency = np.sum(peak_frequencies * (peak_amplitudes - height)) / np.sum(peak_amplitudes - height)

        seg_avg_freqs.append(weighted_avg_frequency)

    return seg_avg_freqs

def event_args_gen(magnitude, freq):
    out_freq = 0
    duty_cycle = 0
    amp = '00'

    #幅值与占空比

    #频率
    if freq == 0:
        duty_cycle = 5


    else:
        out_freq = (freq / 1000) * 50


    return out_freq, duty_cycle, amp

def run(waveform, sr):
    envelopes, magnitudes, num_segs = seg_env_gen(waveform)
    freqs = seg_freq_gen(waveform, sr)

    args_tbl = []
    for i in num_segs:
        freq, duty_cycle, amp = event_args_gen(magnitudes[i], freqs[i])
        args = [freq, duty_cycle, amp]
        args_tbl.append(args)

    return args_tbl







