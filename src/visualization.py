import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


def validate_x_range(x_range, time):
    """
    Valida y ajusta el rango de tiempo proporcionado.

    Args:
        x_range (list or tuple): El rango de tiempo [min_ms, max_ms].
        time (np.ndarray): El array NumPy de tiempo total de la señal en ms.

    Returns:
        list: El rango de tiempo validado y ajustado dentro de los límites de la señal.
    """
    full_min_time = time.min() if len(time) > 0 else 0
    full_max_time = time.max() if len(time) > 0 else 1 

    if x_range is None or len(x_range) != 2:
        # Si no se proporciona un rango válido, se usa el rango completo de la señal
        return [full_min_time, full_max_time]

    min_req, max_req = x_range

    # Ajustar el rango solicitado para que no exceda el rango total de la señal
    valid_min = max(full_min_time, min_req)
    valid_max = min(full_max_time, max_req)

    # Asegurarse de que el rango mínimo no sea mayor que el máximo
    if valid_min >= valid_max:

         return [full_min_time, full_max_time]


    return [valid_min, valid_max]

def validate_x_range(x_range, time):
    if x_range is None:
        return time[0], time[-1]
    return max(time[0], x_range[0]), min(time[-1], x_range[1])

def plot_ecg_signal_single_lead(signal, time, fs, lead_name="ECG Signal", x_range=None):
    st.write(f"Mostrando señal de la derivación **{lead_name}** con cuadrícula estilo papel ECG.")

    x_min, x_max = x_range if x_range else (time[0], time[-1])
    indices = np.where((time >= x_min) & (time <= x_max))[0]

    if len(indices) == 0:
        st.warning("El rango de tiempo seleccionado no contiene datos.")
        return

    time_display = time[indices]
    signal_display = signal[indices]

    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(time_display, signal_display, color='black', linewidth=0.75)

    # Fondo tipo papel ECG
    ax.set_facecolor('#fff5f5')

    # Cuadrícula milimétrica
    ax.xaxis.set_minor_locator(plt.MultipleLocator(40))    # 1 mm = 40 ms
    ax.xaxis.set_major_locator(plt.MultipleLocator(200))   # 5 mm = 200 ms
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.1))   # 1 mm = 0.1 mV
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))   # 5 mm = 0.5 mV

    ax.grid(which='minor', color='lightgray', linewidth=0.5)
    ax.grid(which='major', color='red', linewidth=0.8)

    ax.set_xlabel("Tiempo (ms)")
    ax.set_ylabel("Voltaje (mV)")
    ax.set_title(f"Señal ECG ({lead_name}) con Cuadrícula y Barra de Calibración")

    # Ejes
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-1.0, 1.0)  # fijo para claridad y proporción

    ax.tick_params(axis='x', labelrotation=45, labelsize=8)

    # Barra de calibración: 1 mV de altura x 200 ms de ancho
    cal_x = x_min + 100
    cal_w = 200
    cal_h = 1.0
    ax.plot([cal_x, cal_x], [0, cal_h], color='black', linewidth=2)
    ax.plot([cal_x, cal_x + cal_w], [cal_h, cal_h], color='black', linewidth=2)
    ax.plot([cal_x + cal_w, cal_x + cal_w], [cal_h, 0], color='black', linewidth=2)

    st.pyplot(fig)
    plt.close(fig)

def plot_qrs_detection_single_lead(signal, time, qrs_indices, fs, lead_name="ECG", x_range=None):
    st.write(f"Visualización de picos R detectados en **{lead_name}** con cuadrícula ECG.")

    x_min, x_max = x_range if x_range else (time[0], time[-1])
    indices = np.where((time >= x_min) & (time <= x_max))[0]

    if len(indices) == 0:
        st.warning("El rango de tiempo seleccionado no contiene datos.")
        return

    time_display = time[indices]
    signal_display = signal[indices]

    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(time_display, signal_display, color='black', linewidth=0.75)

    # Fondo ECG
    ax.set_facecolor('#fff5f5')

    # Cuadrícula
    ax.xaxis.set_minor_locator(plt.MultipleLocator(40))
    ax.xaxis.set_major_locator(plt.MultipleLocator(200))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.1))
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))
    ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5)
    ax.grid(which='major', color='red', linestyle='-', linewidth=0.8)

    ax.set_xlabel("Tiempo (ms)")
    ax.set_ylabel("Voltaje (mV)")
    ax.set_title(f"Picos R en {lead_name} con Cuadrícula de Papel ECG")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-1.0, 1.0)
    ax.tick_params(axis='x', labelrotation=45, labelsize=8)

    # picos R
    qrs_times = time[qrs_indices]
    qrs_in_range = (qrs_times >= x_min) & (qrs_times <= x_max)
    qrs_shown = qrs_times[qrs_in_range]
    signal_qrs = signal[qrs_indices[qrs_in_range]]

    ax.scatter(qrs_shown, signal_qrs, color='red', marker='o', s=60, label="Picos R")
    ax.legend(loc='upper right')

    # Barra de calibración
    cal_x = x_min + 100
    cal_w = 200
    cal_h = 1.0
    ax.plot([cal_x, cal_x], [0, cal_h], color='black', linewidth=2)
    ax.plot([cal_x, cal_x + cal_w], [cal_h, cal_h], color='black', linewidth=2)
    ax.plot([cal_x + cal_w, cal_x + cal_w], [cal_h, 0], color='black', linewidth=2)

    st.pyplot(fig)
    plt.close(fig)