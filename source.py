from sim import generate_signal

class SignalSource:
    def __init__(self, mode="sim"):
        self.mode = mode

    def get_samples(self, fs):
        if self.mode == "sim":
            return generate_signal(fs=fs)
        else:
            raise NotImplementedError("SDR mode not implemented yet")