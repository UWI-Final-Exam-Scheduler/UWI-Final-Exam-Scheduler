from App.database import db

class Exam(db.Model):
    __tablename__ = "exams"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    courseCode= db.Column(db.String(20), db.ForeignKey('courses.courseCode'), nullable=False)
    date = db.Column(db.Date, nullable=True, index=True)
    time = db.Column(db.Integer, nullable=False) 
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False, index=True)
    exam_length = db.Column(db.Integer, nullable=False)
    number_of_students = db.Column(db.Integer, nullable=False)
    
    course = db.relationship('Course', back_populates='exams')
    venue = db.relationship("Venue", back_populates="exams")

    def __init__(self, courseCode, date, time, venue_id, exam_length, number_of_students):
        self.courseCode = courseCode
        self.date = date
        self.time = time
        self.venue_id = venue_id
        self.exam_length = exam_length
        self.number_of_students = number_of_students