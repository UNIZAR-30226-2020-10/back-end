from flask import *
from psycopg2.errors import UniqueViolation, InvalidDatetimeFormat
from sqlalchemy.exc import IntegrityError, DataError

from flaskr.db import *

## BUSQUEDA DE CANCIONES Y LISTAS NOMBRE, ARTISTA, ALBUM / CATEGORIAS
## ORDENAR CANCIONES Y LISTAS
## AÑADIR / ELIMINAR / MODIFICAR CATEGORIAS

@app.route('/')
def index():
    return render_template("index.html")


def listar_canciones(dictionary, canciones):
    for song in canciones:
        dictionary[song.id] = {}
        dictionary[song.id]["ID"] = song.id
        dictionary[song.id]["Nombre"] = song.nombre
        dictionary[song.id]["Artistas"] = []
        for artist in song.artistas:
            dictionary[song.id]["Artistas"].append(artist.nombre)
        dictionary[song.id]["Album"] = song.nombre_album
        dictionary[song.id]["Imagen"] = song.album.foto
        dictionary[song.id]["URL"] = song.path
    return dictionary


def obtain_song_list(request):
    if request.method == "POST":
        data = request.get_json()
        cancion = data['cancion']
        lista = data['list']
    else:
        cancion = int(request.args['cancion'])
        lista = int(request.args['list'])

    data_list = fetch_data_by_id(Lista, lista)
    if data_list == "error":
        return "Error_lista"

    data_cancion = fetch_data_by_id(Cancion, cancion)
    if data_cancion == "error":
        return "Error_cancion"

    return data_cancion, data_list


@app.route('/list')
def list_songs():
    try:
        canciones = leer_todo(Cancion)
    except:
        return "Error"
    dict_songs = {}
    dict_songs = listar_canciones(dict_songs, canciones)
    print(dict_songs)
    return jsonify(dict_songs)


@app.route('/list_lists')
def list_lists():
    listas = leer_todo(Lista)
    dict_listas = {}
    for element in listas:
        dict_listas[element.id] = {}
        dict_listas[element.id]["ID"] = element.id
        dict_listas[element.id]["Nombre"] = element.nombre
        dict_listas[element.id]["Desc"] = element.descripcion
        if not element.canciones:
            dict_listas[element.id]["Imagen"] = "default"
        else:
            dict_listas[element.id]["Imagen"] = element.canciones[0].album.foto

    return jsonify(dict_listas)


@app.route('/list_data', methods=['POST', 'GET'])
def list_data():
    if request.method == "POST":
        data = request.get_json()
        lista = data['list']
    else:
        lista = int(request.args['list'])

    data_list = fetch_data_by_id(Lista, lista)
    if data_list == "Error":
        return "Error"

    dict_lista = {data_list.id: {}}
    dict_lista[data_list.id]["ID"] = data_list.id
    dict_lista[data_list.id]["Nombre"] = data_list.nombre
    dict_lista[data_list.id]["Desc"] = data_list.descripcion
    dict_lista[data_list.id]["Canciones"] = listar_canciones(dict_lista[data_list.id]["Canciones"], data_list.canciones)
    dict_lista[data_list.id]["Imagen"] = data_list.canciones[0].album.foto

    return jsonify(dict_lista)


@app.route('/create_list')
def crear_lista():
    if request.method == "POST":
        data = request.get_json()
        lista = data['list']
        desc = data['desc']
    else:
        lista = request.args['list']
        desc = request.args['desc']

    try:
        element = Lista(nombre=lista, descripcion=desc)
        db.session.add(element)
        db.session.commit()
    except IntegrityError:
        return "Error"
    else:
        return "Success"


@app.route('/delete_list', methods=['POST', 'GET'])
def delete_lista():
    if request.method == "POST":
        data = request.get_json()
        lista = data["list"]
    else:
        lista = request.args['list']

    try:
        element = db.session.query(Lista).filter_by(id=lista).all()
        db.session.delete(element[0])
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return "Error"
    else:
        return "Success"


@app.route('/add_to_list')
def add_to_list():
    data_cancion, data_list = obtain_song_list(request)

    try:
        data_list.canciones.append(data_cancion)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return "Error"
    else:
        return "Success"


@app.route('/delete_from_list')
def delete_from_list():
    data_cancion, data_list = obtain_song_list(request)

    try:
        data_list.canciones.remove(data_cancion)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return "Error"
    else:
        return "Success"


@app.route('/search_song')
def search_song():
    if request.method == "POST":
        data = request.get_json()
        nombre = data["Nombre"]

    else:
        nombre = request.args["Nombre"]

    canciones = db.session.query(Cancion).filter_by(nombre=nombre).all()

    return listar_canciones({}, canciones)


@app.route('/test')
def test():
    if request.method == "GET":
        res = request.args['test']

        return res


@app.route('/register')
def registro():
    if request.method == 'POST':
        data = request.get_json()
        email = data["email"]
        nombre = data["nombre"]
        password = data["password"]
        fecha = data["fecha"]
        pais = data["pais"]

    else:
        email = request.args["email"]
        nombre = request.args["nombre"]
        password = request.args["password"]
        fecha = request.args["fecha"]
        pais = request.args["pais"]

    user = Usuario(nombre=nombre, email=email, password=password, fecha_nacimiento=fecha, pais=pais)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:

        if isinstance(e.orig, UniqueViolation):
            return "Clave duplicada"
        else:
            return "Error"

    except DataError as e:

        if isinstance(e.orig, InvalidDatetimeFormat):
            return "Fecha incorrecta"

    return "Success"


@app.route('/delete_user')
def delete_user():

    if request.method == 'POST':
        data = request.get_json()
        email = data["email"]
        password = data["password"]
    else:
        email = request.args["email"]
        password = request.args["password"]

    user = db.session.query(Usuario).filter_by(email=email).all()

    if not user:
        return "No user"

    user = user[0]
    if user.password == password:
        try:
            db.session.delete(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Error"

    return "Success"
