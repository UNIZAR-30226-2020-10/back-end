from flaskr.db import DB

DB.drop_all()
DB.create_all()
