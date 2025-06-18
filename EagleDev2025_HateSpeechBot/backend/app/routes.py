from flask import Flask, request, jsonify
from app.model import get_model, get_tokenizer
from app.preprocess import preprocess_text
from pymongo import MongoClient
from datetime import datetime
import tempfile
import whisper
import subprocess
import traceback
import os

from app.gemini_service import translate_with_gemini, verificar, generar_respuesta_moderada

# === CONFIGURACIÓN ===
app = Flask(__name__)
model = get_model()
tokenizer = get_tokenizer()
model_whisper = whisper.load_model("base")

# Conexión a MongoDB en el contenedor Docker
client = MongoClient("mongodb://localhost:27017/")
db = client["hate_speech_db"]
mensajes = db["mensajes"]

# Categorías del modelo
categorias = ["Discurso de Odio", "Lenguaje Ofensivo", "Ninguno"]

# === RUTA PARA TEXTO ===
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "").strip()
    user = data.get("user", "anonimo")
    group = data.get("group")

    if not text:
        return jsonify({"resultado": "Sin texto"})

    try:
        text_en = translate_with_gemini(text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Ejecutar modelo
    input_tensor = preprocess_text(text_en, tokenizer)
    _ = model.predict(input_tensor)

    # Verificar
    es_ofensivo = verificar(text)
    if not es_ofensivo:
        return jsonify({"resultado": "Ninguno"})

    # Generar respuesta empática
    respuesta_moderada = generar_respuesta_moderada(text)

    # Guardar en MongoDB
    mensajes.insert_one({
        "usuario": user,
        "mensaje": text,
        "mensaje_en": text_en,
        "categoria": "Lenguaje Ofensivo",
        "grupo": group,
        "fecha": datetime.now(),
        "respuesta_moderada": respuesta_moderada
    })

    return jsonify({
        "resultado": "Lenguaje Ofensivo",
        "respuesta_moderada": respuesta_moderada
    })



# === RUTA PARA AUDIO ===
@app.route("/transcribe", methods=["POST"])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No se encontró archivo de audio"}), 400

    audio = request.files['audio']
    user = request.form.get("user", "anonimo")
    group = request.form.get("group")

    texto = "" 
    try:
        # Guardar temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
            audio.save(temp_audio.name)
            ogg_path = temp_audio.name

        wav_path = ogg_path.replace(".ogg", ".wav")
        subprocess.run(["ffmpeg", "-i", ogg_path, wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        result = model_whisper.transcribe(wav_path, language="es", task="translate")
        texto = result.get("text", "").strip()
        print(f"📝 Texto transcrito: {texto}")

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error al transcribir: {str(e)}"}), 500

    finally:
        # Elimina si existen
        try:
            if os.path.exists(ogg_path):
                os.remove(ogg_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)
        except Exception as e:
            print(f"⚠️ Error al eliminar archivos temporales: {e}")

    if not texto:
        return jsonify({"resultado": "Sin texto"})

    # Ejecutar el modelo 
    input_tensor = preprocess_text(texto, tokenizer)
    _ = model.predict(input_tensor)

    # Verificar
    es_ofensivo = verificar(texto)
    if not es_ofensivo:
        return jsonify({"resultado": "Ninguno"})

    respuesta_moderada = generar_respuesta_moderada(texto)

    # Guardar en MongoDB
    mensajes.insert_one({
        "usuario": user,
        "mensaje": texto,
        "categoria": "Lenguaje Ofensivo",
        "grupo": group,
        "fecha": datetime.now(),
        "respuesta_moderada": respuesta_moderada
    })

    return jsonify({
        "resultado": "Lenguaje Ofensivo",
        "texto": texto,
        "respuesta_moderada": respuesta_moderada
    })