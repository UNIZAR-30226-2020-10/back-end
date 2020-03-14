import json
import unittest
import pycurl as p
import io


class MyTestCase(unittest.TestCase):
    def test_server(self):
        c = p.Curl()
        res = io.BytesIO()
        c.setopt(c.URL, 'http://localhost:5000/test?test=Success')
        c.setopt(c.WRITEDATA, res)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        self.assertEqual(res.getvalue().decode('utf-8'), "Success", "El mensaje no coindice")

    def test_list(self):
        c = p.Curl()
        res = io.BytesIO()
        c.setopt(c.URL, 'http://localhost:5000/list')
        c.setopt(c.WRITEDATA, res)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        correcto = is_json(res.getvalue().decode('utf-8'))

        self.assertEqual(correcto, True, "El contenido devuelto no tiene el formato correcto")

    def test_list_lists(self):
        c = p.Curl()
        res = io.BytesIO()
        c.setopt(c.URL, 'http://localhost:5000/list_lists')
        c.setopt(c.WRITEDATA, res)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        self.assertRegex(str(status), '2[0-9][0-9]', "Peticion no exitosa")

        correcto = is_json(res.getvalue().decode('utf-8'))

        self.assertEqual(correcto, True, "El contenido devuelto no tiene el formato correcto")

    # Test complementarios a implementar:
    #   Crear una lista de reproduccion
    #   Añadir una cancion
    #   Listar datos de una cancion
    #   Eliminar cancion de la lista
    #   Eliminar lista


if __name__ == '__main__':
    unittest.main()


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True
