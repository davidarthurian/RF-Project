from dsp import compute_power_spectrum, bin_to_freq
from detection import detect_signals
from clustering import cluster_peaks
from source import SignalSource
from mergeDetection import merge_detections
from logger import log_detections_to_csv

import matplotlib.pyplot as plt
import numpy as np
import time

# -----------------------------
# System configuration
# -----------------------------
fs = 2.4e6  # sample rate in Hz
num_iterations = 10

center_freq_mhz = 100
center_freq_hz = center_freq_mhz * 1e6

csv_filename = "detections.csv"

# SDR source
source = SignalSource(mode="sdr", center_freq=center_freq_hz)

# Storage for final plot
last_power = None
last_threshold = None
last_detections = None
last_freq_axis_mhz = None

try:
    for scan_idx in range(num_iterations):
        timestamp = time.time()

        # 1. Capture samples
        samples = source.get_samples(fs)

        # 2. Convert time-domain IQ samples into frequency-domain power spectrum
        power = compute_power_spectrum(samples)

        # 3. Detect bins above dynamic threshold
        peaks, threshold = detect_signals(power, threshold_offset=18)

        n = len(power)

        # 4. Group nearby FFT bins into rough signal clusters
        clusters = cluster_peaks(peaks, max_gap=100) if len(peaks) > 0 else []

        detections = []

        for cluster in clusters:
            center_bin = int(np.mean(cluster))
            start_bin = cluster[0]
            end_bin = cluster[-1]

            center_freq_offset_hz = bin_to_freq(center_bin, fs, n)

            # Ignore DC spike / center-frequency artifact
            if abs(center_freq_offset_hz) < 50e3:
                continue

            start_freq_offset_hz = bin_to_freq(start_bin, fs, n)
            end_freq_offset_hz = bin_to_freq(end_bin, fs, n)

            bandwidth_hz = abs(end_freq_offset_hz - start_freq_offset_hz)

            # Ignore tiny/narrow artifacts
            if bandwidth_hz < 1e3:
                continue

            avg_power_db = np.mean(power[cluster])
            peak_power_db = np.max(power[cluster])

            detections.append({
                "timestamp": timestamp,
                "center_frequency_mhz": center_freq_offset_hz / 1e6,
                "start_frequency_mhz": start_freq_offset_hz / 1e6,
                "end_frequency_mhz": end_freq_offset_hz / 1e6,
                "bandwidth_khz": bandwidth_hz / 1e3,
                "bandwidth_bins": len(cluster),
                "avg_power_db": avg_power_db,
                "peak_power_db": peak_power_db,
            })

        # 5. Merge nearby detections into cleaner signal objects
        detections = merge_detections(detections)

        # 6. Log detections to CSV
        log_detections_to_csv(
            filename=csv_filename,
            detections=detections,
            scan_index=scan_idx + 1,
            center_freq_mhz=center_freq_mhz
        )

        # 7. Print scan results
        print(f"\nScan {scan_idx + 1}: Detected {len(detections)} signals")

        for d in detections:
            absolute_freq_mhz = center_freq_mhz + d["center_frequency_mhz"]

            print(
                f"Signal at {absolute_freq_mhz:.3f} MHz | "
                f"Offset: {d['center_frequency_mhz']:.3f} MHz | "
                f"BW: {d['bandwidth_khz']:.2f} kHz | "
                f"Width: {d['bandwidth_bins']} bins | "
                f"Peak Power: {d['peak_power_db']:.2f} dB | "
                f"Time: {d['timestamp']:.2f}"
            )

        # Save final scan for plotting
        last_power = power
        last_threshold = threshold
        last_detections = detections

        offset_axis_mhz = np.array([bin_to_freq(i, fs, n) / 1e6 for i in range(n)])
        last_freq_axis_mhz = center_freq_mhz + offset_axis_mhz

finally:
    source.close()

# -----------------------------
# Plot final scan
# -----------------------------
plt.plot(last_freq_axis_mhz, last_power, label="Power Spectrum")

plt.axhline(
    last_threshold,
    linestyle="--",
    color="red",
    linewidth=2,
    label="Detection Threshold"
)

for i, d in enumerate(last_detections):
    absolute_freq_mhz = center_freq_mhz + d["center_frequency_mhz"]

    plt.axvline(
        absolute_freq_mhz,
        linestyle=":",
        color="orange",
        linewidth=2,
        label="Detected Signal" if i == 0 else None
    )

plt.title("Signal Detection - Final Scan")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Power (dB, relative)")
plt.grid(True)
plt.legend()
plt.show()

print(f"\nDetections logged to: {csv_filename}")