import re
import string
from tensorflow.keras.preprocessing.sequence import pad_sequences

MAXLEN = 100

def clean_text(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    return text

def preprocess_text(text, tokenizer):
    text = clean_text(text)
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=MAXLEN)
    return padded
