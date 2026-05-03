import numpy as np

def detect_signals(power, threshold_offset=20):
    noise_floor = np.median(power)
    threshold = noise_floor + threshold_offset

    peaks = np.where(power > threshold)[0]

    return peaks, threshold