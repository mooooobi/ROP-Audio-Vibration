import librosa
import numpy as np

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

def run(window_len, hop_len, bits, waveform, output_path):
    ae_generate = EnvelopeGenerate(window_len=window_len, hop_len=hop_len, bits=bits)
    envelope = ae_generate.process_env(waveform)
    normalized_envelope = ae_generate.normalize_env(envelope)
    ae_generate.save2file(envelope=normalized_envelope,filename=output_path)

def output_env(window_len, hop_len, bits, waveform):
    ae_generate = EnvelopeGenerate(window_len=window_len, hop_len=hop_len, bits=bits)
    envelope = ae_generate.process_env(waveform)
    return envelope

if __name__ == "__main__" :
    wave_path = r"D:\ROP-Audio-Vibration\audio\Liangzhu.wav"
    #wave_path = r"D:\PyLearning\audio\kick.wav"
    #wave_path = r"D:\PyLearning\audio\test_beat.wav"
    waveform, sample_rate = librosa.load(wave_path,sr=None)
    output_file_path = r'D:\ROP-Audio-Vibration\test\output.txt'
    ae_generate = EnvelopeGenerate()
    envelope = ae_generate.process_env(waveform)
    normalized_envelope = ae_generate.normalize_env(envelope)
    ae_generate.save2file(envelope=normalized_envelope,filename=output_file_path)
