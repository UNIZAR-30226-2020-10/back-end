from flask_sqlalchemy import SQLAlchemy
from app import app

POSTGRES_URL = "127.0.0.1:5432"
POSTGRES_USER = "admin"
POSTGRES_PW = "admin"
POSTGRES_DB = "test"

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://{user}:{pw}@{url}/{db}'. \
        format(user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, db=POSTGRES_DB)

db = SQLAlchemy(app)

categorizacion = db.Table('categorizacion',
                          db.Column('categoria', db.String(20), db.ForeignKey('categoria.nombre')),
                          db.Column('cancion', db.String(20), db.ForeignKey('cancion.id'))
                          )


class Categoria(db.Model):
    nombre = db.Column(db.String(20), primary_key=True)
    descripcion = db.Column(db.String(100))
    canciones = db.relationship('Cancion', secondary=categorizacion, backref=db.backref('categorias', lazy='dynamic'))


class Artista(db.Model):
    nombre = db.Column(db.String(20), primary_key=True)
    fecha_nacimiento = db.Column(db.Date)
    pais = db.Column(db.String(40))
    alias = db.Column(db.String(20))


class Album(db.Model):
    nombre = db.Column(db.String(20), primary_key=True)
    descripcion = db.Column(db.String(100))
    fecha = db.Column(db.Date)


class Lista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(100))


class Usuario(db.Model):
    email = db.Column(db.String(25), primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String, nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    pais = db.Column(db.String(40))


class Solicitud(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class ListaCompartida(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class PistaCompartida(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Cancion(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Cambiar por clave compuesta
    audio = db.Column(db.LargeBinary, nullable=False)  # Comprobar como funciona
    nombre = db.Column(db.String(20), nullable=False)
    duracion = db.Column(db.Integer, nullable=False)  # Segundos


# class Cancion(db.Model):
#     path = db.Column(db.String(100), unique=True, nullable=False)
#
#     def __init__(self, name):
#         self.path = name


db.create_all()


# def add_song(song):
#     if not Cancion.query.filter_by(path=song.path):
#
#         db.session.add(song)
#         db.session.commit()
#         return False
#
#     else:
#         return True
