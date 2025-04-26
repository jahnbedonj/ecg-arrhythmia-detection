import openai
import os
from dotenv import load_dotenv

# Cargar las claves desde el archivo .env (para entorno local)
if os.getenv("STREAMLIT_ENV") != "cloud":
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    # Cargar las claves desde Streamlit Secrets (para Streamlit Cloud)
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    openai.organization = st.secrets.get("OPENAI_ORGANIZATION", None)

def interpret_ecg_results(ecg_summary):
    """
    Envía un resumen de los resultados del ECG a la API de OpenAI para obtener una interpretación.
    
    Args:
        ecg_summary (str): Resumen de los resultados del ECG.

    Returns:
        str: Respuesta interpretada por ChatGPT.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un cardiólogo experto que interpreta resultados de ECG."},
                {"role": "user", "content": ecg_summary}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error al comunicarse con la API de OpenAI: {e}"