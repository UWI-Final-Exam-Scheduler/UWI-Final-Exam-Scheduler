from App.controllers.students import import_students_from_csv
from App.models import Student
import pytest

def test_import_students_from_csv_success(empty_db, tmp_path):
    # Create a temporary CSV file
    csv_content = """Student ID\n123456780\n123456781\n123456782\n"""
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_content)

    msg = import_students_from_csv(str(csv_file))
    assert "Added 3 new students" in msg
    assert "Skipped 0 existing students" in msg
    # Check students in DB
    students = Student.query.all()
    assert len(students) == 3
    assert set([s.student_id for s in students]) == {123456780, 123456781, 123456782}

def test_import_students_from_csv_duplicates(empty_db, tmp_path):
    csv_content = """Student ID\n123456780\n123456781\n"""
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_content)
    # First import
    import_students_from_csv(str(csv_file))
    # Second import (should skip duplicates)
    msg = import_students_from_csv(str(csv_file))
    assert "Added 0 new students" in msg
    assert "Skipped 2 existing students" in msg

def test_import_students_from_csv_invalid_id(empty_db, tmp_path):
    csv_content = """Student ID\n12345\n"""
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_content)
    with pytest.raises(ValueError):
        import_students_from_csv(str(csv_file))