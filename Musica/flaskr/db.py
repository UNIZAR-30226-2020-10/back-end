import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flaskr import create_app

app = create_app()

# Configuracion PostgreSQL

env = os.environ['FLASK_ENV']

if env == 'production':
    POSTGRES_URL = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URL

else:
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
                          db.Column('cancion', db.Integer, db.ForeignKey('cancion.id'))
                          )
# Relacion 'compone'
composicion = db.Table('composicion',
                       db.Column('artista', db.String(20), db.ForeignKey('artista.nombre')),
                       db.Column('cancion', db.Integer, db.ForeignKey('cancion.id'))
                       )
# Relacion 'publica'
publicacion = db.Table('publicacion',
                       db.Column('artista', db.String(20), db.ForeignKey('artista.nombre')),
                       db.Column('album', db.String(20), db.ForeignKey('album.nombre'))
                       )

# Relacion 'aparece'
aparicion = db.Table('aparicion',
                     db.Column('lista', db.Integer, db.ForeignKey('lista.id')),
                     db.Column('cancion', db.Integer, db.ForeignKey('cancion.id'))
                     )

# Relacion 'conoce'
amistad = db.Table('amistad',
                   db.Column('usuario1', db.String(25), db.ForeignKey('usuario.email')),
                   db.Column('usuario2', db.String(25), db.ForeignKey('usuario.email'))
                   )


class Categoria(db.Model):
    nombre = db.Column(db.String(20), primary_key=True)
    descripcion = db.Column(db.String(100))
    canciones = db.relationship('Cancion', secondary=categorizacion, backref=db.backref('categorias'))


class Artista(db.Model):
    nombre = db.Column(db.String(20), primary_key=True)
    fecha_nacimiento = db.Column(db.DateTime)
    pais = db.Column(db.String(40))
    alias = db.Column(db.String(20))
    composiciones = db.relationship('Cancion', secondary=composicion, backref=db.backref('artistas'))
    publicaciones = db.relationship('Album', secondary=publicacion,
                                    backref=db.backref('artistas'))


class Album(db.Model):
    nombre = db.Column(db.String(20), primary_key=True)
    descripcion = db.Column(db.String(100))
    fecha = db.Column(db.DateTime)
    foto = db.Column(db.String(50))
    canciones = db.relationship('Cancion', backref='album')  # Relacion 'compuesto'


class Lista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(100))
    canciones = db.relationship('Cancion', secondary=aparicion, backref=db.backref('listas'))
    email_usuario = db.Column(db.String(25), db.ForeignKey('usuario.email'))
    comparticiones = db.relationship('ListaCompartida', backref='lista')  # Relacion 'compartida'


class Usuario(db.Model):
    email = db.Column(db.String(25), primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String, nullable=False)
    fecha_nacimiento = db.Column(db.DateTime)
    pais = db.Column(db.String(40))
    foto = db.Column(db.String(50))
    token = db.Column(db.String(), unique=True)
    fcm_token = db.Column(db.String(), unique=True)
    amistades = db.relationship('Usuario', secondary='amistad', primaryjoin=email == amistad.c.usuario1,
                                secondaryjoin=amistad.c.usuario2 == email)
    listas = db.relationship('Lista', backref='usuario')  # Relacion 'tiene'
    id_ultima_cancion = db.Column(db.Integer, db.ForeignKey('cancion.id'))
    segundo_ultima_cancion = db.Column(db.Integer)

    # Relacion 'recibe'
    solicitudes_recibidas = db.relationship('Solicitud', backref='notificado',
                                            foreign_keys="Solicitud.email_usuario_notificado")

    # Relacion 'envia'
    solicitudes_enviadas = db.relationship('Solicitud', backref='notificante',
                                           foreign_keys="Solicitud.email_usuario_notificante")

    # Relacion 'recibe'
    listas_recibidas = db.relationship('ListaCompartida', backref='notificado',
                                       foreign_keys="ListaCompartida.email_usuario_notificado")

    # Relacion 'envia'
    listas_enviadas = db.relationship('ListaCompartida', backref='notificante',
                                      foreign_keys="ListaCompartida.email_usuario_notificante")

    # Relacion 'envia'
    canciones_enviadas = db.relationship('CancionCompartida', backref='notificante',
                                         foreign_keys="CancionCompartida.email_usuario_notificante")

    # Relacion 'recibe'
    canciones_recibidas = db.relationship('CancionCompartida', backref='notificado',
                                          foreign_keys="CancionCompartida.email_usuario_notificado")


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
    path = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(20), nullable=False)
    duracion = db.Column(db.Integer, nullable=False)  # Segundos
    nombre_album = db.Column(db.String(20), db.ForeignKey('album.nombre'))
    comparticiones = db.relationship('CancionCompartida', backref='cancion')  # Relacion 'compartida'
    reproducciones = db.relationship('Usuario', backref='ultima_cancion')  # Relacion 'ultima'


def leer_todo(tabla):
    return db.session.query(tabla).all()


def fetch_data_by_id(table, clave):
    try:
        data = db.session.query(table).filter_by(id=clave).first()
        return data
    except IntegrityError:
        db.session.rollback()
        return "error"
