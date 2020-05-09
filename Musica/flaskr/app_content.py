"""
Autor: Saúl Flores Benavente
Fecha-última_modificación: 23-04-2020
Fichero que contiene la API de la aplicación TuneIT y sus funciones auxiliares
"""
import datetime

from flask import request, jsonify
from itsdangerous import URLSafeTimedSerializer
from psycopg2.errors import UniqueViolation, InvalidDatetimeFormat
from sqlalchemy.exc import DataError, OperationalError, IntegrityError
from flaskr.db import APP, fetch_data_by_id, Lista, Cancion, DB, Categoria, Artista, leer_todo, \
    Usuario, Aparicion, Album, SeriePodcast, ListaPodcast, Solicitud, MAIL
from flask_mail import Message


# pylint: disable=no-member
# BUSQUEDA DE CANCIONES Y LISTAS NOMBRE, ARTISTA, ALBUM / CATEGORIAS
# ORDENAR CANCIONES Y LISTAS
# AÑADIR / ELIMINAR / MODIFICAR CATEGORIAS


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


def listar(tipo, tabla, usuario=None):
    """
    Lista los datos de tipo <tipo>
    Para cada tipo se llama a una funcion específica
    :param usuario:
    :param tipo:
    :param tabla:
    :return:
    """

    if usuario is not None:
        try:
            usuario = DB.session.query(Usuario).filter_by(email=usuario).first()
        except (IntegrityError, OperationalError):
            DB.session.rollback()
            return "Error"

        if usuario is None:
            return "No existe el usuario"
            dictionary = listar_listas(dato.listas)
        else:

            if tipo == "podcast":
                if usuario.listas_podcast:
                    dictionary = listar_podcast(usuario.listas_podcast[0].series_podcast)
                else:
                    dictionary = []
            elif tipo == "suscripcion":
                dictionary = listar_artistas(usuario.artistas)
            elif tipo == "amistades":
                dictionary = listar_usuarios(usuario.amistades)
            elif tipo == "peticiones_recibidas":
                dictionary = listar_peticiones(usuario.solicitudes_recibidas)
            elif tipo == "peticiones_enviadas":
                dictionary = listar_peticiones(usuario.solicitudes_enviadas)
            else:
                dictionary = listar_listas(usuario.listas)

    else:
        try:
            dato = leer_todo(tabla)
        except (IntegrityError, OperationalError):
            DB.session.rollback()
            return "Error"

        if tipo == "artista":
            dictionary = listar_artistas(dato)
        elif tipo == "album":
            dictionary = listar_albums(dato)
        elif tipo == "categoria":
            dictionary = listar_categorias(dato)
        else:
            dictionary = listar_canciones(dato)

    return dictionary


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
        dictionary["Categorias"] = [categoria.nombre for categoria in song.categorias]
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


def listar_podcast(lista):
    """
    Formatea los datos de una lista de podcast para devolverlos como una lista de ids
    Auxiliar para transformar los datos en formato compatible con json
    :param lista:
    :return:
    """
    podcast = []
    for element in lista:
        podcast.append(element.id)

    return podcast


def listar_categorias(lista):
    """
    Formatea los datos de una lista de categorias para devolverlos como una lista de nombres de
    categoria
    Auxiliar para transformar los datos en formato compatible con json
    :param lista:
    :return:
    """
    categorias = []
    for categoria in lista:
        categorias.append(categoria.nombre)

    return categorias


def listar_usuarios(lista):
    """
    Formatea los datos de una lista de podcast para devolverlos como una lista de diccionarios
    Auxiliar para transformar los datos en formato compatible con json
    :param lista:
    :return:
    """
    usuarios = []
    for usuario in lista:
        if usuario.confirmado:
            dictionary = {"Nombre": usuario.nombre, "Imagen": usuario.foto, "Email": usuario.email,
                          "Fecha": usuario.fecha_nacimiento, "Pais": usuario.pais, "Token":
                              usuario.token}
            usuarios.append(dictionary)

    return usuarios


