import neurokit2 as nk
import numpy as np
import streamlit as st # Importar streamlit para posibles mensajes de estado

def detect_peaks_neurokit2(signal, fs):
    """
    Detecta los picos R en una señal ECG usando NeuroKit2.

    Args:
        signal (np.ndarray): Array NumPy de una dimensión con los valores de voltaje de la señal.
        fs (int): Frecuencia de muestreo de la señal en Hz.

    Returns:
        np.ndarray: Array NumPy con los índices de los picos R detectados.
                    Retorna un array vacío si no se detectan picos.
    """
    # NeuroKit2 espera un array de una dimensión para el análisis
    if signal is None or len(signal) == 0:
        return np.array([])

    try:
        # Procesar la señal ECG para obtener los picos R
        # ** Eliminado handle_artifacts=False **
        _, info = nk.ecg_peaks(signal, sampling_rate=fs)

        # Devolver los índices de los picos R
        # La clave es 'ECG_R_Peaks' según la documentación de NeuroKit2
        qrs_indices = info.get('ECG_R_Peaks', np.array([])).astype(int)

        return qrs_indices

    except Exception as e:
        st.error(f"Error interno en NeuroKit2 durante la detección de picos R: {e}")
        st.exception(e) # Muestra el traceback para depuración
        return np.array([]) # Retorna un array vacío en caso de error


def calculate_heart_rate(qrs_indices, fs):
    """
    Calcula la frecuencia cardíaca promedio en latidos por minuto (bpm)
    a partir de los índices de los picos R.

    Args:
        qrs_indices (np.ndarray): Array NumPy con los índices de los picos R.
        fs (int): Frecuencia de muestreo de la señal en Hz.

    Returns:
        float: Frecuencia cardíaca promedio en bpm. Retorna None si no se puede calcular.
        np.ndarray: Intervalos RR en milisegundos. Retorna un array vacío si no se puede calcular.
    """
    if qrs_indices is None or len(qrs_indices) < 2:
        return None, np.array([])

    # Calcular los intervalos entre picos R en número de muestras
    rr_intervals_samples = np.diff(qrs_indices)

    # Convertir los intervalos RR a segundos
    rr_intervals_sec = rr_intervals_samples / fs

    # Convertir los intervalos RR a milisegundos (útil para visualizar o mostrar)
    rr_intervals_ms = rr_intervals_sec * 1000

    # Calcular la frecuencia cardíaca promedio en latidos por minuto (bpm)
    mean_rr_sec = np.mean(rr_intervals_sec)

    if mean_rr_sec > 0:
        heart_rate_bpm = 60 / mean_rr_sec
        return heart_rate_bpm, rr_intervals_ms
    else:
        st.warning("El intervalo RR promedio es cero o negativo, no se puede calcular una frecuencia cardíaca válida.")
        return None, rr_intervals_ms