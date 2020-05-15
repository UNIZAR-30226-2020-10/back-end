"""
Autor: Alberto Calvo Rubió
Fecha-última_modificación: 22-04-2020
Modulo principal de la aplicación
"""

# pylint: disable=no-member

import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flaskr import create_app

APP, MAIL = create_app()

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

# MANY TO MANY relationships

# Categoria <-> Cancion 'comprende'
categorizacion = DB.Table('categorizacion',
                          DB.Column('categoria', DB.String(20), DB.ForeignKey('categoria.nombre')),
                          DB.Column('cancion', DB.Integer, DB.ForeignKey('cancion.id'))
                          )
# Artista <-> Cancion 'compone'
composicion = DB.Table('composicion',
                       DB.Column('artista', DB.String(20), DB.ForeignKey('artista.nombre')),
                       DB.Column('cancion', DB.Integer, DB.ForeignKey('cancion.id'))
                       )
# Artista <-> Album 'publica'
publicacion = DB.Table('publicacion',
                       DB.Column('artista', DB.String(20), DB.ForeignKey('artista.nombre')),
                       DB.Column('album', DB.String(20), DB.ForeignKey('album.nombre'))
                       )

# Usuario <-> Usuario 'conoce'
amistad = DB.Table('amistad',
                   DB.Column('usuario1', DB.String(25),
                             DB.ForeignKey('usuario.email', ondelete="CASCADE")),
                   DB.Column('usuario2', DB.String(25),
                             DB.ForeignKey('usuario.email', ondelete="CASCADE"))
                   )

# CapituloPodcast <-> Usuario 'escuchado'
cap_escuchado = DB.Table('cap_escuchado',
                         DB.Column('capitulo', DB.String(50),
                                   DB.ForeignKey('capitulo_podcast.id', ondelete="CASCADE")),
                         DB.Column('usuario', DB.String(25),
                                   DB.ForeignKey('usuario.email', ondelete="CASCADE"))
                         )

# SeriePodcast <-> ListaPodcast 'aparece'
aparicion_podcast = DB.Table('aparicion_podcast',
                             DB.Column('serie_podcast', DB.String(50),
                                       DB.ForeignKey('serie_podcast.id')),
                             DB.Column('lista_podcast', DB.Integer,
                                       DB.ForeignKey('lista_podcast.id'))
                             )

# Usuario <-> Artista 'suscrito'
suscripcion = DB.Table('suscripcion',
                       DB.Column('usuario', DB.String(25),
                                 DB.ForeignKey('usuario.email', ondelete="CASCADE")),
                       DB.Column('artista', DB.String(20),
                                 DB.ForeignKey('artista.nombre', ondelete="CASCADE"))
                       )


class Aparicion(DB.Model):
    """
    Aparición de una canción en una lista de reproducción(Lista)
    Relación N:M con atributos
    """
    __tablename__ = 'aparicion'
    id_lista = DB.Column(DB.Integer, DB.ForeignKey('lista.id'), primary_key=True)
    id_cancion = DB.Column(DB.Integer, DB.ForeignKey('cancion.id'), primary_key=True)
    orden = DB.Column(DB.Integer, nullable=False)

    # Lista - Aparicion - Cancion : Associaton object
    cancion = DB.relationship('Cancion', back_populates="apariciones")
    lista = DB.relationship('Lista', back_populates="apariciones")


class Categoria(DB.Model):
    """
    Entidad que representa la categoría de una canción
    """
    nombre = DB.Column(DB.String(20), primary_key=True)
    descripcion = DB.Column(DB.String(100))
    foto = DB.Column(DB.String(150), default='https://psoftware.s3.amazonaws.com/LogoAppFondoEscalaGrises.png')

    # MANY TO MANY relationships
    # Categoria <-> Cancion 'comprende'
    canciones = DB.relationship('Cancion', secondary=categorizacion, back_populates="categorias")


