import numpy as np

def cluster_peaks(peaks, max_gap=3):
    if len(peaks) == 0:
        return []

    clusters = []
    current_cluster = [peaks[0]]

    for i in range(1, len(peaks)):
        if peaks[i] - peaks[i - 1] <= max_gap:
            current_cluster.append(peaks[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [peaks[i]]

    clusters.append(current_cluster)
    return clusters