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


def insertar_cancion(nombre_cancion, nombre_album):
    cancion = Cancion(nombre=nombre_cancion, path="url", duracion=123, nombre_album=nombre_album)

    DB.session.add(cancion)
    DB.session.commit()

    return cancion


def insertar_album(nombre_album):
    album = DB.session.query(Album).filter_by(nombre=nombre_album).all()
    if album:
        delete_album(album[0])

    album = Album(nombre=nombre_album, descripcion="Album1", fecha="1999-12-20", foto="Foto1")

    DB.session.add(album)
    DB.session.commit()

    return album


def insertar_artista(nombre_artista):
    artista = Artista(nombre=nombre_artista, fecha_nacimiento="1999-06-24", pais="España",
                      alias="Perico")
    DB.session.add(artista)

    return artista


def insertar_cancion_album(nombre_cancion, nombre_album):
    album = insertar_album(nombre_album)
    cancion = insertar_cancion(nombre_cancion, album.nombre)

    return cancion, album


def insertar_cancion_album_lista(nombre_cancion, nombre_album):
    album = insertar_album(nombre_album)
    cancion = insertar_cancion(nombre_cancion, album.nombre)
    lista = insert_lista_test()

    lista.canciones.append(cancion)
    DB.session.add(lista)
    DB.session.commit()

    return cancion, album, lista


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
    lista = insert_lista_test()

    lista.canciones.append(cancion)
    DB.session.add(lista)
    DB.session.commit()

    return cancion, album, artista, lista


def insert_lista_test():
    lista = Lista(nombre="TEST_LIST", descripcion="TEST_DESC")
    DB.session.add(lista)
    DB.session.commit()

    return lista


def insert_categoria():
    categoria = Categoria(nombre='Rock', descripcion='Categoria Rock')
    DB.session.add(categoria)
    DB.session.commit()

    return categoria


def delete_lista_test(lista):
    DB.session.delete(lista)
    DB.session.commit()


def delete_cancion(cancion):
    DB.session.delete(cancion)
    DB.session.commit()


def delete_album(album):
    DB.session.delete(album)
    DB.session.commit()


def delete_cancion_album(cancion, album):
    delete_album(album)
    delete_cancion(cancion)


def delete_categoria(cat):
    DB.session.delete(cat)
    DB.session.commit()


def comprobar_json(obj, status, res, res_esperado):
    obj.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

    correcto, data = is_json(res)
    obj.assertEqual(correcto, True, "El contenido devuelto no tiene el formato correcto")

    obj.assertEqual(data, res_esperado)


def get_single_song_esperado(cancion):
    return [{"ID": cancion.id, "Nombre": cancion.nombre,
             "Artistas": [artista.nombre for artista in cancion.artistas],
             "URL": cancion.path, "Imagen": cancion.album.foto,
             "Album": cancion.nombre_album}]


