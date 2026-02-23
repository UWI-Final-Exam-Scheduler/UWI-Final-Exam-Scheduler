from App.models import Course
import csv
from App.database import db

def import_courses_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)               
        for row in reader:
            if not row.get("Subj Code") or not row.get("Crse Numb") or not row.get("Title"):
                raise ValueError(f"Missing required fields in row: {row}")
            
            subject_code = str(row.get("Subj Code")).strip()
            course_number = str(row.get("Crse Numb")).strip()

            courseCode = f"{subject_code}{course_number}"
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