import streamlit as st
import os
import numpy as np
import pandas as pd
import wfdb
import matplotlib.pyplot as plt
from src import file_upload, data_preprocessing, visualization, analysis


st.set_page_config(page_title="Análisis de ECG", page_icon=":heartpulse:")

os.makedirs("temp_data", exist_ok=True)

def main():
    st.title("Análisis de Señales ECG")
    # Cargar archivos
    uploaded_files = st.file_uploader(
        "Sube archivos ECG (.mat y .hea)", type=["mat", "hea"], accept_multiple_files=True
    )
    if uploaded_files:
        mat_file, hea_file = file_upload.upload_files(uploaded_files)
        if mat_file and hea_file:
            st.success("Archivos cargados correctamente.")
            # Procesar los archivos
            try:
                record = wfdb.rdrecord(mat_file[:-4])  # Eliminar la extensión .mat
                ecg_data = record.p_signal
                fs = record.fs  # Frecuencia de muestreo
                st.write(f"Frecuencia de muestreo: {fs} Hz")
                # Calibración de la señal en milisegundos
                time = np.linspace(0, len(ecg_data) / fs, len(ecg_data))
                # Mostrar la señal ECG
                visualization.plot_ecg_signal(ecg_data, time)
                # Detección de QRS
                threshold = st.slider("Ajuste el umbral de detección de QRS", min_value=0.0, max_value=1.0, value=0.5)
                qrs_indices = analysis.detect_qrs(ecg_data, threshold)
                st.write(f"Índices de los complejos QRS: {qrs_indices}")
                # Mostrar los resultados de QRS
                visualization.plot_qrs_detection(ecg_data, qrs_indices, time)

            except Exception as e:
                st.error(f"Error al procesar los archivos: {e}")
        else:
            st.warning("Asegúrate de subir tanto el archivo .mat como el .hea.")

if __name__ == "__main__":
    main()
