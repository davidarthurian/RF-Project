import numpy as np

def generate_signal(fs=2.4e6, duration=1e-3):
    t = np.arange(0, duration, 1/fs)

    signal = (
        np.exp(2j * np.pi * 100e3 * t) +
        0.5 * np.exp(2j * np.pi * 300e3 * t) +
        0.3 * (np.random.randn(len(t)) + 1j*np.random.randn(len(t)))
    )

    return signal