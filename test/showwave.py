import wave
import numpy as np
import matplotlib.pyplot as plt

# 读取音频文件
def read_wave_file(file_path):
    with wave.open(file_path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        
        # 读取音频数据
        audio_data = wf.readframes(n_frames)
        
        # 将音频数据转换为numpy数组
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        return audio_array, framerate

# 绘制波形图
def plot_waveform(audio_array, framerate):
    plt.figure(figsize=(12, 6))
    
    # 创建时间轴
    time = np.linspace(0, len(audio_array) / framerate, num=len(audio_array))
    
    plt.plot(time, audio_array)
    plt.title("Waveform")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()

# 示例使用
file_path = r'D:\ROP-Audio-Vibration\audio\kick.wav'  # 替换为你的音频文件路径
audio_array, framerate = read_wave_file(file_path)
plot_waveform(audio_array, framerate)


