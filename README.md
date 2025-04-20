# Análisis de Señales ECG con Streamlit

Este proyecto permite cargar y analizar señales ECG, detectar complejos QRS y visualizar los resultados de manera interactiva usando **Streamlit**.

## Requisitos

### Librerías necesarias
1. **wfdb**: Para la carga y procesamiento de archivos ECG (formatos `.mat` y `.hea`).
2. **streamlit**: Para crear una interfaz web interactiva.
3. **matplotlib**: Para la visualización de gráficos.
4. **scipy**: Para el procesamiento de señales.
5. **numpy**: Para manipulación de arrays y cálculos.

### Instalación

Crear un entorno virtual con **conda** o **virtualenv** y luego instalar los requisitos utilizando el archivo `requirements.txt`.

```bash
# Crear un entorno con conda
conda create --name ecg-env python=3.8
conda activate ecg-env

# Instalar las dependencias
pip install -r requirements.txt
