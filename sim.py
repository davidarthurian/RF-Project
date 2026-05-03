import numpy as np

def generate_signal(fs=2.4e6, duration=1e-3):
    t = np.arange(0, duration, 1 / fs)

    # Narrow tone at 100 kHz
    tone_1 = np.exp(2j * np.pi * 100e3 * t)

    # Slightly wider "signal-like" tone around 300 kHz
    tone_2 = (
        0.5 * np.exp(2j * np.pi * 295e3 * t) +
        0.5 * np.exp(2j * np.pi * 300e3 * t) +
        0.5 * np.exp(2j * np.pi * 305e3 * t)
    )

    noise = 0.3 * (np.random.randn(len(t)) + 1j * np.random.randn(len(t)))

    signal = tone_1 + tone_2 + noise

    return signal