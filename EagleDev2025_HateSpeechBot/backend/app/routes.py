from flask import Flask, request, jsonify
from app.model import get_model, get_tokenizer
from app.preprocess import preprocess_text
from pymongo import MongoClient
from datetime import datetime
import os
import tempfile
import whisper
import subprocess
import traceback

# === CONFIGURACIÓN ===
app = Flask(__name__)
model = get_model()
tokenizer = get_tokenizer()
model_whisper = whisper.load_model("base")

# Conexión a MongoDB en el contenedor Docker
client = MongoClient("mongodb://localhost:27017/")
db = client["hate_speech_db"]
mensajes = db["mensajes"]

# === RUTA PRINCIPAL ===
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")
    user = data.get("user", "anonimo")
    group = data.get("group", None)

    input_tensor = preprocess_text(text, tokenizer)
    prediction = model.predict(input_tensor)

    categorias = ["Normal", "Ofensivo", "Racista", "Odio"]
    pred_idx = prediction[0].argmax() if prediction.shape[1] > 1 else int(prediction[0][0] > 0.5)
    categoria = categorias[pred_idx]

    # Solo guardar si no es "Normal"
    if categoria != "Normal":
        mensajes.insert_one({
            "usuario": user,
            "mensaje": text,
            "categoria": categoria,
            "grupo": group,
            "fecha": datetime.now()
        })

    return jsonify({"resultado": categoria})

# === RUTA PARA TRANSCRIBIR AUDIO ===
@app.route("/transcribe", methods=["POST"])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No se encontró archivo de audio"}), 400

    audio = request.files['audio']
    user = request.form.get("user", "anonimo")
    group = request.form.get("group")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
        audio.save(temp_audio.name)
        ogg_path = temp_audio.name

    wav_path = ogg_path.replace(".ogg", ".wav")
    subprocess.run(["ffmpeg", "-i", ogg_path, wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"🎙️ Convertido a WAV: {wav_path}")
    print("🧠 Transcribiendo con Whisper...")

    try:
        result = model_whisper.transcribe(wav_path)
        texto = result.get("text", "")
    except Exception as e:
        print("❌ Error al transcribir con whisper:")
        traceback.print_exc()
        os.remove(ogg_path)
        os.remove(wav_path)
        return jsonify({"error": f"Error al transcribir: {str(e)}"}), 500

    os.remove(ogg_path)
    os.remove(wav_path)

    if not texto.strip():
        return jsonify({"resultado": "Sin texto"})

    input_tensor = preprocess_text(texto, tokenizer)
    prediction = model.predict(input_tensor)

    categorias = ["Normal", "Ofensivo", "Racista", "Odio"]
    pred_idx = prediction[0].argmax() if prediction.shape[1] > 1 else int(prediction[0][0] > 0.5)
    categoria = categorias[pred_idx]

    if categoria != "Normal":
        mensajes.insert_one({
            "usuario": user,
            "mensaje": texto,
            "categoria": categoria,
            "grupo": group,
            "fecha": datetime.now()
        })

    return jsonify({"resultado": categoria, "texto": texto})
