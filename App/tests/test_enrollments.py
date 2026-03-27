import pytest
from App.database import db
from App.models import Student, Course
from App.controllers.enrollments import create_enrollment

def test_create_enrollment_success(empty_db):
    student = Student(student_id=123456789)
    course = Course(courseCode="COMP1600", name="Intro to Computing")

    db.session.add(student)
    db.session.add(course)
    db.session.commit()

    msg = create_enrollment(123456789, "COMP1600")
    assert "created successfully" in msg


def test_invalid_student_id_length(empty_db):
    with pytest.raises(ValueError):
        create_enrollment(12345, "COMP1600")


def test_student_not_found(empty_db):
    course = Course(courseCode="COMP1600", name="Intro to Computing")
    db.session.add(course)
    db.session.commit()

    with pytest.raises(ValueError):
        create_enrollment(123456789, "COMP1600")


def test_course_not_found(empty_db):
    student = Student(student_id=123456789)
    db.session.add(student)
    db.session.commit()

    with pytest.raises(ValueError):
        create_enrollment(123456789, "COMP1600")