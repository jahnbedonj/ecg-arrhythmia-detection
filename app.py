import streamlit as st
import os
import numpy as np
import pandas as pd
import wfdb
import matplotlib.pyplot as plt
from src import file_upload, data_preprocessing, visualization, analysis
import neurokit2 as nk


st.set_page_config(page_title="Análisis de ECG", page_icon=":heartpulse:", layout="wide") # Layout wide usa más ancho de la página

# Directorio temporal para guardar archivos cargados
temp_data_dir = "temp_data"
os.makedirs(temp_data_dir, exist_ok=True)


def main(): # O 'app' si has renombrado la función
    st.title("Análisis de Señales ECG")

    # Cargar archivos
    uploaded_files = st.file_uploader(
        "Sube archivos ECG (.mat y .hea)", type=["mat", "hea"], accept_multiple_files=True
    )

    if uploaded_files:
        # Guarda los archivos cargados en el directorio temporal y retorna sus rutas
        # Asegúrate de que file_upload.upload_files maneje correctamente el temp_data_dir
        mat_file_path, hea_file_path = file_upload.upload_files(uploaded_files)

        # Verificar que ambos archivos necesarios fueron cargados y guardados
        if mat_file_path and hea_file_path:
            st.success("Archivos cargados correctamente.")

            # Obtener la ruta base del registro sin extensión para wfdb
            record_name = os.path.splitext(mat_file_path)[0]

            try:
                # Cargar el registro ECG usando wfdb
                record = wfdb.rdrecord(record_name)
                ecg_data = record.p_signal  # Los datos de la señal (NumPy array: muestras x derivaciones)
                fs = record.fs              # Frecuencia de muestreo (int)
                lead_names = record.sig_name # Nombres de las derivaciones (list of str)

                st.write(f"Frecuencia de muestreo: {fs} Hz")
                st.write(f"Derivaciones disponibles: {lead_names}")

                # Verificar si se cargaron datos de señal válidos
                if ecg_data is None or ecg_data.size == 0:
                    st.error("No se pudieron cargar los datos de la señal ECG de los archivos proporcionados.")
                    return # Salir si no hay datos

                # --- Sección para Inspeccionar la Información de la Cabecera---
                # Código añadido para ayudarte a explorar las anotaciones
                #st.subheader("Información de la Cabecera del Registro")
                #st.write("Inspeccionando los atributos del objeto Record para encontrar anotaciones:")

                #st.write("Atributos disponibles:")
                #st.json(list(record.__dict__.keys())) # Mostrar las claves de los atributos en formato JSON

                #st.write("Contenido de 'record.comments':")
                #if record.comments:
                #    for i, comment in enumerate(record.comments):
                #        st.write(f"- Comentario {i+1}: {comment}")
                #else:
                #    st.write("El atributo 'record.comments' está vacío para este registro.")

                # st.write(f"Contenido de 'record.diagnoses_snomed': {getattr(record, 'diagnoses_snomed', 'Atributo no encontrado')}")

                #st.write("Fin de la Información de Cabecera")
                # --- Fin Sección de Inspección ---
            

                # --- Visualización y Análisis---
                st.header("Control de Visualización y Análisis")

                # ** Selección de Derivación **
                selected_lead_name = st.selectbox(
                    "Selecciona la derivación para visualizar y analizar:",
                    lead_names
                )

                # Encontrar el índice de la derivación seleccionada
                selected_lead_index = lead_names.index(selected_lead_name)

                # Extraer la señal de la derivación seleccionada
                signal_to_process = ecg_data[:, selected_lead_index]

                # Calcular el vector de tiempo en milisegundos
                time_ms = np.linspace(0, len(signal_to_process) / fs, len(signal_to_process)) * 1000

                # Obtener el rango completo de tiempo de la señal
                full_min_time_ms = time_ms.min() if len(time_ms) > 0 else 0
                full_max_time_ms = time_ms.max() if len(time_ms) > 0 else 0

                # ** Controles deslizantes para el Rango de Tiempo (Simulación de Zoom/Pan) **
                st.subheader("Rango de Tiempo de Visualización (ms)")

                max_slider_range = max(full_max_time_ms, 1000.0)

                initial_start = full_min_time_ms
                initial_end = full_max_time_ms

                start_time, end_time = st.slider(
                    "Selecciona el rango de tiempo (ms):",
                    min_value=full_min_time_ms,
                    max_value=max_slider_range,
                    value=(initial_start, initial_end),
                    step=40.0, # Un step de 40ms corresponde a 1mm en el papel ECG
                    format="%f ms" # Mostrar valor con decimales
                )

                # Validar y definir el rango de tiempo seleccionado
                if start_time >= end_time:
                     st.warning("El tiempo de inicio debe ser menor que el tiempo de fin. Ajusta los sliders.")
                     # Usar un rango por defecto si los sliders están invertidos
                     selected_x_range = (full_min_time_ms, full_max_time_ms) # O podrías establecer un rango pequeño por defecto
                else:
                    selected_x_range = (start_time, end_time)


                # --- Visualización con Cuadrícula (Objetivo 1) ---
                st.header("Visualización de la Señal ECG con Cuadrícula")
                visualization.plot_ecg_signal_single_lead(signal_to_process, time_ms, fs, selected_lead_name, x_range=selected_x_range)


                # --- Análisis de Frecuencia Cardiaca (Objetivo 2) ---
                st.header("Análisis de Frecuencia Cardiaca")
                st.write(f"Análisis basado en la derivación: **{selected_lead_name}**")

                # ** Detección de Picos R con NeuroKit2 **
                st.subheader("Detección de Picos R")
                st.write("Realizando detección de picos R usando NeuroKit2...")

                # Detectar picos R en la señal COMPLETA (necesitamos todos los picos para análisis general si se requiere)
                all_qrs_indices = analysis.detect_peaks_neurokit2(signal_to_process, fs)

                if len(all_qrs_indices) > 0:
                    # ** Mostrar el conteo total de picos detectados como referencia **
                    st.write(f"Total de picos R detectados en la señal completa: **{len(all_qrs_indices)}**")

                    # ** Filtrar picos R para el rango de tiempo visible **
                    # Convertir los índices de todos los picos a tiempo en ms
                    all_qrs_times_ms = time_ms[all_qrs_indices]

                    # Encontrar los índices de los picos (de la lista completa) que caen dentro del rango de tiempo visible
                    # Usamos np.where para obtener los índices *dentro* de all_qrs_indices
                    indices_of_visible_peaks_in_all = np.where(
                        (all_qrs_times_ms >= selected_x_range[0]) &
                        (all_qrs_times_ms <= selected_x_range[1])
                    )[0] # [0] porque np.where devuelve una tupla con un array

                    # Obtener los *índices originales* de los picos que están en el rango visible
                    qrs_indices_in_visible_range = all_qrs_indices[indices_of_visible_peaks_in_all]


                    # ** Mostrar el conteo de picos en el rango visible **
                    st.success(f"Picos R visibles en el rango seleccionado: **{len(qrs_indices_in_visible_range)}**")


                    # ** Visualización de Picos R detectados **
                    # Pasamos all_qrs_indices a la función de visualización porque ella filtra internamente
                    visualization.plot_qrs_detection_single_lead(signal_to_process, time_ms, all_qrs_indices, fs, selected_lead_name, x_range=selected_x_range)


                    # ** Cálculo y Alerta de Frecuencia Cardiaca **
                    st.subheader("Frecuencia Cardiaca Promedio")

                    # ** Calcular FC y RR solo con los picos R dentro del rango visible **
                    # Si hay suficientes picos en el rango visible para calcular al menos un intervalo RR
                    if len(qrs_indices_in_visible_range) > 1:
                        # Nota: calculate_heart_rate espera los *índices originales* de los picos
                        heart_rate, rr_intervals_ms = analysis.calculate_heart_rate(qrs_indices_in_visible_range, fs)

                        if heart_rate is not None:
                            st.write(f"Frecuencia cardíaca promedio calculada para el **rango visible**: **{heart_rate:.2f} bpm**")
                            st.info("Nota: La frecuencia cardíaca calculada aquí se basa en los picos detectados en el segmento de tiempo actualmente visible.")

                            # Alerta de frecuencia cardíaca (basada en el rango visible)
                            if heart_rate < 60 or heart_rate > 100:
                                st.warning("Alerta: Frecuencia cardíaca fuera del rango normal (60-100 bpm) en el segmento visible.")
                            else:
                                st.success("Frecuencia cardíaca dentro del rango normal (60-100 bpm) en el segmento visible.")

                        else:
                             st.error("No se pudo calcular la frecuencia cardíaca para el rango visible (intervalos RR inválidos).")

                    else:
                        st.warning("No hay suficientes picos R detectados en el rango visible para calcular la frecuencia cardíaca.")


                else:
                    st.warning("No se detectaron picos R en la derivación seleccionada (en toda la señal). No se puede realizar el análisis de frecuencia cardíaca.")
                    st.info(
                        """
                        Posibles razones:
                        - La señal está muy ruidosa en esta derivación.
                        - La detección automática de NeuroKit2 no funcionó correctamente para esta señal/derivación.
                        - La derivación seleccionada no contiene una señal de ECG clara (por ejemplo, es una derivación exploratoria o de bajo voltaje).
                        Considera seleccionar otra derivación si está disponible.
                        """
                    )


            except Exception as e:
                st.error(f"Ocurrió un error durante el procesamiento o análisis: {e}")
                st.exception(e)
        else:
            st.warning("Asegúrate de subir tanto el archivo .mat como el .hea para el registro completo. Ambos son necesarios.")

    # Opcional: Limpiar archivos temporales al finalizar la ejecución del script
    # import shutil
    # if os.path.exists(temp_data_dir):
    #     try:
    #         # shutil.rmtree(temp_data_dir)
    #         if mat_file_path and os.path.exists(mat_file_path): os.unlink(mat_file_path)
    #         if hea_file_path and os.path.exists(hea_file_path): os.unlink(hea_file_path)
    #     except Exception as e:
    #         print(f"Error removing temporary files: {e}")


if __name__ == "__main__":
    main()