def listar_peticiones(lista):
    peticiones = []
    for peticion in lista:
        dictionary = {"ID": peticion.id, "Emisor": listar_usuarios([peticion.notificante]),
                      "Receptor": listar_usuarios([peticion.notificado])}
        peticiones.append(dictionary)

    return peticiones


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
        elif tipo == "usuario":
            res = get_user(dato)
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
    elif tipo == "usuario":
        dict_res = listar_datos_usuario(res)
    else:
        try:
            data = DB.session.query(Aparicion).filter_by(id_lista=dato).order_by(
                Aparicion.orden).all()
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
        print(canciones)
        if canciones:
            dictionary["Canciones"] = listar_canciones([ass.cancion for ass in canciones])
            dictionary["Imagen"] = canciones[0].cancion.album.foto
        else:
            dictionary["Canciones"] = []
            dictionary["Imagen"] = "default"

    else:
        if not listas.apariciones:
            dictionary["Imagen"] = "default"
        else:
            dictionary["Imagen"] = \
                [ass.cancion.album.foto for ass in listas.apariciones if ass.orden == 0][0]

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
                  "Imagen": element.foto,
                  "fecha": element.fecha.strftime("%A, %d %b %Y"),
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


def listar_datos_usuario(usuario):
    """
    Formatea un usuario como un diccionario
    Auxiliar para transformar los datos en formato compatible con json
    El diccionario contiene:
        - Nombre
        - Contraseña
        - Fecha
        - Pais
        - Foto
    :param usuario:
    :return:
    """
    dicty = {"Nombre": usuario.nombre,
             "Password": usuario.password,
             "fecha": usuario.fecha_nacimiento.strftime("%A, %d %b %Y"),
             "Pais": usuario.pais,
             "Foto": usuario.foto}

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
    if type(dato) is str:
        dato = dato.split(" ")

    datos = DB.session.query(Cancion) \
        .filter(Categoria.nombre.in_(dato), Categoria.canciones)

    return datos


def buscar_categorias_list(lista, dato):
    """
    Devuelve una lista con las canciones contenidas en la lista especificada cuya categoria se
    encuentre en la lista de categorias presente en la petición
    :param dato:
    :param lista:
    :return:
    """
    if type(dato) is str:
        dato = dato.split(" ")

    lista = fetch_data_by_id(Lista, int(lista))
    if lista == "error":
        return "Error", False

    if lista is None:
        return "No existe la lista", False

    datos = DB.session.query(Cancion) \
        .filter(Categoria.nombre.in_(dato), Categoria.canciones)

    datos = [cancion for cancion in datos if cancion in [ass.cancion for ass in lista.apariciones]]
    return datos, True


def buscar_usuarios(nombre):
    """
    Devuelve los usuarios cuyo nombre contiene la subcadena buscada
    :param nombre:
    :return:
    """
    resultados = DB.session.query(Usuario).filter(Usuario.nombre.ilike('%' + nombre + '%'),
                                                  Usuario.confirmado).all()
    return resultados


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

    datos = [ass.cancion for ass in lista.apariciones if
             (dato in ass.cancion.nombre) or (dato in ass.cancion.nombre_album) or (
                     ass.cancion in artistas)]

    return datos, True


def search_lista(lista, usuario):
    """
    Devuelve una lista de listas que contiene todas las listas de reproducción
    :param usuario:
    :param lista:
    :return:
    """
    datos = DB.session.query(Lista).filter(Lista.nombre.ilike('%' + lista + '%'),
                                           Lista.email_usuario == usuario, Usuario.listas)

    return datos


# -------------------------------------------------------------------------------------------------

@APP.route('/list', methods=['POST', 'GET'])  # Test DONE
def list_songs():
    """
    Lista en formato json las canciones presentes en la base de datos y su información básica
    :return:
    """
    return jsonify(listar("cancion", Cancion))


