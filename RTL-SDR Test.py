from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt

center_freq = 100e6
sample_rate = 2.4e6
num_samples = 256 * 1024

sdr = None

try:
    sdr = RtlSdr()
    sdr.sample_rate = sample_rate
    sdr.center_freq = center_freq
    sdr.gain = 30

    samples = sdr.read_samples(num_samples)

finally:
    if sdr is not None:
        sdr.close()

fft_vals = np.fft.fftshift(np.fft.fft(samples))
power = 20 * np.log10(np.abs(fft_vals) + 1e-12)

freq_axis = np.fft.fftshift(np.fft.fftfreq(len(samples), d=1 / sample_rate))
absolute_freq_mhz = (center_freq + freq_axis) / 1e6

plt.plot(absolute_freq_mhz, power)
plt.title("Live RF Spectrum")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Power (dB, relative)")
plt.grid(True)
plt.show()