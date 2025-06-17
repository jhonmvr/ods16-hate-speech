from flask import Flask, request, jsonify
from app.model import get_model, get_tokenizer
from app.preprocess import preprocess_text
from pymongo import MongoClient
from datetime import datetime

# === CONFIGURACIÓN ===
app = Flask(__name__)
model = get_model()
tokenizer = get_tokenizer()

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

    input_tensor = preprocess_text(text, tokenizer)
    prediction = model.predict(input_tensor)

    categorias = ["Normal", "Ofensivo", "Racista", "Odio"]
    pred_idx = prediction[0].argmax() if prediction.shape[1] > 1 else int(prediction[0][0] > 0.5)
    categoria = categorias[pred_idx]

    if categoria != "Normal":
        mensajes.insert_one({
            "usuario": user,
            "mensaje": text,
            "categoria": categoria,
            "fecha": datetime.now()
        })

    return jsonify({"resultado": categoria})
