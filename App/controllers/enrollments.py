from App.models import Enrollment, Student, Course
from App.controllers import normalize_course_code
import csv
from App.database import db

def import_enrollments_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)               
        for row in reader:
            if not row.get("Student ID") or not row.get("Course Code"):
                raise ValueError(f"Missing required fields in row: {row}")
            
            student_id = int(row.get("Student ID"))
            course_code = row.get("Course Code")

            existing_student = Student.query.filter_by(student_id=student_id).first()
            if not existing_student:
                raise ValueError(f"Student with ID {student_id} does not exist.")
            
            existing_course = Course.query.filter_by(courseCode=course_code).first()
            if not existing_course:
                raise ValueError(f"Course with code {course_code} does not exist.")
            
            existing = Enrollment.query.filter_by(student_id=student_id, courseCode=course_code).first()
            if not existing:
                enrollment = Enrollment(student_id=student_id, courseCode=course_code)
                db.session.add(enrollment)
        try:
            db.session.commit()    
        except Exception as e:
            db.session.rollback()
            raise e
        return "Enrollments imported successfully!"
    
def create_enrollment(student_id, course_code):
    if len(str(student_id)) != 9:
        raise ValueError("student_id must be exactly 9 digits")
    
    course_code = normalize_course_code(course_code)

    existing_student = Student.query.filter_by(student_id=student_id).first()
    if not existing_student:
        raise ValueError(f"Student with ID {student_id} does not exist.")
    
    existing_course = Course.query.filter_by(courseCode=course_code).first()
    if not existing_course:
        raise ValueError(f"Course with code {course_code} does not exist.")
    
    existing = Enrollment.query.filter_by(student_id=student_id, courseCode=course_code).first()
    if existing:
        raise ValueError(f"Enrollment for student {student_id} in course {course_code} already exists.")
    
    enrollment = Enrollment(student_id=student_id, courseCode=course_code)
    db.session.add(enrollment)
    try:
        db.session.commit()    
    except Exception as e:
        db.session.rollback()
        raise e
    return f"Enrollment for student {student_id} in course {course_code} created successfully!"