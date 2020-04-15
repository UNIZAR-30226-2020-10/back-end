"""
Autor: Alberto Calvo Rubió
Fecha-última_modificación: 08-04-2020
Modulo principal de la aplicación
"""

# pylint: disable=no-member

import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flaskr import create_app

APP = create_app()

# Configuracion PostgreSQL

ENV = os.environ['FLASK_ENV']

if ENV == 'production':
    POSTGRES_URL = os.environ['DATABASE_URL']
    APP.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URL

elif ENV == 'development_wind':
    POSTGRES_URL = "localhost:5432"
    POSTGRES_USER = "admin"
    POSTGRES_PW = "admin"
    POSTGRES_DB = "test"
    APP.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql+psycopg2://{user}:{pw}@{url}/{DB}'. \
            format(user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, DB=POSTGRES_DB)
else:
    POSTGRES_URL = "DB:5432"
    POSTGRES_USER = "admin"
    POSTGRES_PW = "admin"
    POSTGRES_DB = "test"
    APP.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql+psycopg2://{user}:{pw}@{url}/{DB}'. \
            format(user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, DB=POSTGRES_DB)

DB = SQLAlchemy(APP)

# Relaciones N:M

# Relacion 'comprende'
categorizacion = DB.Table('categorizacion',
                          DB.Column('categoria', DB.String(20), DB.ForeignKey('categoria.nombre')),
                          DB.Column('cancion', DB.Integer, DB.ForeignKey('cancion.id'))
                          )
# Relacion 'compone'
composicion = DB.Table('composicion',
                       DB.Column('artista', DB.String(20), DB.ForeignKey('artista.nombre')),
                       DB.Column('cancion', DB.Integer, DB.ForeignKey('cancion.id'))
                       )
# Relacion 'publica'
publicacion = DB.Table('publicacion',
                       DB.Column('artista', DB.String(20), DB.ForeignKey('artista.nombre')),
                       DB.Column('album', DB.String(20), DB.ForeignKey('album.nombre'))
                       )

# Relacion 'aparece'
aparicion = DB.Table('aparicion',
                     DB.Column('lista', DB.Integer, DB.ForeignKey('lista.id')),
                     DB.Column('cancion', DB.Integer, DB.ForeignKey('cancion.id'))
                     )

# Relacion 'conoce'
amistad = DB.Table('amistad',
                   DB.Column('usuario1', DB.String(25), DB.ForeignKey('usuario.email')),
                   DB.Column('usuario2', DB.String(25), DB.ForeignKey('usuario.email'))
                   )


class Categoria(DB.Model):
    nombre = DB.Column(DB.String(20), primary_key=True)
    descripcion = DB.Column(DB.String(100))
    canciones = DB.relationship('Cancion',
                                secondary=categorizacion, backref=DB.backref('categorias'))


class Artista(DB.Model):
    nombre = DB.Column(DB.String(20), primary_key=True)
    fecha_nacimiento = DB.Column(DB.DateTime)
    pais = DB.Column(DB.String(40))
    alias = DB.Column(DB.String(20))
    composiciones = DB.relationship('Cancion',
                                    secondary=composicion, backref=DB.backref('artistas'))
    publicaciones = DB.relationship('Album',
                                    secondary=publicacion, backref=DB.backref('artistas'))


class Album(DB.Model):
    nombre = DB.Column(DB.String(20), primary_key=True)
    descripcion = DB.Column(DB.String(100))
    fecha = DB.Column(DB.DateTime)
    foto = DB.Column(DB.String(100))
    canciones = DB.relationship('Cancion', backref='album')  # Relacion 'compuesto'


