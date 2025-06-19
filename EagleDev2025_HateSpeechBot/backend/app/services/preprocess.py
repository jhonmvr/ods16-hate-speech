import re
import string
from tensorflow.keras.preprocessing.sequence import pad_sequences

MAXLEN = 50

def clean_text(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    return text

def preprocess_text(text, tokenizer):
    sequence = tokenizer.texts_to_sequences([text.lower()])
    padded = pad_sequences(sequence, maxlen=MAXLEN, padding='post')
    return padded