class Artista(DB.Model):
    """
    Entidad que representa un compositor de canciones, puede ser el artista principal o secundario
    """
    nombre = DB.Column(DB.String(20), primary_key=True)
    fecha_nacimiento = DB.Column(DB.DateTime)
    pais = DB.Column(DB.String(40))
    alias = DB.Column(DB.String(20))
    foto = DB.Column(DB.String(150), default='https://psoftware.s3.amazonaws.com/LogoAppFondoEscalaGrises.png')

    # MANY TO MANY relationships
    # Artista <-> Cancion 'compone'
    composiciones = DB.relationship('Cancion', secondary=composicion, back_populates="artistas")
    # Artista <-> Album 'publica'
    publicaciones = DB.relationship('Album', secondary=publicacion, back_populates="artistas")
    # Artista <-> Usuario 'suscrito'
    suscriptores = DB.relationship('Usuario', secondary=suscripcion, back_populates="artistas")


class Album(DB.Model):
    """
    Entidad que representa un conjunto de canciones que son lanzadas por Artista/s de forma conjunta
    """
    nombre = DB.Column(DB.String(20), primary_key=True)
    descripcion = DB.Column(DB.String(100))
    fecha = DB.Column(DB.DateTime)
    foto = DB.Column(DB.String(150), default='https://psoftware.s3.amazonaws.com/LogoAppFondoEscalaGrises.png')

    # MANY TO MANY relationships
    # Album <-> Artista 'publica'
    artistas = DB.relationship('Artista', secondary=publicacion, back_populates="publicaciones")

    # ONE TO MANY relationships
    # Album -> Cancion 'compuesto'
    canciones = DB.relationship('Cancion', back_populates="album")


class Lista(DB.Model):
    """
    Entidad que representa una lista de producción, de usuarios o del sistema
    """
    id = DB.Column(DB.Integer, primary_key=True)
    nombre = DB.Column(DB.String(20), nullable=False)
    descripcion = DB.Column(DB.String(100))
    foto = DB.Column(DB.String(150),
                     default='https://psoftware.s3.amazonaws.com/LogoAppFondoEscalaGrises.png')

    # MANY TO MANY relationships
    # Lista <-> Cancion 'aparece' Association Object: Aparicion
    apariciones = DB.relationship('Aparicion', back_populates="lista",
                                  cascade="save-update, delete")

    # ONE TO MANY relationships
    # Lista -> ListaCompartida 'compartida'
    comparticiones = DB.relationship('ListaCompartida', back_populates="lista",
                                     cascade="save-update, delete")

    # MANY TO ONE relationships
    # Lista <- Usuario 'tiene'
    email_usuario = DB.Column(DB.String(25), DB.ForeignKey('usuario.email', ondelete="CASCADE"))
    usuario = DB.relationship('Usuario', back_populates="listas")


class Usuario(DB.Model):
    """
    Entidad que reprenta a un usuario del sistema de canciones y podcast
    """
    email = DB.Column(DB.String(50), primary_key=True)
    nombre = DB.Column(DB.String(20), nullable=False)
    password = DB.Column(DB.String, nullable=False)
    fecha_nacimiento = DB.Column(DB.DateTime)
    pais = DB.Column(DB.String(40))
    foto = DB.Column(DB.String(150), default='https://psoftware.s3.amazonaws.com/user_default.jpg')
    token = DB.Column(DB.String(200), unique=True)
    confirmado = DB.Column(DB.Boolean(), default=False)

    # MANY TO MANY relationships
    # Usuario <-> Artista 'suscrito'
    artistas = DB.relationship('Artista', secondary=suscripcion, back_populates="suscriptores")
    # Usuario <-> CapituloPodcast 'escuchado'
    cap_escuchados = DB.relationship('CapituloPodcast', secondary=cap_escuchado,
                                     back_populates="oyentes")
    # Usuario <-> Usuario 'conoce'
    amistades = DB.relationship('Usuario', secondary='amistad',
                                primaryjoin=email == amistad.c.usuario1,
                                secondaryjoin=amistad.c.usuario2 == email)

    # ONE TO MANY relationships
    # Usuario -> Lista 'tiene'
    listas = DB.relationship('Lista', back_populates="usuario", cascade='save-update, delete')
    # Usuario -> ListaPodcast 'tiene' de podcast
    listas_podcast = DB.relationship('ListaPodcast', back_populates="usuario",
                                     cascade='save-update, delete')
    # Usuario -> Solicitud 'envia'
    solicitudes_enviadas = DB.relationship('Solicitud', back_populates="notificante",
                                           foreign_keys="Solicitud.email_usuario_notificante",
                                           cascade='save-update, delete')
    # Usuario -> ListaCompartida 'envia'
    listas_enviadas = DB.relationship('ListaCompartida', back_populates="notificante",
                                      foreign_keys="ListaCompartida.email_usuario_notificante",
                                      cascade='save-update, delete')
    # Usuario -> CancionCompartida 'envia'
    canciones_enviadas = DB.relationship('CancionCompartida', back_populates="notificante",
                                         foreign_keys="CancionCompartida.email_usuario_notificante",
                                         cascade='save-update, delete')
    # Usuario -> Solicitud 'recibe'
    solicitudes_recibidas = DB.relationship('Solicitud', back_populates="notificado",
                                            foreign_keys="Solicitud.email_usuario_notificado",
                                            cascade='save-update, delete')
    # Usuario -> ListaCompartida 'recibe'
    listas_recibidas = DB.relationship('ListaCompartida', back_populates="notificado",
                                       foreign_keys="ListaCompartida.email_usuario_notificado",
                                       cascade='save-update, delete')
    # Relacion 'recibe'
    canciones_recibidas = DB.relationship('CancionCompartida', back_populates="notificado",
                                          foreign_keys="CancionCompartida.email_usuario_notificado",
                                          cascade='save-update, delete')

    # MANY TO ONE relationships
    # Usuario <- Cancion 'ultima'
    id_ultima_cancion = DB.Column(DB.Integer, DB.ForeignKey('cancion.id'))
    ultima_cancion = DB.relationship('Cancion', back_populates="usuarios_ultima_cancion")
    segundo_ultima_cancion = DB.Column(DB.Integer)


