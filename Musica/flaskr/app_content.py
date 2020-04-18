"""
Autor: Saúl Flores Benavente
Fecha-última_modificación: 08-04-2020
Fichero que contiene la API de la aplicación TuneIT y sus funciones auxiliares
"""

from flask import request, jsonify, render_template
from psycopg2.errors import UniqueViolation, InvalidDatetimeFormat
from sqlalchemy.exc import DataError, OperationalError, IntegrityError
from flaskr.db import APP, fetch_data_by_id, Lista, Cancion, DB, Categoria, Artista, leer_todo, \
    Usuario, Aparicion


# pylint: disable=no-member
# BUSQUEDA DE CANCIONES Y LISTAS NOMBRE, ARTISTA, ALBUM / CATEGORIAS
# ORDENAR CANCIONES Y LISTAS
# AÑADIR / ELIMINAR / MODIFICAR CATEGORIAS

@APP.route('/', methods=['POST', 'GET'])
def index():
    """
    Redirige a la pagina principal
    Esto desaparecerá
    :return:
    """
    return render_template("index.html")


def listar_canciones(canciones):
    """
    Formatea los datos de una lista de canciones para devolverlos como una lista de diccionarios
    Auxiliar para transformar los datos en formato compatible con json
    Los diccionarios contienen:
        - ID
        - Nombre
        - Artistas
        - Albúm
        - Imagen
        - URL de la cancion
    :param canciones:
    :return:
    """
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
    """
    Formatea los datos de una lista de listas para devolverlos como una lista de diccionarios
    Auxiliar para transformar los datos en formato compatible con json
    :param listas:
    :return:
    """
    dictionary = []
    for element in listas:
        dictionary.append(listar_datos_lista(element))

    return dictionary


def listar_datos_lista(listas, canciones=[]):
    """
    Formatea una lista de reproducción como un diccionario que incluye las canciones que
    pertenecen a esa lista
    Auxiliar para transformar los datos en formato compatible con json
    El diccionario contiene:
        - ID
        - Nombre
        - Descripción
        - Imagen
        - Canciones, solo si <canciones> es True
    :param listas:
    :param canciones:
    :return:
    """
    dictionary = {"ID": listas.id, "Nombre": listas.nombre, "Desc": listas.descripcion}
    if canciones:
        dictionary["Canciones"] = listar_canciones([ass.canciones for ass in canciones])
        dictionary["Imagen"] = canciones[0].canciones.album.foto
    else:
        if not listas.canciones:
            dictionary["Imagen"] = "default"
        else:
            dictionary["Imagen"] = \
                [ass.canciones.album.foto for ass in listas.canciones if ass.orden == 0][0]

    return dictionary


def obtain_song_list(req):
    """
    Obtiene una cancion y una lista dadas en una petición
    Devuelve error si no se pueden encontrar
    :param req:
    :return:
    """
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

    if data_list is None:
        return None, None, "No existe la lista"

    data_cancion = fetch_data_by_id(Cancion, cancion)
    if data_cancion == "error":
        return None, None, "Error_cancion"

    if data_cancion is None:
        return None, None, "No existe la cancion"

    return data_cancion, data_list, "Success"


def buscar_categorias(req):
    """
    Devuelve una lista con las canciones cuya categoria se encuentre en la lista de
    categorias presente en la petición
    :param req:
    :return:
    """
    if req.method == "POST":
        data = req.get_json()
        dato = data["Categorias"]

    else:
        dato = req.args["Categorias"].split(" ")

    datos = DB.session.query(Cancion).filter(Categoria.nombre.in_(dato), Categoria.canciones)

    return datos


def buscar_categorias_list(req):
    """
    Devuelve una lista con las canciones contenidas en la lista especificada cuya categoria se
    encuentre en la lista de categorias presente en la petición
    :param req:
    :return:
    """
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

    if lista is None:
        return "No existe la lista", False

    datos = DB.session.query(Cancion) \
        .filter(Categoria.nombre.in_(dato), Categoria.canciones)

    datos = [cancion for cancion in datos if cancion in [ass.canciones for ass in lista.canciones]]
    return datos, True


def search(req):
    """
    Devuelve una lista de canciones cuyo nombre, autor o album se contengan la subcadena
    presente en la petición
    :param req:
    :return:
    """
    if req.method == "POST":
        data = req.get_json()
        dato = data["Nombre"]

    else:
        dato = req.args["Nombre"]

    canciones = DB.session.query(Cancion).filter(Cancion.nombre.ilike('%' + dato + '%'))
    albumes = DB.session.query(Cancion).filter(Cancion.nombre_album.ilike('%' + dato + '%'))
    artista = DB.session.query(Cancion).filter(
        Artista.nombre.ilike('%' + dato + '%'), Artista.composiciones
    )

    datos = canciones.union(albumes, artista)

    return datos


