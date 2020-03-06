from create_app import app
from db import db


@app.route('/')
def hello_world():
    return 'Hello World!'