class Lista(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    nombre = DB.Column(DB.String(20), nullable=False)
    descripcion = DB.Column(DB.String(100))
    canciones = DB.relationship('Cancion', secondary=aparicion, backref=DB.backref('listas'))
    email_usuario = DB.Column(DB.String(25), DB.ForeignKey('usuario.email'))
    comparticiones = DB.relationship('ListaCompartida', backref='lista')  # Relacion 'compartida'


class Usuario(DB.Model):
    email = DB.Column(DB.String(25), primary_key=True)
    nombre = DB.Column(DB.String(20), nullable=False)
    password = DB.Column(DB.String, nullable=False)
    fecha_nacimiento = DB.Column(DB.DateTime)
    pais = DB.Column(DB.String(40))
    foto = DB.Column(DB.String(100), default='https://psoftware.s3.amazonaws.com/user_default.jpg')
    token = DB.Column(DB.String(), unique=True)
    fcm_token = DB.Column(DB.String(), unique=True)
    amistades = DB.relationship('Usuario', secondary='amistad',
                                primaryjoin=email == amistad.c.usuario1,
                                secondaryjoin=amistad.c.usuario2 == email)
    listas = DB.relationship('Lista', backref='usuario')  # Relacion 'tiene'
    id_ultima_cancion = DB.Column(DB.Integer, DB.ForeignKey('cancion.id'))
    segundo_ultima_cancion = DB.Column(DB.Integer)

    # Relacion 'recibe'
    solicitudes_recibidas = DB.relationship('Solicitud', backref='notificado',
                                            foreign_keys="Solicitud.email_usuario_notificado")

    # Relacion 'envia'
    solicitudes_enviadas = DB.relationship('Solicitud', backref='notificante',
                                           foreign_keys="Solicitud.email_usuario_notificante")

    # Relacion 'recibe'
    listas_recibidas = DB.relationship('ListaCompartida', backref='notificado',
                                       foreign_keys="ListaCompartida.email_usuario_notificado")

    # Relacion 'envia'
    listas_enviadas = DB.relationship('ListaCompartida', backref='notificante',
                                      foreign_keys="ListaCompartida.email_usuario_notificante")

    # Relacion 'envia'
    canciones_enviadas = DB.relationship('CancionCompartida', backref='notificante',
                                         foreign_keys="CancionCompartida.email_usuario_notificante")

    # Relacion 'recibe'
    canciones_recibidas = DB.relationship('CancionCompartida', backref='notificado',
                                          foreign_keys="CancionCompartida.email_usuario_notificado")


class Solicitud(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    email_usuario_notificado = DB.Column(DB.String(25), DB.ForeignKey('usuario.email'))
    email_usuario_notificante = DB.Column(DB.String(25), DB.ForeignKey('usuario.email'))


class ListaCompartida(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    id_lista = DB.Column(DB.Integer, DB.ForeignKey('lista.id'))
    email_usuario_notificado = DB.Column(DB.String(25), DB.ForeignKey('usuario.email'))
    email_usuario_notificante = DB.Column(DB.String(25), DB.ForeignKey('usuario.email'))


class CancionCompartida(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    id_cancion = DB.Column(DB.Integer, DB.ForeignKey('cancion.id'))
    email_usuario_notificado = DB.Column(DB.String(25), DB.ForeignKey('usuario.email'))
    email_usuario_notificante = DB.Column(DB.String(25), DB.ForeignKey('usuario.email'))


class Cancion(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)  # Cambiar por clave compuesta
    path = DB.Column(DB.String(150), nullable=False)
    nombre = DB.Column(DB.String(20), nullable=False)
    duracion = DB.Column(DB.Integer, nullable=False)  # Segundos
    nombre_album = DB.Column(DB.String(20), DB.ForeignKey('album.nombre'))

    # Relacion 'compartida'
    comparticiones = DB.relationship('CancionCompartida', backref='cancion')

    # Relacion 'ultima'
    reproducciones = DB.relationship('Usuario', backref='ultima_cancion')


DB.create_all()


def leer_todo(tabla):
    """
    Devuelve todos los datos de la tabla especificada
    :param tabla:
    :return:
    """
    return DB.session.query(tabla).all()


def fetch_data_by_id(table, clave):
    """
    Devuelve el dato con clave <clave> de la tabla <tabla>
    :param table:
    :param clave:
    :return:
    """
    try:
        data = DB.session.query(table).filter_by(id=clave).first()
        return data
    except IntegrityError:
        DB.session.rollback()
        return "error"
