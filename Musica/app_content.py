from flask import *

from db import *


@app.route('/')
def index():
    return render_template("index.html")


def listar_canciones(dictionary, canciones):
    for song in canciones:
        dictionary[song.id] = {}
        dictionary[song.id]["Nombre"] = song.nombre
        dictionary[song.id]["Artistas"] = []
        for artist in song.artistas:
            dictionary[song.id]["Artistas"].append(artist.nombre)
        dictionary[song.id]["Album"] = song.nombre_album
        dictionary[song.id]["URL"] = song.audio
    return dictionary


@app.route('/list')
def list_songs():
    canciones = leer_todo(Cancion)
    dict_songs = {}
    dict_songs = listar_canciones(dict_songs, canciones)
    return jsonify(dict_songs)


@app.route('/list_lists')
def list_lists():
    listas = leer_todo(Lista)
    dict_listas = {}
    for element in listas:
        dict_listas[element.id] = {}
        dict_listas[element.id]["Nombre"] = element.nombre
        dict_listas[element.id]["Desc"] = element.descripcion

    return jsonify(dict_listas)


@app.route('/list_data', methods=['POST', 'GET'])
def list_data():
    lista = ""
    if request.method == "POST":
        lista = int(request.form['list'])
    else:
        lista = int(request.args['list'])

    data_list = fetch_data(Lista, lista)
    if data_list == "error":
        return "error"

    dict_lista = {data_list.id: {}}
    dict_lista[data_list.id]["Nombre"] = data_list.nombre
    dict_lista[data_list.id]["Desc"] = data_list.descripcion
    dict_lista[data_list.id]["Canciones"] = {}
    dict_lista[data_list.id]["Canciones"] = listar_canciones(dict_lista[data_list.id]["Canciones"], data_list.canciones)

    return jsonify(dict_lista)


@app.route('/create_list')
def crear_lista():
    if request.method == "POST":
        lista = int(request.form['list'])
        desc = request.form['list']
    else:
        lista = int(request.args['list'])
        desc = request.form['list']

    element = Lista(nombre=lista, descripcion=desc)
    db.session.add(element)
    db.session.commit()


@app.route('/add_to_list')
def add_to_list():
    if request.method == "POST":
        cancion = int(request.form['cancion'])
        lista = int(request.form['list'])
    else:
        cancion =int(request.args['cancion'])
        lista = int(request.args['list'])

    data_list = fetch_data(Lista, lista)
    if data_list == "error":
        return "error_lista"

    data_cancion = fetch_data(Cancion, cancion)
    if data_list == "error":
        return "error_cancion"

    data_list.canciones.append(data_cancion)
    db.session.commit()



