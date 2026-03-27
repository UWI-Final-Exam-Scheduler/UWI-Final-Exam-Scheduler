import pytest
from App.controllers.courses import normalize_course_code, create_course

'''
   Unit Tests
'''

def test_normalize_course_code_lowercase():
    assert normalize_course_code("comp1600") == "COMP1600"


def test_normalize_course_code_already_uppercase():
    assert normalize_course_code("COMP1600") == "COMP1600"


def test_normalize_course_code_invalid_length():
    with pytest.raises(Exception):
        normalize_course_code("CO1600")  # 1 character short

def test_normalize_course_code_too_long():
    with pytest.raises(Exception):
        normalize_course_code("COMP16000") # 1 character longer


def test_normalize_course_code_invalid_format():
    with pytest.raises(Exception):
        normalize_course_code("1600COMP")  # wrong format

def test_create_course_success(empty_db):
    msg = create_course("comp1600", "Introduction to Computing")
    assert msg == "Course COMP1600 created successfully!"


def test_create_course_duplicate(empty_db):
    create_course("COMP1600", "Introduction to Computing")

    with pytest.raises(ValueError):
        create_course("COMP1600", "Introduction to Computing")