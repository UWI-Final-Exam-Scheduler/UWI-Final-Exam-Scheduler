from App.models import User, Admin
from App.database import db
from App.controllers.admin import create_admin

def create_user(username, password, role='user'):
    if role == 'admin':
        newuser = Admin(username=username, password=password, role=role)
    else:
        newuser = User(username=username, password=password, role=role)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_username(username):
    result = db.session.execute(db.select(User).filter_by(username=username))
    return result.scalar_one_or_none()

def get_user(id):
    return db.session.get(User, id)

def get_all_users():
    return db.session.scalars(db.select(User)).all()

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username, role=None):
    user = get_user(id)
    if user:
        user.username = username

        if role is not None:
            user.role = role
        # user is already in the session; no need to re-add
        db.session.commit()
        return True
    return None