@APP.route('/list_<tipo>', methods=['POST', 'GET'])  # Test DONE
def listing(tipo):
    """
    Lista en formato json la informacion basica del tipo especificado
    Parametros de la peticion:
        - usuario: usuario cuyas listas se van a mostrar
    :return:
    """
    resultado = None

    if tipo == "albums":
        resultado = listar("album", Album)

    elif tipo == "artists":
        resultado = listar("artista", Artista)

    elif tipo == "podcast":
        usuario = leer_datos(request, ["email"])
        resultado = listar("podcast", None, usuario)

    elif tipo == "categories":
        resultado = listar("categoria", Categoria)

    elif tipo == "suscriptions":
        usuario = leer_datos(request, ["email"])
        resultado = listar("suscripcion", None, usuario)

    elif tipo == "lists":  # Listas de reproduccion
        usuario = leer_datos(request, ["usuario"])
        resultado = listar("lista", None, usuario)

    elif tipo == "friends":
        usuario = leer_datos(request, ["email"])
        resultado = listar("amistades", None, usuario)

    elif tipo == "peticiones_recibidas":
        usuario = leer_datos(request, ["email"])
        resultado = listar("peticiones_recibidas", None, usuario)

    elif tipo == "peticiones_enviadas":
        usuario = leer_datos(request, ["email"])
        resultado = listar("peticiones_enviadas", None, usuario)

    if resultado is None:
        return "Url incorrecta"

    print(resultado, type(resultado))

    return jsonify(resultado)


@APP.route('/list_<tipo>_data', methods=['POST', 'GET'])  # Test DONE
def list_data(tipo):
    """
    Lista en formato json la información de una lista de reproducción incluyendo las canciones
    que la componen
    Parametros de la peticion:
        - lista
    :return:
    """
    resultado = None

    if tipo == "albums":
        album = leer_datos(request, ["album"])
        resultado = listar_datos("album", Album, album)

    elif tipo == "artist":
        artista = leer_datos(request, ["artista"])
        resultado = listar_datos("artista", Artista, artista)

    elif tipo == "lists":
        lista = leer_datos(request, ["lista"])
        resultado = listar_datos("lista", Lista, lista)

    if resultado is None:
        return "Url incorrecta"

    return jsonify(resultado)


@APP.route('/create_list', methods=['POST', 'GET'])  # Test DONE
def crear_lista():
    """
    Crea una lista de reproducción con la información proporcionada en la petición
    Parametros de la peticion:
        - lista
        - desc
        - usuario
    :return:
    """
    lista, desc, usuario = leer_datos(request, ["lista", "desc", "usuario"])

    if lista == "Favoritos":
        return "No favoritos"

    try:
        element = Lista(nombre=lista, descripcion=desc, email_usuario=usuario)
        DB.session.add(element)
        DB.session.commit()
    except (IntegrityError, OperationalError):
        return "Error"
    else:
        return "Success"


@APP.route('/delete_list', methods=['POST', 'GET'])  # Test DONE
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


@APP.route('/add_to_list', methods=['POST', 'GET'])  # Test DONE
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
            data_list.apariciones.append(
                Aparicion(cancion=data_cancion, orden=len(data_list.apariciones)))
            DB.session.commit()
        except (IntegrityError, OperationalError):
            DB.session.rollback()
            return "Error"
        else:
            return msg
    else:
        return msg


@APP.route('/delete_from_list', methods=['POST', 'GET'])  # Test DONE
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
    asociacion = [ass for ass in data_list.apariciones if ass.cancion.id == data_cancion.id]
    if data_cancion is not None and data_list is not None and asociacion != []:
        try:
            DB.session.delete(asociacion[0])

            for cancion in data_list.apariciones:
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
    apariciones = DB.session.query(Aparicion).filter_by(id_lista=lista)
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


@APP.route('/podcast_fav', methods=['POST', 'GET'])
def podcast_fav():
    """
    Añade un podcast a la lista de podcast favoritos de un usuario
    Si el podcast esta en la bd solo lo añade a la lista, si no esta, se añade el podcast a la
    base de datos
    Parametros de la petición:
        - email
        - podcast
        - nombre
    :return:
    """
    podcast, nombre, email = leer_datos(request, ["podcast", "nombre", "email"])

    serie = fetch_data_by_id(SeriePodcast, podcast)
    if serie == "error":
        return "Error"

    if serie is None:
        serie = SeriePodcast(id=podcast, nombre=nombre, capitulos=[])

    try:
        lista = DB.session.query(ListaPodcast).filter_by(email_usuario=email).first()
        if lista is not None:
            lista.series_podcast.append(serie)
        else:
            return "No existe"

        DB.session.commit()
    except (IntegrityError, OperationalError):
        return "Error"

    return "Success"


