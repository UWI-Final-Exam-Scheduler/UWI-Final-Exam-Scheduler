from App.models import Exam, Course, Venue
from App.models.enrollment import Enrollment
from App.strategies.loadfromlast import LoadFromLastStrategy
from App.services.exam_scheduler_service import ExamSchedulerService
from App.database import db
from datetime import datetime

def generate_timetable(pdf_path=None, admin_id=None):
    # strategy = LoadFromLastStrategy()
    scheduler = ExamSchedulerService()
    # Pass admin_id to the scheduler if supported, else set it in the service/model layer
    result = scheduler.generate_timetable(pdf_path=pdf_path, admin_id=admin_id)

    if Enrollment.query.count() > 0:
        sync_exams_with_enrollment_data()
    return result

def get_all_exams():
    exams = db.session.query(Exam).all()
    if not exams:
        return f"No exams found."
    exam_json = []
    for exam in exams:
        exam_json.append({
            "courseCode": exam.courseCode,
            "exam_date":  exam.date.strftime("%Y-%m-%d") if exam.date else None,   
            "time": exam.time, 
            "venue_id": exam.venue_id,
            "exam_length": exam.exam_length,
            "number_of_students": exam.number_of_students,
            "exam_id": exam.id
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
            "exam_id": exam.id,
            "courseCode": exam.courseCode,
            "exam_date": exam.date.strftime("%Y-%m-%d"), 
            "time": exam.time, 
            "venue_id": exam.venue_id,
            "exam_length": exam.exam_length,
            "number_of_students": exam.number_of_students
        })
    return exam_json

def reschedule_exam(
    exam_id,
    date_str=None,
    time=None,
    venue_id=None,
    unschedule=False,
    prevent_merge=False,
):
    exam = db.session.get(Exam, exam_id)
    if not exam:
        return None, f"Exam with id {exam_id} not found"
    
    if unschedule:
        exam.date = None
        exam.time = 0
        exam.venue_id = None
        db.session.commit()
        return exam, None

    if not any([date_str, time is not None, venue_id is not None]):
        return None, "At least one of date, time or venue_id is required"

    try:
        # validate and set date
        if date_str:
            if isinstance(date_str, str):
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            elif isinstance(date_str, datetime):
                date_obj = date_str.date()
            else:
                return None, "Invalid date format, must be YYYY-MM-DD"

            if date_obj.weekday() >= 5:
                return None, "Exams cannot be scheduled on weekends"

            exam.date = date_obj

        # validate and set time
        if time is not None:
            try:
                valid_time = int(time)
            except Exception:
                return None, "Time must be an integer (9, 1, or 4)"

            if valid_time not in [9, 1, 4]:
                return None, "Invalid time slot. Please choose a valid time slot (9, 1, or 4)"

            exam.time = valid_time

        # set venue
        if venue_id is not None:
            exam.venue_id = venue_id

        #split conflict check 
        sibling_scheduled = (
            db.session.query(Exam)
            .filter(
                Exam.id != exam.id,
                Exam.courseCode == exam.courseCode,
                Exam.date.isnot(None),
                Exam.time.isnot(None),
            )
            .all()
        )

        if sibling_scheduled:
            allowed_date = sibling_scheduled[0].date
            allowed_time = sibling_scheduled[0].time

            if exam.date != allowed_date or exam.time != allowed_time:
                db.session.rollback()
                return None, (
                    f"Split conflict: {exam.courseCode} already has scheduled split(s) at "
                    f"{allowed_date.strftime('%Y-%m-%d')} time {allowed_time}. "
                    "All splits must share the same date and time."
                )
        if not prevent_merge:
            if exam.date is not None and exam.time is not None and exam.venue_id is not None:
                existing_same_slot = (
                    db.session.query(Exam)
                    .filter(
                        Exam.id != exam.id,
                        Exam.courseCode == exam.courseCode,
                        Exam.date == exam.date,
                        Exam.time == exam.time,
                        Exam.venue_id == exam.venue_id,
                    )
                    .all()
                )

                if existing_same_slot:
                    venue_obj = db.session.get(Venue, exam.venue_id)
                    if venue_obj is not None:
                        merged_total = exam.number_of_students + sum(
                            e.number_of_students for e in existing_same_slot
                        )
                        if merged_total > venue_obj.capacity:
                            db.session.rollback()
                            return None, (
                                f"Cannot auto-merge: merged total {merged_total} exceeds "
                                f"venue capacity {venue_obj.capacity}"
                            )

                    keeper = existing_same_slot[0]
                    keeper.number_of_students += exam.number_of_students
                    db.session.delete(exam)
                    db.session.commit()
                    return keeper, None

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
            "exam_id": exam.id,
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
    
def split_exam(exam_id, splits, venue_id=None, time=None, date=None):
    existing = db.session.query(Exam).filter_by(id=exam_id).first()
    if not existing:
        return None, f"No exam found for ID {exam_id}"

    # splits can be between 2 -4 (just a rule i added)
    if not (2 <= len(splits) <= 4):
        return None, "Number of splits must be between 2 and 4"

    # this is just to ensure that each split has at least 1 student
    for s in splits:
        if s["number_of_students"] < 1:
            return None, "Each split must have at least 1 student"

    total_students = existing.number_of_students
    split_total = sum(s["number_of_students"] for s in splits)
    if split_total != total_students:
        return None, (
            f"Split totals ({split_total}) must equal the total enrolled "
            f"students ({total_students})"
        )

    # Use the first existing exam split as the template for inherited attributes like date and time 
    course_code = existing.courseCode
    exam_date = datetime.strptime(date, "%Y-%m-%d").date() if date else existing.date
    exam_time = time if time is not None else existing.time
    exam_venue_id = venue_id if venue_id is not None else None

    # # Delete all existing exam records for this course before creating new splits
    # for exam in existing:
    #     db.session.delete(exam)
    db.session.delete(existing) 

    # Create new split records — same date/time/length, individual student counts
    new_exams = []
    for split in splits:
        new_exam = Exam(
            courseCode=course_code,
            date=exam_date,
            time=exam_time,
            venue_id=exam_venue_id,  
            exam_length=existing.exam_length,
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

    for e in exams_to_merge:
        print(f"  id={e.id}  courseCode='{e.courseCode}'")
    
    if len(exams_to_merge) != len(exam_ids):
        found_ids = {e.id for e in exams_to_merge}
        missing = [eid for eid in exam_ids if eid not in found_ids]
        return None, f"Exam IDs not found: {missing}"

    # all exam splits must share the same course code to be merged
    course_codes = {e.courseCode for e in exams_to_merge}
    if len(course_codes) > 1:
        return None, "All exams to merge must share the same courseCode"  #mock test

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



