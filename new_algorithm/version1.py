import numpy as np
import librosa
import math
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import timeit

threshold = 20
event_freq = 5

window_len = 2048
hop_len = 1024
bits = 8

class EnvelopeGenerate:
    def __init__(self, window_len:int=2048, hop_len:int=1024, bits:int=8) -> None:
        self.window_len = window_len
        self.hop_len = hop_len
        self.bits = bits

    def process_env(self,waveform):
        if (len(waveform)-self.window_len) % self.hop_len != 0:
            frame_num = int((len(waveform)-self.window_len)/self.hop_len) + 1
            pad_num = frame_num*self.hop_len + self.window_len - len(waveform)
            waveform = np.pad(waveform,(0,pad_num),mode='edge')
        frame_num = int((len(waveform)-self.window_len)/self.hop_len)
        waveform_ae = []
        for t in range(frame_num):
            current_frame = waveform[t*self.hop_len:(t*self.hop_len + self.window_len)]
            current_ae = max(current_frame)
            waveform_ae.append(current_ae)
        return np.array(waveform_ae)
    
    def normalize_env(self, envelope):
        max_val = np.max(envelope)
        min_val = np.min(envelope)
        normalized_envelope = ((envelope - min_val) / (max_val - min_val)) * (2 ** self.bits - 1)
        return normalized_envelope.astype(int)
    
    def save2file(self, envelope, filename):
        if np.issubdtype(envelope.dtype, np.integer):
            binary_strings = [format(int(val), '0{}b'.format(self.bits)) for val in envelope]
            with open(filename, 'w') as file:
                for a, b in zip(envelope, binary_strings):
                    file.write(f"{a}\t{b}\n")
        else:
            with open(filename, 'w') as file:
                np.savetxt(file, envelope)

def output_env(window_len, hop_len, bits, waveform):
    ae_generate = EnvelopeGenerate(window_len=window_len, hop_len=hop_len, bits=bits)
    envelope = ae_generate.process_env(waveform)
    return envelope