@APP.route('/delete_podcast_fav', methods=['POST', 'GET'])
def delete_podcast_fav():
    """
    Elimina un podcast de la lista de favoritos de un usuario
    Parametros de la petición:
        - email
        - podcast
    :return:
    """
    podcast, email = leer_datos(request, ["podcast", "email"])

    try:
        lista = DB.session.query(ListaPodcast).filter_by(email_usuario=email).first()
        podcast = fetch_data_by_id(SeriePodcast, podcast)

        if lista is not None and podcast != "error":
            lista.series_podcast.remove(podcast)
        elif podcast == "error":
            return "No existe el podcast"
        else:
            return "No existe lista"

        DB.session.commit()
    except (IntegrityError, OperationalError):
        return "Error"

    return "Success"


@APP.route('/podcast_is_fav', methods=['POST', 'GET'])
def podcast_is_fav():
    """
    Devuelve "true" si el podcast esta en la lista de favoritos del usuario especificado y false
    en caso contrario.
    Parametros de la petición:
        - email
        - podcast
    :return:
    """
    podcast, usuario = leer_datos(request, ["podcast", "email"])

    try:
        existe = DB.session.query(SeriePodcast).filter(SeriePodcast.id == podcast,
                                                       Usuario.listas_podcast,
                                                       ListaPodcast.series_podcast,
                                                       Usuario.email == usuario).first()
        return str(existe is not None)
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"


@APP.route('/is_fav', methods=['POST', 'GET'])
def is_fav():
    """
    Devuleve true si la cancion esta en la lista de favoritos del usuario especificado
    Parametros de la peticion:
        - cancion
        - email
    :return:
    """
    cancion, usuario = leer_datos(request, ["cancion", "email"])

    try:
        existe = DB.session.query(Lista).filter(Usuario.email == usuario,
                                                Cancion.id == cancion,
                                                Lista.nombre == "Favoritos",
                                                Usuario.listas,
                                                Lista.apariciones,
                                                Aparicion.cancion).first()

        return str(existe is not None)
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"


@APP.route('/search_list', methods=['POST', 'GET'])  # Test DONE
def buscar_listas():
    """
    Busca una lista de reproducción en la base de datos
    Parametros de la peticion:
        - lista
    :return:
    """
    lista, usuario = leer_datos(request, ["lista", "usuario"])
    listas = search_lista(lista, usuario)
    result = listar_listas(listas)
    return jsonify(result)


@APP.route('/search', methods=['POST', 'GET'])  # Test DONE
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


@APP.route('/search_in_list', methods=['POST', 'GET'])  # Test DONE
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


@APP.route('/filter_category', methods=['POST', 'GET'])  # Test DONE
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


@APP.route('/filter_category_in_list', methods=['POST', 'GET'])  # Test DONE
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


@APP.route('/test', methods=['POST', 'GET'])  # Test DONE
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
        user = get_user(email)
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return False, "Error", None

    if user is None:
        return False, "No user", None

    if not user.confirmado:
        return False, "Sin confirmar", None

    return user.password == password, "Contraseña incorrecta", user


def get_user(email):
    """
    Hace una query a la base de datos para buscar el usuario especificado
    :param email:
    :return:
    """
    user = DB.session.query(Usuario).filter_by(email=email).first()
    return user


def send_mail(email, token):
    msg = Message(
        "Confirmation Email",
        body="https://psoftware.herokuapp.com/confirm_email/" + token,
        recipients=[email],
        sender=APP.config["MAIL_DEFAULT_SENDER"]
    )
    MAIL.send(msg)


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
        DB.session.add(Lista(nombre="Favoritos", descripcion="Tus canciones favoritas",
                             email_usuario=user.email))
        DB.session.add(ListaPodcast(nombre="Favoritos",
                                    email_usuario=user.email))
        DB.session.commit()

        print("Todo bien")

        serializer = URLSafeTimedSerializer(APP.config['SECRET_KEY'])
        token = serializer.dumps(email, salt=APP.config['SECURITY_PASSWORD_SALT'])

        send_mail(email, token)

    except (IntegrityError, OperationalError) as error:
        DB.session.rollback()
        if isinstance(error.orig, UniqueViolation):
            return "Clave duplicada"

        return "Error"

    except DataError as error:
        DB.session.rollback()
        print(error)
        if isinstance(error.orig, InvalidDatetimeFormat):
            return "Fecha incorrecta"

    except Exception as error2:
        print(error2)

    return "Success"


