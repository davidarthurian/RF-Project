import numpy as np

def detect_signals(power, threshold_offset=6):
    noise_floor = np.mean(power)
    threshold = noise_floor + threshold_offset

    peaks = np.where(power > threshold)[0]

    return peaks, threshold