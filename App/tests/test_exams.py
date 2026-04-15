from datetime import date, datetime
import pytest
from App.database import db
from App.models import Venue, Exam
from App.controllers.exams import (
    get_all_exams,
    get_exams_by_date,
    reschedule_exam,
    get_exams_that_need_rescheduling,
    get_all_days_with_exams,
    split_exam,
    merge_exams
)


def create_exam(course="COMP1600", admin_id=None, students=50, exam_date=None, time=9, venue_id=None):
    exam = Exam(
        courseCode=course,
        admin_id=admin_id,
        number_of_students=students,
        date=exam_date,
        time=time,
        venue_id=venue_id,
        exam_length=2
    )
    db.session.add(exam)
    db.session.commit()
    return exam


def create_venue(capacity=200):
    venue = Venue(name="Test Room", capacity=capacity)
    db.session.add(venue)
    db.session.commit()
    return venue


def test_get_all_exams_empty(empty_db):
    result = get_all_exams()
    assert result == "No exams found."


def test_get_all_exams_success(empty_db):
    create_exam()
    result = get_all_exams()
    assert isinstance(result, list)
    assert result[0]["courseCode"] == "COMP1600"


def test_get_exams_by_date_none(empty_db):
    result = get_exams_by_date("2025-01-01")
    assert result == []


def test_get_exams_by_date_success(empty_db):
    d = date(2025, 5, 1)
    create_exam(exam_date=d)
    result = get_exams_by_date("2025-05-01")
    assert len(result) == 1
    assert result[0]["exam_date"] == "2025-05-01"


def test_reschedule_exam_not_found(empty_db):
    exam, err = reschedule_exam(999)
    assert exam is None
    assert "not found" in err


def test_reschedule_exam_unschedule(empty_db):
    exam = create_exam(exam_date=date(2025,5,1), time=9, venue_id=1)
    updated, err = reschedule_exam(exam.id, unschedule=True)

    assert err is None
    assert updated.date is None
    assert updated.time == 0
    assert updated.venue_id is None


def test_reschedule_exam_invalid_time(empty_db):
    exam = create_exam()
    updated, err = reschedule_exam(exam.id, time=10)
    assert updated is None
    assert "Invalid time slot" in err


def test_reschedule_exam_weekend_block(empty_db):
    exam = create_exam()
    # 2025-05-03 is a Saturday
    updated, err = reschedule_exam(exam.id, date_str="2025-05-03")
    assert updated is None
    assert "weekends" in err


def test_reschedule_exam_success(empty_db):
    venue = create_venue()
    exam = create_exam()

    updated, err = reschedule_exam(
        exam.id,
        date_str="2025-05-01",
        time=9,
        venue_id=venue.id
    )

    assert err is None
    assert updated.date.strftime("%Y-%m-%d") == "2025-05-01"
    assert updated.time == 9


def test_reschedule_exam_merge_success(empty_db):
    venue = create_venue(capacity=200)

    e1 = create_exam(students=50)
    e2 = create_exam(students=30)

    reschedule_exam(e1.id, "2025-05-01", 9, venue.id)
    merged, err = reschedule_exam(e2.id, "2025-05-01", 9, venue.id)

    assert err is None
    assert merged.number_of_students == 80


def test_reschedule_exam_merge_exceeds_capacity(empty_db):
    venue = create_venue(capacity=60)

    e1 = create_exam(students=50)
    e2 = create_exam(students=30)

    reschedule_exam(e1.id, "2025-05-01", 9, venue.id)
    updated, err = reschedule_exam(e2.id, "2025-05-01", 9, venue.id)

    assert updated is None
    assert "exceeds venue capacity" in err


def test_get_exams_that_need_rescheduling(empty_db):
    result = get_exams_that_need_rescheduling()
    assert result == []


def test_get_exams_that_need_rescheduling_success(empty_db):
    create_exam()
    result = get_exams_that_need_rescheduling()
    assert len(result) == 1


def test_get_all_days_with_exams(empty_db):
    result = get_all_days_with_exams()
    assert result == []


def test_get_all_days_with_exams_success(empty_db):
    create_exam(exam_date=date(2025,5,1))
    result = get_all_days_with_exams()
    assert "2025-05-01" in result


def test_split_exam_invalid_id(empty_db):
    result, err = split_exam(999, [])
    assert result is None
    assert "No exam found" in err


def test_split_exam_invalid_split_count(empty_db):
    exam = create_exam()
    result, err = split_exam(exam.id, [{"number_of_students": 10}])
    assert result is None
    assert "between 2 and 4" in err


def test_split_exam_total_mismatch(empty_db):
    exam = create_exam(students=50)
    splits = [{"number_of_students": 20}, {"number_of_students": 20}]
    result, err = split_exam(exam.id, splits)
    assert result is None
    assert "must equal the total" in err


def test_split_exam_success(empty_db):
    exam = create_exam(students=50)
    splits = [
        {"number_of_students": 20},
        {"number_of_students": 30}
    ]

    new_exams, err = split_exam(exam.id, splits)

    assert err is None
    assert len(new_exams) == 2


def test_merge_exams_invalid_count(empty_db):
    result, err = merge_exams([1])
    assert result is None
    assert "At least 2 exam IDs" in err


def test_merge_exams_different_courses(empty_db):
    e1 = create_exam(course="COMP1600")
    e2 = create_exam(course="MATH1140")

    result, err = merge_exams([e1.id, e2.id])
    assert result is None
    assert "must share the same courseCode" in err


def test_merge_exams_success(empty_db):
    e1 = create_exam(students=20)
    e2 = create_exam(students=30)

    result, err = merge_exams([e1.id, e2.id])

    assert err is None
    assert result.number_of_students == 50