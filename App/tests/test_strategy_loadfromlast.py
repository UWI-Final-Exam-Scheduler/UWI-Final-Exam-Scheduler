import pytest
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from App.strategies.loadfromlast import LoadFromLastStrategy
from App.models import Course, Venue, Exam
from App.database import db


def create_venue(name="Room A", capacity=200):
    v = Venue(name=name, capacity=capacity)
    db.session.add(v)
    db.session.commit()
    return v


def test_is_weekend():
    strategy = LoadFromLastStrategy()
    saturday = date(2025, 5, 3)
    monday = date(2025, 5, 5)

    assert strategy.is_weekend(saturday) is True
    assert strategy.is_weekend(monday) is False


def test_get_exam_period_returns_valid_range():
    strategy = LoadFromLastStrategy()
    start, end = strategy.get_exam_period(2025, 5)

    assert start < end
    assert start.weekday() < 5
    assert end.weekday() == 4 


def test_get_weekdays_returns_valid_days():
    strategy = LoadFromLastStrategy()
    start = date(2025, 5, 1)
    end = date(2025, 5, 30)

    days = strategy.get_weekdays(start, end)

    assert len(days) <= 15
    assert all(d.weekday() < 5 for d in days)
    assert days[-1].weekday() == 4


def test_map_exam_date_to_year():
    strategy = LoadFromLastStrategy()

    old_date = date(2024, 5, 6)  # Monday
    mapped = strategy.map_exam_date_to_year(old_date, 2024, 2025, 5)

    assert isinstance(mapped, date)
    assert mapped.weekday() < 5


def test_resolve_pdf_path_direct():
    strategy = LoadFromLastStrategy()
    path = strategy.resolve_pdf_path("test.pdf")

    assert str(path) == "test.pdf"


def test_resolve_pdf_path_not_found():
    strategy = LoadFromLastStrategy()

    with patch("pathlib.Path.glob", return_value=[]):
        with pytest.raises(FileNotFoundError):
            strategy.resolve_pdf_path()


@patch("pdfplumber.open")
def test_execute_inserts_exams(mock_pdf, empty_db):
    strategy = LoadFromLastStrategy()

    create_venue("Room A")

    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [
        [
            ["1 COMP 1600 Intro to Computing MONDAY 06 MAY 2024 9:00 AM Room A 2 50"]
        ]
    ]

    mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

    result = strategy.execute(pdf_path="fake.pdf")

    exams = Exam.query.all()
    courses = Course.query.all()

    assert result["inserted"] == 1
    assert len(exams) == 1
    assert len(courses) == 1


@patch("pdfplumber.open")
def test_execute_skips_invalid_rows(mock_pdf, empty_db):
    strategy = LoadFromLastStrategy()

    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [[
        ["INVALID ROW TEXT"]
    ]]

    mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

    result = strategy.execute(pdf_path="fake.pdf")

    assert result["inserted"] == 0
    assert result["skipped"] > 0


@patch("pdfplumber.open")
def test_execute_skips_missing_venue(mock_pdf, empty_db):
    strategy = LoadFromLastStrategy()

    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [[
        [
            "1 COMP 1600 Intro to Computing Monday 06 May 2024 9:00 AM Room A 2 50"
        ]
    ]]

    mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

    result = strategy.execute(pdf_path="fake.pdf")

    exams = Exam.query.all()

    assert len(exams) == 0
    assert result["skipped"] > 0


@patch("pdfplumber.open")
def test_execute_prevents_duplicates(mock_pdf, empty_db):
    strategy = LoadFromLastStrategy()

    create_venue("Room A")

    row = ["1 COMP 1600 Intro to Computing MONDAY 06 MAY 2024 9:00 AM Room A 2 50"]

    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [
        [row],
        [row]
    ]

    mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

    strategy.execute(pdf_path="fake.pdf")
    strategy.execute(pdf_path="fake.pdf")

    exams = Exam.query.all()

    assert len(exams) == 1


@patch("pdfplumber.open")
def test_execute_creates_course_if_missing(mock_pdf, empty_db):
    strategy = LoadFromLastStrategy()

    create_venue("Room A")

    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [
        [
            ["1 COMP 9999 New Course MONDAY 06 MAY 2024 9:00 AM Room A 2 50"]
        ]
    ]

    mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

    result = strategy.execute(pdf_path="fake.pdf")

    course = Course.query.filter_by(courseCode="COMP9999").first()

    assert course is not None
    assert result["created_courses"] == 1