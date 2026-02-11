import click, pytest, sys, csv
from flask.cli import with_appcontext, AppGroup
from datetime import datetime

from flask.cli import with_appcontext, AppGroup
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from App.models.course import Courses


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    course = Courses(name="MATH1100")
    db.session.add(course)
    db.session.commit()


def normalize(value):
    if not value:
        return None
    return " ".join(str(value).split())  # Remove extra spaces

def parse_exam_date(date_str):
    date_str = normalize(date_str)
    return datetime.strptime(date_str.strip(), "%A %d %B %Y").date()

def parse_exam_time(time_str):
    time_str = normalize(time_str)
    return datetime.strptime(time_str.strip(), "%I:%M %p").time()

@app.cli.command("read-file", help="reads data file into the database")
def read_file():
    with open('test.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with open('output.txt', 'w') as f:                
            for row in reader:
                id = int(normalize(row.get("id"))) if row.get("id") else None
                subject_code = str(normalize(row.get("Subj Code"))) if row.get("Subj Code") else None
                course_number = str(normalize(row.get("Crse Numb"))) if row.get("Crse Numb") else None
                title = str(normalize(row.get("Title"))) if row.get("Title") else None

                exam_date = parse_exam_date(row.get("Date")) if row.get("Date") else None
                exam_time = parse_exam_time(row.get("Exam Time")) if row.get("Exam Time") else None

                room = str(normalize(row.get("Room"))) if row.get("Room") else None
                exam_length = int(normalize(row.get("Exam Length"))) if row.get("Exam Length") else None
                num_students = int(normalize(row.get("Number of Students"))) if row.get("Number of Students") else None

                f.write(f"{id}, {subject_code}, {course_number}, {title}, {exam_date.isoformat()}, {exam_time.strftime('%H:%M')}, {room}, {exam_length}, {num_students}\n")
            print('Data Parsed')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

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