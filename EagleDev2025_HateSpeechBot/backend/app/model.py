# Carga del modelo y tokenizer
import pickle
import os
from keras.saving import load_model

# Rutas
MODEL_PATH = "app/model/hate_speech_model.keras"
TOKENIZER_PATH = "app/model/tokenizer.pickle"

def get_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Modelo no encontrado: {MODEL_PATH}")
    return load_model(MODEL_PATH)

def get_tokenizer():
    if not os.path.exists(TOKENIZER_PATH):
        raise FileNotFoundError(f"Tokenizer no encontrado: {TOKENIZER_PATH}")
    with open(TOKENIZER_PATH, "rb") as handle:
        return pickle.load(handle)