def myFFT(waveform, sr, threshold):
    
    fft_result = np.fft.fft(waveform)
    fft_freqs = np.fft.fftfreq(len(waveform), 1/sr)

    positive_freqs = fft_freqs[:len(waveform)//2]
    magnitude = np.abs(fft_result)[:len(waveform)//2]

    min_freq_distance_hz = 5
    min_peak_distance = int(min_freq_distance_hz * len(waveform) / sr)

    peaks, _ = find_peaks(magnitude, height=threshold, distance=min_peak_distance)

    if len(peaks) == 0:
            peak_freqs = np.array([0])
            peak_amps = np.array([0])
    else:
        peak_freqs = positive_freqs[peaks]
        peak_amps = magnitude[peaks]

    return peak_freqs, peak_amps

def noise_range_gen(center_freq, fraction=1/6):
     
    # width = center_freq//6


    # min_freq = center_freq - width//2
    # max_freq = center_freq + (width - width//2)

     
    multiplier = 2 ** fraction

    min_freq = round(center_freq / multiplier)
    max_freq = round(center_freq * multiplier)
    freq_range = (min_freq, max_freq)

    print(f"{freq_range}")

    return freq_range

def linear_mapping(data, orig_range, target_range):
    orig_min, orig_max = orig_range
    target_min, target_max = target_range

    data = np.array(data)

    # 线性映射公式
    mapped_data = target_min + (data - orig_min) * (target_max - target_min) / (orig_max - orig_min)
    
    # 取整
    mapped_data = mapped_data.astype(int)
    
    return mapped_data


def freq_map(center_freq):

    #假设中心频率范围100到10000，电刺激频率50到300
    nfreq_range = (10, 100)
    efreq_range = (50, 500)

    elec_freq = linear_mapping(int(math.sqrt(center_freq)), nfreq_range, efreq_range)

    return elec_freq

def quadratic_mapping(data, orig_range, target_range):
    orig_min, orig_max = orig_range
    target_min, target_max = target_range

    data = np.array(data)

    # 步骤 1: 归一化数据到 [0, 1]
    normalized_data = (data - orig_min) / (orig_max - orig_min)
    
    # 步骤 2: 应用二次方函数
    quadratic_data = normalized_data ** 2
    
    # 步骤 3: 将二次方后的数据映射到目标范围 
    mapped_data = target_min + quadratic_data * (target_max - target_min)

    mapped_data = mapped_data.astype(int)
    
    return mapped_data

def pulse_width_map(waveform, sr, event_freq):
    #分段
    segment_length = sr // event_freq
    num_segments = len(waveform) // segment_length
    segments = np.array_split(waveform[:num_segments * segment_length], num_segments)

    envelopes = []
    magnitudes = []
    rms_energys = []
    nor_rms_energys = []

    for segment in segments:
        envelope = output_env(window_len=window_len,hop_len=hop_len,bits=bits,waveform=segment)

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

        #rms energy
        current_rms = np.sqrt(np.mean(np.square(nor_env)))
        rms_energys.append(current_rms)

    #rms归一化
    max_rms = np.max(rms_energys)
    min_rms = np.min(rms_energys)
    nor_rms = ((rms_energys - min_rms) / (max_rms - min_rms)) * (2 ** bits - 1)
    nor_rms_energys = nor_rms.astype(int)

    #map
    rms_range = (0,255)
    pw_range = (200,800)
    pws = quadratic_mapping(data=nor_rms_energys, orig_range=rms_range, target_range=pw_range)

    return pws

def norm(data, max_value, min_value, bits):

    nor_data = ((data - min_value) / (max_value - min_value)) * (2 ** bits - 1)
    nor_data = nor_data.astype(int)

    return nor_data

def magnitude_map(waveform, sr, event_freq):
    #分段
    segment_length = sr // event_freq
    num_segments = len(waveform) // segment_length
    segments = np.array_split(waveform[:num_segments * segment_length], num_segments)

    envelopes = []
    magnitudes = []
    rms_energys = []
    nor_rms_energys = []

    for segment in segments:
        envelope = output_env(window_len=window_len,hop_len=hop_len,bits=bits,waveform=segment)

        #归一化
        max_val = np.max(waveform)
        min_val = 0
        nor_env = norm(envelope, max_val, min_val, bits)
        envelopes.append(nor_env)

        #包络详细信息
        max = np.max(nor_env)
        min = np.min(nor_env)
        mean = int(np.mean(nor_env))
        diff = max - min
        magnitude = [max, min, mean, diff]
        magnitudes.append(magnitude)

        #rms energy
        current_rms = np.sqrt(np.mean(np.square(nor_env)))
        rms_energys.append(current_rms)

    #rms归一化
    max_rms = np.max(rms_energys)
    min_rms = np.min(rms_energys)
    nor_rms_energys = norm(rms_energys, max_rms, min_rms, bits)

    #map
    rms_range = (0,255)

    return nor_rms_energys


def event_gen(event_freq, waveform, sr, center_freq):

    segment_length = sr // event_freq
    num_segments = len(waveform) // segment_length
    segments = np.array_split(waveform[:num_segments * segment_length], num_segments)

    noise_range = noise_range_gen(center_freq,1/6)

    trigger = 0
    mag = 0
    elec_freq = 0
    magnitudes = []
    elec_freqs = []
    events = [elec_freqs, magnitudes]

    mags = magnitude_map(waveform=waveform, sr=sr, event_freq=event_freq)

    for i, segment in enumerate(segments):
        trigger = 0
        peak_freqs, peak_amps = myFFT(segment, sr, threshold)
        min_noise, max_noise = noise_range

        for j, freq in enumerate(peak_freqs):

            if freq >= min_noise and freq <= max_noise:
                trigger = 1
                break
        
        if trigger == 0:
            elec_freq = 0
            mag = 0
        elif trigger == 1:
            elec_freq = freq_map(center_freq)
            mag = mags[i]
        
        elec_freqs.append(elec_freq)
        magnitudes.append(mag)

    return events, event_freq

def gen_file(events, output_file_path):
    with open(output_file_path, "w") as file:
        for i in range(len(events[0])):
            file.write(f"{events[0][i]}\t{events[1][i]}\n")

def show_vibration(events):
    binary_data = [1 if x > 0 else 0 for x in events[0]]
    labels = [str(i) for i in range(len(events[0]))]

    #计算占比
    total_count = len(events[0])
    positive_count = sum(binary_data)
    percentage_positive = (positive_count / total_count) * 100

    print(f'刺激占比: {percentage_positive:.2f}%')

    #显示刺激时刻
    plt.figure(figsize=(12, 4))
    plt.bar(labels, events[1])
    plt.xticks([])
    plt.grid()
    plt.show()

if __name__ == "__main__" :

    start_time = timeit.default_timer()

    filename = r'D:\ROP-Audio-Vibration\audio\walkThruFire.mp3'
    output_file = r'D:\ROP-Audio-Vibration\test\output_v1.txt'
    waveform, sr = librosa.load(filename, sr=None)
    
    end_time = timeit.default_timer()
    print(f"{end_time - start_time}")

    center_freq = 8000
    events, event_freq = event_gen(event_freq=event_freq, waveform=waveform, sr=sr, center_freq=center_freq) 


    gen_file(events, output_file)
    
    show_vibration(events)



        





