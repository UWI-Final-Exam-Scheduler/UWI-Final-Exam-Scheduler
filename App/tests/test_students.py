import pytest
from App.controllers.students import create_student

def test_create_student_success(empty_db):
    msg = create_student(123456789)
    assert msg == "Student 123456789 created successfully!"

def test_create_student_duplicate(empty_db):
    create_student(123456789)
    with pytest.raises(ValueError):
        create_student(123456789)