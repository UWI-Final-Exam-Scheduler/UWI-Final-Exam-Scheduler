import pytest
from App.controllers.courses import normalize_course_code, create_course, get_course_by_code,get_subject_codes

def test_normalize_course_code_lowercase():
    assert normalize_course_code("comp1600") == "COMP1600"


def test_normalize_course_code_already_uppercase():
    assert normalize_course_code("COMP1600") == "COMP1600"


def test_normalize_course_code_invalid_length():
    with pytest.raises(Exception):
        normalize_course_code("CO1600")  

def test_normalize_course_code_too_long():
    with pytest.raises(Exception):
        normalize_course_code("COMP16000") 


def test_normalize_course_code_invalid_format():
    with pytest.raises(Exception):
        normalize_course_code("1600COMP")  

def test_create_course_success(empty_db):
    msg = create_course("comp1600", "Introduction to Computing")
    assert msg == "Course COMP1600 created successfully!"


def test_create_course_duplicate(empty_db):
    create_course("COMP1600", "Introduction to Computing")

    with pytest.raises(ValueError):
        create_course("COMP1600", "Introduction to Computing")

def test_get_course_by_code_success(empty_db):
    create_course("COMP1600", "Intro to Computing")
    result = get_course_by_code("comp1600")
    assert result["courseCode"] == "COMP1600"
    assert result["name"] == "Intro to Computing"
    assert result["enrolledStudents"] == "0"


def test_get_course_by_code_not_found(empty_db):
    result = get_course_by_code("COMP1600")
    assert result == "Course with code COMP1600 not found."

def test_get_subject_codes(empty_db):
    create_course("COMP1600", "Intro to Computing")
    create_course("MATH1140", "Calculus")
    result = get_subject_codes()
    assert "COMP" in result
    assert "MATH" in result