class Solicitud(DB.Model):
    """
    Tipo de entidad Notificacion que representa una invitación de amistad para establecer
     una relación de amistad entre usuarios
    """
    id = DB.Column(DB.Integer, primary_key=True)

    # MANY TO ONE relationships
    # Solicitud <- Usuario 'envia'
    email_usuario_notificante = DB.Column(DB.String(25),
                                          DB.ForeignKey('usuario.email', ondelete="CASCADE"),
                                          nullable=False)
    notificante = DB.relationship('Usuario', back_populates="solicitudes_enviadas",
                                  foreign_keys=email_usuario_notificante)

    # Solicitud <- Usuario 'recibe'
    email_usuario_notificado = DB.Column(DB.String(25),
                                         DB.ForeignKey('usuario.email', ondelete="CASCADE"),
                                         nullable=False)
    notificado = DB.relationship('Usuario', back_populates="solicitudes_recibidas",
                                 foreign_keys=email_usuario_notificado)


class ListaCompartida(DB.Model):
    """
    Tipo de entidad Notificacion que representa una compartición de una loista de producción
    """
    id = DB.Column(DB.Integer, primary_key=True)
    notificacion = DB.Column(DB.Boolean, default=True)

    # MANY TO ONE relationships
    # ListaCompartida <- Lista 'compartida'
    id_lista = DB.Column(DB.Integer, DB.ForeignKey('lista.id'), nullable=False)
    lista = DB.relationship('Lista', back_populates="comparticiones")

    # ListaCompartida <- Usuario 'envia'
    email_usuario_notificante = DB.Column(DB.String(25),
                                          DB.ForeignKey('usuario.email', ondelete="CASCADE"),
                                          nullable=False)
    notificante = DB.relationship('Usuario', back_populates="listas_enviadas",
                                  foreign_keys=email_usuario_notificante)

    # ListaCompartida <- Usuario 'recibe'
    email_usuario_notificado = DB.Column(DB.String(25),
                                         DB.ForeignKey('usuario.email', ondelete="CASCADE"),
                                         nullable=False)
    notificado = DB.relationship('Usuario', back_populates="listas_recibidas",
                                 foreign_keys=email_usuario_notificado)


