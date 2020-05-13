import json
import unittest
import pycurl as p
import io

from flaskr.db import *


def curl(url):
    c = p.Curl()
    res = io.BytesIO()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, res)
    c.perform()
    status = c.getinfo(c.RESPONSE_CODE)

    return status, res.getvalue().decode('utf-8')


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False, None
    return True, json_object


def insertar_album(nombre_album):
    album = Album(nombre=nombre_album, descripcion="Album1", fecha="1999-12-20", foto="Foto1")

    DB.session.add(album)
    DB.session.commit()

    return album


def insertar_cancion(nombre_cancion, nombre_album):
    cancion = Cancion(nombre=nombre_cancion, path="url", duracion=123, nombre_album=nombre_album)

    DB.session.add(cancion)
    DB.session.commit()

    return cancion


def insertar_artista(nombre_artista):
    artista = Artista(nombre=nombre_artista, fecha_nacimiento="1999-06-24", pais="España",
                      alias="Perico")
    DB.session.add(artista)
    DB.session.commit()

    return artista


def insertar_usuario():
    usuario = Usuario(email="prueba@gmail.com", nombre="PRUEBA", password="12345")
    DB.session.add(usuario)
    DB.session.commit()

    return usuario


def insert_lista_test():
    usuario = insertar_usuario()
    lista = Lista(nombre="TEST_LIST", descripcion="TEST_DESC", email_usuario=usuario.email)
    DB.session.add(lista)
    DB.session.commit()

    return lista, usuario


def insert_categoria():
    categoria = Categoria(nombre='Rock', descripcion='Categoria Rock')
    DB.session.add(categoria)
    DB.session.commit()

    return categoria


def insertar_cancion_album(nombre_cancion, nombre_album):
    album = insertar_album(nombre_album)
    cancion = insertar_cancion(nombre_cancion, album.nombre)

    return cancion, album


def insertar_cancion_album_lista(nombre_cancion, nombre_album):
    album = insertar_album(nombre_album)
    cancion = insertar_cancion(nombre_cancion, album.nombre)
    lista, usuario = insert_lista_test()

    aparicion = Aparicion(cancion=cancion, orden=len(lista.apariciones))
    lista.apariciones.append(aparicion)
    DB.session.add(lista)
    DB.session.commit()

    return cancion, album, lista, aparicion, usuario


def insertar_cancion_album_artista(nombre_cancion, nombre_album, nombre_artista):
    album = insertar_album(nombre_album)
    cancion = insertar_cancion(nombre_cancion, album.nombre)
    artista = insertar_artista(nombre_artista)

    artista.composiciones.append(cancion)
    DB.session.add(artista)
    DB.session.commit()

    return cancion, album, artista


def insertar_cancion_album_artista_lista(nombre_cancion, nombre_album, nombre_artista):
    cancion, album, artista = insertar_cancion_album_artista(nombre_cancion, nombre_album,
                                                             nombre_artista)
    lista, usuario = insert_lista_test()

    aparicion = Aparicion(cancion=cancion, orden=len(lista.apariciones))
    lista.apariciones.append(aparicion)
    DB.session.add(lista)
    DB.session.commit()

    return cancion, album, artista, lista, aparicion, usuario


def comprobar_json(obj, peticion, res_esperado):
    status, res = curl(peticion)
    obj.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

    correcto, data = is_json(res)
    obj.assertEqual(correcto, True, "El contenido devuelto no tiene el formato correcto")

    obj.assertEqual(data, res_esperado)


def buscar_en_lista(tipo, obj):
    cancion, album, lista, aparicionl, usuario = insertar_cancion_album_lista("Song1", "Album1")

    if tipo == "cancion":
        tipo = cancion
    else:
        tipo = album

    comprobar_json(obj,
                   'http://localhost:5000/search_in_list?nombre=%s&lista=%s'
                   % (tipo.nombre, lista.id),
                   get_single_song_esperado(cancion))


def get_single_song_esperado(cancion):
    return [{"ID": cancion.id, "Nombre": cancion.nombre,
             "Artistas": [artista.nombre for artista in cancion.artistas],
             "URL": cancion.path, "Imagen": cancion.album.foto,
             "Album": cancion.nombre_album,
             "Categorias": [categoria.nombre for categoria in cancion.categorias]}]


def get_single_album_esperado(album):

    return [{"Nombre": album.nombre,
             "Artistas": [artista.nombre for artista in album.artistas],
             "fecha": album.fecha.strftime("%A, %d %b %Y"),
             "Desc": album.descripcion, "Imagen": album.foto}]


def get_single_artist_esperado(artista):
    return [{"Nombre": artista.nombre,
             "Pais": artista.pais}]


