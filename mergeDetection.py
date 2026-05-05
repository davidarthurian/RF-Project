def merge_detections(detections, merge_threshold_mhz=0.02):
    if not detections:
        return []

    detections = sorted(detections, key=lambda d: d["center_frequency_mhz"])
    merged = [detections[0]]

    for d in detections[1:]:
        prev = merged[-1]

        if abs(d["center_frequency_mhz"] - prev["center_frequency_mhz"]) < merge_threshold_mhz:
            # Merge into previous
            prev["center_frequency_mhz"] = (prev["center_frequency_mhz"] + d["center_frequency_mhz"]) / 2
            prev["bandwidth_khz"] += d["bandwidth_khz"]
            prev["peak_power_db"] = max(prev["peak_power_db"], d["peak_power_db"])
        else:
            merged.append(d)

    return merged