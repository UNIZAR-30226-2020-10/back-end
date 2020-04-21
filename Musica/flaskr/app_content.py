"""
Autor: Saúl Flores Benavente
Fecha-última_modificación: 08-04-2020
Fichero que contiene la API de la aplicación TuneIT y sus funciones auxiliares
"""

from flask import request, jsonify, render_template
from psycopg2.errors import UniqueViolation, InvalidDatetimeFormat
from sqlalchemy.exc import DataError, OperationalError, IntegrityError
from flaskr.db import APP, fetch_data_by_id, Lista, Cancion, DB, Categoria, Artista, leer_todo, \
    Usuario, Aparicion, Album


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


def leer_datos(req, etiquetas):
    """
    Extrae de la peticion los datos especificados en <etiquetas>
    :param req:
    :param etiquetas:
    :return:
    """
    datos = []
    if req.method == "POST":
        data = req.get_json()
        for etiqueta in etiquetas:
            datos.append(data[etiqueta])
    else:
        for etiqueta in etiquetas:
            datos.append(req.args[etiqueta])

    if len(datos) == 1:
        return datos[0]

    return datos


def listar(tipo, tabla):
    """
    Lista los datos de tipo <tipo>
    Para cada tipo se llama a una funcion específica
    :param tipo:
    :param tabla:
    :return:
    """
    try:
        dato = leer_todo(tabla)
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"

    if tipo == "lista":
        dict_songs = listar_listas(dato)
    elif tipo == "artista":
        dict_songs = listar_artistas(dato)
    elif tipo == "album":
        dict_songs = listar_albums(dato)
    else:
        dict_songs = listar_canciones(dato)

    return dict_songs


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


def listar_albums(albums):
    """
    Formatea los datos de una lista de albumes para devolverlos como una lista de diccionarios
    Auxiliar para transformar los datos en formato compatible con json
    :param albums:
    :return:
    """
    album_list = []
    for element in albums:
        album_list.append(listar_datos_albums(element))

    return album_list


def listar_artistas(artistas):
    """
    Formatea los datos de una lista de artistas para devolverlos como una lista de diccionarios
    Auxiliar para transformar los datos en formato compatible con json
    :param artistas:
    :return:
    """
    dictionary = []
    for artista in artistas:
        dictionary.append(listar_datos_artistas(artista))

    return dictionary


def listar_datos(tipo, tabla, dato):
    """
    Lista los datos de un elemento de tipo <tipo> con id <dato>
    Se lista llamando a la función específica de cada elemento
    :param tipo:
    :param tabla:
    :param dato:
    :return:
    """
    try:
        if tipo == "album" or tipo == "artista":
            res = DB.session.query(tabla).filter_by(nombre=dato).first()
        else:
            res = DB.session.query(tabla).filter_by(id=int(dato)).first()
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"

    if res is None:
        return "No existe " + tipo

    if tipo == "album":
        dict_res = listar_datos_albums(res, True)
    elif tipo == "artista":
        dict_res = listar_datos_artistas(res, True)
    else:
        try:
            data = DB.session.query(Aparicion).filter_by(lista=dato).order_by(Aparicion.orden)
        except IntegrityError:
            DB.session.rollback()
            return "Error"
        dict_res = listar_datos_lista(res, data)

    return dict_res


def listar_datos_lista(listas, canciones=None):
    """
    Formatea una lista de reproducción como un diccionario que incluye las canciones que
    pertenecen a esa lista
    Auxiliar para transformar los datos en formato compatible con json
    El diccionario contiene:
        - ID
        - Nombre
        - Descripción
        - Imagen
        - Canciones, solo si <canciones> es distinto de None
    :param listas:
    :param canciones:
    :return:
    """
    dictionary = {"ID": listas.id, "Nombre": listas.nombre, "Desc": listas.descripcion}

    # Canciones es una lista de las canciones ordenadas según el gusto del usuario
    if canciones is not None:
        if canciones:
            dictionary["Canciones"] = listar_canciones([ass.canciones for ass in canciones])
            dictionary["Imagen"] = canciones[0].canciones.album.foto
        else:
            dictionary["Canciones"] = []
            dictionary["Imagen"] = "default"

    else:
        if not listas.canciones:
            dictionary["Imagen"] = "default"
        else:
            dictionary["Imagen"] = \
                [ass.canciones.album.foto for ass in listas.canciones if ass.orden == 0][0]

    return dictionary


def listar_datos_albums(element, canciones=False):
    """
    Formatea un album como un diccionario
    Auxiliar para transformar los datos en formato compatible con json
    El diccionario contiene:
        - Nombre
        - Descripción
        - Fecha
        - Artistas
        - Canciones, solo si <canciones> es True
    :param element:
    :param canciones:
    :return:
    """
    dictionary = {"Nombre": element.nombre,
                  "Desc": element.descripcion,
                  "fecha": element.fecha,
                  "Artistas": [artista.nombre for artista in element.artistas]}

    if canciones:
        dictionary["Canciones"] = listar_canciones(element.canciones)

    return dictionary


