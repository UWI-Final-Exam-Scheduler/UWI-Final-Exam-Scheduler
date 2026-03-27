from datetime import date
from App.database import db
from App.models import Course, Venue, Exam
from App.controllers.exams import get_exams_by_date, reschedule_exam


def test_get_exams_by_date(empty_db):
    course = Course(courseCode="COMP1600", name="Intro to Computing")
    venue = Venue(name="Room A", capacity=100)

    db.session.add(course)
    db.session.add(venue)
    db.session.commit()

    exam = Exam(
        courseCode="COMP1600",
        date=date(2026, 5, 4),
        time=4,
        venue_id=venue.id,
        exam_length=120,
        number_of_students=50
    )

    db.session.add(exam)
    db.session.commit()

    exams = get_exams_by_date("2026-05-04")

    assert len(exams) == 1
    assert exams[0]["courseCode"] == "COMP1600"


def test_reschedule_exam(empty_db):
    course = Course(courseCode="COMP1600", name="Intro to Computing")
    venue = Venue(name="Room A", capacity=100)

    db.session.add(course)
    db.session.add(venue)
    db.session.commit()

    exam = Exam(
        courseCode="COMP1600",
        date=date(2026, 5, 4),
        time=4,
        venue_id=venue.id,
        exam_length=120,
        number_of_students=50
    )

    db.session.add(exam)
    db.session.commit()

    updated_exam, error = reschedule_exam(
        "COMP1600",
        date_str="2026-05-10",
        time=9
    )

    assert error is None
    assert updated_exam.time == 9

def test_reschedule_exam_not_found(empty_db):
    updated_exam, error = reschedule_exam("COMP1600", date_str="2026-05-10")
    assert updated_exam is None
    assert error == "Exam with course code COMP1600 not found"

def test_reschedule_exam_no_values_given(empty_db):
    course = Course(courseCode="COMP1600", name="Intro to Computing")
    venue = Venue(name="Room A", capacity=100)
    db.session.add(course)
    db.session.add(venue)
    db.session.commit()

    exam = Exam(
        courseCode="COMP1600",
        date=date(2026, 5, 4),
        time=4,
        venue_id=venue.id,
        exam_length=120,
        number_of_students=50
    )
    db.session.add(exam)
    db.session.commit()

    updated_exam, error = reschedule_exam("COMP1600")
    assert updated_exam is None
    assert error == "At least one of date, time or venue_id is required"

def test_unschedule_exam(empty_db):
    course = Course(courseCode="COMP1600", name="Intro to Computing")
    venue = Venue(name="Room A", capacity=100)
    db.session.add(course)
    db.session.add(venue)
    db.session.commit()

    exam = Exam(
        courseCode="COMP1600",
        date=date(2026, 5, 4),
        time=4,
        venue_id=venue.id,
        exam_length=120,
        number_of_students=50
    )
    db.session.add(exam)
    db.session.commit()

    updated_exam, error = reschedule_exam("COMP1600", unschedule=True)
    assert error is None
    assert updated_exam.date is None
    assert updated_exam.time == 0

def test_get_exams_by_date_empty(empty_db):
    result = get_exams_by_date("2026-05-04")
    assert result == []