def search_in_list(req):
    """
    Devuelve una lista de canciones contenidas en la lista especificada cuyo nombre,
    autor o album se contengan la subcadena presente en la petición
    :param req:
    :return:
    """
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

    if lista is None:
        return "No existe la lista", False

    artistas = DB.session.query(Cancion).filter(Artista.nombre.ilike('%' + dato + '%'),
                                                Artista.composiciones).all()

    datos = [ass.canciones for ass in lista.canciones if
             (dato in ass.canciones.nombre) or (dato in ass.canciones.nombre_album) or (
                     ass.canciones in artistas)]

    return datos, True


def buscar_lista(req):
    """
    Devuelve una lista de listas que contiene todas las listas de reproducción
    :param req:
    :return:
    """
    if req.method == "POST":
        data = req.get_json()
        lista = data["Lista"]

    else:
        lista = req.args["Lista"]

    datos = DB.session.query(Lista).filter(Lista.nombre.ilike('%' + lista + '%'))

    return datos


# -------------------------------------------------------------------------------------------------
@APP.route('/search', methods=['POST', 'GET'])
def buscar_general():
    """
    Devuelve en formato json los resultados de la busqueda de canciones por autor, artistas y albúm
    :return:
    """
    res = search(request)
    res = listar_canciones(res)
    return jsonify(res)


@APP.route('/search_in_list', methods=['POST', 'GET'])
def buscar_general_lista():
    """
    Devuelve en formato json los resultados de la busqueda de canciones por autor, artistas y
    albúm en una lista de reproducción específica
    :return:
    """
    res, exito = search_in_list(request)
    if not exito:
        return res

    res = listar_canciones(res)
    return jsonify(res)


@APP.route('/list', methods=['POST', 'GET'])
def list_songs():
    """
    Lista en formato json las canciones presentes en la base de datos y su información básica
    :return:
    """
    try:
        canciones = leer_todo(Cancion)
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"
    dict_songs = listar_canciones(canciones)
    return jsonify(dict_songs)


@APP.route('/list_lists', methods=['POST', 'GET'])
def list_lists():
    """
    Lista en formato json las listas de reproducción y su información básica de la base de datos
    :return:
    """
    try:
        listas = leer_todo(Lista)
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"
    dict_listas = listar_listas(listas)
    return jsonify(dict_listas)


@APP.route('/list_data', methods=['POST', 'GET'])
def list_data():
    """
    Lista en formato json la información de una lista de reproducción incluyendo las canciones
    que la componen
    :return:
    """
    if request.method == "POST":
        data = request.get_json()
        lista = data['list']
    else:
        lista = int(request.args['list'])

    data_list = fetch_data_by_id(Lista, lista)
    if data_list is None:
        return "No existe la lista"
    try:
        data = DB.session.query(Aparicion).filter_by(lista=lista).order_by(Aparicion.orden)
    except IntegrityError:
        DB.session.rollback()
        return "Error"

    dict_lista = listar_datos_lista(data_list, data)
    return jsonify(dict_lista)


@APP.route('/create_list', methods=['POST', 'GET'])
def crear_lista():
    """
    Crea una lista de reproducción con la información proporcionada en la petición
    :return:
    """
    if request.method == "POST":
        data = request.get_json()
        lista = data['list']
        desc = data['desc']
    else:
        lista = request.args['list']
        desc = request.args['desc']

    try:
        element = Lista(nombre=lista, descripcion=desc)
        DB.session.add(element)
        DB.session.commit()
    except (IntegrityError, OperationalError):
        return "Error"
    else:
        return "Success"


@APP.route('/delete_list', methods=['POST', 'GET'])
def delete_lista():
    """
    Borra la lista de reproducción especificada
    :return:
    """
    if request.method == "POST":
        data = request.get_json()
        lista = data["list"]
    else:
        lista = request.args['list']

    try:
        element = DB.session.query(Lista).filter_by(id=lista).first()
        DB.session.delete(element)
        DB.session.commit()
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"
    else:
        return "Success"


@APP.route('/add_to_list', methods=['POST', 'GET'])
def add_to_list():
    """
    Añade la canción especificada a la lista de reproducción especificada
    :return:
    """
    data_cancion, data_list, msg = obtain_song_list(request)
    if data_cancion is not None and data_list is not None:
        try:
            data_list.canciones.append(
                Aparicion(canciones=data_cancion, orden=len(data_list.canciones)))
            DB.session.commit()
        except (IntegrityError, OperationalError):
            DB.session.rollback()
            return "Error"
        else:
            return msg
    else:
        return msg


