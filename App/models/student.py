from App.database import db 

class Student(db.Model):
    __tablename__='students'
    
    student_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    
    enrollments = db.relationship('Enrollment', back_populates='student')

    def __init__(self, student_id):
        self.student_id = student_id
    