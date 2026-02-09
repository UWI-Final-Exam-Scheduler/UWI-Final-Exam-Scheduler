from .user import create_user, create_admin
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass','bob@mail.com')
    create_admin('admin', 'adminpass', 'admin@mail.com')
