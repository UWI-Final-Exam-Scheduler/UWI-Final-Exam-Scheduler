from App.models import Admin
from App.database import db

def create_admin(username, password, role='admin'):
    newadmin = Admin(username=username, password=password, role=role)
    db.session.add(newadmin)
    db.session.commit()
    return newadmin