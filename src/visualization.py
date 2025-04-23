import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_ecg_signal(ecg_data, time):
    st.write("Mostrando la señal ECG...")
    df_ecg = pd.DataFrame({
        'Tiempo (ms)': time,
        'Voltaje (mV)': ecg_data[:, 0]
    })
    st.line_chart(df_ecg.set_index('Tiempo (ms)'))
    st.write("Este grafico muestra la señal ECG en milisegundos.")
    st.write("Eje X: Tiempo (ms) - Eje Y: Voltaje (mV)")

def plot_qrs_detection(ecg_data, qrs_indices, time):
    st.write("Mostrando los puntos de los complejos QRS detectados...")
    
    # dataFrame con la señal y los puntos QRS
    df_ecg = pd.DataFrame({
        'Voltaje (mV)': ecg_data[:, 0]
    })

    # puntos QRS
    qrs_signal = np.zeros_like(ecg_data[:, 0])
    qrs_signal[qrs_indices] = ecg_data[qrs_indices, 0]

    st.line_chart(df_ecg.set_index(pd.Index(range(len(ecg_data)))))

    # puntos QRS y otro gráfico para resaltarlos
    st.write(f"Índices de los complejos QRS: {qrs_indices}")
    st.write(f"Se han detectado {len(qrs_indices)} puntos QRS")
    
    df_qrs = pd.DataFrame({
        'Voltaje QRS': qrs_signal
    })
    
    # gráfico de los puntos QRS
    st.line_chart(df_qrs.set_index(pd.Index(range(len(ecg_data)))))

