#思路：按照测试结果，取event变化频率为5Hz，即event片段长度为200ms，即在44.1KHz采样得到的音频信号中，每8820个样本为一个event
#考虑到event之间转换的平滑处理，在event间添加2205或2940个样本的过渡带，即20Hz或15Hz，测试得到人能分辨的刺激频率在0-20Hz左右
#在每段event中，提取max,min,rms,频率等作为参数

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import Ampitude_Envelope
from scipy.signal import find_peaks

event_freq = 2
height = 200
window_len = 2048
hop_len = 1024
bits = 8

def seg_env_gen(waveform, sr):
    #分段
    segment_length = sr // event_freq
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
        nor_env = nor_env.astype(int)
        envelopes.append(nor_env)

        #包络详细信息
        max = np.max(nor_env)
        min = np.min(nor_env)
        mean = int(np.mean(nor_env))
        diff = max - min
        magnitude = [max, min, mean, diff]
        magnitudes.append(magnitude)

    return envelopes, magnitudes, num_segments

def seg_freq_gen(waveform, sr):
    #分段
    segment_length = sr // event_freq
    num_segments = len(waveform) // segment_length
    segments = np.array_split(waveform[:num_segments * segment_length], num_segments)

    seg_avg_freqs = []
    main_freqs = []
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
            main_freq = 0
        else:
            peak_frequencies = frequencies[peaks]
            peak_amplitudes = np.abs(fft_result[peaks])
            weighted_avg_frequency = np.sum(peak_frequencies * (peak_amplitudes - height)) / np.sum(peak_amplitudes - height)
            weighted_avg_frequency = weighted_avg_frequency.astype(int)
            max_amplitude_idx = np.argmax(peak_amplitudes)
            main_freq = peak_frequencies[max_amplitude_idx]
            
        seg_avg_freqs.append(weighted_avg_frequency)
        main_freqs.append(main_freq)

    #归一化
    max_val = np.max(seg_avg_freqs)
    min_val = np.min(seg_avg_freqs)
    nor_seg_avg_freqs = ((seg_avg_freqs - min_val) / (max_val - min_val)) * (2 ** bits - 1)
    nor_seg_avg_freqs = nor_seg_avg_freqs.astype(int)

    return seg_avg_freqs, main_freqs

def event_gen(magnitude, freq):
    event = 0

    if(magnitude[0] < 5 or freq < 20):
        event = 0
    elif(freq >= 20 and freq < 100):
        if((magnitude[0] / magnitude[2]) > 2 and magnitude[2] < 36): #类似kick，只敲一下，其他时刻幅度接近0
            if(magnitude[0] < 36):
                event = 1
            elif(magnitude[0] < 72):
                event = 2
            elif(magnitude[0] < 109):
                event = 3
            elif(magnitude[0] < 145):
                event = 4
            elif(magnitude[0] < 181):
                event = 5
            elif(magnitude[0] < 217):
                event = 6
            elif(magnitude[0] <= 255):
                event = 7
            else:
                event = 0
        else: #其他普通低频情况
            if(magnitude[2] < 36):
                event = 1
            elif(magnitude[2] < 72):
                event = 2
            elif(magnitude[2] < 109):
                event = 3
            elif(magnitude[2] < 145):
                event = 4
            elif(magnitude[2] < 181):
                event = 5
            elif(magnitude[2] < 217):
                event = 6
            elif(magnitude[2] <= 255):
                event = 7
            else:
                event = 0
    elif(freq >= 100 and freq < 180):
        if((magnitude[0] / magnitude[2]) > 2 and magnitude[2] < 36): #类似kick，只敲一下，其他时刻幅度接近0
            if(magnitude[0] < 42):
                event = 8
            elif(magnitude[0] < 85):
                event = 9
            elif(magnitude[0] < 127):
                event = 10
            elif(magnitude[0] < 170):
                event = 11
            elif(magnitude[0] < 212):
                event = 12
            elif(magnitude[0] <= 255):
                event = 13
            else:
                event = 0
        else: #其他普通情况
            if(magnitude[2] < 42):
                event = 8
            elif(magnitude[2] < 85):
                event = 9
            elif(magnitude[2] < 127):
                event = 10
            elif(magnitude[2] < 170):
                event = 11
            elif(magnitude[2] < 212):
                event = 12
            elif(magnitude[2] <= 255):
                event = 13
            else:
                event = 0
    elif(freq >= 180 and freq < 300): 
        if((magnitude[0] / magnitude[2]) > 2 and magnitude[2] < 36): #类似kick，只敲一下，其他时刻幅度接近0
            if(magnitude[0] < 51):
                event = 14
            elif(magnitude[0] < 102):
                event = 15
            elif(magnitude[0] < 153):
                event = 16
            elif(magnitude[0] < 204):
                event = 17
            elif(magnitude[0] <= 255):
                event = 18
            else:
                event = 0
        else: #其他普通情况
            if(magnitude[2] < 51):
                event = 14
            elif(magnitude[2] < 102):
                event = 15
            elif(magnitude[2] < 153):
                event = 16
            elif(magnitude[2] < 204):
                event = 17
            elif(magnitude[2] <= 255):
                event = 18
            else:
                event = 0
    elif(freq >= 300 and freq < 500):
        if((magnitude[0] / magnitude[2]) > 2 and magnitude[2] < 36): #类似kick，只敲一下，其他时刻幅度接近0
            if(magnitude[0] < 85):
                event = 19
            elif(magnitude[0] < 170):
                event = 20
            elif(magnitude[0] <= 255):
                event = 21
            else:
                event = 0
        else: #其他普通情况
            if(magnitude[2] < 85):
                event = 19
            elif(magnitude[2] < 170):
                event = 20
            elif(magnitude[2] <= 255):
                event = 21
            else:
                event = 0
    elif(freq >= 500 ):
        if((magnitude[0] / magnitude[2]) > 2 and magnitude[2] < 36): #类似kick，只敲一下，其他时刻幅度接近0
            if(magnitude[0] < 63):
                event = 22
            elif(magnitude[0] < 128):
                event = 23
            elif(magnitude[0] < 191):
                event = 24
            elif(magnitude[0] <= 255):
                event = 25
            else:
                event = 0
        else: #其他普通情况
            if(magnitude[2] < 63):
                event = 22
            elif(magnitude[2] < 128):
                event = 23
            elif(magnitude[2] < 191):
                event = 24
            elif(magnitude[2] <= 255):
                event = 25
            else:
                event = 0

    return event

def run(waveform, sr, output_path):
    envelopes, magnitudes, num_segs = seg_env_gen(waveform, sr)
    avg_freqs, main_freqs = seg_freq_gen(waveform, sr)

    event = 0

    with open(output_path, 'w') as file:

        for i in range(num_segs):
            event = event_gen(magnitudes[i], main_freqs[i])
            file.write(f"{event}\n")


if __name__ == "__main__" :
    filename = r'D:\ROP-Audio-Vibration\audio\Liangzhu.wav'
    waveform, sr = librosa.load(filename, sr=None) 
    output_path = r'D:\ROP-Audio-Vibration\test\output.txt'
    run(waveform, sr, output_path)
   






