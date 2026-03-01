import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from flask.cli import with_appcontext, AppGroup
from App.controllers.enrollments import create_enrollment, import_enrollments_from_csv
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users )
from App.controllers.courses import import_courses_from_csv, create_course, get_all_courses, get_course_by_code, get_courses_by_subject
from App.controllers.students import import_students_from_csv, create_student
from App.controllers.admin import create_admin
from App.controllers.venue import import_venues_from_csv


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)


@app.cli.command("db-reset", help="Drops and recreates the database")
def db_reset():
    db.drop_all()
    db.create_all()

@app.cli.command("import-all-courses", help="reads courses data file into the database")
def read_courses():
    try:
        msg = import_courses_from_csv("Test Data/courses.csv")
        print(msg)
    except Exception as e:
        print(f"Error importing courses: {e}")

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
def create_user_command(username, password):
    create_user(username, password)
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
def create_admin_command(username, password):
    create_admin(username, password)
    print(f'{username} created!')


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