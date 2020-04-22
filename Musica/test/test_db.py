from flaskr.db import *

usuario = Usuario(nombre="User", email="a@hotmail.com", password="12345")
lista = Lista(descripcion="Una lista", nombre="Lista", email_usuario=usuario.email)

DB.session.add(usuario)
DB.session.add(lista)
DB.session.commit()
