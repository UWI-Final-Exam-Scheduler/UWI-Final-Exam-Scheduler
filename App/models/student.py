from App.database import db 

class Student(db.Model):
    __tablename__='students'
    
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    student_id = db.Column(db.Integer, nullable=False, unique=True)
    
    enrollments = db.relationship('Enrollment', back_populates='student')

    def __init__(self, id):
        self.id = id
    