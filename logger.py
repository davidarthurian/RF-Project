import csv
from pathlib import Path

CSV_COLUMNS = [
    "timestamp",
    "scan_index",
    "absolute_frequency_mhz",
    "offset_frequency_mhz",
    "start_frequency_mhz",
    "end_frequency_mhz",
    "bandwidth_khz",
    "bandwidth_bins",
    "avg_power_db",
    "peak_power_db",
]

def log_detections_to_csv(filename, detections, scan_index, center_freq_mhz):
    file_path = Path(filename)
    file_exists = file_path.exists()

    with open(file_path, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)

        if not file_exists:
            writer.writeheader()

        for d in detections:
            absolute_frequency_mhz = center_freq_mhz + d["center_frequency_mhz"]

            writer.writerow({
                "timestamp": d["timestamp"],
                "scan_index": scan_index,
                "absolute_frequency_mhz": absolute_frequency_mhz,
                "offset_frequency_mhz": d["center_frequency_mhz"],
                "start_frequency_mhz": center_freq_mhz + d["start_frequency_mhz"],
                "end_frequency_mhz": center_freq_mhz + d["end_frequency_mhz"],
                "bandwidth_khz": d["bandwidth_khz"],
                "bandwidth_bins": d["bandwidth_bins"],
                "avg_power_db": d["avg_power_db"],
                "peak_power_db": d["peak_power_db"],
            })