from App.database import db

class ClashMatrix(db.Model):
    __tablename__ = "clash_matrix"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    course1 = db.Column(db.String(20), db.ForeignKey('courses.courseCode'), nullable=False) 
    course2 = db.Column(db.String(20), db.ForeignKey('courses.courseCode'), nullable=False) 
    clash_count = db.Column(db.Integer, nullable=False, default=0)

    courseCode1 = db.relationship('Course', foreign_keys=[course1])
    courseCode2 = db.relationship('Course', foreign_keys=[course2])

    __table_args__ = (db.UniqueConstraint('course1', 'course2', name='course_clash'),) #tuple containing one object to ensure unique combinations

    def __init__(self, course1, course2, clash_count=0):
        self.course1 = course1
        self.course2 = course2
        self.clash_count = clash_count