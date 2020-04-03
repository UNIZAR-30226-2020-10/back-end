from flask import *
from psycopg2.errors import UniqueViolation, InvalidDatetimeFormat
from sqlalchemy.exc import DataError, OperationalError

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


def obtain_song_list(req):
    if req.method == "POST":
        data = req.get_json()
        cancion = data['cancion']
        lista = data['list']
    else:
        cancion = int(req.args['cancion'])
        lista = int(req.args['list'])

    data_list = fetch_data_by_id(Lista, lista)
    if data_list == "error":
        return None, None, "Error_lista"
    elif data_list is None:
        return None, None, "No existe la lista"

    data_cancion = fetch_data_by_id(Cancion, cancion)
    if data_cancion == "error":
        return None, None, "Error_cancion"
    elif data_cancion is None:
        return None, None, "No existe la cancion"

    return data_cancion, data_list, "Success"


def buscar_categorias(req):
    if req.method == "POST":
        data = req.get_json()
        dato = data["Categorias"]

    else:
        dato = req.args["Categorias"].split(" ")

    datos = db.session.query(Cancion).filter(Categoria.nombre.in_(dato), Categoria.canciones)

    return datos


def buscar_categorias_list(req):
    if req.method == "POST":
        data = req.get_json()
        dato = data["Categorias"]
        lista = data["Lista"]

    else:
        dato = req.args["Categorias"].split(" ")
        lista = req.args["Lista"]

    lista = fetch_data_by_id(Lista, int(lista))
    if lista == "error":
        return "Error", False
    elif lista is None:
        return "No existe la lista", False

    datos = db.session.query(Cancion) \
        .filter(Categoria.nombre.in_(dato), Categoria.canciones)

    datos = [cancion for cancion in datos if cancion in lista.canciones]
    return datos


def search(req):
    if req.method == "POST":
        data = req.get_json()
        dato = data["Nombre"]

    else:
        dato = req.args["Nombre"]

    canciones = db.session.query(Cancion).filter(Cancion.nombre.ilike('%' + dato + '%'))
    albumes = db.session.query(Cancion).filter(Cancion.nombre_album.ilike('%' + dato + '%'))
    artista = db.session.query(Cancion).filter(Artista.nombre.ilike('%' + dato + '%'), Artista.composiciones)

    datos = canciones.union(albumes, artista)

    return datos


def search_in_list(req):
    if req.method == "POST":
        data = req.get_json()
        dato = data["Nombre"]
        lista = data["Lista"]

    else:
        dato = req.args["Nombre"]
        lista = req.args["Lista"]

    lista = fetch_data_by_id(Lista, int(lista))
    if lista == "error":
        return "Error", False
    elif lista is None:
        return "No existe la lista", False

    artistas = db.session.query(Cancion).filter(Artista.nombre.ilike('%' + dato + '%'), Artista.composiciones).all()

    datos = [cancion for cancion in lista.canciones if
             (dato in cancion.nombre) or (dato in cancion.nombre_album) or (cancion in artistas)]

    return datos, True


def buscar_lista(req):
    if req.method == "POST":
        data = req.get_json()
        lista = data["Lista"]

    else:
        lista = req.args["Lista"]

    datos = db.session.query(Lista).filter(Lista.nombre.ilike('%' + lista + '%'))

    return datos


# ---------------------------------------------------------------------------------------------------
@app.route('/search', methods=['POST', 'GET'])
def buscar_general():
    res = search(request)
    res = listar_canciones(res)
    return jsonify(res)


@app.route('/search_in_list', methods=['POST', 'GET'])
def buscar_general_lista():
    res, exito = search_in_list(request)
    if not exito:
        return res
    else:
        res = listar_canciones(res)
        return jsonify(res)


@app.route('/list', methods=['POST', 'GET'])
def list_songs():
    try:
        canciones = leer_todo(Cancion)
    except (IntegrityError, OperationalError):
        db.session.rollback()
        return "Error"
    dict_songs = listar_canciones(canciones)
    return jsonify(dict_songs)


@app.route('/list_lists', methods=['POST', 'GET'])
def list_lists():
    try:
        listas = leer_todo(Lista)
    except (IntegrityError, OperationalError):
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
    elif data_list is None:
        return "No existe la lista"

    dict_lista = listar_datos_lista(data_list, True)
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
    except (IntegrityError, OperationalError):
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
    except (IntegrityError, OperationalError):
        db.session.rollback()
        return "Error"
    else:
        return "Success"


@app.route('/add_to_list', methods=['POST', 'GET'])
def add_to_list():
    data_cancion, data_list, msg = obtain_song_list(request)
    if data_cancion is not None and data_list is not None:
        try:
            data_list.canciones.append(data_cancion)
            db.session.commit()
        except (IntegrityError, OperationalError):
            db.session.rollback()
            return "Error"
        else:
            return msg
    else:
        return msg


@app.route('/delete_from_list', methods=['POST', 'GET'])
def delete_from_list():
    data_cancion, data_list, msg = obtain_song_list(request)
    if data_cancion is not None and data_list is not None:
        try:
            data_list.canciones.remove(data_cancion)
            db.session.commit()
        except (IntegrityError, OperationalError):
            db.session.rollback()
            return "Error"
        else:
            return msg
    else:
        return msg


@app.route('/search_list', methods=['POST', 'GET'])
def search_list():
    listas = buscar_lista(request)
    result = listar_listas(listas)
    return jsonify(result)


@app.route('/filter_category', methods=['POST', 'GET'])
def filter_category():
    canciones = buscar_categorias(request)
    result = listar_canciones(canciones)
    return jsonify(result)


@app.route('/filter_category_in_list', methods=['POST', 'GET'])
def filter_category_list():
    canciones = buscar_categorias_list(request)
    result = listar_canciones(canciones)
    return jsonify(result)


@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method == "GET":
        res = request.args['test']

        return res


# -----------------------------------------------------------------------------------------------------
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
    except (IntegrityError, OperationalError):
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
    except (IntegrityError, OperationalError) as e:
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
        except (IntegrityError, OperationalError):
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
        except (IntegrityError, OperationalError):
            db.session.rollback()
            return "Error"
    else:
        return msg
