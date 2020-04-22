"""
Autor: Alberto Calvo Rubió
Fecha-última_modificación: 12-04-2020
Pruebas y poblar base de datos
"""

from flaskr.db import *
import datetime

DB.drop_all()
DB.create_all()


def insert_to_list(lista, cancion):
    lista.append(Aparicion(cancion=cancion, orden=len(lista)))


albumes = [
    Album(nombre='Album1', descripcion='album1', fecha=datetime.datetime(1990, 1, 1)),
    Album(nombre='Album2', descripcion='album2', fecha=datetime.datetime(1991, 1, 2)),
    Album(nombre='Album3', descripcion='album3', fecha=datetime.datetime(1992, 1, 1)),
    Album(nombre='Album4', descripcion='album4', fecha=datetime.datetime(1993, 6, 1)),
    Album(nombre='Album5', descripcion='album5', fecha=datetime.datetime(1994, 6, 1)),
    Album(nombre='Album6', descripcion='album6', fecha=datetime.datetime(1995, 6, 1)),
    Album(nombre='Album7', descripcion='album7', fecha=datetime.datetime(1996, 6, 1)),
    Album(nombre='Album8', descripcion='album8', fecha=datetime.datetime(1997, 6, 1)),
    Album(nombre='Album9', descripcion='album9', fecha=datetime.datetime(1998, 6, 1)),
    Album(nombre='Album10', descripcion='album10', fecha=datetime.datetime(1999, 6, 1)),
    Album(nombre='Album11', descripcion='album11', fecha=datetime.datetime(2000, 6, 1)),
    Album(nombre='Album12', descripcion='album12', fecha=datetime.datetime(2001, 6, 1))
]