@APP.route('/confirm_email/<token>', methods=['POST', 'GET'])
def confirmar(token):
    expiration = 3600
    serializer = URLSafeTimedSerializer(APP.config['SECRET_KEY'])

    try:
        email = serializer.loads(
            token,
            salt=APP.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )

        user = get_user(email)

        if user.confirmado:
            return "Ya estaba confirmado"
        else:
            user.confirmado = True
            DB.session.commit()

            return "Usuario " + email + " confirmado correctamente"

    except Exception as e:
        DB.session.rollback()
        print(e)
        return "Error"


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
        except (IntegrityError, OperationalError) as error:
            print(error)
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


@APP.route('/info_usuario', methods=['POST', 'GET'])
def info_usuario():
    """
    Devuelve la información básica de un usuario
    Parametros de la peticion:
        - email
    :return:
    """
    email = leer_datos(request, ["email"])

    return jsonify(listar_datos("usuario", Usuario, email))


@APP.route('/modify', methods=['POST', 'GET'])
def modificar_perfil():
    """
    Modifica los datos de un usuario a partir de los datos recibidos en la peticion.
    Parametros de la peticion:
        - email: email del usuario OBLIGATORIO
        - password: OBLIGATORIO
        - new_password: NO OBLIGATORIO
        - fecha: formato MM(/ | -)DD(/ | -)AAAA NO OBLIGATORIO
        - nombre: NO OBLIGATORIO
        - pais: NO OBLIGATORIO
    :return:
    """
    etiquetas = []
    if request.method == 'POST':
        datos = request.get_json()
        for element in datos:
            etiquetas.append(element)
    else:
        datos = request.args
        for element in request.args:
            etiquetas.append(element)

    try:
        usuario = get_user(datos["email"])

        if usuario is None:
            return "No existe usuario"

        contraseña = datos["password"]
        if usuario.password != contraseña:
            return "Contraseña incorrecta"

        if "new_password" in etiquetas:
            usuario.password = datos["new_password"]

        if "fecha" in etiquetas:
            lista = datos["fecha"].replace("-", "/").split("/", 3)
            usuario.fecha_nacimiento = datetime.date(int(lista[2]), int(lista[0]), int(lista[1]))

        if "nombre" in etiquetas:
            usuario.nombre = datos["nombre"]

        if "pais" in etiquetas:
            usuario.pais = datos["pais"]

        DB.session.commit()

        return "Success"

    except (IntegrityError, OperationalError, DataError) as error:
        DB.session.rollback()
        print(error)
        if isinstance(error.orig, InvalidDatetimeFormat):
            return "Fecha incorrecta"
        return "Error"


@APP.route('/search_users', methods=['POST', 'GET'])
def search_user():
    """
    Busca los usuarios que coinciden con la cadena introducida
    Parametros de la peticion:
        - nombre: cadena a buscar
    :return:
    """
    nombre = leer_datos(request, ['nombre'])

    resultados = buscar_usuarios(nombre)
    usuarios = listar_usuarios(resultados)

    return jsonify(usuarios)


@APP.route('/suscription', methods=['POST', 'GET'])
def suscripcion():
    """
    Se sucribe a un artista
    :return:
    """
    usuario, artista = leer_datos(request, ["email", "artista"])

    try:
        user = get_user(usuario)

        if user is None:
            return "No existe usuario"

        artist = DB.session.query(Artista).filter_by(nombre=artista).first()

        if artist is None:
            return "No existe artista"

        user.artistas.append(artist)

        DB.session.add(user)
        DB.session.commit()

        return "Success"

    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"


@APP.route('/unsuscribe', methods=['POST', 'GET'])
def desuscribir():
    """
    Se elimina la suscripcion
    :return:
    """
    usuario, artista = leer_datos(request, ["email", "artista"])

    try:
        user = get_user(usuario)

        if user is None:
            return "No existe usuario"

        artist = DB.session.query(Artista).filter_by(nombre=artista).first()

        if artist is None:
            return "No existe artista"

        user.artistas.remove(artist)

        DB.session.add(user)
        DB.session.commit()

        return "Success"

    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"


