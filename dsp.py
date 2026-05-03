import numpy as np

def compute_power_spectrum(samples):
    fft_vals = np.fft.fftshift(np.fft.fft(samples))
    power = 20 * np.log10(np.abs(fft_vals) + 1e-12)
    return power

def bin_to_freq(bin_index, fs, n):
    return (bin_index - n//2) * (fs / n)