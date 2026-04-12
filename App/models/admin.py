from App.models import User
from App.database import db

class Admin(User):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, primary_key=True)
    exams = db.relationship("Exam", back_populates="admin")
    
    __mapper_args__ = {'polymorphic_identity': 'admin'}
    
    def __init__(self, username, password, role='admin'):
        super().__init__(username, password, role=role)

    