class MyTestCase(unittest.TestCase):

    def test_server(self):
        status, res = curl('http://localhost:5000/test?test=Success')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertEqual(res, "Success", "El mensaje no coindice")

    def test_list(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")

        status, res = curl('http://localhost:5000/list')

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_cancion_album(cancion, album)

    def test_list_lists(self):
        lista = insert_lista_test()

        status, res = curl('http://localhost:5000/list_lists')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        correcto, data = is_json(res)
        self.assertEqual(correcto, True, "El contenido devuelto no tiene el formato correcto")

        res_esperado = [{"ID": lista.id, "Nombre": lista.nombre, "Imagen": "default",
                         "Desc": lista.descripcion}]
        self.assertEqual(data, res_esperado)

        delete_lista_test(lista)

    def test_list_data(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        lista = insert_lista_test()
        lista.canciones.append(cancion)
        DB.session.add(lista)
        DB.session.commit()

        status, res = curl('http://localhost:5000/list_data?list=%s' % lista.id)

        res_esperado = {"ID": lista.id, "Nombre": lista.nombre,
                        "Imagen": lista.canciones[0].album.foto,
                        "Desc": lista.descripcion,
                        "Canciones": get_single_song_esperado(cancion)}
        comprobar_json(self, status, res, res_esperado)

        delete_lista_test(lista)
        delete_cancion_album(cancion, album)

    def test_crear_lista(self):
        status, res = curl('http://localhost:5000/create_list?list=TEST_LIST&desc=TEST_DESC')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertNotEqual(res, "ERROR", "No se ha creado la lista")

        elements = DB.session.query(Lista).filter_by(nombre='TEST_LIST').all()
        DB.session.delete(elements[0])
        DB.session.commit()

    def test_eliminar_lista(self):
        lista = Lista(nombre="Test_lista_delete", descripcion="Test_desc_delete")
        DB.session.add(lista)
        DB.session.commit()

        status, res = curl('http://localhost:5000/delete_list?list=%d' % lista.id)
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertNotEqual(res, "ERROR", "No se ha eliminado la lista")

    def test_add_to_list(self):
        lista = Lista(nombre="Test_lista", descripcion="Test_desc")
        cancion = Cancion(nombre='Test_song', duracion=123, path='test_path')
        DB.session.add(lista)
        DB.session.add(cancion)
        DB.session.commit()

        status, res = curl(
            'http://localhost:5000/add_to_list?cancion=%d&list=%d' % (cancion.id, lista.id))
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertEqual(res, "Success", "No se ha podido añadir")

        DB.session.delete(lista)
        DB.session.delete(cancion)
        DB.session.commit()

    def test_search_song(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        cancion2 = insertar_cancion(cancion.nombre, album.nombre)
        status, res = curl('http://localhost:5000/search?Nombre=%s' % cancion.nombre)

        res_esperado = [{"ID": cancion.id, "Nombre": cancion.nombre, "Artistas": cancion.artistas,
                         "URL": cancion.path, "Imagen": cancion.album.foto,
                         "Album": cancion.nombre_album},
                        {"ID": cancion2.id, "Nombre": cancion2.nombre, "Artistas": cancion2.artistas,
                         "URL": cancion2.path, "Imagen": cancion2.album.foto,
                         "Album": cancion2.nombre_album}]

        comprobar_json(self, status, res, res_esperado)

        delete_cancion(cancion2)
        delete_cancion_album(cancion, album)

    def test_search_list(self):
        lista = insert_lista_test()
        lista2 = insert_lista_test()
        status, res = curl('http://localhost:5000/search_list?Lista=%s' % lista.nombre)

        res_esperado = [{"ID": lista.id, "Nombre": lista.nombre, "Imagen": "default",
                         "Desc": lista.descripcion},
                        {"ID": lista2.id, "Nombre": lista2.nombre, "Imagen": "default",
                         "Desc": lista2.descripcion}]

        comprobar_json(self, status, res, res_esperado)

        delete_lista_test(lista)
        delete_lista_test(lista2)

    def test_search_song_by_album(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        status, res = curl('http://localhost:5000/search?Nombre=%s' % album.nombre)

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_cancion_album(cancion, album)

    def test_search_song_by_artist(self):
        cancion, album, artista = insertar_cancion_album_artista("Song1", "Album1", "Artista1")

        status, res = curl('http://localhost:5000/search?Nombre=%s' % artista.nombre)

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        DB.session.delete(artista)
        delete_cancion_album(cancion, album)

    def test_search_song_on_list(self):
        cancion, album, lista = insertar_cancion_album_lista("Song1", "Album1")

        status, res = curl('http://localhost:5000/search_in_list?Nombre=%s&Lista=%s' % (cancion.nombre, lista.id))

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_lista_test(lista)
        delete_cancion_album(cancion, album)

    def test_search_song_by_album_on_list(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        lista = insert_lista_test()

        lista.canciones.append(cancion)
        DB.session.add(lista)
        DB.session.commit()

        status, res = curl('http://localhost:5000/search_in_list?Nombre=%s&Lista=%s'
                           % (album.nombre, lista.id))

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_lista_test(lista)
        delete_cancion_album(cancion, album)

    def test_search_song_by_artist_on_list(self):
        cancion, album, artista, lista = insertar_cancion_album_artista_lista("Song1", "Album1", "Artista1")

        status, res = curl('http://localhost:5000/search_in_list?Nombre=%s&Lista=%s'
                           % (artista.nombre, lista.id))

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        DB.session.delete(artista)
        delete_lista_test(lista)
        delete_cancion_album(cancion, album)

    def test_filter_categorias(self):
        categoria = insert_categoria()
        cancion, album = insertar_cancion_album("Song1", "Album1")

        categoria.canciones.append(cancion)
        DB.session.commit()

        status, res = curl('http://localhost:5000/filter_category?Categorias=%s' % categoria.nombre)

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_categoria(categoria)
        delete_cancion_album(cancion, album)

    def test_filter_categorias_lista(self):
        categoria = insert_categoria()
        cancion, album, lista = insertar_cancion_album_lista("Song1", "Album1")

        categoria.canciones.append(cancion)
        DB.session.commit()

        status, res = curl('http://localhost:5000/filter_category_in_list?Categorias=%s&Lista=%s' %
                           (categoria.nombre, lista.id))

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_categoria(categoria)
        delete_lista_test(lista)
        delete_cancion_album(cancion, album)

    # Test complementarios a implementar:
    #   Crear una lista de reproduccion - Done
    #   Añadir una cancion - Done
    #   Listar datos de una cancion
    #   Eliminar cancion de la lista - Done
    #   Eliminar lista - Done
    #   Listar Canciones de una lista
    #   Busquedas


if __name__ == '__main__':
    DB.drop_all()
    DB.create_all()
    unittest.main()
