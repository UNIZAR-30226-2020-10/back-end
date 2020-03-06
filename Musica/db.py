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


class Cancion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, name):
        self.path = name


db.create_all()


def add_song(song):
    if not Cancion.query.filter_by(path=song.path):

        db.session.add(song)
        db.session.commit()
        return False

    else:
        return True
