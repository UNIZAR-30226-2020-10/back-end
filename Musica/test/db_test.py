from flaskr.db import *
import datetime


def poblar():
    categorias = [
        Categoria(nombre='Rock', descripcion='Categoria Rock'),
        Categoria(nombre='Pop', descripcion='Categoria Pop')
    ]

    artistas = [
        Artista(nombre='Alan Walker', fecha_nacimiento=datetime.datetime(1990, 1, 2)),
        Artista(nombre='Paco', fecha_nacimiento=datetime.datetime(1991, 5, 1))
    ]

    albumes = [
        Album(nombre='Mi album 1', descripcion='album 1', fecha=datetime.datetime(2000, 6, 1)),
        Album(nombre='Mi album 2', descripcion='album 2', fecha=datetime.datetime(2015, 6, 1))
    ]

    listas = [
        Lista(nombre='Favoritas', descripcion='Canciones favoritas'),
        Lista(nombre='Gimnasio', descripcion='Canciones para entrenar en el gimnasio')
    ]

    usuarios = [
        Usuario(email='paco@gmail.com', nombre='Paco', password='passpaco',
                fecha_nacimiento=datetime.datetime(2000, 1, 1), pais='Spain'),
        Usuario(email='laura@gmail.com', nombre='Laura', password='passlaura',
                fecha_nacimiento=datetime.datetime(2001, 1, 1), pais='France')
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
        Cancion(path='https://psoftware.s3.amazonaws.com/alan_walker-fade.mp3', nombre='Fade', duracion=120),
        Cancion(path='https://psoftware.s3.amazonaws.com/alan_walker-spectre.mp3', nombre='Spectre', duracion=180)
    ]

    db.session.add_all(categorias)
    db.session.add_all(artistas)
    db.session.add_all(albumes)
    db.session.add_all(listas)
    db.session.add_all(usuarios)
    db.session.add_all(solicitudes)
    db.session.add_all(listas_compartidas)
    db.session.add_all(canciones_compartidas)
    db.session.add_all(canciones)

    # Añadir relaciones

    # Relacion comprende
    categorias[0].canciones.append(canciones[0])
    categorias[0].canciones.append(canciones[1])
    canciones[1].categorias.append(categorias[1])

    # Relacion composicion
    artistas[0].composiciones.append(canciones[0])
    artistas[0].composiciones.append(canciones[1])
    canciones[1].artistas.append(artistas[1])

    # Relacion publicacion
    artistas[0].publicaciones.append(albumes[0])
    artistas[0].publicaciones.append(albumes[1])
    albumes[0].artistas.append(artistas[1])

    # Relacion aparece
    listas[0].canciones.append(canciones[0])
    listas[0].canciones.append(canciones[1])
    canciones[1].listas.append(listas[1])

    # Relacion amistad
    usuarios[0].amistades.append(usuarios[1])
    usuarios[1].amistades.append(usuarios[0])

    # Relaciones 1:N

    # Relacion compuesto
    albumes[0].canciones.append(canciones[0])
    albumes[0].canciones.append(canciones[1])
    canciones[1].album = albumes[1]  # Sobreescribe lo anterior aposta

    # Relacion tiene
    usuarios[0].listas.append(listas[0])
    usuarios[1].listas.append(listas[1])
    listas[0].email_usuario = usuarios[0].email

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
        Solicitud(email_usuario_notificado=usuarios[0].email, email_usuario_notificante=usuarios[1].email),
        Solicitud(email_usuario_notificado=usuarios[1].email, email_usuario_notificante=usuarios[0].email)
    ]
    db.session.add_all(solicitudes)

    listas_compartidas = [
        ListaCompartida(email_usuario_notificado=usuarios[0].email, email_usuario_notificante=usuarios[1].email),
        ListaCompartida(email_usuario_notificado=usuarios[1].email, email_usuario_notificante=usuarios[0].email)
    ]
    db.session.add_all(listas_compartidas)

    canciones_compartidas = [
        CancionCompartida(email_usuario_notificado=usuarios[0].email, email_usuario_notificante=usuarios[1].email),
        CancionCompartida(email_usuario_notificado=usuarios[1].email, email_usuario_notificante=usuarios[0].email)
    ]
    db.session.add_all(canciones_compartidas)

    db.session.commit()
