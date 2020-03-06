import flask as f

from create_app import app
from db import db


@app.route('/')
def index():
    return f.render_template('index.html')


def generate():
    yield 'static/musica/file_example_MP3_1MG.mp3'


@app.route('/', methods=['POST'])
def reproduce():
    return f.render_template('index.html', response=generate())
