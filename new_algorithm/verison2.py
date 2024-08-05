import numpy as np
import librosa
import matplotlib.pyplot as plt
import timeit

sample_rate = 16000
event_freq = 5

noise_freq_min = 7000
noise_freq_max = 8000

hearing_t = 1

elec_stim_mag_min = 0
elec_stim_mag_max = 255

def norm(data, target_min, target_max):

    min_value = np.min(data)
    max_value = np.max(data)

    nor_data = ((data - min_value) / (max_value - min_value)) * (target_max - target_min)
    nor_data = nor_data.astype(int)

    return nor_data

def sound_power_db(waveform, sr, event_freq, freq_min, freq_max):

    # 设置 STFT 参数
    n_fft = int(sr / event_freq)
    hop_length = int(sr / event_freq)
    win_length = int(sr / event_freq)

    # 计算 STFT
    D = librosa.stft(waveform, n_fft=n_fft, hop_length=hop_length, win_length=win_length)

    # 将幅度谱转换为功率谱
    power_spectrogram = np.abs(D) ** 2

    # 计算对应的频率 bin
    freqs = np.fft.fftfreq(n_fft, 1/sr)
    freq_indices = np.where((freqs >= freq_min) & (freqs <= freq_max))[0]

    # 计算每一帧在设定频率范围内的功率
    frame_power = np.sum(power_spectrogram[freq_indices, :], axis=0)

    # 设置参考功率（可以根据实际情况选择）
    reference_power = np.max(frame_power)

    # 计算声强（以dB为单位）
    frame_db = 10 * np.log10(frame_power / reference_power + 1e-10)  # +1e-10防止log(0)

    return frame_db

def db_2_stimulation_mag(db, mag_min, mag_max):

    stim_mag = norm(data=db, target_min=mag_min, target_max=mag_max)

    return stim_mag

def gen_file(events, output_file_path):
    with open(output_file_path, "w") as file:
        for i in range(len(events)):
            file.write(f"{events[i]}\n")

def show_vibration(events):

    labels = [str(i) for i in range(len(events))]

    #显示刺激时刻
    plt.figure(figsize=(12, 4))
    plt.bar(labels, events)
    plt.xticks([])
    plt.grid()
    plt.show()

def load_wave(wave_path, sample_rate):

    waveform, sr = librosa.load(wave_path, sr=sample_rate)

    return waveform, sr

if __name__ == "__main__":

    filename = r'D:\ROP-Audio-Vibration\audio\alone.mp3'
    output_file = r'D:\ROP-Audio-Vibration\test\output_v2.txt'
    waveform, sr = librosa.load(filename, sr=sample_rate)

    db = sound_power_db(waveform, sr, event_freq, noise_freq_min, noise_freq_max)

    mag = db_2_stimulation_mag(db, elec_stim_mag_min, elec_stim_mag_max)

    gen_file(mag, output_file)

    show_vibration(mag)

