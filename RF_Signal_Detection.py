import numpy as np
import matplotlib.pyplot as plt

# Simulated signal: two frequencies + noise
fs = 2.4e6
t = np.arange(0, 1e-3, 1/fs)

signal = (
    np.exp(2j * np.pi * 100e3 * t) +   # tone 1
    0.5 * np.exp(2j * np.pi * 300e3 * t) +  # tone 2
    0.2 * (np.random.randn(len(t)) + 1j*np.random.randn(len(t)))
)

# FFT
fft_vals = np.fft.fftshift(np.fft.fft(signal))
power = 20 * np.log10(np.abs(fft_vals))

# Plot
plt.plot(power)
plt.title("Simulated Spectrum")
plt.show()