from App.models import Student
import csv
from App.database import db

def import_students_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)               
        for row in reader:
            if not row.get("Student ID"):
                raise ValueError(f"Missing required fields in row: {row}")
            
            student_id = int(row.get("Student ID"))
            
            existing = Student.query.filter_by(student_id=student_id).first()
            if not existing:
                student = Student(student_id=student_id)
                db.session.add(student)
        try:
            db.session.commit()    
        except Exception as e:
            db.session.rollback()
            raise e
        return "Students imported successfully!"
    
def create_student(student_id):
    if len(str(student_id)) != 9:
        raise ValueError("student_id must be exactly 9 digits")
    
    existing = Student.query.filter_by(student_id=student_id).first()
    if existing:
        raise ValueError(f"Student with ID {student_id} already exists.")
    
    student = Student(student_id=student_id)
    db.session.add(student)
    try:
        db.session.commit()    
    except Exception as e:
        db.session.rollback()
        raise e
    return f"Student {student_id} created successfully!"