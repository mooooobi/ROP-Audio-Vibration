import argparse
import librosa
from feature import Ampitude_Envelope, RMS_energy

def get_parser():
    p = argparse.ArgumentParser(conflict_handler='resolve')
    p.add_argument('--feature', type=str)
    p.add_argument('--wave_path', type=str)
    p.add_argument('--win_len', type=int, default=2048)
    p.add_argument('--hop_len', type=int, default=1024)
    p.add_argument('--bits', type=int, default=8)
    p.add_argument('--output_path', type=str)

    return p

p = get_parser()
opt = p.parse_args()
#print(opt)

waveform, sample_rate = librosa.load(opt.wave_path,sr=None)

Ampitude_Envelope.run(opt.win_len, opt.hop_len, opt.bits, waveform, opt.output_path)
#RMS_energy.run(opt.win_len, opt.hop_len, opt.bits, waveform, opt.output_path)