artistas = [
    Artista(nombre='Alan Walker', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Cartoon', fecha_nacimiento=datetime.datetime(1991, 5, 1)),
    Artista(nombre='Deaf kev', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Different heaven', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Disfigure', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Electro light', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Electonomia', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Janji', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Spekterm', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Tobu', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Daniel levi', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Coleman trapp', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Ehde', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
    Artista(nombre='Johnning', fecha_nacimiento=datetime.datetime(1990, 1, 2))
]

categorias = [
    Categoria(nombre='Rock', descripcion='Categoria Rock'),
    Categoria(nombre='Pop', descripcion='Categoria Pop'),
    Categoria(nombre='EDM', descripcion='Categoria EDM'),
    Categoria(nombre='Electronica', descripcion='Categoria Electronic'),
    Categoria(nombre='Clasica', descripcion='Categoria Clasica'),
]

listas = [
    Lista(nombre='Favoritas', descripcion='Canciones favoritas'),
    Lista(nombre='Gimnasio', descripcion='Canciones para entrenar en el gimnasio'),
    Lista(nombre='Mis favoritos', descripcion='Mis canciones favoritas'),
    Lista(nombre='Coche', descripcion='Canciones para escuchar en el coche')
]

usuarios = [
    Usuario(email='elon@gmail.com', nombre='Elon Musk', password='passelon',
            fecha_nacimiento=datetime.datetime(2000, 1, 1), pais='United States of America',
            foto='https://psoftware.s3.amazonaws.com/usuario_elon-musk.jpeg'),
    Usuario(email='karen@gmail.com', nombre='Karen Sparck Jones', password='passkaren',
            fecha_nacimiento=datetime.datetime(2001, 1, 1), pais='United Kingdom',
            foto='https://psoftware.s3.amazonaws.com/usuario_karen.png')
]

solicitudes = [
    Solicitud(),
    Solicitud()
]

listas_compartidas = [
    ListaCompartida(),
    ListaCompartida()
]

canciones_compartidas = [
    CancionCompartida(),
    CancionCompartida()
]

canciones = [
    Cancion(path='https://psoftware.s3.amazonaws.com/alan_walker-fade.mp3',
            nombre='Fade', duracion=120),
    Cancion(path='https://psoftware.s3.amazonaws.com/alan_walker-spectre.mp3',
            nombre='Spectre', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/cartoon-on_and_on-daniel-levi.mp3',
            nombre='On & on', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/cartoon-why_we_lose-coleman_trapp.mp3',
            nombre='Why we lose', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/deaf_kev-invincible.mp3',
            nombre='Invincible', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/different_heaven-my_heart-ehde.mp3',
            nombre='My heart', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/disfigure-blank.mp3',
            nombre='Blank', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/electro_light-symbolism.mp3',
            nombre='Symbolism', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/elektronomia-sky_high.mp3',
            nombre='Skyhigh', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/janji-heroes_tonight-johnning.mp3',
            nombre='Heroes tonigth', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/spektrem-shine.mp3',
            nombre='Shine', duracion=180),
    Cancion(path='https://psoftware.s3.amazonaws.com/tobu-hope.mp3',
            nombre='Hope', duracion=180),
]

series_podcast = [
    SeriePodcast(nombre='SeriePodcast1'),
    SeriePodcast(nombre='SeriePodcast2')
]

capitulos_podcast = [
    CapituloPodcast(nombre='CapituloPodcast1'),
    CapituloPodcast(nombre='CapituloPodcast2')
]

listas_podcast = [
    ListaPodcast(nombre='Favoritos')
]

DB.session.add_all(categorias)
DB.session.add_all(artistas)
DB.session.add_all(albumes)
DB.session.add_all(listas)
DB.session.add_all(usuarios)
DB.session.add_all(solicitudes)
DB.session.add_all(listas_compartidas)
DB.session.add_all(canciones_compartidas)
DB.session.add_all(canciones)
DB.session.add_all(series_podcast)
DB.session.add_all(capitulos_podcast)
DB.session.add_all(listas_podcast)

# Añadir relaciones

# Relacion comprende
categorias[0].canciones.append(canciones[0])
categorias[0].canciones.append(canciones[1])
canciones[1].categorias.append(categorias[1])
canciones[1].categorias.append(categorias[2])
canciones[2].categorias.append(categorias[3])
canciones[2].categorias.append(categorias[4])
canciones[3].categorias.append(categorias[1])
canciones[3].categorias.append(categorias[2])
canciones[4].categorias.append(categorias[3])
canciones[5].categorias.append(categorias[4])
canciones[6].categorias.append(categorias[1])
canciones[7].categorias.append(categorias[2])
canciones[8].categorias.append(categorias[3])
canciones[9].categorias.append(categorias[4])
canciones[10].categorias.append(categorias[1])
canciones[11].categorias.append(categorias[2])
canciones[11].categorias.append(categorias[3])

# Relacion composicion
artistas[0].composiciones.append(canciones[0])
artistas[0].composiciones.append(canciones[1])
artistas[1].composiciones.append(canciones[2])
artistas[1].composiciones.append(canciones[3])
artistas[2].composiciones.append(canciones[4])
artistas[3].composiciones.append(canciones[5])
artistas[4].composiciones.append(canciones[6])
artistas[5].composiciones.append(canciones[7])
artistas[6].composiciones.append(canciones[8])
artistas[7].composiciones.append(canciones[9])
artistas[8].composiciones.append(canciones[10])
artistas[9].composiciones.append(canciones[11])
artistas[10].composiciones.append(canciones[2])
artistas[11].composiciones.append(canciones[3])
artistas[12].composiciones.append(canciones[5])
artistas[13].composiciones.append(canciones[9])

# Relacion publicacion
artistas[0].publicaciones.append(albumes[0])
artistas[0].publicaciones.append(albumes[1])
albumes[0].artistas.append(artistas[1])

# Relacion aparece
for i in range(len(canciones)):
    insert_to_list(listas[0].apariciones, canciones[i])

for i in range(4, 8):
    insert_to_list(listas[1].apariciones, canciones[i])

for i in range(8, 12):
    insert_to_list(listas[2].apariciones, canciones[i])

for i in range(4, 12):
    insert_to_list(listas[3].apariciones, canciones[i])


# Relacion amistad
usuarios[0].amistades.append(usuarios[1])
usuarios[1].amistades.append(usuarios[0])

# Relaciones 1:N

# Relacion compuesto
for i in range(len(canciones)):
    canciones[i].album = albumes[i%len(albumes)]
albumes[0].canciones.append(canciones[0])
albumes[0].canciones.append(canciones[1])
albumes[0].canciones.append(canciones[2])
albumes[0].canciones.append(canciones[3])
albumes[0].canciones.append(canciones[4])
albumes[0].canciones.append(canciones[5])
albumes[0].canciones.append(canciones[6])
albumes[1].canciones.append(canciones[7])
albumes[1].canciones.append(canciones[8])
albumes[1].canciones.append(canciones[9])
albumes[1].canciones.append(canciones[10])
albumes[1].canciones.append(canciones[11])

# Relacion tiene
usuarios[0].listas.append(listas[0])
usuarios[1].listas.append(listas[1])

# Relacion compartida (lista)
listas[1].comparticiones.append(listas_compartidas[0])
listas[1].comparticiones.append(listas_compartidas[1])

# Relacion compartida (cancion)
canciones[0].comparticiones.append(canciones_compartidas[0])
canciones[0].comparticiones.append(canciones_compartidas[1])

# Relacion ultima
usuarios[0].id_ultima_cancion = canciones[0].id
usuarios[1].id_ultima_cancion = canciones[0].id

# Relaciones recibe y envia (solicitud, listacompartida y cancioncompartida)
solicitudes = [
    Solicitud(email_usuario_notificado=usuarios[0].email,
              email_usuario_notificante=usuarios[1].email),
    Solicitud(email_usuario_notificado=usuarios[1].email,
              email_usuario_notificante=usuarios[0].email)
]
DB.session.add_all(solicitudes)

listas_compartidas = [
    ListaCompartida(email_usuario_notificado=usuarios[0].email,
                    email_usuario_notificante=usuarios[1].email),
    ListaCompartida(email_usuario_notificado=usuarios[1].email,
                    email_usuario_notificante=usuarios[0].email)
]
DB.session.add_all(listas_compartidas)

canciones_compartidas = [
    CancionCompartida(email_usuario_notificado=usuarios[0].email,
                      email_usuario_notificante=usuarios[1].email),
    CancionCompartida(email_usuario_notificado=usuarios[1].email,
                      email_usuario_notificante=usuarios[0].email)
]
DB.session.add_all(canciones_compartidas)

# Relacion compuesta
series_podcast[0].capitulos.append(capitulos_podcast[0])
series_podcast[1].capitulos.append(capitulos_podcast[1])

# Relacion escuchado
usuarios[0].cap_escuchados.append(capitulos_podcast[0])
capitulos_podcast[1].oyentes.append(usuarios[1])

# Relacion compuesta
listas_podcast[0].series_podcast.append(series_podcast[0])
listas_podcast[0].series_podcast.append(series_podcast[1])

# Relacion tiene
usuarios[0].listas_podcast.append(listas_podcast[0])

DB.session.commit()
