import numpy as np
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter, ellip

# 生成白噪声
def generate_white_noise(duration, sample_rate):
    samples = duration * sample_rate
    white_noise = np.random.normal(0, 1, samples)
    return white_noise

# 创建带通滤波器
def ellip_filter(data, lowcut, highcut, sample_rate, rp, rs, order=3):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = ellip(order, rp, rs, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

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
lowcut = 445 # 带通滤波器的低端频率，单位为Hz
highcut = 561  # 带通滤波器的高端频率，单位为Hz
center_freq = 125 # 设置中心频率
rp = 0.01  # 通带最大波动（dB）
rs = 30.0  # 阻带最小衰减（dB）
order = 2  # 滤波器的阶数

# 根据中心频率生成掩蔽噪声频率范围
lowcut, highcut = noise_range_gen(center_freq=center_freq)

# 生成白噪声
white_noise = generate_white_noise(duration, sample_rate)

# 应用带通滤波器生成窄带噪声
#narrowband_noise = ellip_filter(white_noise, lowcut, highcut, sample_rate, rp, rs, order)

narrowband_noise = butter_filter(white_noise, lowcut, highcut, sample_rate, order)

narrowband_noise = narrowband_noise * 0.25

# 将生成的窄带噪声保存为WAV文件
write(r"D:\ROP-Audio-Vibration\output_narrowband_noise.wav", sample_rate, np.int16(narrowband_noise * 32767))

#print("窄带噪声已生成并保存为 narrowband_noise.wav")
