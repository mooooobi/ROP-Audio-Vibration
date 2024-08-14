import numpy as np
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter

# 生成白噪声
def generate_white_noise(duration, sample_rate):
    samples = duration * sample_rate
    white_noise = np.random.normal(0, 1, samples)
    return white_noise

# 创建带通滤波器
def bandpass_filter(data, lowcut, highcut, sample_rate, order=5):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

# 设定参数
duration = 10 # 持续时间，单位为秒
sample_rate = 44100  # 采样率，单位为Hz
lowcut = 800 # 带通滤波器的低端频率，单位为Hz
highcut = 1200  # 带通滤波器的高端频率，单位为Hz

# 生成白噪声
white_noise = generate_white_noise(duration, sample_rate)

# 应用带通滤波器生成窄带噪声
narrowband_noise = bandpass_filter(white_noise, lowcut, highcut, sample_rate)

# 将生成的窄带噪声保存为WAV文件
write(r".\output_narrowband_noise.wav", sample_rate, np.int16(narrowband_noise * 32767))

print("窄带噪声已生成并保存为 narrowband_noise.wav")
