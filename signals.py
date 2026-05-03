def summarize_detections(peaks, fs, n, bin_to_freq):
    detections = []

    for p in peaks:
        freq_hz = bin_to_freq(p, fs, n)

        detections.append({
            "frequency_hz": freq_hz,
            "frequency_mhz": freq_hz / 1e6
        })

    return detections