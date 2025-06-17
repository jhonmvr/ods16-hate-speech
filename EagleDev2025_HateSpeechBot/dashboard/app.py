from flask import Flask, render_template, request
from pymongo import MongoClient
import pandas as pd
from collections import Counter

app = Flask(__name__, template_folder="templates")

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hate_speech_db"]
mensajes = db["mensajes"]

@app.route('/')
def dashboard():
    # Filtros
    categoria = request.args.get('categoria')
    usuario = request.args.get('usuario')
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')

    query = {}
    if categoria:
        query['categoria'] = categoria
    if usuario:
        query['usuario'] = usuario
    if desde or hasta:
        query['fecha'] = {}
        if desde:
            query['fecha']['$gte'] = pd.to_datetime(desde)
        if hasta:
            query['fecha']['$lte'] = pd.to_datetime(hasta)

    # Obtener datos
    data = list(mensajes.find(query))
    df = pd.DataFrame(data)

    # Datos para las gráficas
    categorias = ['Odio', 'Racista', 'Ofensivo']
    conteos = df['categoria'].value_counts().reindex(categorias, fill_value=0).tolist() if not df.empty else [0, 0, 0, 0]
    conteos_dict = dict(zip(categorias, conteos))

    usuarios = mensajes.distinct('usuario')
    total_mensajes = len(df)
    top_usuarios = Counter(df['usuario']).most_common(3) if not df.empty else []
    top_grupos = Counter(df['grupo'].fillna('Sin grupo')).most_common(3) if not df.empty else []

    return render_template(
        "index.html",
        datos=df.to_dict('records'),
        categorias=categorias,
        conteos_dict=conteos_dict,
        categoria=categoria,
        usuario=usuario,
        desde=desde,
        hasta=hasta,
        usuarios=usuarios,
        total_mensajes=total_mensajes,
        top_usuarios=top_usuarios,
        top_grupos=top_grupos
    )

if __name__ == '__main__':
    app.run(debug=True, port=8500)
