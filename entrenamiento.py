import pandas as pd
import sqlite3
import numpy as np
import pickle
from ResourceLoggingCSVLogger import ResourceLoggingCSVLogger
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense, Dropout
from keras.saving import save_model  # nuevo para .keras

# 1. Cargar dataset
df = pd.read_csv("./data_set/labeled_data.csv")
df = df[['tweet', 'class']]

# 2. Guardar en SQLite
conn = sqlite3.connect("hate_speech.db")
df.to_sql("tweets", conn, if_exists="replace", index=False)

# 3. Preprocesamiento
X = df['tweet'].astype(str)
y = df['class']

tokenizer = Tokenizer(num_words=10000, oov_token="<OOV>")
tokenizer.fit_on_texts(X)
sequences = tokenizer.texts_to_sequences(X)
padded = pad_sequences(sequences, maxlen=50, padding='post')

# Guardar tokenizer
with open("tokenizer.pickle", "wb") as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# 4. Dividir en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(padded, y, test_size=0.2, random_state=42)

# 5. Modelo optimizado para CPU
model = Sequential([
    Embedding(input_dim=10000, output_dim=16, input_length=50),
    GlobalAveragePooling1D(),
    Dense(16, activation='relu'),
    Dropout(0.3),
    Dense(3, activation='softmax')
])

model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

# 6. Entrenamiento
model.fit(
    X_train, y_train,
    epochs=10,
    validation_split=0.1,
    batch_size=32,
    callbacks=[ResourceLoggingCSVLogger()]
)

# 7. Evaluación
y_pred = np.argmax(model.predict(X_test), axis=1)
print(classification_report(y_test, y_pred, target_names=['Hate', 'Offensive', 'Neither']))

# 8. Guardar modelo en formato .keras
save_model(model, "hate_speech_model.keras")