class CancionCompartida(DB.Model):
    """
    Tipo de entidad Notificación que representa una compartición de canción
    """
    id = DB.Column(DB.Integer, primary_key=True)
    notificacion = DB.Column(DB.Boolean, default=True)

    # MANY TO ONE relationships
    # CancionCompartida <- Usuario
    email_usuario_notificante = DB.Column(DB.String(25),
                                          DB.ForeignKey('usuario.email', ondelete="CASCADE"),
                                          nullable=False)
    notificante = DB.relationship('Usuario', back_populates="canciones_enviadas",
                                  foreign_keys=email_usuario_notificante)

    # CancionCompartida <- Usuario
    email_usuario_notificado = DB.Column(DB.String(25),
                                         DB.ForeignKey('usuario.email', ondelete="CASCADE"),
                                         nullable=False)
    notificado = DB.relationship('Usuario', back_populates="canciones_recibidas",
                                 foreign_keys=email_usuario_notificado)

    # CancionCompartida <- Cancion
    id_cancion = DB.Column(DB.Integer, DB.ForeignKey('cancion.id'), nullable=False)
    cancion = DB.relationship('Cancion', back_populates="comparticiones")


class Cancion(DB.Model):
    """
    Entidad que representa una canción de un Artista en un Album
    """
    id = DB.Column(DB.Integer, primary_key=True)
    path = DB.Column(DB.String(150), nullable=False)
    nombre = DB.Column(DB.String(20), nullable=False)
    duracion = DB.Column(DB.Integer, nullable=False)  # Segundos

    # MANY TO MANY relationships
    # Cancion <-> Categoria 'comprende'
    categorias = DB.relationship('Categoria', secondary=categorizacion, back_populates="canciones")
    # Cancion <-> Artista 'compone'
    artistas = DB.relationship('Artista', secondary=composicion, back_populates="composiciones")
    # Cancion <-> Lista 'aparece' Association Object: Aparicion
    apariciones = DB.relationship('Aparicion', back_populates="cancion",
                                  cascade="save-update, delete")

    # ONE TO MANY relationships
    # Cancion -> CancionCompartida 'compartida'
    comparticiones = DB.relationship('CancionCompartida', back_populates="cancion")
    # Cancion -> Usuario 'ultima'
    usuarios_ultima_cancion = DB.relationship('Usuario', back_populates="ultima_cancion")

    # MANY TO ONE relationships
    # Cancion <- Album 'compuesto'
    nombre_album = DB.Column(DB.String(20), DB.ForeignKey('album.nombre'))
    album = DB.relationship('Album', back_populates="canciones")


class SeriePodcast(DB.Model):
    """
    Entidad que representa un conjunto de capitulos de podcast
    """
    id = DB.Column(DB.String(50), primary_key=True)
    nombre = DB.Column(DB.String(150), nullable=False)

    # MANY TO MANY relationships
    # SeriePodcast <-> ListaPodcast 'aparece'
    listas_podcast = DB.relationship('ListaPodcast', secondary=aparicion_podcast,
                                     back_populates="series_podcast")

    # ONE TO MANY relationships
    # SeriePodcast -> CapituloPodcast 'compuesta'
    capitulos = DB.relationship('CapituloPodcast', back_populates="serie")


class CapituloPodcast(DB.Model):
    """
    Entidad que representa un único capitulo de una serie de podcast
    """
    id = DB.Column(DB.String(50), primary_key=True)
    nombre = DB.Column(DB.String(150))

    # MANY TO MANY relationships
    # CapituloPodcast <-> Usuario 'escuchado'
    oyentes = DB.relationship('Usuario', secondary=cap_escuchado, back_populates="cap_escuchados")

    # MANY TO ONE relationships
    # CapituloPodcast <- SeriePodcast 'compuesta'
    id_serie = DB.Column(DB.String(50), DB.ForeignKey('serie_podcast.id'), nullable=False)
    serie = DB.relationship('SeriePodcast', back_populates="capitulos")


class ListaPodcast(DB.Model):
    """
    Entidad que representa un conjunto de series de podcast
    """
    id = DB.Column(DB.Integer, primary_key=True)
    nombre = DB.Column(DB.String(150))

    # MANY TO MANY relationships
    # ListaPodcast <-> SeriePodcast 'aparece'
    series_podcast = DB.relationship('SeriePodcast', secondary=aparicion_podcast,
                                     back_populates="listas_podcast")

    # MANY TO ONE relationships
    # ListaPodcast <- Usuario 'tiene'
    email_usuario = DB.Column(DB.String(25), DB.ForeignKey('usuario.email', ondelete="CASCADE"),
                              nullable=False)
    usuario = DB.relationship('Usuario', back_populates="listas_podcast")


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
