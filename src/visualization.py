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


def plot_ecg_signal_single_lead(signal, time, fs, lead_name="ECG Signal", x_range=None): # <-- Añadir x_range=None
    """
    Plotea una única señal ECG con una cuadrícula que simula el papel electrocardiográfico,
    permitiendo especificar el rango del eje X.

    Args:
        signal (np.ndarray): Array NumPy con los valores de voltaje de la señal (ya en mV).
        time (np.ndarray): Array NumPy con los valores de tiempo correspondientes (ya en ms).
        fs (int): Frecuencia de muestreo de la señal en Hz.
        lead_name (str): Nombre de la derivación a mostrar.
        x_range (list or tuple, optional): Rango de tiempo [min_ms, max_ms] para el eje X.
                                           Si es None, se usa el rango completo.
    """
    st.write(f"Mostrando la señal de la derivación '{lead_name}' con cuadrícula de papel ECG...")

    # Validar y ajustar el rango X
    display_x_range = validate_x_range(x_range, time)
    x_min, x_max = display_x_range

    # Filtrar datos para el rango de visualización para mejorar el rendimiento si la señal es muy larga
    indices_in_range = np.where((time >= x_min) & (time <= x_max))[0]
    if len(indices_in_range) == 0:
        st.warning("El rango de tiempo seleccionado no contiene datos de señal.")
        return # Salir si no hay datos en el rango

    time_display = time[indices_in_range]
    signal_display = signal[indices_in_range]
    fig, ax = plt.subplots(figsize=(15, 6))

    # Plotear la señal dentro del rango seleccionado
    ax.plot(time_display, signal_display, color='black', linewidth=0.75, label=lead_name)

    # Configurar la cuadrícula tipo papel ECG
    minor_grid_interval_ms = 40
    major_grid_interval_ms = 200

    minor_grid_interval_mv = 0.1
    major_grid_interval_mv = 0.5

    ax.grid(which='both', axis='both', linestyle='-', color='lightgray', linewidth=0.5, zorder=-1)

    y_min, y_max = signal_display.min(), signal_display.max() 

    major_v_start = np.floor(x_min / major_grid_interval_ms) * major_grid_interval_ms
    major_h_start = np.floor(y_min / major_grid_interval_mv) * major_grid_interval_mv


    v_lines = np.arange(major_v_start, x_max + major_grid_interval_ms, major_grid_interval_ms)
    for vline in v_lines:

         if vline >= x_min and vline <= x_max + major_grid_interval_ms:
             ax.axvline(x=vline, color='gray', linestyle='-', linewidth=1, zorder=0)

    h_lines = np.arange(major_h_start, y_max + major_grid_interval_mv, major_grid_interval_mv)
    for hline in h_lines:
         if hline >= y_min and hline <= y_max + major_grid_interval_mv:
             ax.axhline(y=hline, color='gray', linestyle='-', linewidth=1, zorder=0)
    # configuración de la cuadrícula

    # Configurar etiquetas de los ejes para reflejar ms y mV
    ax.set_xlabel("Tiempo (ms)")
    ax.set_ylabel("Voltaje (mV)")
    ax.set_title(f"Señal ECG ({lead_name}) con Cuadrícula de Papel ECG")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min - major_grid_interval_mv, y_max + major_grid_interval_mv)

    st.pyplot(fig)
    plt.close(fig)


def plot_qrs_detection_single_lead(signal, time, qrs_indices, fs, lead_name="ECG Signal", x_range=None): # <-- Añadir x_range=None
    """
    Plotea una única señal ECG con picos R detectados sobre una cuadrícula tipo papel ECG,
    permitiendo especificar el rango del eje X.

    Args:
        signal (np.ndarray): Array NumPy con los valores de voltaje de la señal (ya en mV).
        time (np.ndarray): Array NumPy con los valores de tiempo correspondientes (ya en ms).
        qrs_indices (np.ndarray): Array NumPy con los índices de los picos R detectados.
        fs (int): Frecuencia de muestreo de la señal en Hz.
        lead_name (str): Nombre de la derivación a mostrar.
        x_range (list or tuple, optional): Rango de tiempo [min_ms, max_ms] para el eje X.
                                           Si es None, se usa el rango completo.
    """
    st.write(f"Mostrando los picos R detectados en la derivación '{lead_name}'...")

    # Validar y ajustar el rango X
    display_x_range = validate_x_range(x_range, time)
    x_min, x_max = display_x_range

    # Filtrar datos de la señal para el rango de visualización
    indices_in_range = np.where((time >= x_min) & (time <= x_max))[0]
    if len(indices_in_range) == 0:
        st.warning("El rango de tiempo seleccionado no contiene datos de señal para mostrar picos R.")
        return # Salir si no hay datos en el rango

    time_display = time[indices_in_range]
    signal_display = signal[indices_in_range]

    # Filtrar los picos R para incluir solo aquellos dentro del rango de tiempo visible
    qrs_indices_in_range = qrs_indices[(time[qrs_indices] >= x_min) & (time[qrs_indices] <= x_max)]


    fig, ax = plt.subplots(figsize=(15, 6)) 

    # Plotear la señal dentro del rango seleccionado
    ax.plot(time_display, signal_display, color='black', linewidth=0.75, label=lead_name)

    # Plotear los picos R detectados que están dentro del rango seleccionado
    time_qrs_in_range = time[qrs_indices_in_range]
    signal_qrs_in_range = signal[qrs_indices_in_range]
    ax.plot(time_qrs_in_range, signal_qrs_in_range, 'ro', markersize=5, zorder=10, label='Picos R') # zorder para asegurar que los marcadores estén arriba


    # Configurar la cuadrícula tipo papel ECG
    minor_grid_interval_ms = 40
    major_grid_interval_ms = 200

    minor_grid_interval_mv = 0.1
    major_grid_interval_mv = 0.5

    ax.grid(which='both', axis='both', linestyle='-', color='lightgray', linewidth=0.5, zorder=-1)

    y_min, y_max = signal_display.min(), signal_display.max() # Usar el rango de la señal visible

    major_v_start = np.floor(x_min / major_grid_interval_ms) * major_grid_interval_ms
    major_h_start = np.floor(y_min / major_grid_interval_mv) * major_grid_interval_mv

    v_lines = np.arange(major_v_start, x_max + major_grid_interval_ms, major_grid_interval_ms)
    for vline in v_lines:
         if vline >= x_min and vline <= x_max + major_grid_interval_ms:
             ax.axvline(x=vline, color='gray', linestyle='-', linewidth=1, zorder=0)

    h_lines = np.arange(major_h_start, y_max + major_grid_interval_mv, major_grid_interval_mv)
    for hline in h_lines:
         if hline >= y_min and hline <= y_max + major_grid_interval_mv:
             ax.axhline(y=hline, color='gray', linestyle='-', linewidth=1, zorder=0)
    # Fin configuración de la cuadrícula


    ax.set_xlabel("Tiempo (ms)")
    ax.set_ylabel("Voltaje (mV)")
    ax.set_title(f"Picos R detectados en la derivación '{lead_name}'")
    ax.legend()
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min - major_grid_interval_mv, y_max + major_grid_interval_mv)


    st.pyplot(fig)
    plt.close(fig)