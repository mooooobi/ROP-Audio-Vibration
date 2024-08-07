# 功能：根据音乐在患者掩蔽噪声频率内的能量，计算电刺激强度（幅度） ps.电刺激的方波频率与占空比不改变
# 输入：掩蔽噪声频率范围，电刺激强度（幅度）承受范围
# 输出：每一次电刺激的强度（幅度）
# 实现方法：
# 将一次电刺激视作一次事件，事件频率为5Hz，即将音频按每200ms为一个片段切片；
# 对每个片段进行fft，得到不同频率的能量，提取掩蔽噪声频率范围内的能量；
# 对各片段的能量进行归一化，线性映射为电刺激强度（幅度）

import numpy as np
import librosa
import matplotlib.pyplot as plt
import timeit

# 归一化，输出【0，1】
def norm(data, target_min, target_max):

    min_value = np.min(data)
    max_value = np.max(data)

    nor_data = ((data - min_value) / (max_value - min_value)) * (target_max - target_min)
    nor_data = nor_data.astype(int)

    return nor_data

# 提取音频指定频率范围内能量
def sound_power_db(waveform, sr, event_freq, freq_min, freq_max):

    # 设定stft参数
    # 使用stft相当于合并了分段与fft两个步骤，即窗口不重叠的stft，故此处参数均相等
    n_fft = int(sr / event_freq)
    hop_length = int(sr / event_freq)
    win_length = int(sr / event_freq)

    D = librosa.stft(waveform, n_fft=n_fft, hop_length=hop_length, win_length=win_length)
    
    # 转换为能量谱
    power_spectrogram = np.abs(D) ** 2

    # 提取指定频率范围内的能量
    freqs = np.fft.fftfreq(n_fft, 1/sr)
    freq_indices = np.where((freqs >= freq_min) & (freqs <= freq_max))[0]
    target_power = np.sum(power_spectrogram[freq_indices, :], axis=0)

    # 单位转换为分贝
    reference_power = np.max(target_power)
    frame_db = 10 * np.log10(target_power / reference_power + 1e-10)  # +1e-10防止log(0)

    return frame_db

# 能量映射为电刺激强度（幅度）
def db_2_stimulation_mag(db, mag_min, mag_max):

    # 对能量进行归一化，范围是患者电刺激感知阈值到痛阈
    stim_mag = norm(data=db, target_min=mag_min, target_max=mag_max)

    return stim_mag

# 输出每个事件（片段）的电刺激强度（幅度）到指定文件
def gen_file(data, output_file_path):
    with open(output_file_path, "w") as file:
        for i in range(len(data)):
            file.write(f"{data[i]}\n")

# 图形化显示电刺激强度（幅度）的变化
def show_vibration(data):

    labels = [str(i) for i in range(len(data))]

    plt.figure(figsize=(12, 4))
    plt.bar(labels, data)
    plt.xticks([])
    plt.grid()
    plt.show()

# 加载音频
def load_wave(wave_path, sample_rate):

    waveform, sr = librosa.load(wave_path, sr=sample_rate)

    return waveform, sr

# 设置音频采样频率
sample_rate = 16000
# 设置事件频率（电刺激事件）
event_freq = 5

# 设置掩蔽噪声频率范围
noise_freq_min = 7000
noise_freq_max = 8000

# 设置电刺激强度（幅度）范围
elec_stim_mag_min = 0 # 感知阈值
elec_stim_mag_max = 255 # 痛阈

# 使用演示
if __name__ == "__main__":

    # 加载音频，这一步可提前处理，得到waveform和sr即可
    filename = r'D:\ROP-Audio-Vibration\audio\spectre.mp3'
    output_file = r'D:\ROP-Audio-Vibration\test\output_v2.txt'
    waveform, sr = librosa.load(filename, sr=sample_rate)

    # 根据频率范围，得到每个片段的能量
    db = sound_power_db(waveform=waveform, sr=sr, event_freq=event_freq, freq_min=noise_freq_min, freq_max=noise_freq_max)

    # 能量转为电刺激强度
    mag = db_2_stimulation_mag(db=db, mag_min=elec_stim_mag_min, mag_max=elec_stim_mag_max)

    # 输出到文件
    gen_file(data=mag, output_file_path=output_file)

    # #如有需要，图形化显示
    # show_vibration(data=mag)