def listar_datos_artistas(artista, datos=False):
    """
    Formatea un artista como un diccionario
    Auxiliar para transformar los datos en formato compatible con json
    El diccionario contiene:
        - Nombre
        - Pais
        - Albumes, solo si <datos> es True
    :param artista:
    :param datos:
    :return:
    """
    dicty = {"Nombre": artista.nombre,
             "Pais": artista.pais}

    if datos:
        dicty["Albumes"] = listar_albums(artista.publicaciones)

    return dicty


def obtain_song_list(lista, cancion):
    """
    Obtiene una cancion y una lista dadas en una petición
    Devuelve error si no se pueden encontrar
    :param cancion:
    :param lista:
    :return:
    """
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


def buscar_categorias(dato):
    """
    Devuelve una lista con las canciones cuya categoria se encuentre en la lista de
    categorias presente en la petición
    :param dato:
    :return:
    """
    dato = dato.split(" ")
    datos = DB.session.query(Cancion).filter(Categoria.nombre.in_(dato), Categoria.canciones)

    return datos


def buscar_categorias_list(lista, dato):
    """
    Devuelve una lista con las canciones contenidas en la lista especificada cuya categoria se
    encuentre en la lista de categorias presente en la petición
    :param dato:
    :param lista:
    :return:
    """
    dato = dato.split(" ")
    lista = fetch_data_by_id(Lista, int(lista))
    if lista == "error":
        return "Error", False

    if lista is None:
        return "No existe la lista", False

    datos = DB.session.query(Cancion) \
        .filter(Categoria.nombre.in_(dato), Categoria.canciones)

    datos = [cancion for cancion in datos if cancion in [ass.canciones for ass in lista.canciones]]
    return datos, True


def search(dato):
    """
    Devuelve una lista de canciones cuyo nombre, autor o album se contengan la subcadena
    presente en la petición
    :param dato:
    :return:
    """
    canciones = DB.session.query(Cancion).filter(Cancion.nombre.ilike('%' + dato + '%'))
    albumes = DB.session.query(Cancion).filter(Cancion.nombre_album.ilike('%' + dato + '%'))
    artista = DB.session.query(Cancion).filter(
        Artista.nombre.ilike('%' + dato + '%'), Artista.composiciones
    )

    datos = canciones.union(albumes, artista)

    return datos


def search_in_list(lista, dato):
    """
    Devuelve una lista de canciones contenidas en la lista especificada cuyo nombre,
    autor o album se contengan la subcadena presente en la petición
    :param dato:
    :param lista:
    :return:
    """
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


def search_lista(lista):
    """
    Devuelve una lista de listas que contiene todas las listas de reproducción
    :param lista:
    :return:
    """
    datos = DB.session.query(Lista).filter(Lista.nombre.ilike('%' + lista + '%'))

    return datos


# -------------------------------------------------------------------------------------------------

@APP.route('/list', methods=['POST', 'GET'])
def list_songs():
    """
    Lista en formato json las canciones presentes en la base de datos y su información básica
    :return:
    """
    return jsonify(listar("cancion", Cancion))


@APP.route('/list_lists', methods=['POST', 'GET'])
def list_lists():
    """
    Lista en formato json las listas de reproducción y su información básica de la base de datos
    :return:
    """
    return jsonify(listar("lista", Lista))


@APP.route('/list_albums', methods=['POST', 'GET'])
def list_albums():
    """
    Lista en formato json los álbumes y su información básica de la base de datos
    :return:
    """
    return jsonify(listar("album", Album))


@APP.route('/list_artists', methods=['POST', 'GET'])
def list_artist():
    """
    Lista en formato json los artistas y su información básica de la base de datos
    :return:
    """
    return jsonify(listar("artist", Artista))


@APP.route('/list_data', methods=['POST', 'GET'])
def list_data_list():
    """
    Lista en formato json la información de una lista de reproducción incluyendo las canciones
    que la componen
    Parametros de la peticion:
        - lista
    :return:
    """
    lista = leer_datos(request, ["lista"])
    return jsonify(listar_datos("lista", Lista, lista))


@APP.route('/list_albums_data', methods=['POST', 'GET'])
def list_albums_data():
    """
    Lista en formato json la información de un álbum incluyendo las canciones que lo componen
    Parametros de la peticion:
        - album
    :return:
    """
    album = leer_datos(request, ["album"])
    return jsonify(listar_datos("album", Album, album))


