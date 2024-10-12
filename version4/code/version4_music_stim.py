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
def linear_mapping(data, orig_range, target_range):
    orig_min, orig_max = orig_range
    target_min, target_max = target_range

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

    # 单位转换为分贝
    reference_power = np.max(target_power)
    frame_db = 10 * np.log10(target_power / reference_power + 1e-10)  # +1e-10防止log(0)

    return frame_db

#优化副歌部分电刺激体感变化不明显的问题
#对强度范围线性放大，低于阈值部分置最低值
def optimaize_mag(data, ratio, mag_min, mag_max):
    threshold = int(mag_min + ratio * (mag_max - mag_min))
    relu_data = thre_ReLU(data, threshold)
    opt_mag = linear_mapping(data=relu_data, orig_range=(threshold, mag_max), target_range=(mag_min, mag_max))
    return opt_mag

# 能量映射为电刺激强度（幅度）
def db_2_stimulation_mag(db, mag_min, mag_max):

    # 对能量进行归一化，范围是患者电刺激感知阈值到痛阈
    norm_mag = norm(data=db)
    stim_mag = linear_mapping(data=norm_mag, orig_range=(0,1), target_range=(mag_min,mag_max))

    return stim_mag

# 输出每个事件（片段）的电刺激强度（幅度）到指定文件
def gen_file(data, output_file_path):
    with open(output_file_path, "w") as file:
        file.write(f"{len(data)}\n")
        for i in range(len(data)):
            file.write(f"{data[i]}")
            if(i != len(data) - 1):
                file.write(",")

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

def batch_run(input_file, output_file, sample_rate, event_freq, fn_range, opt_ratio):

    input_path = input_file.split('\\')

    output_path = output_file.split('\\')

    noise_freq_min, noise_freq_max = fn_range

    for i in range(8):
        input_path[-1] = f"0{i+1}.wav"
        output_path[-1] = f"0{i+1}.txt"
        input_file = '\\'.join(input_path)
        output_file = '\\'.join(output_path)

        waveform, sr = librosa.load(input_file, sr=sample_rate)

        # 根据频率范围，得到每个片段的能量
        db = sound_power_db(waveform=waveform, sr=sr, event_freq=event_freq, freq_min=noise_freq_min, freq_max=noise_freq_max)

        # 能量转为电刺激强度
        mag = db_2_stimulation_mag(db=db, mag_min=0, mag_max=255)

        # 如有需要，增加opt_ratio参数，优化强度，增强副歌部分体感变化
        mag = optimaize_mag(data=mag, ratio=opt_ratio, mag_min=0, mag_max=255)

        # 输出到文件
        gen_file(data=mag, output_file_path=output_file)




# 设置音频采样频率
sample_rate = 16000
# 设置事件频率（电刺激事件）
event_freq = 5

# 设置掩蔽噪声频率范围
noise_freq_min = 7127
noise_freq_max = 8980

# 设置电刺激强度（幅度）范围
elec_stim_mag_min = 0 # 感知阈值
elec_stim_mag_max = 255 # 痛阈

# 设置优化比例，比例越大，副歌部分强度变化越明显，但其他部分强度变低
opt_ratio = 0.25

# 使用演示
if __name__ == "__main__":

    # 加载音频，这一步可提前处理，得到waveform和sr即可
    filename = r"D:\ROP-Audio-Vibration\version4\music_wav\08.wav"
    output_file = r'D:\ROP-Audio-Vibration\version4\music_stim_txt\test\08.txt'
    waveform, sr = librosa.load(filename, sr=sample_rate)

    # # 根据频率范围，得到每个片段的能量
    # db = sound_power_db(waveform=waveform, sr=sr, event_freq=event_freq, freq_min=noise_freq_min, freq_max=noise_freq_max)

    # # 能量转为电刺激强度
    # mag = db_2_stimulation_mag(db=db, mag_min=elec_stim_mag_min, mag_max=elec_stim_mag_max)

    # # 如有需要，增加opt_ratio参数，优化强度，增强副歌部分体感变化
    # mag = optimaize_mag(data=mag, ratio=opt_ratio, mag_min=elec_stim_mag_min, mag_max=elec_stim_mag_max)

    # # 输出到文件
    # gen_file(data=mag, output_file_path=output_file)

    # #如有需要，图形化显示
    #show_vibration(data=mag)

    batch_run(input_file=filename, output_file=output_file, sample_rate=sample_rate, event_freq=event_freq, fn_range=(noise_freq_min, noise_freq_max), opt_ratio=opt_ratio)