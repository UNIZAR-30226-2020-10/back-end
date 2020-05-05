"""
Módulo INIT del paquete flaskr
Define la función que crea la aplicación que define este paquete
"""

from flask import Flask
from flask_cors import CORS
from flask_mail import Mail


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
    app_created.config['SECURITY_PASSWORD_SALT'] = 'sa9ksa9823fs98g'

    # Mail
    app_created.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app_created.config['MAIL_PORT'] = 587
    app_created.config['MAIL_USE_TLS'] = True
    app_created.config['MAIL_USERNAME'] = 'tuneit.music@gmail.com'  # enter your email here
    app_created.config['MAIL_DEFAULT_SENDER'] = 'tuneit.music@gmail.com'  # enter your email here
    app_created.config['MAIL_PASSWORD'] = 'tuneit_password1'

    mail = Mail(app_created)

    return app_created, mail
