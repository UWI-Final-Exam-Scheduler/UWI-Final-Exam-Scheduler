import os
import pytest
from App.database import db
from App.models import Enrollment, Student, Course
from App.controllers.enrollments import import_enrollments_from_csv

def test_import_enrollments_success(empty_db, tmp_path):
    # Setup students and courses
    db.session.add(Student(student_id=123456789))
    db.session.add(Course(courseCode="COMP1600", name="Intro to Computing"))
    db.session.commit()

    csv_content = """Student ID,Course Code\n123456789,COMP1600\n"""
    csv_file = tmp_path / "enrollments.csv"
    csv_file.write_text(csv_content)

    msg = import_enrollments_from_csv(str(csv_file))
    assert "Added 1 new enrollments" in msg
    assert "Skipped 0 existing enrollments" in msg
    enrollments = Enrollment.query.all()
    assert len(enrollments) == 1
    assert enrollments[0].student_id == 123456789
    assert enrollments[0].courseCode == "COMP1600"

def test_import_enrollments_duplicate(empty_db, tmp_path):
    db.session.add(Student(student_id=123456789))
    db.session.add(Course(courseCode="COMP1600", name="Intro to Computing"))
    db.session.commit()
    csv_content = """Student ID,Course Code\n123456789,COMP1600\n"""
    csv_file = tmp_path / "enrollments.csv"
    csv_file.write_text(csv_content)
    import_enrollments_from_csv(str(csv_file))
    msg = import_enrollments_from_csv(str(csv_file))
    assert "Added 0 new enrollments" in msg
    assert "Skipped 1 existing enrollments" in msg

def test_import_enrollments_invalid_student(empty_db, tmp_path):
    from App.models import Course
    db.session.add(Course(courseCode="COMP1600", name="Intro to Computing"))
    db.session.commit()
    csv_content = """Student ID,Course Code\n123456789,COMP1600\n"""
    csv_file = tmp_path / "enrollments.csv"
    csv_file.write_text(csv_content)
    with pytest.raises(ValueError):
        import_enrollments_from_csv(str(csv_file))

def test_import_enrollments_invalid_course(empty_db, tmp_path):
    db.session.add(Student(student_id=123456789))
    db.session.commit()
    csv_content = """Student ID,Course Code\n123456789,COMP1600\n"""
    csv_file = tmp_path / "enrollments.csv"
    csv_file.write_text(csv_content)
    with pytest.raises(ValueError):
        import_enrollments_from_csv(str(csv_file))

def test_import_enrollments_invalid_id_length(empty_db, tmp_path):
    db.session.add(Student(student_id=123456789))
    db.session.add(Course(courseCode="COMP1600", name="Intro to Computing"))
    db.session.commit()
    csv_content = """Student ID,Course Code\n12345,COMP1600\n"""
    csv_file = tmp_path / "enrollments.csv"
    csv_file.write_text(csv_content)
    with pytest.raises(ValueError):
        import_enrollments_from_csv(str(csv_file))