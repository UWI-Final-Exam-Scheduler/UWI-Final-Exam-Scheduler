from App.models import Course
import csv
from App.database import db

def normalize_course_code(courseCode):
    if len(courseCode) != 8:
        raise Exception("courseCode must be exactly 8 characters (e.g. COMP1600)")

    letters = courseCode[:4]
    numbers = courseCode[4:]

    if not letters.isalpha() or not numbers.isdigit():
        raise Exception("courseCode must be 4 letters followed by 4 digits (e.g. COMP1600)")

    return letters.upper() + numbers

def import_courses_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)               
        for row in reader:
            if not row.get("Subj Code") or not row.get("Crse Numb") or not row.get("Title"):
                raise ValueError(f"Missing required fields in row: {row}")
            
            subject_code = str(row.get("Subj Code")).strip()
            course_number = str(row.get("Crse Numb")).strip()

            courseCode = f"{subject_code}{course_number}"
            courseCode = normalize_course_code(courseCode)

            title = str(row.get("Title")).strip()
            
            existing = Course.query.filter_by(courseCode=courseCode).first()
            if not existing:
                course = Course(courseCode=courseCode, name=title)
                db.session.add(course)
        try:
            db.session.commit()    
        except Exception as e:
            db.session.rollback()
            raise e
        return "Courses imported successfully!"
    
def create_course(courseCode, name):
    courseCode = normalize_course_code(courseCode)
    
    existing = Course.query.filter_by(courseCode=courseCode).first()
    if existing:
        raise ValueError(f"Course with code {courseCode} already exists.")
    
    course = Course(courseCode=courseCode, name=name)
    db.session.add(course)
    try:
        db.session.commit()    
    except Exception as e:
        db.session.rollback()
        raise e
    return f"Course {courseCode} created successfully!"