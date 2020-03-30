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
    except ValueError as e:
        return False, None
    return True, json_object


def insertar_cancion(nombre_cancion, nombre_album):
    cancion = Cancion(nombre=nombre_cancion, path="url", duracion=123, nombre_album=nombre_album)

    db.session.add(cancion)
    db.session.commit()

    return cancion


def insertar_album(nombre_album):
    album = db.session.query(Album).filter_by(nombre=nombre_album).all()
    if album:
        delete_album(album[0])

    album = Album(nombre=nombre_album, descripcion="Album1", fecha="1999-12-20", foto="Foto1")

    db.session.add(album)
    db.session.commit()

    return album


def insertar_cancion_album(nombre_cancion, nombre_album):
    album = insertar_album(nombre_album)
    cancion = insertar_cancion(nombre_cancion, album.nombre)

    return cancion, album


def insert_lista_test():
    lista = Lista(nombre="TEST_LIST", descripcion="TEST_DESC")
    db.session.add(lista)
    db.session.commit()

    return lista


def delete_lista_test(lista):
    db.session.delete(lista)
    db.session.commit()


def delete_cancion(cancion):
    db.session.delete(cancion)
    db.session.commit()


def delete_album(album):
    db.session.delete(album)
    db.session.commit()


def delete_cancion_album(cancion, album):
    delete_album(album)
    delete_cancion(cancion)


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
        db.session.add(lista)
        db.session.commit()

        status, res = curl('http://localhost:5000/list_data?list=%s' % lista.id)

        res_esperado = {"ID": lista.id, "Nombre": lista.nombre, "Imagen": lista.canciones[0].album.foto,
                        "Desc": lista.descripcion,
                        "Canciones": get_single_song_esperado(cancion)}
        comprobar_json(self, status, res, res_esperado)

        delete_lista_test(lista)
        delete_cancion_album(cancion, album)

    def test_crear_lista(self):
        status, res = curl('http://localhost:5000/create_list?list=TEST_LIST&desc=TEST_DESC')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertNotEqual(res, "ERROR", "No se ha creado la lista")

        elements = db.session.query(Lista).filter_by(nombre='TEST_LIST').all()
        db.session.delete(elements[0])
        db.session.commit()

    def test_eliminar_lista(self):
        lista = Lista(nombre="Test_lista_delete", descripcion="Test_desc_delete")
        db.session.add(lista)
        db.session.commit()

        status, res = curl('http://localhost:5000/delete_list?list=%d' % lista.id)
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertNotEqual(res, "ERROR", "No se ha eliminado la lista")

    def test_add_to_list(self):
        lista = Lista(nombre="Test_lista", descripcion="Test_desc")
        cancion = Cancion(nombre='Test_song', duracion=123, path='test_path')
        db.session.add(lista)
        db.session.add(cancion)
        db.session.commit()

        status, res = curl('http://localhost:5000/add_to_list?cancion=%d&list=%d' % (cancion.id, lista.id))
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertEqual(res, "Success", "No se ha podido añadir")

        db.session.delete(lista)
        db.session.delete(cancion)
        db.session.commit()

    def test_search_song(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        cancion2 = insertar_cancion(cancion.nombre, album.nombre)
        status, res = curl('http://localhost:5000/search_song?Nombre=%s' % cancion.nombre)

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
        status, res = curl('http://localhost:5000/search_list?Nombre=%s' % lista.nombre)

        res_esperado = [{"ID": lista.id, "Nombre": lista.nombre, "Imagen": "default",
                         "Desc": lista.descripcion},
                        {"ID": lista2.id, "Nombre": lista2.nombre, "Imagen": "default",
                         "Desc": lista2.descripcion}]

        comprobar_json(self, status, res, res_esperado)

        delete_lista_test(lista)
        delete_lista_test(lista2)

    def test_search_song_by_album(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        status, res = curl('http://localhost:5000/search_song_by_album?Nombre=%s' % album.nombre)

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_cancion_album(cancion, album)

    def test_search_song_by_artist(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        artista = Artista(nombre="Artista1", fecha_nacimiento="1999-06-24", pais="España",
                          alias="Perico")
        artista.composiciones.append(cancion)
        db.session.add(artista)
        db.session.commit()

        status, res = curl('http://localhost:5000/search_song_by_artist?Nombre=%s' % artista.nombre)

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        db.session.delete(artista)
        delete_cancion_album(cancion, album)

    def test_search_song_on_list(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        lista = insert_lista_test()

        lista.canciones.append(cancion)
        db.session.add(lista)
        db.session.commit()

        status, res = curl('http://localhost:5000/search_song_list?Nombre=%s&Lista=%s' % (cancion.nombre, lista.id))

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_lista_test(lista)
        delete_cancion_album(cancion, album)

    def test_search_song_by_album_on_list(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        lista = insert_lista_test()

        lista.canciones.append(cancion)
        db.session.add(lista)
        db.session.commit()

        status, res = curl('http://localhost:5000/search_song_by_album_list?Nombre=%s&Lista=%s'
                           % (album.nombre, lista.id))

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        delete_lista_test(lista)
        delete_cancion_album(cancion, album)

    def test_search_song_by_artist_on_list(self):
        cancion, album = insertar_cancion_album("Song1", "Album1")
        artista = Artista(nombre="Artista1", fecha_nacimiento="1999-06-24", pais="España",
                          alias="Perico")
        artista.composiciones.append(cancion)
        lista = insert_lista_test()
        lista.canciones.append(cancion)
        db.session.add(artista)
        db.session.add(lista)
        db.session.commit()

        status, res = curl('http://localhost:5000/search_song_by_artist_list?Nombre=%s&Lista=%s'
                           % (artista.nombre, lista.id))

        comprobar_json(self, status, res, get_single_song_esperado(cancion))

        db.session.delete(artista)
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
    db.drop_all()
    db.create_all()
    unittest.main()
