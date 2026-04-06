from App.models import Student
import csv
from App.database import db

def import_students_from_csv(file_path):
    existing_student_ids = {
        sid for (sid,) in db.session.query(Student.student_id).all()
    }
    inserted = 0
    skipped_existing = 0

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)    
        students = []
        for row in reader:
            if not row.get("Student ID"):
                raise ValueError(f"Missing required fields in row: {row}")
            
            student_id = row.get("Student ID")

            if len(str(student_id)) != 9:
                raise ValueError("student_id must be exactly 9 digits")
            
            if not str(student_id).isdigit():
                raise ValueError("student_id must contain only digits (no letters or other characters)")
            
            student_id = int(student_id)

            if student_id in existing_student_ids:
                skipped_existing += 1
                continue

            students.append(Student(student_id=student_id))
            existing_student_ids.add(student_id)
            inserted += 1
            
            if len(students) == 1000:
                db.session.bulk_save_objects(students)
                db.session.commit()
                students = []
        try:
            if students:
                db.session.bulk_save_objects(students)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return (
            f"Students imported successfully! Added {inserted} new students. "
            f"Skipped {skipped_existing} existing students."
        )

def create_student(student_id):
    if len(str(student_id)) != 9:
        raise ValueError("student_id must be exactly 9 digits")
    
    if not str(student_id).isdigit():
        raise ValueError("student_id must contain only digits (no letters or other characters)")
    
    student_id = int(student_id)
    
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