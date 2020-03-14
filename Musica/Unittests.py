import json
import unittest
import pycurl as p
import io
from app import app
from db import *


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
        return False
    return True


class MyTestCase(unittest.TestCase):

    def test_server(self):
        status, res = curl('http://localhost:5000/test?test=Success')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertEqual(res, "Success", "El mensaje no coindice")

    def test_list(self):
        status, res = curl('http://localhost:5000/list')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        correcto = is_json(res)
        self.assertEqual(correcto, True, "El contenido devuelto no tiene el formato correcto")

    def test_list_lists(self):
        status, res = curl('http://localhost:5000/list_lists')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        correcto = is_json(res)
        self.assertEqual(correcto, True, "El contenido devuelto no tiene el formato correcto")

    def test_crear_lista(self):
        status, res = curl('http://localhost:5000/create_list?list=TEST_LIST&desc=TEST_DESC')
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertNotEqual(res, "ERROR", "No se ha creado la lista")

        '''elements = db.session.query(Lista).filter_by(nombre='TEST_LIST').all()
        db.session.delete(elements[0])
        db.session.commit()'''

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

    # Test complementarios a implementar:
    #   Crear una lista de reproduccion - Done
    #   Añadir una cancion - Done
    #   Listar datos de una cancion
    #   Eliminar cancion de la lista - Done
    #   Eliminar lista - Done


if __name__ == '__main__':
    unittest.main()