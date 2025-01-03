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
def norm(data):

    min_value = np.min(data)
    max_value = np.max(data)

    nor_data = ((data - min_value) / (max_value - min_value))

    return nor_data

#小于阈值的数值置为阈值
def thre_ReLU(data, threshold):
    relu_data = [x if x >= threshold else threshold for x in data]
    return relu_data

# 线性映射
def linear_mapping(data, target_range):
    target_min, target_max = target_range

    orig_min = np.min(data)
    orig_max = np.max(data)

    data = np.array(data)

    # 线性映射公式
    mapped_data = target_min + (data - orig_min) * (target_max - target_min) / (orig_max - orig_min)
    
    # 取整
    mapped_data = mapped_data.astype(int)
    
    return mapped_data

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

    # #print(target_power)
    # print(np.max(target_power))

    # 单位转换为分贝
    reference_power = np.max(target_power)
    frame_db = 10 * np.log10(target_power / reference_power + 1e-10)  # +1e-10防止log(0)

    return frame_db

#计算有效平均值
def gen_effective_mean(data):
    binary_data = [1 if x > 0 else 0 for x in data]
    length = np.sum(binary_data)

    return round((np.sum(data) / length),2)

#优化副歌部分电刺激体感变化不明显的问题
#对强度范围线性放大，低于阈值部分置最低值
def optimaize_mag(data, mag_thre, mag_min, mag_max):

    #计算优化比例
    
    total_count = len(data)
    binary_data = [1 if x > mag_thre else 0 for x in data]
    positive_count = sum(binary_data)

    ratio = round(0.95*(positive_count / total_count), 2)
    #print(f"{ratio}\n")

    threshold = int(mag_min + ratio * (mag_max - mag_min))
    #print(f"{threshold}\n")
    relu_data = thre_ReLU(data, threshold)
    opt_mag = linear_mapping(data=relu_data, target_range=(mag_min, mag_max))

    return opt_mag

#对数组中所有数据乘以同一个系数，使得均值为指定值
def normalize_mag(data, target_mean):
    current_mean = gen_effective_mean(data)
    if current_mean == 0:
        return 0
    if current_mean <= target_mean:
        return data
    
    factor = target_mean / current_mean

    return [round(x*factor,2) for x in data]

# 能量映射为电刺激强度（幅度）
def db_2_stimulation_mag(db, mag_min, mag_max):

    # 对能量进行归一化，范围是患者电刺激感知阈值到痛阈
    norm_mag = norm(data=db)
    stim_mag = linear_mapping(data=norm_mag, target_range=(mag_min,mag_max))

    return stim_mag

# 根据中心频率和1/6倍频程生成掩蔽噪声频率范围
def noise_range_gen(center_freq, fraction=1/6):
     
    multiplier = 2 ** fraction

    min_freq = round(center_freq / multiplier)
    max_freq = round(center_freq * multiplier)
    freq_range = (min_freq, max_freq)

    print(f"{freq_range}")

    return min_freq, max_freq

# 输出每个事件（片段）的电刺激强度（幅度）到指定文件
def gen_file(data, output_file_path):
    with open(output_file_path, "w") as file:
        #print(len(data))
        for i in range(len(data)):
            file.write(f"{data[i]}")
            if(i != len(data) - 1):
                file.write(",")

# 图形化显示电刺激强度（幅度）的变化
def show_vibration(data):

    # #计算占比
    # total_count = len(data)
    # binary_data = [1 if x > 200 else 0 for x in data]
    # positive_count = sum(binary_data)
    # percentage_positive = (positive_count / total_count) * 100

    # print(f'刺激占比: {percentage_positive:.2f}%')

    labels = [str(i) for i in range(len(data))]

    plt.figure(figsize=(12, 4))
    plt.bar(labels, data)
    plt.xticks([])
    plt.ylim(0, 255)
    plt.grid()
    plt.show()

    print(np.sum(data))

    print(round((np.sum(data) / len(data)),2))

    binary_data = [1 if x > 0 else 0 for x in data]
    length = np.sum(binary_data)
    print(round((np.sum(data) / length),2))

