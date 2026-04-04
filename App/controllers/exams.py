from App.models import Exam, Course
from App.models.enrollment import Enrollment
from App.strategies.loadfromlast import LoadFromLastStrategy
from App.controllers.venue import get_venue_by_name
from App.database import db
from datetime import datetime


def generate_timetable():
    strategy = LoadFromLastStrategy()
    result = strategy.execute()
    return result

def createTestExams():
    exam1 = Exam(courseCode="ACCT1002", date=datetime(2026, 5, 4).date(), time=9, venue_id=7, exam_length=120, number_of_students= 5)
    exam2 = Exam(courseCode="AGBU1005", date=datetime(2026, 5, 4).date(), time=1, venue_id=7, exam_length=120, number_of_students= 5)
    exam3 = Exam(courseCode="AGBU2000", date=datetime(2026, 5, 5).date(), time=9, venue_id=8, exam_length=120, number_of_students= 10)
    exam4 = Exam(courseCode="AGBU2002", date=datetime(2026, 6, 5).date(), time=1, venue_id=9, exam_length=120, number_of_students= 7)
    exam5 = Exam(courseCode="BIOC2061", date=datetime(2026, 6, 5).date(), time=4, venue_id=9, exam_length=120, number_of_students= 2)
    exam6 = Exam(courseCode="BIOL0100", date=datetime(2026, 6, 9).date(), time=9, venue_id=10, exam_length=120, number_of_students= 3)
    exam7 = Exam(courseCode="BIOL0100", date=datetime(2026, 6, 9).date(), time=9, venue_id=7, exam_length=120, number_of_students= 10)
    db.session.add_all([exam1, exam2, exam3, exam4, exam5, exam6, exam7])
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
        exam.venue_id = None
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

def sync_exams_with_enrollment_data():
    enrolled_students_per_course = db.session.query(
        Enrollment.courseCode,
        db.func.count(Enrollment.student_id)
    ).group_by(Enrollment.courseCode).all()

    enrollment_counts = {row.courseCode: row[1] for row in enrolled_students_per_course}

    for course_code, total_enrolled in enrollment_counts.items():
        exam_list = (
            Exam.query
            .filter_by(courseCode=course_code)
            .order_by(Exam.number_of_students.desc())  # largest first (important)
            .all()
        )

        if not exam_list:
            continue

        remaining = total_enrolled

        for i, exam in enumerate(exam_list):
            if remaining <= exam.number_of_students:
                exam.number_of_students = remaining
                for extra in exam_list[i + 1:]: # this is if the enrolled data fits in the first split(s) and the remaining is deleted
                    db.session.delete(extra)

                remaining = 0 # remaining is set to zero after
                break
            else:
                remaining -= exam.number_of_students # remaining enrolled students that need to be placed in the next splits
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    

def split_exam(course_code, splits, venue_id=None, time=None, date=None):
    existing = db.session.query(Exam).filter_by(courseCode=course_code).all()
    if not existing:
        return None, f"No exam found for course code {course_code}"

    total_students = sum(e.number_of_students for e in existing)
    split_total = sum(s["number_of_students"] for s in splits)
    if split_total != total_students:
        return None, (
            f"Split totals ({split_total}) must equal the total enrolled "
            f"students ({total_students})"
        )

    #this is just to ensure that each split has at least 1 student
    for s in splits:
        if s["number_of_students"] < 1:
            return None, "Each split must have at least 1 student"

    # splits can be between 2 -4 (just a rule i added)
    if not (2 <= len(splits) <= 4):
        return None, "Number of splits must be between 2 and 4"

    # Use the first existing exam split as the template for inherited attributes like date and time 
    template = existing[0]
    exam_date = datetime.strptime(date, "%Y-%m-%d").date() if date else template.date
    exam_time = time if time is not None else template.time
    exam_venue_id = venue_id if venue_id is not None else None

    # Delete all existing exam records for this course before creating new splits
    for exam in existing:
        db.session.delete(exam)

    # Create new split records — same date/time/length, individual student counts
    new_exams = []
    for split in splits:
        new_exam = Exam(
            courseCode=course_code,
            date=exam_date,
            time=exam_time,
            venue_id=exam_venue_id,  
            exam_length=template.exam_length,
            number_of_students=split["number_of_students"],
        )
        db.session.add(new_exam)
        new_exams.append(new_exam)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, str(e)

    return new_exams, None

def merge_exams(exam_ids):
    if len(exam_ids) < 2:
        return None, "At least 2 exam IDs are required to merge"

    exams_to_merge = db.session.query(Exam).filter(Exam.id.in_(exam_ids)).all()

    if len(exams_to_merge) != len(exam_ids):
        found_ids = {e.id for e in exams_to_merge}
        missing = [eid for eid in exam_ids if eid not in found_ids]
        return None, f"Exam IDs not found: {missing}"

    # all exam splits must share the same course code to be merged
    course_codes = {e.courseCode for e in exams_to_merge}
    if len(course_codes) > 1:
        return None, "All exams to merge must share the same courseCode"

    #we keep the first split and update the count and delete remaining splits 
    keeper = exams_to_merge[0]
    keeper.number_of_students = sum(e.number_of_students for e in exams_to_merge)

    for exam in exams_to_merge[1:]:
        db.session.delete(exam)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, str(e)

    return keeper, None



