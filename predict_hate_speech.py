import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import os
from keras.saving import load_model  # para .keras

# --- Rutas ---
model_path = "hate_speech_model.keras"
tokenizer_path = "tokenizer.pickle"

# --- Verificar existencia ---
if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Modelo no encontrado: {model_path}")

if not os.path.exists(tokenizer_path):
    raise FileNotFoundError(f"❌ Tokenizer no encontrado: {tokenizer_path}")

# --- Cargar modelo y tokenizer ---
print("📦 Cargando modelo y tokenizer...")
model = load_model(model_path)

with open(tokenizer_path, "rb") as handle:
    tokenizer = pickle.load(handle)

# --- Función de predicción ---
def predict_text(texts):
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=50, padding='post')
    predictions = model.predict(padded)

    labels = ['Hate Speech', 'Offensive Language', 'Neither']
    for i, text in enumerate(texts):
        pred_class = np.argmax(predictions[i])
        confidence = predictions[i][pred_class]
        print(f"\n📝 Texto: {text}")
        print(f"🔎 Predicción: {labels[pred_class]} (Confianza: {confidence:.2f})")

# --- Uso interactivo ---
if __name__ == "__main__":
    print("🤖 Clasificador de hate speech - Modelo multiclase")

    # Puedes cambiar estos textos de prueba
    sample_inputs = [
        "i love u so much",
        "mijin",
        "gordo por que te portas como la verga",
        "I hate you",
        "You are a terrible person",
        "You are the worst and you should disappear",
        "What a lovely day for a walk in the park",
        "Nobody cares what you think, idiot",
        "== Hello... ==  ASP.NET is not a language.. its a .NET technology which enables server side programming for web development.. Infact ASP.NET should not be under the catagory ``.NET programming languages``...  Nawin"
    ]

    predict_text(sample_inputs)
