from flask import Flask, render_template, request
from pymongo import MongoClient
import pandas as pd

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

    # Procesar conteos
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        conteos = df['categoria'].value_counts().to_dict()
    else:
        conteos = {}

    # Listas para los select
    categorias = mensajes.distinct('categoria')
    usuarios = mensajes.distinct('usuario')

    return render_template(
        "index.html",
        datos=df.to_dict('records'),
        categorias=categorias,
        conteos_dict=conteos,
        categoria=categoria,
        usuario=usuario,
        desde=desde,
        hasta=hasta,
        usuarios=usuarios
    )

if __name__ == '__main__':
    app.run(debug=True, port=8500)
