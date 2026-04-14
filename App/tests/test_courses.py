import pytest
from App.controllers.courses import normalize_course_code, import_courses_from_csv, get_course_by_code, get_subject_codes, get_all_courses, get_courses_by_subject, course_exists
from App.models import Course, Enrollment
from App.database import db

def test_import_courses_success(empty_db, tmp_path):
    csv_content = """Subj Code,Crse Numb,Title\nCOMP,1600,Intro to Computing\nMATH,1140,Calculus\n"""
    csv_file = tmp_path / "courses.csv"
    csv_file.write_text(csv_content)

    msg = import_courses_from_csv(str(csv_file))
    assert "Added 2 new courses" in msg
    assert "Skipped 0 existing courses" in msg
    courses = Course.query.all()
    assert len(courses) == 2
    assert set([c.courseCode for c in courses]) == {"COMP1600", "MATH1140"}
    assert set([c.name for c in courses]) == {"Intro to Computing", "Calculus"}

def test_import_courses_duplicate(empty_db, tmp_path):
    csv_content = """Subj Code,Crse Numb,Title\nCOMP,1600,Intro to Computing\n"""
    csv_file = tmp_path / "courses.csv"
    csv_file.write_text(csv_content)
    import_courses_from_csv(str(csv_file))
    msg = import_courses_from_csv(str(csv_file))
    assert "Added 0 new courses" in msg
    assert "Skipped 1 existing courses" in msg

def test_import_courses_invalid_row(empty_db, tmp_path):
    csv_content = """Subj Code,Crse Numb,Title\n,1600,Intro to Computing\n"""
    csv_file = tmp_path / "courses.csv"
    csv_file.write_text(csv_content)
    with pytest.raises(ValueError):
        import_courses_from_csv(str(csv_file))

def test_get_course_by_code_success_import(empty_db, tmp_path):
    csv_content = """Subj Code,Crse Numb,Title\nCOMP,1600,Intro to Computing\n"""
    csv_file = tmp_path / "courses.csv"
    csv_file.write_text(csv_content)
    import_courses_from_csv(str(csv_file))
    result = get_course_by_code("comp1600")
    assert result["courseCode"] == "COMP1600"
    assert result["name"] == "Intro to Computing"
    assert result["enrolledStudents"] == "0"

def test_get_course_by_code_not_found_import(empty_db):
    result = get_course_by_code("COMP1600")
    assert result == "Course with code COMP1600 not found."

def test_get_subject_codes_import(empty_db, tmp_path):
    csv_content = """Subj Code,Crse Numb,Title\nCOMP,1600,Intro to Computing\nMATH,1140,Calculus\n"""
    csv_file = tmp_path / "courses.csv"
    csv_file.write_text(csv_content)
    import_courses_from_csv(str(csv_file))
    result = get_subject_codes()
    assert "COMP" in result
    assert "MATH" in result

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

def test_get_all_courses_empty(empty_db):
    result = get_all_courses()
    assert isinstance(result, dict)
    assert result["courses"] == []
    assert result["total"] == 0

def test_get_all_courses_with_courses_and_enrollments(empty_db):
    c1 = Course(courseCode="COMP1600", name="Intro to Computing")
    c2 = Course(courseCode="MATH1140", name="Calculus")
    db.session.add_all([c1, c2])
    db.session.commit()
    # Add enrollments
    db.session.add(Enrollment(student_id=1, courseCode="COMP1600"))
    db.session.add(Enrollment(student_id=2, courseCode="COMP1600"))
    db.session.add(Enrollment(student_id=3, courseCode="MATH1140"))
    db.session.commit()
    result = get_all_courses()
    assert result["total"] == 2
    codes = {c["courseCode"] for c in result["courses"]}
    assert codes == {"COMP1600", "MATH1140"}
    for c in result["courses"]:
        if c["courseCode"] == "COMP1600":
            assert c["enrolledStudents"] == "2"
        if c["courseCode"] == "MATH1140":
            assert c["enrolledStudents"] == "1"

def test_get_all_courses_pagination(empty_db):
    for i in range(25):
        db.session.add(Course(courseCode=f"COMP1{i:03}", name=f"Course {i}"))
    db.session.commit()
    result = get_all_courses(page=2, per_page=10)
    assert result["page"] == 2
    assert result["per_page"] == 10
    assert len(result["courses"]) == 10

def test_get_courses_by_subject_empty(empty_db):
    result = get_courses_by_subject("COMP")
    assert isinstance(result, str)
    assert "No courses found for subject COMP" in result

def test_get_courses_by_subject_with_courses_and_pagination(empty_db):
    for i in range(15):
        db.session.add(Course(courseCode=f"COMP1{i:03}", name=f"Course {i}"))
    db.session.commit()
    result = get_courses_by_subject("COMP", page=2, per_page=10)
    assert result["page"] == 2
    assert result["per_page"] == 10
    assert len(result["courses"]) == 5

def test_course_exists_true_false(empty_db):
    db.session.add(Course(courseCode="COMP1600", name="Intro to Computing"))
    db.session.commit()
    assert course_exists("COMP1600") is True
    assert course_exists("MATH1140") is False