from typing import Literal
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Configurar tu API KEY
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  

# Inicializar modelo Gemini
def crear_modelo_gemini():
    return genai.GenerativeModel("gemini-2.0-flash")


def translate_with_gemini(text: str) -> str:
    """
    Traduce un texto del español al inglés usando Gemini.
    Retorna solo la traducción.
    """
    prompt = (
        f"Translate the following text to English. "
        f"Return only the translation without extra explanation:\n\n{text}"
    )
    try:
        response = crear_modelo_gemini().generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Error con Gemini: {str(e)}")

def verificar(texto_original: str) -> bool:
    """
    Determina si un mensaje contiene discurso de odio o lenguaje ofensivo
    usando el modelo de Gemini de forma independiente.

    Retorna True si Gemini considera que es ofensivo.
    """
    prompt = f"""
Analiza el siguiente mensaje y responde si contiene lenguaje ofensivo o discurso de odio.
Mensaje: "{texto_original}"

¿Este mensaje es ofensivo o incita al odio?
Responde solo con una palabra: 'Sí' o 'No'.
"""
    try:
        respuesta = crear_modelo_gemini().generate_content(prompt)
        return respuesta.text.strip().lower().startswith("sí")
    except Exception as e:
        print(f"⚠️ Error al verificar con Gemini: {str(e)}")
        return False  # Si Gemini falla, asumimos que no es ofensivo

def generar_respuesta_moderada(texto_ofensivo: str) -> str:
    """
    Genera una respuesta empática y moderadora para sustituir un mensaje ofensivo.
    """
    prompt = f"""
Este mensaje ha sido detectado como ofensivo:
"{texto_ofensivo}"

Tu tarea es generar una respuesta empática que invite al respeto, desactive el lenguaje ofensivo y eduque al autor de manera no confrontativa. 
Usa un tono amable, respetuoso y breve. No repitas el mensaje original ni insultes al autor. Solo responde con un mensaje sugerido para sustituirlo o reflexionar.
"""
    try:
        respuesta = crear_modelo_gemini().generate_content(prompt)
        return respuesta.text.strip()
    except Exception as e:
        print(f"⚠️ Error al generar respuesta moderada: {str(e)}")
        return "Por favor, recordemos expresarnos con respeto."