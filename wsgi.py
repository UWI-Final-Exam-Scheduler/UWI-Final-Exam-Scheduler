from dotenv import load_dotenv
load_dotenv()

import click, pytest, sys
from flask.cli import AppGroup
from App.controllers.enrollments import import_enrollments_from_csv
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users )
from App.controllers.courses import course_exists, get_subject_codes, import_courses_from_csv, get_all_courses, get_course_by_code, get_courses_by_subject
from App.controllers.students import import_students_from_csv
from App.controllers.admin import create_admin
from App.controllers.venue import import_venues_from_csv,get_all_venues, get_venue_by_name
from App.models.enrollment import Enrollment
from App.controllers.clash_matrix import create_clash_matrix, view_conflicting_courses, view_course_clashes
from App.controllers.exams import generate_timetable, get_all_days_with_exams, get_all_exams, get_exams_by_date, get_exams_that_need_rescheduling, merge_exams, reschedule_exam, split_exam, sync_exams_with_enrollment_data
from App.controllers.user_preference import get_user_preferences, update_user_preferences
from App.models.exam import Exam
from App.models.venue import Venue
from App.models.admin import Admin
import json
global exam_id, venue_id, split_exam_ids

app = create_app()
migrate = get_migrate(app)

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database."""
    db.create_all()
    print("Database initialized.")

@app.cli.command("db-reset", help="Drops and recreates the database")
def db_reset():
    db.drop_all()
    db.create_all()

'''
User Commands
'''
user_cli = AppGroup('user', help='User object commands') 

@user_cli.command("create", help="Creates a user")
@click.argument("username", default="admin")
@click.argument("password", default="adminpass")
@click.argument("role", default="admin")
def create_user_command(username, password, role):
    create_user(username, password, role=role)
    print(f'{username} created!')

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

@user_cli.command("get-preferences", help="Get user preferences")
@click.argument("user_id", default=1, type=int)
def get_user_preferences_command(user_id):
    preferences = get_user_preferences(user_id)
    print(preferences)

#eg: flask user update-preferences 1 --abs_threshold 10 --perc_threshold 0.2
@user_cli.command("update-preferences", help="Update user preferences")
@click.argument("user_id", default=1, type=int)
@click.option("--abs_threshold", type=int, help="New absolute threshold")
@click.option("--perc_threshold", type=float, help="New percentage threshold")
def update_user_preferences_command(user_id, abs_threshold, perc_threshold):
    updated_preferences = update_user_preferences(user_id, abs_threshold=abs_threshold, perc_threshold=perc_threshold)
    print(f"Updated preferences for user {user_id}: {updated_preferences}")


'''
Admin Commands
'''
admin_cli = AppGroup('admin', help='Admin object commands')
@admin_cli.command("create", help="Creates an admin")
@click.argument("username", default="admin")
@click.argument("password", default="adminpass")
def create_admin_command(username, password, role='admin'):
    create_admin(username, password, role=role)
    print(f'{username} created!')

#Uploading data commands
@admin_cli.command("import-venues", help="Imports venues from a CSV file")
def import_venues_command():
    try:
        msg = import_venues_from_csv("Test Data/venues.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing venues: {e}")

@admin_cli.command("import-students", help="Imports students from a CSV file")
def import_students_command():
    try:
        msg = import_students_from_csv("Test Data/students.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing students: {e}")

@admin_cli.command("import-courses", help="Imports courses from a CSV file")
def import_courses_command():
    try:
        msg = import_courses_from_csv("Test Data/sem2_courses.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing courses: {e}")

@admin_cli.command("import-past-timetable", help="Imports past timetable from a CSV file")
@click.option('--admin_username', default=None, help='Admin username to associate with imported exams')
def import_past_timetable_command(admin_username):
    try:
        admin = None
        if admin_username:
            admin = Admin.query.filter_by(username=admin_username).first()
        if not admin:
            admin = Admin.query.first()
        if not admin:
            print("No admin found in the database. Please create an admin first.")
            return
        msg = generate_timetable(
            "Test Data/UWI Timetable Cross Reference Final 202510 17NOV2025.pdf",
            admin_id=admin.id
        )
        print(msg)
    except Exception as e:
        print(f"Error importing past timetable: {e}")

@admin_cli.command("import-enrollments", help="Imports enrollments from a CSV file")
def import_enrollments_command():
    try:
        msg = import_enrollments_from_csv("Test Data/enrollments.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing enrollments: {e}")


#venues commands
@admin_cli.command("view-venues", help="View all venues in the database")
def view_venues():
    try:
        venues = get_all_venues()
        print(venues)
    except Exception as e:
        print(f"Error viewing venues: {e}")

@admin_cli.command("view-venue", help="View a venue by its name")
@click.argument("venue_name", default="Mechanical Design Office (MD2)")
def view_venue(venue_name):
    try:
        venue = get_venue_by_name(venue_name)
        print(venue)
    except Exception as e:
        print(f"Error viewing venue: {e}")


#courses commands
#will show courses on page 1
@admin_cli.command("view-courses", help="View all courses (paginated)")
@click.option("--page", default=1, help="Page number")
@click.option("--per_page", default=20, help="Courses per page")
def view_courses(page, per_page):
    try:
        result = get_all_courses(page=page, per_page=per_page)
        print(result)
    except Exception as e:
        print(f"Error viewing courses: {e}")

@admin_cli.command("view-course", help="View a course by its code")
@click.argument("course_code", default="COMP1600")
def view_course(course_code):
    try:
        result = get_course_by_code(course_code)
        print(result)
    except Exception as e:
        print(f"Error viewing course: {e}")

@admin_cli.command("view-courses-by-subject", help="View courses by subject code (paginated)")
@click.argument("subject_code", default="COMP")
@click.option("--page", default=1, help="Page number")
@click.option("--per_page", default=20, help="Courses per page")
def view_courses_by_subject(subject_code, page, per_page):
    try:
        result = get_courses_by_subject(subject_code, page=page, per_page=per_page)
        print(result)
    except Exception as e:
        print(f"Error viewing courses by subject: {e}")

@admin_cli.command("view-subject-codes", help="View all subject codes")
def view_subject_codes():
    try:
        result = get_subject_codes()
        print(result)
    except Exception as e:
        print(f"Error viewing subject codes: {e}")

@admin_cli.command("course-exists", help="Check if a course exists by code")
@click.argument("course_code", default="COMP9000")
def course_exists_command(course_code):
    try:
        exists = course_exists(course_code)
        print(f"Exists: {exists}")
    except Exception as e:
        print(f"Error checking course existence: {e}")


#clash matrix commands
@app.cli.command("create-clash-matrix", help="Creates the clash matrix from enrollments")
def create_clash_matrix_command():
    try:
        enrollments = db.session.query(Enrollment.student_id, Enrollment.courseCode).all()
        result = create_clash_matrix(enrollments)
        print("Clash matrix created successfully!")
    except Exception as e:
        print(f"Error creating clash matrix: {e}")

@admin_cli.command("view-conflicting-courses", help="View conflicting courses based on clash matrix")
@click.argument("abs_threshold", default=5, type=int)
@click.argument("perc_threshold", default=0.1, type=float)
def view_conflicts_command(abs_threshold, perc_threshold):
    try:
        conflicts = view_conflicting_courses(abs_threshold=abs_threshold, perc_threshold=perc_threshold)
        print(conflicts)
    except Exception as e:
        print(f"Error viewing conflicting courses: {e}")

@admin_cli.command("view-course-clashes", help="View clashes for a specific course based on clash matrix")
@click.argument("course_code", default="COMP1602")
@click.argument("abs_threshold", default=5, type=int)
@click.argument("perc_threshold", default=0.1, type=float)
def view_course_clashes_command(course_code, abs_threshold, perc_threshold):
    try:
        clashes = view_course_clashes(course_code, abs_threshold=abs_threshold, perc_threshold=perc_threshold)
        print(clashes)
    except Exception as e:
        print(f"Error viewing course clashes: {e}")

#exam commands
@admin_cli.command("get-all-exams", help="Get all exams in the database")
def get_all_exams_command():
    try:
        exams = get_all_exams()
        print(exams)
    except Exception as e:
        print(f"Error getting exams: {e}")

@admin_cli.command("get-exams-by-date", help="Get exams by date (YYYY-MM-DD)")
@click.argument("exam_date", default ="2026-12-01")
def get_exams_by_date_command(exam_date):
    try:
        exams = get_exams_by_date(exam_date)
        print(exams)
    except Exception as e:
        print(f"Error getting exams by date: {e}")



# Reschedule exam command with dynamic lookup for LAW3020 and New Wing if not provided
@admin_cli.command("reschedule-exam", help="Reschedule an exam")
@click.argument("exam_id", required=False, type=int)
@click.option("--date", default="2026-12-11", help="New exam date (YYYY-MM-DD)")
@click.option("--time", default=4, type=int, help="New exam time (9, 1, or 4)")
@click.option("--venue_id", required=False, type=int, help="New venue ID")
@click.option("--unschedule", is_flag=True, help="Unschedule the exam")
@click.option("--prevent_merge", is_flag=True, help="Prevent auto-merging of splits")
def reschedule_exam_command(exam_id, date, time, venue_id, unschedule, prevent_merge):
    try:
        # lookup for LAW3020 exam_id if not provided
        if not exam_id:
            law_exam = Exam.query.filter_by(courseCode="LAW3020").first()
            if law_exam:
                exam_id = law_exam.id
            else:
                print("No exam found for LAW3020.")
                return
        # lookup for New Wing venue_id if not provided
        if not venue_id:
            venue = Venue.query.filter(Venue.name.ilike("%New Wing%"))
            venue = venue.first() if venue else None
            if venue:
                venue_id = venue.id
            else:
                print("No venue found for 'New Wing'.")
                return
        exam, error = reschedule_exam(
            exam_id, date_str=date, time=time, venue_id=venue_id,
            unschedule=unschedule, prevent_merge=prevent_merge
        )
        if error:
            print(f"Error: {error}")
        else:
            print(f"Exam updated: {exam}")
    except Exception as e:
        print(f"Error rescheduling exam: {e}")

@admin_cli.command("get-exams-need-rescheduling", help="List exams that need rescheduling")
def get_exams_that_need_rescheduling_command():
    try:
        exams = get_exams_that_need_rescheduling()
        print(exams)
    except Exception as e:
        print(f"Error: {e}")

@admin_cli.command("get-all-days-with-exams", help="Get all days with scheduled exams")
def get_all_days_with_exams_command():
    try:
        days = get_all_days_with_exams()
        print(days)
    except Exception as e:
        print(f"Error: {e}")

#required is set to False for the sake of automated testing, but in production it is required and the command should not run if exam_id is not provided
@admin_cli.command("split-exam", help="Split an exam into multiple sessions")
@click.argument("splits_json", default='[{"number_of_students":100},{"number_of_students":108}]')
@click.option("--exam_id", required=False, type=int, help="Exam ID to split")
@click.option("--venue_id", required=False, type=int, help="Venue ID for splits")
@click.option("--time", default=4, type=int, help="Time for splits")
@click.option("--date", default="2026-12-03", help="Date for splits (YYYY-MM-DD)")
def split_exam_command(splits_json, exam_id, venue_id, time, date):
    try:
        # Query for BIOL1262 exam_id if not provided
        if not exam_id:
            biol_exam = Exam.query.filter_by(courseCode="BIOL1262").first()
            if biol_exam:
                exam_id = biol_exam.id
            else:
                print("No exam found for BIOL1262.")
                return
        # Query for Mechanical Design Office (MD2) venue id if not provided
        if not venue_id:
            venue = Venue.query.filter(Venue.name.ilike("%Mechanical Design Office (MD2)%")).first()
            if venue:
                venue_id = venue.id
            else:
                print("No venue found for 'Mechanical Design Office (MD2)'.")
                return
        splits = json.loads(splits_json)
        result, error = split_exam(exam_id, splits, venue_id=venue_id, time=time, date=date)
        if error:
            print(f"Error: {error}")
        else:
            print("Exam split successfully.")
    except Exception as e:
        print(f"Error splitting exam: {e}")


@admin_cli.command("merge-exams", help="Merge multiple exam splits into one")
@click.argument("exam_ids_json", required=False)
@click.option("--course_code", default="BIOL1262", help="Course code for split exams")
@click.option("--date", default="2026-12-03", help="Date for splits (YYYY-MM-DD)")
@click.option("--time", default=4, type=int, help="Time for splits")
@click.option("--venue_id", required=False, type=int, help="Venue ID for splits")
def merge_exams_command(exam_ids_json, course_code, date, time, venue_id):
    try:
        # Query for Mechanical Design Office (MD2) venue id if not provided
        if not venue_id:
            venue = Venue.query.filter(Venue.name.ilike("%Mechanical Design Office (MD2)%")).first()
            if venue:
                venue_id = venue.id
            else:
                print("No venue found for 'Mechanical Design Office (MD2)'.")
                return
            
        if not exam_ids_json:
            # Query split exam IDs for the given course, date, time, and venue
            split_exams = Exam.query.filter_by(
                courseCode=course_code,
                date=date,
                time=time,
                venue_id=venue_id
            ).order_by(Exam.id).all()
            exam_ids = [e.id for e in split_exams]
            print(f"Found split exams: {[{'id': e.id, 'number_of_students': e.number_of_students} for e in split_exams]}")
            if not exam_ids:
                print("No split exams found to merge.")
                return
        else:
            exam_ids = json.loads(exam_ids_json)
        result, error = merge_exams(exam_ids)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Exams merged: {result}")
    except Exception as e:
        print(f"Error merging exams: {e}")

# add the group to the cli
app.cli.add_command(user_cli) 
app.cli.add_command(admin_cli) 


'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)