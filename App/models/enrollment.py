from App.database import db

class Enrollments(db.Model):
    __tablename__ = "enrollment"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id= db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Courses', back_populates='enrollments')

    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='student_course'),)

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id