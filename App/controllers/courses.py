from App.models import Course, Enrollment
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

def get_all_courses():
    courses = db.session.query(Course).all()
    if not courses: 
        return f"No courses found."
    course_json = []
    for course in courses:
        course_json.append({
            "courseCode": course.courseCode,
            "name": course.name
        })
    return course_json

def get_course_by_code(courseCode):
    courseCode = normalize_course_code(courseCode)
    course = db.session.query(Course).filter_by(courseCode=courseCode).first()
    if not course:
        return f"Course with code {courseCode} not found."
    students = len(db.session.query(Enrollment).filter_by(courseCode=courseCode).all())
    return {
        "courseCode": course.courseCode,
        "name": course.name,
        "enrolledStudents": str(students)
    }

def get_courses_by_subject(subjectCode):
    subjectCode = subjectCode.upper()
    courses = db.session.query(Course).filter(Course.courseCode.startswith(subjectCode)).all()
    if not courses:
        return f"No courses found for subject {subjectCode}."
    courses_json = []
    for course in courses:
        course_data = get_course_by_code(course.courseCode)
        if course_data:
            courses_json.append(course_data)
    return courses_json

    