class MyTestCase(unittest.TestCase):
    """
    Tests unitarios de la aplicacion TuneIt
    Se prueban las distintas peticiones para comprobar su fucnionamiento
    Test pendientes en comentarios
    """

    @classmethod
    def setUp(cls):
        DB.session.close()
        DB.drop_all()
        DB.create_all()

    def test_server(self):
        status, res = curl('http://localhost:5000/test?test=Success')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertEqual(res, "Success", "El mensaje no coindice")

    def test_list(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")

        comprobar_json(self, 'http://localhost:5000/list', get_single_song_esperado(cancion))

        # delete([cancion, album])

    def test_list_lists(self):
        lista, usuario = insert_lista_test()

        res_esperado = [{"ID": lista.id, "Nombre": lista.nombre, "Imagen": "default",
                         "Desc": lista.descripcion}]
        comprobar_json(self, 'http://localhost:5000/list_lists?email=%s' %
                       usuario.email, res_esperado)

    def test_list_albums(self):
        album = insertar_album("Album")

        res_esperado = get_single_album_esperado(album)
        comprobar_json(self, 'http://localhost:5000/list_albums', res_esperado)

    def test_list_artists(self):
        artista = insertar_artista("Artista")

        res_esperado = get_single_artist_esperado(artista)
        comprobar_json(self, 'http://localhost:5000/list_artists', res_esperado)

    def test_list_data(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        lista, usuario = insert_lista_test()
        aparicion = Aparicion(cancion=cancion, orden=len(lista.apariciones))
        lista.apariciones.append(aparicion)
        DB.session.add(lista)
        DB.session.commit()

        res_esperado = {"ID": lista.id, "Nombre": lista.nombre,
                        "Imagen": lista.apariciones[0].cancion.album.foto,
                        "Desc": lista.descripcion,
                        "Canciones": get_single_song_esperado(cancion)}
        comprobar_json(self, 'http://localhost:5000/list_lists_data?lista=%s' % lista.id,
                       res_esperado)

    # Test list_albums_data

    # Test list_artists_data

    def test_crear_lista(self):
        usuario = insertar_usuario()

        status, res = curl(
            'http://localhost:5000/create_list?lista=TEST_LIST&desc=TEST_DESC&usuario=%s' %
            usuario.email)
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertNotEqual(res, "ERROR", "No se ha creado la lista")

    def test_eliminar_lista_con_datos(self):
        cancion, album, lista, aparicion, usuario = insertar_cancion_album_lista("Song1",
                                                                                 "Album1")

        status, res = curl('http://localhost:5000/delete_list?lista=%d' % lista.id)
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertNotEqual(res, "ERROR", "No se ha eliminado la lista")

    def test_eliminar_lista(self):
        lista, usuario = insert_lista_test()

        status, res = curl('http://localhost:5000/delete_list?lista=%d' % lista.id)
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertNotEqual(res, "ERROR", "No se ha eliminado la lista")

    def test_add_to_list(self):
        lista, usuario = insert_lista_test()
        cancion = Cancion(nombre='Test_song', duracion=123, path='test_path')
        DB.session.add(cancion)
        DB.session.commit()

        status, res = curl(
            'http://localhost:5000/add_to_list?cancion=%d&lista=%d' % (cancion.id, lista.id))
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertEqual(res, "Success", "No se ha podido añadir")

    def test_delete_from_list(self):
        cancion, album, lista, aparicion, usuario = insertar_cancion_album_lista("Song1", "Album1")
        status, res = curl('http://localhost:5000/delete_from_list?cancion=%d&lista=%d' %
                           (cancion.id,
                            lista.id))

        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertEqual(res, "Success", "No se ha podido añadir")

    # Test reorder

    # Test podcast_fav

    # Test delete_podcast_fav

    def test_search_song(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")

        comprobar_json(self, 'http://localhost:5000/search?nombre=%s' % cancion.nombre,
                       {'Albums': [],
                        'Canciones': get_single_song_esperado(cancion),
                        'Artistas': []})

    def test_search_list(self):
        lista, usuario = insert_lista_test()

        res_esperado = [{"ID": lista.id, "Nombre": lista.nombre, "Imagen": "default",
                         "Desc": lista.descripcion}]
        comprobar_json(self, 'http://localhost:5000/search_list?lista=%s&usuario=%s'
                       % (lista.nombre, usuario.email), res_esperado)

    def test_search_song_by_album(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")

        comprobar_json(self, 'http://localhost:5000/search?nombre=%s' % album.nombre,
                       {'Albums': get_single_album_esperado(album),
                        'Canciones': get_single_song_esperado(cancion),
                        'Artistas': []})

    def test_search_song_by_artist(self):
        cancion, album, artista = insertar_cancion_album_artista("Song1", "Album1", "Artista1")

        comprobar_json(self, 'http://localhost:5000/search?nombre=%s' % artista.nombre,
                       {'Albums': [],
                        'Canciones': get_single_song_esperado(cancion),
                        'Artistas': get_single_artist_esperado(artista)})

    def test_search_song_on_list(self):
        buscar_en_lista('cancion', self)

    def test_search_song_by_album_on_list(self):
        buscar_en_lista('album', self)

    def test_search_song_by_artist_on_list(self):
        cancion, album, artista, lista, aparicion, usuario = \
            insertar_cancion_album_artista_lista(
                "Song1",
                "Album1",
                "Artista1")

        comprobar_json(self, 'http://localhost:5000/search_in_list?nombre=%s&lista=%s'
                       % (artista.nombre, lista.id), get_single_song_esperado(cancion))

    def test_filter_categorias(self):
        categoria = insert_categoria()
        cancion, album = insertar_cancion_album("Song1", "Album1")

        categoria.canciones.append(cancion)
        DB.session.commit()

        comprobar_json(self, 'http://localhost:5000/filter_category?categorias=%s' %
                       categoria.nombre, get_single_song_esperado(cancion))

    def test_filter_categorias_lista(self):
        categoria = insert_categoria()
        cancion, album, lista, aparicion, usuario = insertar_cancion_album_lista("Song1", "Album1")

        categoria.canciones.append(cancion)
        DB.session.commit()

        comprobar_json(self, 'http://localhost:5000/filter_category_in_list?categorias=%s&lista=%s'
                       % (categoria.nombre, lista.id), get_single_song_esperado(cancion))

    # Test inicio_sesion

    # Test registro

    # Test eliminar usuario

    # Test info_usuario

    # Test modify


if __name__ == '__main__':
    unittest.main()
