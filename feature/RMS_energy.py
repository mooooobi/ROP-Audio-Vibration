import librosa
import numpy as np

class RMSGenerate:
    def __init__(self, window_len:int=2048, hop_len:int=1024, bits:int=8) -> None:
        self.window_len = window_len
        self.hop_len = hop_len
        self.bits = bits

    def process_rms(self,waveform):
        if (len(waveform)-self.window_len) % self.hop_len != 0:
            frame_num = int((len(waveform)-self.window_len)/self.hop_len) + 1
            pad_num = frame_num*self.hop_len + self.window_len - len(waveform)
            waveform = np.pad(waveform,(0,pad_num),mode='edge')
        frame_num = int((len(waveform)-self.window_len)/self.hop_len)
        rms = []
        for t in range(frame_num):
            current_frame = waveform[t*self.hop_len:(t*self.hop_len + self.window_len)]
            current_rms = np.sqrt(np.mean(np.square(current_frame)))
            rms.append(current_rms)
        return np.array(rms)
    
    def normalize_rms(self, rms):
        max_val = np.max(rms)
        min_val = np.min(rms)
        normalized_rms = ((rms - min_val) / (max_val - min_val)) * (2 ** self.bits - 1)
        return normalized_rms.astype(int)
    
    def save2file(self, rms, filename):
        if np.issubdtype(rms.dtype, np.integer):
            binary_strings = [format(int(val), '0{}b'.format(self.bits)) for val in rms]
            with open(filename, 'w') as file:
                for a, b in zip(rms, binary_strings):
                    file.write(f"{a}\t{b}\n")
        else:
            with open(filename, 'w') as file:
                np.savetxt(file, rms)

def run(window_len, hop_len, bits, waveform, output_path):
    rms_generate = RMSGenerate(window_len=window_len, hop_len=hop_len, bits=bits)
    rms = rms_generate.process_rms(waveform)
    normalized_rms = rms_generate.normalize_rms(rms)
    rms_generate.save2file(rms=normalized_rms,filename=output_path)


if __name__ == "__main__" :
    wave_path = r"D:\ROP-Audio-Vibration\audio\Liangzhu.wav"
    waveform, sample_rate = librosa.load(wave_path,sr=None)
    output_file_path = 'D:\ROP-Audio-Vibration\output.txt'
    rms_generate = RMSGenerate()
    rms = rms_generate.process_rms(waveform)
    normalized_rms = rms_generate.normalize_rms(rms)
    rms_generate.save2file(rms=normalized_rms,filename=output_file_path)