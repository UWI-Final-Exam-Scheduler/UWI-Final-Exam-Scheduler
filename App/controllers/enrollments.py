from App.controllers.exams import sync_exams_with_enrollment_data
from App.models import Enrollment, Student, Course
from App.controllers import normalize_course_code
import csv
from App.database import db
from App.controllers.clash_matrix import create_clash_matrix
import csv

def import_enrollments_from_csv(file_path):
    # Load all existing student IDs and course codes for faster validation
    existing_student_ids = set([s.student_id for s in Student.query.with_entities(Student.student_id).all()]) 
    existing_course_codes = set([c.courseCode for c in Course.query.with_entities(Course.courseCode).all()])
    existing_enrollments = {
        (student_id, course_code)
        for student_id, course_code in db.session.query(Enrollment.student_id, Enrollment.courseCode).all()
    }
    inserted = 0
    skipped_existing = 0

    parsed_rows = []

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

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

            parsed_rows.append((student_id, course_code))

        try:
            enrollments = []
            for student_id, course_code in parsed_rows:
                enrollment_key = (student_id, course_code)
                if enrollment_key in existing_enrollments:
                    skipped_existing += 1
                    continue

                enrollments.append(Enrollment(student_id=student_id, courseCode=course_code))
                existing_enrollments.add(enrollment_key)
                inserted += 1

                if len(enrollments) == 1000:
                    db.session.bulk_save_objects(enrollments)
                    db.session.commit()
                    enrollments = []

            if enrollments:
                db.session.bulk_save_objects(enrollments)
                db.session.commit()

            # Rebuild clash matrix using the current enrollment dataset.
            enrollment_rows = db.session.query(Enrollment.student_id, Enrollment.courseCode).all()
            create_clash_matrix(enrollment_rows)

            # update exam with latest enrollment data
            sync_exams_with_enrollment_data()
        except Exception as e:
            db.session.rollback()
            raise e
   
        return (
            f"Enrollments imported successfully! Added {inserted} new enrollments. "
            f"Skipped {skipped_existing} existing enrollments."
        )