def batch_test(input_file, output_file, sample_rate, event_freq, fn_range, mag_thre1, mag_thre2):

    input_path = input_file.split('\\')

    noise_freq_min, noise_freq_max = fn_range

    mags = []


    for i in range(8):
        input_path[-1] = f"0{i+1}.wav"
        input_file = '\\'.join(input_path)

        waveform, sr = librosa.load(input_file, sr=sample_rate)

        # 根据频率范围，得到每个片段的能量
        db = sound_power_db(waveform=waveform, sr=sr, event_freq=event_freq, freq_min=noise_freq_min, freq_max=noise_freq_max)

        # 能量转为电刺激强度
        mag = db_2_stimulation_mag(db=db, mag_min=0, mag_max=255)

        mag = optimaize_mag(data=mag, mag_thre=mag_thre1, mag_min=0, mag_max=255)

        mag = normalize_mag(mag, effective_mean)

        mag = optimaize_mag(data=mag, mag_thre=mag_thre2, mag_min=0, mag_max=255)

        mag = normalize_mag(mag, effective_mean)

        mags.append(mag)

    with open(output_file, 'w') as file:
        heads = ["sum", "average", "effective_average"]
        file.write(f" \t{heads[0]:^15}{heads[1]:^10}{heads[2]:^20}\n")
        for i in range(8):
            data = mags[i]
            binary_data = [1 if x > 0 else 0 for x in data]
            length = np.sum(binary_data)

            file.write(f"{i+1}\t")
            file.write(f"{round(np.sum(data), 2):^15}{round((np.sum(data) / len(data)),2):^10}{round((np.sum(data) / length),2):^20}\n")
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i, ax in enumerate(axes.flat):

        data = mags[i]

        labels = [str(j) for j in range(len(data))]
        #ax.figure(figsize=(12, 4))
        ax.bar(labels, data)
        ax.set_title(f'Chart {i+1}')
        ax.set_xticks([])
        ax.set_ylim(0, 255)
        ax.grid()
        
    # 自动调整子图间距
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    
    

# 加载音频
def load_wave(wave_path, sample_rate):

    waveform, sr = librosa.load(wave_path, sr=sample_rate)

    return waveform, sr

# 设置音频采样频率
sample_rate = 16000
# 设置事件频率（电刺激事件）
event_freq = 10
# 设置掩蔽噪声频率范围
# noise_freq_min = 400
# noise_freq_max = 2500

center_freq = 7000
noise_freq_min, noise_freq_max = noise_range_gen(center_freq=center_freq)

# 设置电刺激强度（幅度）范围
elec_stim_mag_min = 0 # 感知阈值
elec_stim_mag_max = 255 # 痛阈

mag_thre1 = 185
mag_thre2 = 120
# 设置统一的有效平均值
effective_mean = 85

# 使用演示
if __name__ == "__main__":

    # 加载音频，这一步可提前处理，得到waveform和sr即可
    filename = r"D:\ROP-Audio-Vibration\version4\music_wav\08.wav"
    output_file = r'D:\ROP-Audio-Vibration\new_algorithm\batch_test.txt'
    #waveform, sr = librosa.load(filename, sr=sample_rate)

    # # 根据频率范围，得到每个片段的能量
    # db = sound_power_db(waveform=waveform, sr=sr, event_freq=event_freq, freq_min=noise_freq_min, freq_max=noise_freq_max)

    # # 能量转为电刺激强度
    # mag = db_2_stimulation_mag(db=db, mag_min=elec_stim_mag_min, mag_max=elec_stim_mag_max)

    # # 如有需要，增加opt_ratio参数，优化强度，增强副歌部分体感变化
    # mag = optimaize_mag(data=mag, mag_min=elec_stim_mag_min, mag_max=elec_stim_mag_max)

    # mag = normalize_mag(mag, effective_mean)

    # # 输出到文件
    # gen_file(data=mag, output_file_path=output_file)

    # # #如有需要，图形化显示
    # show_vibration(data=mag)

    batch_test(input_file=filename, output_file=output_file, sample_rate=sample_rate, event_freq=event_freq, fn_range=(noise_freq_min, noise_freq_max), mag_thre1=mag_thre1, mag_thre2=mag_thre2)

