from App.database import db

class Course(db.Model):
    __tablename__ = "courses"

    courseCode = db.Column(db.String(20), nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)

    enrollments = db.relationship('Enrollment', back_populates='course')
    exams = db.relationship('Exam', back_populates='course')
    
    def __init__(self, courseCode, name):
        self.courseCode = courseCode
        self.name = name