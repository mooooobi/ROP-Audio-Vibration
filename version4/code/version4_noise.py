import numpy as np
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter, ellip

# 生成白噪声
def generate_white_noise(duration, sample_rate):
    samples = duration * sample_rate
    white_noise = np.random.normal(0, 1, samples)
    return white_noise

# 生成静音以分隔噪声
def generate_silence(duration, sample_rate):
    samples = duration * sample_rate
    silence = np.zeros(samples)
    return silence

# 创建带通滤波器
# 巴特沃兹滤波器
def butter_filter(data, lowcut, highcut, sample_rate, order=5):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

# 根据中心频率和1/6倍频程生成掩蔽噪声频率范围
def noise_range_gen(center_freq, fraction=1/6):
     
    multiplier = 2 ** fraction

    min_freq = round(center_freq / multiplier)
    max_freq = round(center_freq * multiplier)
    freq_range = (min_freq, max_freq)

    print(f"{freq_range}")

    return min_freq, max_freq

# 设定参数
duration = 5 # 持续时间，单位为秒
sample_rate = 44100  # 采样率，单位为Hz
order = 2  # 滤波器的阶数
total_time = 300

# 设定通带频率，以下二者选其一
# 方法一：直接设置
lowcut = 7127 # 带通滤波器的低端频率，单位为Hz
highcut = 8980  # 带通滤波器的高端频率，单位为Hz

# # 方法二：通过中心频率以及倍频程计算得到
# center_freq = 125 # 设置中心频率
# lowcut, highcut = noise_range_gen(center_freq=center_freq, fraction=1/6) # 根据中心频率生成掩蔽噪声频率范围

# 使用演示
if __name__ == "__main__":
    # 生成白噪声
    white_noise = generate_white_noise(duration, sample_rate)

    # 应用带通滤波器生成窄带噪声
    noise_basic = butter_filter(white_noise, lowcut, highcut, sample_rate, order)

    # 减弱噪声能量，使得在人体听力舒适范围内
    noise_basic = noise_basic * 0.2

    # 生成暂停时的静音
    silence = generate_silence(duration, sample_rate)

    # 计算循环次数
    times = int(total_time / (duration * 2))

    # 合成响5s停5s的掩蔽噪声
    noise = np.hstack([np.hstack((noise_basic, silence)) for i in range(times)])

    # 将生成的窄带噪声保存为WAV文件
    write(r"D:\ROP-Audio-Vibration\version4\noise_wav\noise.wav", sample_rate, np.int16(noise * 32767))