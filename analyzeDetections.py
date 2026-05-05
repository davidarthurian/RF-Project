import pandas as pd

CSV_FILE = "detections.csv"
GROUP_TOLERANCE_MHZ = 0.05  # group detections within 50 kHz

df = pd.read_csv(CSV_FILE)

if df.empty:
    print("No detections found.")
    exit()

df = df.sort_values("absolute_frequency_mhz").reset_index(drop=True)

groups = []
current_group = [df.iloc[0]]

for i in range(1, len(df)):
    current = df.iloc[i]
    previous = current_group[-1]

    if abs(current["absolute_frequency_mhz"] - previous["absolute_frequency_mhz"]) <= GROUP_TOLERANCE_MHZ:
        current_group.append(current)
    else:
        groups.append(current_group)
        current_group = [current]

groups.append(current_group)

summary_rows = []

for group in groups:
    group_df = pd.DataFrame(group)

    summary_rows.append({
        "center_frequency_mhz": group_df["absolute_frequency_mhz"].mean(),
        "min_frequency_mhz": group_df["absolute_frequency_mhz"].min(),
        "max_frequency_mhz": group_df["absolute_frequency_mhz"].max(),
        "detections": len(group_df),
        "unique_scans": group_df["scan_index"].nunique(),
        "avg_bandwidth_khz": group_df["bandwidth_khz"].mean(),
        "max_bandwidth_khz": group_df["bandwidth_khz"].max(),
        "avg_peak_power_db": group_df["peak_power_db"].mean(),
        "max_peak_power_db": group_df["peak_power_db"].max(),
    })

summary = pd.DataFrame(summary_rows)
summary = summary.sort_values(
    by=["unique_scans", "avg_peak_power_db"],
    ascending=False
)

print("\nPersistent Signal Summary")
print(summary.to_string(index=False))