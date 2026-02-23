from App.models import Admin
from App.database import db

def create_admin(username, password):
    newadmin = Admin(username=username, password=password)
    db.session.add(newadmin)
    db.session.commit()
    return newadmin