@APP.route('/solicitud_amistad', methods=['POST', 'GET'])
def solicitud_amistad():
    """
    Realiza una peticion de amistad
    :return:
    """
    emisor, receptor = leer_datos(request, ["emisor", "receptor"])

    try:
        emisor = get_user(emisor)

        if emisor is None:
            return "No existe emisor"

        receptor = get_user(receptor)

        if receptor is None:
            return "No existe receptor"

        if emisor == receptor:
            return "Mismo usuario"

        s = Solicitud(email_usuario_notificado=receptor.email,
                      email_usuario_notificante=emisor.email)
        DB.session.add(s)
        DB.session.commit()

        return "Success"
    except (IntegrityError, OperationalError):
        DB.session.rollback()
        return "Error"


@APP.route('/responder_peticion', methods=['POST', 'GET'])
def responder_peticion():
    peticion, response = leer_datos(request, ['peticion', 'respuesta'])

    try:
        peticion = DB.session.query(Solicitud).filter_by(id=int(peticion)).first()
        if peticion is None:
            return "No existe peticion"

        if response == "Acepto":
            peticion.notificado.amistades.append(peticion.notificante)
            peticion.notificante.amistades.append(peticion.notificado)

        DB.session.delete(peticion)
        DB.session.commit()
        return "Success"
    except (IntegrityError, OperationalError) as e:
        print(e)
        DB.session.rollback()
        return "Error"


@APP.route('/delete_friend', methods=['POST', 'GET'])
def eliminar_amigo():
    usuario, ya_no_amigo = leer_datos(request, ['email', 'amigo'])

    try:
        usuario = get_user(usuario)
        if usuario is None:
            return "No existe usuario"

        ya_no_amigo = get_user(ya_no_amigo)
        if ya_no_amigo is None:
            return "No existe amigo"

        usuario.amistades.remove(ya_no_amigo)
        ya_no_amigo.amistades.remove(usuario)

        DB.session.commit()
        return "Success"
    except (IntegrityError, OperationalError) as e:
        print(e)
        DB.session.rollback()
        return "Error"


@APP.route('/set_last_song', methods=['POST', 'GET'])
def set_ultima_cancion():
    usuario, cancion, segundo = leer_datos(request, ["email",
                                                     "cancion",
                                                     "segundo"])

    try:
        usuario = get_user(usuario)
        if usuario is None:
            return "No existe usuario"

        usuario.id_ultima_cancion = int(cancion)
        usuario.segundo_ultima_cancion = int(segundo)
        DB.session.commit()

        return "Success"

    except (IntegrityError, OperationalError) as e:
        print(e)
        DB.session.rollback()
        return "Error"


@APP.route('/get_last_song', methods=['POST', 'GET'])
def get_ultima_cancion():
    usuario = leer_datos(request, ["email"])

    try:
        usuario = get_user(usuario)
        if usuario is None:
            return "No existe usuario"

        if usuario.ultima_cancion is None:
            return jsonify({"Cancion": None,
                            "Segundo": usuario.segundo_ultima_cancion})

        return jsonify({"Cancion": listar_canciones([usuario.ultima_cancion]),
                        "Segundo": usuario.segundo_ultima_cancion})

    except (IntegrityError, OperationalError) as e:
        print(e)
        DB.session.rollback()
        return "Error"


@APP.route('/set_token', methods=['POST', 'GET'])
def set_token():
    usuario, token = leer_datos(request, ["email", "token"])

    try:
        usuario = get_user(usuario)
        if usuario is None:
            return "No existe usuario"

        usuario.token = token
        DB.session.commit()

        return "Success"

    except (IntegrityError, OperationalError) as e:
        print(e)
        DB.session.rollback()
        return "Error"


@APP.route('/get_token', methods=['POST', 'GET'])
def get_token():
    usuario, token = leer_datos(request, ["email", "token"])

    try:
        usuario = get_user(usuario)
        if usuario is None:
            return "No existe usuario"

        return jsonify(usuario.token)

    except (IntegrityError, OperationalError) as e:
        print(e)
        DB.session.rollback()
        return "Error"
