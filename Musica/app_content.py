import flask as f
import os


from db import *

@app.route('/')
def index():
    return f.render_template('index.html')


def generate():
    yield 'static/musica/file_example_MP3_1MG.mp3'


@app.route('/', methods=['POST'])
def reproduce():
    return f.render_template('index.html', response=generate())


@app.route('/add', methods=['POST'])
def insert():
    name = f.request.form['name']+'.mp3'
    if name in os.listdir('./static/musica'):
        song = Cancion('/static/musica/'+name)
        error = add_song(song)
        if error:
            f.flash("Already exists", 'error')
        else:
            f.flash("Add successful", 'info')
        return f.redirect('/')
    else:
        f.flash("Add error", 'error')
        return f.redirect('/')

