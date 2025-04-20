import numpy as np
from scipy.signal import butter, filtfilt

def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def filter_ecg(ecg_data, fs, cutoff=0.5):
    b, a = butter_lowpass(cutoff, fs)
    return filtfilt(b, a, ecg_data)
