from flask import Flask
from flask_cors import CORS


def create_app():
    app_created = Flask(__name__)
    CORS(app_created)
    app_created.secret_key = 'development'

    return app_created
