from App.models import Enrollment, Student, Course
from App.controllers import normalize_course_code
import csv
from App.database import db

def import_enrollments_from_csv(file_path):
    # Load all existing student IDs and course codes for faster validation
    existing_student_ids = set([s.student_id for s in Student.query.with_entities(Student.student_id).all()]) 
    existing_course_codes = set([c.courseCode for c in Course.query.with_entities(Course.courseCode).all()])
    
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        enrollments = []

        for row in reader:
            if not row.get("Student ID") or not row.get("Course Code"):
                raise ValueError(f"Missing required fields in row: {row}")
            
            student_id = row.get("Student ID")

            if len(str(student_id)) != 9:
                raise ValueError("student_id must be exactly 9 digits")
    
            if not str(student_id).isdigit():
                raise ValueError("student_id must contain only digits (no letters or other characters)")
            
            student_id = int(student_id)

            course_code = row.get("Course Code")
            course_code = normalize_course_code(course_code)

            if student_id not in existing_student_ids:
                raise ValueError(f"Student with ID {student_id} does not exist.")
            
            if course_code not in existing_course_codes:
                raise ValueError(f"Course with code {course_code} does not exist.")

            enrollments.append(Enrollment(student_id=student_id, courseCode=course_code))

            if len(enrollments) == 1000:
                db.session.bulk_save_objects(enrollments)
                db.session.commit()
                enrollments = []
        try:
            if enrollments:
                db.session.bulk_save_objects(enrollments)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return "Enrollments imported successfully!"

# def import_enrollments_from_csv(file_path):
#     # Load all existing student IDs and course codes
#     existing_student_ids = set([s.student_id for s in Student.query.with_entities(Student.student_id).all()])
#     existing_course_codes = set([c.courseCode for c in Course.query.with_entities(Course.courseCode).all()])
#     # # Load all existing enrollments as (student_id, courseCode) tuples
#     # existing_enrollments = set([(e.student_id, e.courseCode) for e in Enrollment.query.with_entities(Enrollment.student_id, Enrollment.courseCode).all()])

#     with open(file_path, newline='') as csvfile:
#         reader = csv.DictReader(csvfile)   
#         enrollments = []            
#         for row in reader:
#             if not row.get("Student ID") or not row.get("Course Code"):
#                 raise ValueError(f"Missing required fields in row: {row}")
            
#             student_id = row.get("Student ID")

#             if len(str(student_id)) != 9:
#                 raise ValueError("student_id must be exactly 9 digits")
    
#             if not str(student_id).isdigit():
#                 raise ValueError("student_id must contain only digits (no letters or other characters)")
            
#             student_id = int(student_id)

#             course_code = row.get("Course Code")
#             course_code = normalize_course_code(course_code)

#             existing_student = Student.query.filter_by(student_id=student_id).first()
#             if not existing_student:
#                 raise ValueError(f"Student with ID {student_id} does not exist.")
            
#             existing_course = Course.query.filter_by(courseCode=course_code).first()
#             if not existing_course:
#                 raise ValueError(f"Course with code {course_code} does not exist.")
            
#             existing = Enrollment.query.filter_by(student_id=student_id, courseCode=course_code).first()
#             if not existing:
#                 enrollments.append(Enrollment(student_id=student_id, courseCode=course_code))
             
#             if len(enrollments) == 1000:
#                 db.session.bulk_save_objects(enrollments)
#                 db.session.commit()
#                 enrollments = []
#         try:
#             if enrollments:
#                 db.session.bulk_save_objects(enrollments)
#                 db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             raise e
#         return "Enrollments imported successfully!"
    
def create_enrollment(student_id, course_code):
    if len(str(student_id)) != 9:
        raise ValueError("student_id must be exactly 9 digits")
    
    if not str(student_id).isdigit():
        raise ValueError("student_id must contain only digits (no letters or other characters)")
    
    student_id = int(student_id)
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

def get_all_enrollments():
    enrollments = Enrollment.query.all()

    if not enrollments:
        return []
    
    enrollment_json = []
    for enrollment in enrollments:
        enrollment_json.append({
            "student_id": enrollment.student_id,
            "courseCode": enrollment.courseCode
        })
    
    return enrollment_json

def get_enrollments_by_student(student_id):
    if len(str(student_id)) != 9:
        raise ValueError("student_id must be exactly 9 digits")
    
    if not str(student_id).isdigit():
        raise ValueError("student_id must contain only digits (no letters or other characters)")
    
    student_id = int(student_id)

    enrollments = Enrollment.query.filter_by(student_id=student_id).all()

    if not enrollments:
        return []
    
    enrollment_json = []
    for enrollment in enrollments:
        enrollment_json.append({
            "student_id": enrollment.student_id,
            "courseCode": enrollment.courseCode
        })
    
    return enrollment_json