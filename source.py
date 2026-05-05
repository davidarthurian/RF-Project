from sim import generate_signal
from rtlsdr import RtlSdr

class SignalSource:
    def __init__(self, mode="sim", center_freq=100e6, sample_rate=2.4e6):
        self.mode = mode
        self.fs = sample_rate

        if self.mode == "sdr":
            self.sdr = RtlSdr()
            self.sdr.sample_rate = self.fs
            self.sdr.center_freq = center_freq
            self.sdr.gain = 'auto'

    def get_samples(self, fs):
        if self.mode == "sim":
            return generate_signal(fs=fs)

        elif self.mode == "sdr":
            return self.sdr.read_samples(256*1024)

    def close(self):
        if self.mode == "sdr":
            self.sdr.close()