"""
Módulo INIT del paquete flaskr
Define la función que crea la aplicación que define este paquete
"""

from flask import Flask
from flask_cors import CORS


def create_app():
    """
    Crea la aplicación Flask que se va a usar
    La hace compatible con CORS y establece la clave secreta
    Configuraciones iniciales en esta funciñon
    :return:
    """
    app_created = Flask(__name__)
    CORS(app_created)
    app_created.secret_key = 'development'

    return app_created
