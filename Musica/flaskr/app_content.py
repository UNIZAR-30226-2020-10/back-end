from flask import *
from psycopg2.errors import UniqueViolation, InvalidDatetimeFormat
from sqlalchemy.exc import DataError

from flaskr.db import *


## BUSQUEDA DE CANCIONES Y LISTAS NOMBRE, ARTISTA, ALBUM / CATEGORIAS
## ORDENAR CANCIONES Y LISTAS
## AÑADIR / ELIMINAR / MODIFICAR CATEGORIAS

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html")


def listar_canciones(canciones):
    lista = []
    for song in canciones:
        dictionary = {"ID": song.id, "Nombre": song.nombre, "Artistas": []}
        for artist in song.artistas:
            dictionary["Artistas"].append(artist.nombre)
        dictionary["Album"] = song.nombre_album
        dictionary["Imagen"] = song.album.foto
        dictionary["URL"] = song.path
        lista.append(dictionary)
    return lista


def listar_listas(listas):
    dictionary = []
    for element in listas:
        dictionary.append(listar_datos_lista(element, False))

    return dictionary


def listar_datos_lista(listas, canciones):
    dictionary = {"ID": listas.id, "Nombre": listas.nombre, "Desc": listas.descripcion}
    if canciones:
        dictionary["Canciones"] = listar_canciones(listas.canciones)
    if not listas.canciones:
        dictionary["Imagen"] = "default"
    else:
        dictionary["Imagen"] = listas.canciones[0].album.foto

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


def buscar(req, donde, que):
    if req.method == "POST":
        data = req.get_json()
        dato = data["Nombre"]

    else:
        dato = req.args["Nombre"]

    datos = buscar_sub(donde, que, dato)

    return datos


def buscar_sub(donde, que, dato):
    try:
        if que == "nombre":
            datos = db.session.query(donde).filter_by(nombre=dato).all()
        elif que == "album":
            datos = db.session.query(donde).filter_by(nombre_album=dato).all()
        elif que == "artista":
            artista = db.session.query(donde).filter_by(nombre=dato).all()
            datos = artista[0].composiciones

    except IntegrityError:
        return "Error"

    return datos


def buscar_lista(req, tipo):
    if req.method == "POST":
        data = req.get_json()
        dato = data["Nombre"]
        lista = data["Lista"]

    else:
        dato = req.args["Nombre"]
        lista = req.args["Lista"]

    try:
        lista = fetch_data_by_id(Lista, int(lista))

        if lista == "error":
            return "Error"

        if tipo == "cancion":
            datos = [cancion for cancion in lista.canciones if cancion.nombre == dato]
        elif tipo == "album":
            datos = [cancion for cancion in lista.canciones if cancion.nombre_album == dato]
        elif tipo == "artista":
            artista = db.session.query(Artista).filter_by(nombre=dato).all()
            datos = [cancion for cancion in artista[0].composiciones if cancion in lista.canciones]
        else:
            return "Error"

        return datos
    except IntegrityError:
        return "Error"


@app.route('/list', methods=['POST', 'GET'])
def list_songs():
    try:
        canciones = leer_todo(Cancion)
    except None:
        db.session.rollback()
        return "Error"
    dict_songs = listar_canciones(canciones)
    return jsonify(dict_songs)


@app.route('/list_lists', methods=['POST', 'GET'])
def list_lists():
    try:
        listas = leer_todo(Lista)
    except None:
        db.session.rollback()
        return "Error"
    dict_listas = listar_listas(listas)
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

    dict_lista = [listar_datos_lista(data_list, True)]
    return jsonify(dict_lista)


@app.route('/create_list', methods=['POST', 'GET'])
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
        element = db.session.query(Lista).filter_by(id=lista).first()
        db.session.delete(element)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return "Error"
    else:
        return "Success"


@app.route('/add_to_list', methods=['POST', 'GET'])
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


@app.route('/delete_from_list', methods=['POST', 'GET'])
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


@app.route('/search_song', methods=['POST', 'GET'])
def search_song():
    canciones = buscar(request, Cancion, "nombre")
    return jsonify(listar_canciones(canciones))


@app.route('/search_list', methods=['POST', 'GET'])
def search_list():
    listas = buscar(request, Lista, "nombre")
    return jsonify(listar_listas(listas))


@app.route('/search_song_by_album', methods=['POST', 'GET'])
def search_song_by_album():
    canciones = buscar(request, Cancion, "album")
    result = listar_canciones(canciones)
    return jsonify(result)


@app.route('/search_song_by_artist', methods=['POST', 'GET'])
def search_song_by_artist():
    canciones = buscar(request, Artista, "artista")
    result = listar_canciones(canciones)
    return jsonify(result)


@app.route('/search_song_list', methods=['POST', 'GET'])
def search_song_list():
    canciones = buscar_lista(request, "cancion")
    return jsonify(listar_canciones(canciones))


@app.route('/search_song_by_album_list', methods=['POST', 'GET'])
def search_song_by_album_list():
    canciones = buscar_lista(request, "album")
    result = listar_canciones(canciones)
    return jsonify(result)


@app.route('/search_song_by_artist_list', methods=['POST', 'GET'])
def search_song_by_artist_list():
    canciones = buscar_lista(request, "artista")
    result = listar_canciones(canciones)
    return jsonify(result)


@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method == "GET":
        res = request.args['test']

        return res


def autentificacion(req):
    if req.method == 'POST':
        data = req.get_json()
        email = data["email"]
        password = data["password"]
    else:
        email = req.args["email"]
        password = req.args["password"]

    try:
        user = db.session.query(Usuario).filter_by(email=email).first()
    except IntegrityError:
        db.session.rollback()
        return False, "Error", None

    if not user:
        return False, "No user", None

    return user.password == password, "Contraseña incorrecta", user


@app.route('/register', methods=['POST', 'GET'])
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
        db.session.rollback()
        if isinstance(e.orig, UniqueViolation):
            return "Clave duplicada"
        else:
            return "Error"

    except DataError as e:
        db.session.rollback()
        if isinstance(e.orig, InvalidDatetimeFormat):
            return "Fecha incorrecta"

    return "Success"


@app.route('/delete_user', methods=['POST', 'GET'])
def delete_user():
    entro, msg, user = autentificacion(request)

    if entro:
        try:
            db.session.delete(user)
            db.session.commit()

            return "Success"
        except IntegrityError:
            db.session.rollback()
            return "Error"
    else:
        return msg


@app.route('/sign_in', methods=['POST', 'GET'])
def inicio_sesion():
    entro, msg, user = autentificacion(request)

    if entro:
        try:
            return "Success"
        except IntegrityError:
            db.session.rollback()
            return "Error"
    else:
        return msg
