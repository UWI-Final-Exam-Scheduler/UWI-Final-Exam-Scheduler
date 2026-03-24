from App.models import Exam, Course
from App.strategies.loadfromlast import LoadFromLastStrategy
from App.controllers.venue import get_venue_by_name
from App.database import db
from datetime import datetime


def generate_timetable():
    strategy = LoadFromLastStrategy()
    result = strategy.execute()
    return result

def createTestExams():
    exam1 = Exam(courseCode="ACCT1002", date=datetime(2026, 5, 4).date(), time=9, venue_id=7, exam_length=120, number_of_students= 100)
    exam2 = Exam(courseCode="AGBU1005", date=datetime(2026, 5, 4).date(), time=1, venue_id=7, exam_length=120, number_of_students= 100)
    exam3 = Exam(courseCode="AGBU2000", date=datetime(2026, 5, 5).date(), time=9, venue_id=8, exam_length=120, number_of_students= 100)
    exam4 = Exam(courseCode="AGBU2002", date=datetime(2026, 6, 5).date(), time=1, venue_id=9, exam_length=120, number_of_students= 180)
    exam5 = Exam(courseCode="BIOC2061", date=datetime(2026, 6, 5).date(), time=4, venue_id=9, exam_length=120, number_of_students= 220)
    exam6 = Exam(courseCode="BIOL0100", date=datetime(2026, 6, 9).date(), time=9, venue_id=10, exam_length=120, number_of_students= 250)
    db.session.add_all([exam1, exam2, exam3, exam4, exam5, exam6])
    db.session.commit()

def get_all_exams():
    exams = db.session.query(Exam).all()
    if not exams:
        return f"No exams found."
    exam_json = []
    for exam in exams:
        exam_json.append({
            "courseCode": exam.courseCode,
            "exam_date": exam.date.strftime("%Y-%m-%d"),   
            "time": exam.time, 
            "venue_id": exam.venue_id,
            "exam_length": exam.exam_length,
            "number_of_students": exam.number_of_students

        })
    return exam_json

def get_exams_by_date(exam_date):
    date_str = datetime.strptime(exam_date, "%Y-%m-%d").date()
    exams = db.session.query(Exam).filter_by(date=date_str).all()
    if not exams:
        return []
    exam_json = []
    for exam in exams:
        exam_json.append({
            "id": exam.id,
            "courseCode": exam.courseCode,
            "exam_date": exam.date.strftime("%Y-%m-%d"), 
            "time": exam.time, 
            "venue_id": exam.venue_id,
            "exam_length": exam.exam_length,
            "number_of_students": exam.number_of_students
        })
    return exam_json


def reschedule_exam(exam_course_code, date_str=None, time=None, venue_id=None, unschedule=False):
    exam = db.session.query(Exam).filter_by(courseCode=exam_course_code).first()
    if not exam:
        return None, f"Exam with course code {exam_course_code} not found"

    if unschedule:
        exam.date = None
        exam.time = 0
        db.session.commit()
        return exam, None

    if not any([date_str, time, venue_id]):
        return None, "At least one of date, time or venue_id is required"

    try:
        if date_str:
            exam.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if time:
            exam.time = time
        if venue_id:
            exam.venue_id = venue_id

        db.session.commit()
        return exam, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)
    
def get_exams_that_need_rescheduling():
    exams = db.session.query(Exam).filter(Exam.date == None).all()
    if not exams:
        return []
    exam_json = []
    for exam in exams:
        exam_json.append({
            "id": exam.id,
            "courseCode": exam.courseCode,
            "exam_date": exam.date.strftime("%Y-%m-%d") if exam.date else None,
            "time": exam.time,
            "venue_id": exam.venue_id,
            "exam_length": exam.exam_length,
            "number_of_students": exam.number_of_students
        })
    return exam_json

def get_all_days_with_exams():
    exams = db.session.query(Exam).all()
    if not exams:
        return []
    days_with_exams = set()
    for exam in exams:
        if exam.date:
            days_with_exams.add(exam.date.strftime("%Y-%m-%d"))
    return list(days_with_exams)