@APP.route('/list_artist_data', methods=['POST', 'GET'])
def list_artist_data():
    """
    Lista en formato json la información de un artista incluyendo las canciones que lo componen
    Parametros de la peticion:
        - artista
    :return:
    """
    artista = leer_datos(request, ["artista"])
    return jsonify(listar_datos("artista", Artista, artista))


@APP.route('/create_list', methods=['POST', 'GET'])
def crear_lista():
    """
    Crea una lista de reproducción con la información proporcionada en la petición
    Parametros de la peticion:
        - lista
        - desc
    :return:
    """
    lista, desc = leer_datos(request, ["lista", "desc"])

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
    Parametros de la peticion:
        - lista
    :return:
    """
    lista = leer_datos(request, ["lista"])

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
    Parametros de la peticion:
        - lista
        - cancion
    :return:
    """
    lista, cancion = leer_datos(request, ["lista", "cancion"])

    data_cancion, data_list, msg = obtain_song_list(int(lista), int(cancion))
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
    Parametros de la peticion:
        - lista
        - cancion
    :return:
    """
    lista, cancion = leer_datos(request, ["lista", "cancion"])

    data_cancion, data_list, msg = obtain_song_list(int(lista), int(cancion))
    asociacion = [ass for ass in data_list.canciones if ass.canciones.id == data_cancion.id]
    if data_cancion is not None and data_list is not None and asociacion != []:
        try:
            DB.session.delete(asociacion[0])

            for cancion in data_list.canciones:
                if cancion.orden > asociacion[0].orden:
                    cancion.orden -= 1
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
    """
    Cambia de posición una canción dentro de una lista de reproducción
    Parametros de la peticion:
        - lista
        - before: posicion incial
        - after: posicion final
    :return:
    """
    lista, before, after = leer_datos(request, ["lista", "before", "after"])

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
def buscar_listas():
    """
    Busca una lista de reproducción en la base de datos
    Parametros de la peticion:
        - lista
    :return:
    """
    lista = leer_datos(request, ["lista"])
    listas = search_lista(lista)
    result = listar_listas(listas)
    return jsonify(result)


@APP.route('/search', methods=['POST', 'GET'])
def buscar_general():
    """
    Devuelve en formato json los resultados de la busqueda de canciones por autor, artistas y albúm
    Parametros de la peticion:
        - nombre
    :return:
    """
    dato = leer_datos(request, ["nombre"])
    res = search(dato)
    res = listar_canciones(res)
    return jsonify(res)


@APP.route('/search_in_list', methods=['POST', 'GET'])
def buscar_general_lista():
    """
    Devuelve en formato json los resultados de la busqueda de canciones por autor, artistas y
    albúm en una lista de reproducción específica
    Parametros de la peticion:
        - lista
        - nombre
    :return:
    """
    lista, nombre = leer_datos(request, ["lista", "nombre"])
    res, exito = search_in_list(lista, nombre)
    if not exito:
        return res

    res = listar_canciones(res)
    return jsonify(res)


@APP.route('/filter_category', methods=['POST', 'GET'])
def filter_category():
    """
    Devuelve una lista de canciones pertenecientes a las categorias en el filtro
    Parametros de la peticion:
        - categorias
    :return:
    """
    categorias = leer_datos(request, ["categorias"])
    canciones = buscar_categorias(categorias)
    result = listar_canciones(canciones)
    return jsonify(result)


@APP.route('/filter_category_in_list', methods=['POST', 'GET'])
def filter_category_list():
    """
    Devuelve una lista de canciones pertenecientes a las categorias en el filtro y a la lista de
    reproducción indicada
    Parametros de la peticion:
        - lista
        - categorias
    :return:
    """
    lista, categorias = leer_datos(request, ["lista", "categorias"])
    canciones, exito = buscar_categorias_list(lista, categorias)
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
def autentificacion(email, password):
    """
    Comprueba que existe el usuario especificado y que los datos de inicio de sesión son correctos
    :param password:
    :param email:
    :return:
    """
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
    Parametros de la peticion:
        - email
        - nombre
        - password
        - fecha
        - pais
    :return:
    """
    email, nombre, password, fecha, pais = leer_datos(request,
                                                      ["email", "nombre", "password", "fecha",
                                                       "pais"])

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
    Parametros de la peticion:
        - email
        - password
    :return:
    """
    email, password = leer_datos(request, ["email", "password"])
    entro, msg, user = autentificacion(email, password)

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
    Parametros de la peticion:
        - email
        - password
    :return:
    """
    email, password = leer_datos(request, ["email", "password"])
    entro, msg, _ = autentificacion(email, password)

    if entro:
        try:
            return "Success"
        except (IntegrityError, OperationalError):
            DB.session.rollback()
            return "Error"
    else:
        return msg
