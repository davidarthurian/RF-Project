from dsp import compute_power_spectrum, bin_to_freq
from detection import detect_signals
from clustering import cluster_peaks
from source import SignalSource

import matplotlib.pyplot as plt
import numpy as np
import time

fs = 2.4e6  # sample rate in Hz
num_iterations = 10

source = SignalSource(mode="sim")

last_power = None
last_threshold = None
last_detections = None
last_freq_axis_mhz = None

for scan_idx in range(num_iterations):
    timestamp = time.time()

    samples = source.get_samples(fs)
    power = compute_power_spectrum(samples)

    peaks, threshold = detect_signals(power, threshold_offset=20)

    n = len(power)
    clusters = cluster_peaks(peaks) if len(peaks) > 0 else []

    detections = []

    for cluster in clusters:
        center_bin = int(np.mean(cluster))
        start_bin = cluster[0]
        end_bin = cluster[-1]

        center_freq_hz = bin_to_freq(center_bin, fs, n)
        start_freq_hz = bin_to_freq(start_bin, fs, n)
        end_freq_hz = bin_to_freq(end_bin, fs, n)

        bandwidth_hz = abs(end_freq_hz - start_freq_hz)
        avg_power_db = np.mean(power[cluster])
        peak_power_db = np.max(power[cluster])

        detections.append({
            "timestamp": timestamp,
            "center_frequency_mhz": center_freq_hz / 1e6,
            "start_frequency_mhz": start_freq_hz / 1e6,
            "end_frequency_mhz": end_freq_hz / 1e6,
            "bandwidth_khz": bandwidth_hz / 1e3,
            "bandwidth_bins": len(cluster),
            "avg_power_db": avg_power_db,
            "peak_power_db": peak_power_db,
        })

    print(f"\nScan {scan_idx + 1}: Detected {len(detections)} signals")

    for d in detections:
        print(
            f"Signal at {d['center_frequency_mhz']:.3f} MHz | "
            f"BW: {d['bandwidth_khz']:.2f} kHz | "
            f"Width: {d['bandwidth_bins']} bins | "
            f"Peak Power: {d['peak_power_db']:.2f} dB | "
            f"Time: {d['timestamp']:.2f}"
        )

    last_power = power
    last_threshold = threshold
    last_detections = detections
    last_freq_axis_mhz = np.array([bin_to_freq(i, fs, n) / 1e6 for i in range(n)])

# Plot final scan
plt.plot(last_freq_axis_mhz, last_power, label="Power Spectrum")
plt.axhline(
    last_threshold,
    linestyle="--",
    color="red",
    linewidth=2,
    label="Detection Threshold"
)

for i, d in enumerate(last_detections):
    plt.axvline(
        d["center_frequency_mhz"],
        linestyle=":",
        color="orange",
        linewidth=2,
        label="Detected Signal" if i == 0 else None
    )

plt.title("Signal Detection - Final Scan")
plt.xlabel("Frequency Offset from Center Frequency (MHz)")
plt.ylabel("Power (dB, relative)")
plt.grid(True)
plt.legend()
plt.show()