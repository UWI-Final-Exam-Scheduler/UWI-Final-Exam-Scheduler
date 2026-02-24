from App.database import db

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    courseCode= db.Column(db.String(20), db.ForeignKey('courses.courseCode'), nullable=False)

    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    __table_args__ = (db.UniqueConstraint('student_id', 'courseCode', name='student_course'),)

    def __init__(self, student_id, courseCode):
        self.student_id = student_id
        self.courseCode = courseCode