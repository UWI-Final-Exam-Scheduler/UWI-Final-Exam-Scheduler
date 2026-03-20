from App.models import Course, Enrollment
import csv
from App.database import db
from collections import Counter

def normalize_course_code(courseCode):
    if len(courseCode) not in [7, 8]:
        raise Exception("courseCode must be 3 or 4 letters followed by 4 digits (e.g. LAW1010 or COMP1600)")

    letters = courseCode[:-4]
    numbers = courseCode[-4:]

    if not letters.isalpha() or not numbers.isdigit():
        raise Exception("courseCode must be 4 letters followed by 4 digits (e.g. COMP1600)")

    return letters.upper() + numbers

def import_courses_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)   
        courses = []            
        for row in reader:
            if not row.get("Subj Code") or not row.get("Crse Numb") or not row.get("Title"):
                raise ValueError(f"Missing required fields in row: {row}")

            subject_code = str(row.get("Subj Code")).strip()
            course_number = str(row.get("Crse Numb")).strip()

            courseCode = f"{subject_code}{course_number}"
            courseCode = normalize_course_code(courseCode)

            title = str(row.get("Title")).strip()

            courses.append(Course(courseCode=courseCode, name=title))

            if len(courses) == 1000:
                db.session.bulk_save_objects(courses)
                db.session.commit()
                courses = []
        try:
            if courses:
                db.session.bulk_save_objects(courses)
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

def get_all_courses(page=1, per_page=20):
    courses = db.session.query(Course).paginate(page=page, per_page=per_page)
    if not courses:
        return f"No courses found."

    course_list = list(courses)
    course_codes = [course.courseCode for course in course_list]
    enrollments = db.session.query(Enrollment.courseCode).filter(Enrollment.courseCode.in_(course_codes)).all()
    enrollment_counts = Counter(e.courseCode for e in enrollments)

    course_json = []
    for course in course_list:
        course_json.append({
            "courseCode": course.courseCode,
            "name": course.name,
            "enrolledStudents": str(enrollment_counts.get(course.courseCode, 0))
        })
    return {
        'page': courses.page,
        'per_page': courses.per_page,
        'total': courses.total,
        'pages': courses.pages,
        'has_next': courses.has_next,
        'has_prev': courses.has_prev,
        'courses': course_json
    }

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

def get_courses_by_subject(subjectCode, page=1, per_page=20):
    subjectCode = subjectCode.upper()
    pagination = db.session.query(Course).filter(Course.courseCode.startswith(subjectCode)).paginate(page=page, per_page=per_page)
    if not pagination.items:
        return f"No courses found for subject {subjectCode}."

    course_codes = [c.courseCode for c in pagination.items]
    enrollments = db.session.query(Enrollment.courseCode).filter(Enrollment.courseCode.in_(course_codes)).all()
    enrollment_counts = Counter(e.courseCode for e in enrollments)

    return {
        'courses': [
            {
                'courseCode': c.courseCode,
                'name': c.name,
                'enrolledStudents': str(enrollment_counts.get(c.courseCode, 0))
            }
            for c in pagination.items
        ],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }

def get_subject_codes():
    subject_codes = db.session.query(Course.courseCode).distinct().all()
    if not subject_codes:
        return "No subject codes found."
    return sorted(set(code[0][:4] for code in subject_codes))

    