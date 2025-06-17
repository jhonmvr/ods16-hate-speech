# Carga del modelo y tokenizer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import json

# Cargar modelo entrenado
model = load_model("modelo.keras")

# Cargar tokenizer
with open("tokenizer.json") as f:
    tokenizer_json = f.read()  # lee como string
    tokenizer = tokenizer_from_json(tokenizer_json) 

# Exponer modelo y tokenizer
def get_model():
    return model

def get_tokenizer():
    return tokenizer