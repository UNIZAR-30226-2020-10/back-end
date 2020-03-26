from flask import Flask


def create_app():
    app_created = Flask(__name__)
    app_created.secret_key = 'development'

    return app_created
