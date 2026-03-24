import csv
from pathlib import Path
import traceback

import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from flask.cli import with_appcontext, AppGroup
from App.controllers.enrollments import create_enrollment, import_enrollments_from_csv
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users )
from App.controllers.courses import get_subject_codes, import_courses_from_csv, create_course, get_all_courses, get_course_by_code, get_courses_by_subject
from App.controllers.students import import_students_from_csv, create_student
from App.controllers.admin import create_admin
from App.controllers.venue import import_venues_from_csv
from App.models.course import Course
from App.models.enrollment import Enrollment
from App.models.student import Student
from App.models.venue import Venue
from App.controllers.clash_matrix import create_clash_matrix, view_conflicting_courses, view_course_clashes
from App.controllers.exams import createTestExams, generate_timetable, get_all_days_with_exams, get_all_exams, get_exams_by_date, reschedule_exam
from App.models.clash_matrix import ClashMatrix
# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)


@app.cli.command("db-reset", help="Drops and recreates the database")
def db_reset():
    db.drop_all()
    db.create_all()

@app.cli.command("load-from-last", help="Loads all the previous exams into the ")
def import_timetable():
    try:
        result = generate_timetable()
        print(result)
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")

@app.cli.command("import-all-courses", help="reads courses data file into the database")
def read_courses():
    try:
        Course.query.delete() # clear existing courses before importing new ones
        db.session.commit()
        print("Existing courses cleared. Loading new courses...")

        msg = import_courses_from_csv("Test Data/sem2_courses.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing courses: {e}")

@app.cli.command("export-courses", help="Exports all courses in the database to a CSV file")
def export_courses():
    try:
        courses = Course.query.all()
        output_path = Path("Test Data/sem2_courses.csv")

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Subj Code", "Crse Numb", "Title"])
            for course in courses:
                subject = course.courseCode[:4]
                number = course.courseCode[4:]
                writer.writerow([subject, number, course.name])
        print(f"Exported {len(courses)} courses to {output_path}")
    except Exception as e:
        print(f"Error exporting courses: {e}")

@app.cli.command("export-clash-matrix", help="Exports the clash matrix table to a CSV file")
def export_clash_matrix():
    try:
        clashes = ClashMatrix.query.order_by(ClashMatrix.course1, ClashMatrix.course2).all()
        output_path = Path("Test Data/clash_matrix.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Course 1", "Course 2", "Clash Count"])
            for clash in clashes:
                writer.writerow([
                    clash.course1,
                    clash.course2,
                    clash.clash_count
                ])
        print(f"Exported {len(clashes)} clash rows to {output_path}")
    except Exception as e:
        print(f"Error exporting clash matrix: {e}")

@app.cli.command("create-course", help="Creates a course")
@click.argument("course_code")
@click.argument("name", nargs=-1)
def create_course_command(course_code, name):
    name = " ".join(name)
    try:
        msg = create_course(course_code, name)
        print(msg)
    except Exception as e:
        print(f"Error creating course: {e}")

@app.cli.command("import-all-students", help="reads students data file into the database")
def read_students():
    try:
        Student.query.delete() # clear existing students before importing new ones
        db.session.commit()
        print("Existing students cleared. Loading new students...")

        msg = import_students_from_csv("Test Data/students.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing students: {e}")

@app.cli.command("create-student", help="Creates a student")
@click.argument("student_id")
def create_student_command(student_id):
    try:
        msg = create_student(student_id)
        print(msg)
    except Exception as e:
        print(f"Error creating student: {e}")

@app.cli.command("import-all-enrollments", help="reads enrollments data file into the database")
def read_enrollments():
    try:
        Enrollment.query.delete() # clear existing enrollments before importing new ones
        db.session.commit()
        print("Existing enrollments cleared. Loading new enrollments...")

        msg = import_enrollments_from_csv("Test Data/enrollments.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing enrollments: {e}")     

@app.cli.command("create-enrollment", help="Creates an enrollment")
@click.argument("student_id")
@click.argument("course_code")
def create_enrollment_command(student_id, course_code):
    try:
        msg = create_enrollment(student_id, course_code)
        print(msg)
    except Exception as e:
        print(f"Error creating enrollment: {e}")

@app.cli.command("import-all-venues", help="reads venues data file into the database")
def read_venues():
    try:
        msg = import_venues_from_csv("Test Data/venues.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing venues: {e}")

