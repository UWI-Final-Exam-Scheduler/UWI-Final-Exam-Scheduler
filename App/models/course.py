from App.database import db

class Courses(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    def __init__(self, name):
        self.name = name