@APP.route('/delete_from_list', methods=['POST', 'GET'])
def delete_from_list():
    """
    Borra la canción especificada de la lista de reproducción especificada
    :return:
    """
    data_cancion, data_list, msg = obtain_song_list(request)
    asociacion = [ass for ass in data_list.canciones if ass.canciones.id == data_cancion.id]
    if data_cancion is not None and data_list is not None and asociacion != []:
        try:
            data_list.canciones.remove(asociacion)
            DB.session.commit()
        except (IntegrityError, OperationalError):
            DB.session.rollback()
            return "Error"
        else:
            return msg
    else:
        return msg


@APP.route('/reorder', methods=['POST', 'GET'])
def reorder_list():
    if request.method == 'POST':
        data = request.get_json()
        lista = data["list"]
        before = data["before"]
        after = data["after"]
    else:
        lista = request.args["list"]
        before = request.args["before"]
        after = request.args["after"]

    before = int(before)
    after = int(after)
    apariciones = DB.session.query(Aparicion).filter_by(lista=lista)
    if before > after:
        min_lim = after
        max_lim = before
        indice = 1
    else:
        min_lim = before + 1
        max_lim = after + 1
        indice = -1

    for aparicion in apariciones:
        if aparicion.orden in range(min_lim, max_lim):
            aparicion.orden += indice
        elif aparicion.orden == before:
            aparicion.orden = after

    try:
        DB.session.commit()
    except (IntegrityError, OperationalError):
        return "Error"

    return "Success"


@APP.route('/search_list', methods=['POST', 'GET'])
def search_list():
    """
    Busca una lista de reproducción en la base de datos
    :return:
    """
    listas = buscar_lista(request)
    result = listar_listas(listas)
    return jsonify(result)


@APP.route('/filter_category', methods=['POST', 'GET'])
def filter_category():
    """
    Devuelve una lista de canciones pertenecientes a las categorias en el filtro
    :return:
    """
    canciones = buscar_categorias(request)
    result = listar_canciones(canciones)
    return jsonify(result)


@APP.route('/filter_category_in_list', methods=['POST', 'GET'])
def filter_category_list():
    """
    Devuelve una lista de canciones pertenecientes a las categorias en el filtro y a la lista de
    reproducción indicada
    :return:
    """
    canciones, exito = buscar_categorias_list(request)
    if not exito:
        return canciones

    result = listar_canciones(canciones)
    return jsonify(result)


@APP.route('/test', methods=['POST', 'GET'])
def test():
    """
    Test para mostrar que el servidor responde peticiones
    :return:
    """
    if request.method == "GET":
        res = request.args['test']

        return res

    return "Error"


# ------------------------------------------------------------------------------------------------
def autentificacion(req):
    """
    Comprueba que existe el usuario especificado y que los datos de inicio de sesión son correctos
    :param req:
    :return:
    """
    if req.method == 'POST':
        data = req.get_json()
        email = data["email"]
        password = data["password"]
    else:
        email = req.args["email"]
        password = req.args["password"]

    try:
        user = DB.session.query(Usuario).filter_by(email=email).first()
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return False, "Error", None

    if not user:
        return False, "No user", None

    return user.password == password, "Contraseña incorrecta", user


@APP.route('/register', methods=['POST', 'GET'])
def registro():
    """
    Registrar el usuario y sus datos en la base de datos
    :return:
    """
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
        DB.session.add(user)
        DB.session.commit()
    except (IntegrityError, OperationalError) as error:
        DB.session.rollback()
        if isinstance(error.orig, UniqueViolation):
            return "Clave duplicada"

        return "Error"

    except DataError as error:
        DB.session.rollback()
        if isinstance(error.orig, InvalidDatetimeFormat):
            return "Fecha incorrecta"

    return "Success"


@APP.route('/delete_user', methods=['POST', 'GET'])
def delete_user():
    """
    Eliminar el usuario especificado de la base de datos
    :return:
    """
    entro, msg, user = autentificacion(request)

    if entro:
        try:
            DB.session.delete(user)
            DB.session.commit()

            return "Success"
        except (IntegrityError, OperationalError):
            DB.session.rollback()
            return "Error"
    else:
        return msg


@APP.route('/sign_in', methods=['POST', 'GET'])
def inicio_sesion():
    """
    Inicio de sesion
    :return:
    """
    entro, msg, _ = autentificacion(request)

    if entro:
        try:
            return "Success"
        except (IntegrityError, OperationalError):
            DB.session.rollback()
            return "Error"
    else:
        return msg
