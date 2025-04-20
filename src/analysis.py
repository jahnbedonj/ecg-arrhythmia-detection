import numpy as np
from scipy.signal import find_peaks

def detect_qrs(ecg_data, threshold=0.5):
    # Detectar los complejos QRS
    qrs_indices, _ = find_peaks(ecg_data[:, 0], height=threshold)
    return qrs_indices
