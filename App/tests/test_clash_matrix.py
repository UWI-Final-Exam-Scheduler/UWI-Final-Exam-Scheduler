import pytest
from App.controllers.clash_matrix import (
    create_clash_matrix, view_conflicting_courses, view_course_clashes, normalize_percentage_threshold, absolute_threshold, exceeds_percentage_threshold
)
from App.models.clash_matrix import ClashMatrix
from App.models.enrollment import Enrollment
from App.database import db

def test_create_clash_matrix_basic(empty_db):
    enrollments = [
        (1, "COMP1600"), (1, "MATH1140"), (2, "COMP1600"), (2, "MATH1140"), (2, "INFO1600")
    ]
    db.session.bulk_save_objects([Enrollment(student_id=s, courseCode=c) for s, c in enrollments])
    db.session.commit()
    clash_matrix = create_clash_matrix([(e.student_id, e.courseCode) for e in Enrollment.query.all()])
    assert clash_matrix["COMP1600"]["MATH1140"] == 2
    assert clash_matrix["MATH1140"]["COMP1600"] == 2
    assert clash_matrix["COMP1600"]["INFO1600"] == 1
    assert clash_matrix["INFO1600"]["COMP1600"] == 1

def test_create_clash_matrix_empty(empty_db):
    clash_matrix = create_clash_matrix([])
    assert clash_matrix == {}
    assert ClashMatrix.query.count() == 0

def test_create_clash_matrix_idempotent(empty_db):
    enrollments = [(1, "COMP1600"), (1, "MATH1140")]
    db.session.bulk_save_objects([Enrollment(student_id=s, courseCode=c) for s, c in enrollments])
    db.session.commit()
    create_clash_matrix([(e.student_id, e.courseCode) for e in Enrollment.query.all()])
    create_clash_matrix([(e.student_id, e.courseCode) for e in Enrollment.query.all()])
    assert ClashMatrix.query.count() == 1

def test_view_conflicting_courses_none(empty_db):
    result = view_conflicting_courses(abs_threshold=1)
    assert result["total_conflicts"] == 0
    assert result["conflicting_courses"] == []

def test_view_conflicting_courses_with_conflict(empty_db):
    enrollments = [
        (1, "COMP1600"), (1, "MATH1140"), (2, "COMP1600"), (2, "MATH1140")
    ]
    db.session.bulk_save_objects([Enrollment(student_id=s, courseCode=c) for s, c in enrollments])
    db.session.commit()
    create_clash_matrix([(e.student_id, e.courseCode) for e in Enrollment.query.all()])
    result = view_conflicting_courses(abs_threshold=1)
    assert result["total_conflicts"] == 1
    assert result["conflicting_courses"][0]["clash_count"] == 2

def test_view_course_clashes_found(empty_db):
    enrollments = [
        (1, "COMP1600"), (1, "MATH1140"), (2, "COMP1600"), (2, "MATH1140")
    ]
    db.session.bulk_save_objects([Enrollment(student_id=s, courseCode=c) for s, c in enrollments])
    db.session.commit()
    create_clash_matrix([(e.student_id, e.courseCode) for e in Enrollment.query.all()])
    result = view_course_clashes("COMP1600", abs_threshold=1)
    assert result["total_clashes"] == 1
    assert result["clashes"][0]["clash_count"] == 2

def test_view_course_clashes_not_found(empty_db):
    result = view_course_clashes("NONEXIST", abs_threshold=1)
    assert isinstance(result, str)
    assert "No clashes found" in result

def test_normalize_percentage_threshold():
    assert normalize_percentage_threshold(0.2) == 0.2
    assert normalize_percentage_threshold(20) == 0.2
    assert normalize_percentage_threshold(1) == 1
    with pytest.raises(ValueError):
        normalize_percentage_threshold(-1)
    with pytest.raises(ValueError):
        normalize_percentage_threshold(200)

def test_absolute_threshold_true():
    assert absolute_threshold(6, abs_threshold=5) is True

def test_absolute_threshold_false():
    assert absolute_threshold(4, abs_threshold=5) is False

def test_exceeds_percentage_threshold_true():
    enrollment_count = {"COMP1600": 10, "MATH1140": 20}
    assert exceeds_percentage_threshold(2, enrollment_count, "COMP1600", "MATH1140", perc_thresh=0.1) is True

def test_exceeds_percentage_threshold_zero_class():
    enrollment_count = {"COMP1600": 0, "MATH1140": 20}
    assert exceeds_percentage_threshold(2, enrollment_count, "COMP1600", "MATH1140", perc_thresh=0.1) is False