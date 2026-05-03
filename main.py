from simulation import generate_signal
from dsp import compute_power_spectrum
from detection import detect_signals

import matplotlib.pyplot as plt

samples = generate_signal()

power = compute_power_spectrum(samples)

peaks, threshold = detect_signals(power)

print(f"Detected {len(peaks)} signal bins")

plt.plot(power)
plt.axhline(threshold, color='r', linestyle='--')
plt.title("Signal Detection")
plt.show()