@app.cli.command("view_courses", help="View all courses in the database")
def view_courses():
    try:
        courses = get_all_courses()
        print(courses)
    except Exception as e:
        print(f"Error viewing courses: {e}")

@app.cli.command("view_course", help="View a course by its code")
@click.argument("course_code")
def view_course(course_code):
    try:
        course = get_course_by_code(course_code)
        print(course)
    except Exception as e:
        print(f"Error viewing course: {e}")

@app.cli.command("view_courses_by_subject", help="View courses by subject code")
@click.argument("subject_code")
def view_courses_by_subject(subject_code):
    try:
        courses = get_courses_by_subject(subject_code)
        print(courses)
    except Exception as e:
        print(f"Error viewing courses by subject: {e}")

@app.cli.command("view_subject_codes", help="View all subject codes")
def view_subject_codes():
    try:
        subject_codes = get_subject_codes()
        print(subject_codes)
    except Exception as e:
        print(f"Error viewing subject codes: {e}")

@app.cli.command("create-clash-matrix", help="Creates the clash matrix")  
def create_clash_matrix_command():
    try:
        enrollments = db.session.query(Enrollment.student_id, Enrollment.courseCode).all()
        clash_matrix = create_clash_matrix(enrollments)
        print("Clash matrix created successfully!")
    except Exception as e:
        print(f"Error creating clash matrix: {e}")

@app.cli.command("create-test-exams", help="Creates test exams in the database")
def create_test_exams_command():
    try:
        createTestExams()
        print("Test exams created successfully!")
    except Exception as e:
        print(f"Error creating test exams: {e}")

@app.cli.command("get-exams", help="Get all exams in the database")
def get_exams_command():
    try:
        exams = get_all_exams()
        print(exams)
    except Exception as e:
        print(f"Error getting exams: {e}")

@app.cli.command("get-exams-by-date", help="Get exams by date")
@click.argument("exam_date")
def get_exams_by_date_command(exam_date):
    try:
        exams = get_exams_by_date(exam_date)
        print(exams)
    except Exception as e:
        print(f"Error getting exams by date: {e}")

@app.cli.command("reschedule-exam", help="Reschedules an exam")
@click.argument("exam_course_code")
@click.option("--date", help="New exam date")
@click.option("--time", help="New exam time")
@click.option("--venue", help="New exam venue")
def reschedule_exam_command(exam_course_code, date, time, venue):
    try:
        exam, error = reschedule_exam(exam_course_code, date_str=date, time_str=time, venue_id=venue)
        if error:
            print(f"Error rescheduling exam: {error}")
        else:
            print(f"Exam rescheduled successfully: {exam}")
    except Exception as e:
        print(f"Error rescheduling exam: {e}")

@app.cli.command("get-days-with-exams", help="Get all days that have exams scheduled")
def get_days_with_exams_command():
    try:
        days = get_all_days_with_exams()
        print(days)
    except Exception as e:
        print(f"Error viewing conflicting courses: {e}")

@app.cli.command("clear-exams")
def clear_exams():
    db.session.query(Exam).delete()
    db.session.commit()
    print("All rows in Exam table deleted.")
'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="admin")
@click.argument("password", default="adminpass")
@click.argument("role", default="admin")
def create_user_command(username, password, role):
    create_user(username, password, role=role)
    print(f'{username} created!')

# this command will be : flask user create admin adminpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

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

@admin_cli.command("view-conflicts", help="View conflicting courses based on clash matrix")
@click.argument("abs_threshold", default=5, type=int)
@click.argument("perc_threshold", default=0.1, type=float)
def view_conflicts_command(abs_threshold, perc_threshold):
    try:
        conflicts = view_conflicting_courses(abs_threshold=abs_threshold, perc_threshold=perc_threshold)
        print(conflicts)
    except Exception as e:
        print(f"Error viewing conflicting courses: {e}")

@admin_cli.command("view-course-clashes", help="View clashes for a specific course based on clash matrix")
@click.argument("course_code", default="FOUN1105")
@click.argument("abs_threshold", default=5, type=int)
@click.argument("perc_threshold", default=0.1, type=float)
def view_course_clashes_command(course_code, abs_threshold, perc_threshold):
    try:
        clashes = view_course_clashes(course_code, abs_threshold=abs_threshold, perc_threshold=perc_threshold)
        print(clashes)
    except Exception as e:
        print(f"Error viewing course clashes: {e}")

app.cli.add_command(admin_cli) # add the group to the cli

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