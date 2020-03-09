from flask_sqlalchemy import SQLAlchemy
from app import app

# Configuracion PostgreSQL

POSTGRES_URL = "127.0.0.1:5432"
POSTGRES_USER = "admin"
POSTGRES_PW = "admin"
POSTGRES_DB = "test"

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://{user}:{pw}@{url}/{db}'. \
        format(user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, db=POSTGRES_DB)

db = SQLAlchemy(app)


# Relaciones N:M

# Relacion 'comprende'
categorizacion = db.Table('categorizacion',
                          db.Column('categoria', db.String(20), db.ForeignKey('categoria.nombre')),
                          db.Column('cancion', db.String(20), db.ForeignKey('cancion.id'))
                          )
# Relacion 'compone'
composicion = db.Table('composicion',
                       db.Column('artista', db.String(20), db.ForeignKey('artista.nombre')),
                       db.Column('cancion', db.Integer, db.ForeignKey('cancion.id'))
                       )
# Relacion 'publica'
publicacion = db.table('publicacion',
                       db.Column('artista', db.String(20), db.ForeignKey('artista.nombre')),
                       db.Column('album', db.String(20), db.ForeignKey('album.nombre'))
                       )
# Relacion aparece
aparicion = db.table('aparicion',
                     db.Column('lista', db.Integer, db.ForeignKey('lista.id')),
                     db.Column('cancion', db.Integer, db.ForeignKey('cancion.id'))
                     )
# Relacion 'conoce'
amistad = db.table('amistar',
                     db.Column('usuario', db.String(25), db.ForeignKey('usuario.email')),
                     db.Column('usuario', db.String(25), db.ForeignKey('usuario.email'))
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
    composiciones = db.relationship('Cancion', secondary=composicion, backref=db.backref('artistas', lazy='dynamic'))
    publicaciones = db.relationship('Album', secondary=publicacion, backref=db.backref('artistas', lazy='dynamic'))


class Album(db.Model):
    nombre = db.Column(db.String(20), primary_key=True)
    descripcion = db.Column(db.String(100))
    fecha = db.Column(db.Date)
    canciones = db.relationship('Cancion', backref='album')  # Relacion 'compuesto'


class Lista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(100))
    canciones = db.relationship('Cancion', secondary=aparicion, backref=db.backref('listas', lazy='dynamic'))
    email_usuario = db.Column(db.String(25), db.ForeignKey('usuario.email'))
    comparticiones = db.relationship('ListaCompartida', backref='lista')  # Relacion 'compartida'


class Usuario(db.Model):
    email = db.Column(db.String(25), primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String, nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    pais = db.Column(db.String(40))
    id_ultima_cancion = db.Column(db.Integer, db.ForeignKey('cancion.id'))
    segundo_ultima_cancion = db.Column(db.Integer)
    listas = db.relationship('Lista', backref='usuario')  # Relacion 'tiene'
    amistades = db.relationship('Usuario', secondary='amistades')
    solicitudes_recibidas = db.relationship('Solicitud', backref='notificado')          # Relacion 'recibe'
    canciones_recibidas = db.relationship('CancionCompartida', backref='notificado')    # Relacion 'recibe'
    listas_recibidas = db.relationship('ListaCompartida', backref='notificado')         # Relacion 'recibe'
    solicitudes_enviadas = db.relationship('Solicitud', backref='notificante')          # Relacion 'envia'
    canciones_enviadas = db.relationship('CancionCompartida', backref='notificante')    # Relacion 'envia'
    listas_enviadas = db.relationship('ListaCompartida', backref='notificante')         # Relacion 'envia'

class Solicitud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_usuario_notificado = db.Column(db.String(25), db.ForeignKey('usuario.email'))
    email_usuario_notificante = db.Column(db.String(25), db.ForeignKey('usuario.email'))


class ListaCompartida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_lista = db.Column(db.Integer, db.ForeignKey('lista.id'))
    email_usuario_notificado = db.Column(db.String(25), db.ForeignKey('usuario.email'))
    email_usuario_notificante = db.Column(db.String(25), db.ForeignKey('usuario.email'))


class CancionCompartida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cancion = db.Column(db.Integer, db.ForeignKey('cancion.id'))
    email_usuario_notificado = db.Column(db.String(25), db.ForeignKey('usuario.email'))
    email_usuario_notificante = db.Column(db.String(25), db.ForeignKey('usuario.email'))


class Cancion(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Cambiar por clave compuesta
    audio = db.Column(db.LargeBinary, nullable=False)  # Comprobar como funciona
    nombre = db.Column(db.String(20), nullable=False)
    duracion = db.Column(db.Integer, nullable=False)  # Segundos
    nombre_album = db.Column(db.String(20), db.ForeignKey('album.nombre'))
    comparticiones = db.relationship('CancionCompartida', backref='cancion') #  Relacion 'compartida'
    reproducciones = db.relationship('Usuario', backref='ultima_cancion')  # Relacion 'ultima'


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
