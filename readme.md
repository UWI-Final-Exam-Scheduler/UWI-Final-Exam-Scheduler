# UWI Final Exam Scheduler

## Overview

The UWI Final Exam Scheduler is a Flask-based web application designed to streamline the exam scheduling process and reduce the occurrence of back-to-back exams for students. It provides tools for importing data, generating schedules, managing exam allocations, and detecting scheduling conflicts via a clash matrix.

---

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** PostgreSQL (NeonDB) with SQLAlchemy ORM
- **Migrations:** Flask-Migrate
- **Testing:** Pytest (with isolated test database)
- **Data Processing:** Pandas / CSV handling
- **Deployment:** Render

---

The UWI Final Exam Scheduler is a Flask-based web application designed to streamline the exam scheduling process and reduce the occurrence of back-to-back exams for students. It provides tools for importing data, generating schedules, and managing exam allocations efficiently.

---

## Live Deployment

The deployed application can be accessed here:

[https://uwi-final-exam-scheduler.onrender.com/](https://uwi-final-exam-scheduler.onrender.com/)

---

## Running the Project Locally

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variable

Before running the application or tests, set the `ENV` variable to control the environment mode:

**For Windows PowerShell:**

```powershell
$env:ENV="development"
```

**For production:**

```powershell
$env:ENV="production"
```

**For testing:**

```powershell
$env:ENV="test"
```

After changing the environment variable, reload your terminal or VS Code window to ensure the new value is picked up.

### 3. Run the Application

```bash
flask run
```

The application is accessible at:

```
http://127.0.0.1:8080
```

To run with Gunicorn (mirrors production):

```bash
gunicorn -c gunicorn_config.py wsgi:app
```

Or via the npm script:

```bash
npm run prod-serve
```

---

## WSGI CLI Commands

The project includes several custom Flask CLI commands to manage the database and load data. All commands are run using the `flask` CLI. For grouped commands, use the group prefix (e.g., `flask user ...`, `flask admin ...`).

### Reset Database

Drops all tables and recreates the database schema.

```bash
flask db-reset
```

---

### 2. User and Admin Management

**Create a user:**

```bash
flask user create <username> <password> <role>
```

Example:

```bash
flask user create test_user testpass admin
```

**Create an admin:**

```bash
flask admin create <username> <password>
```

Example:

```bash
flask admin create admin1 adminpass
```

---

### 3. Import Data

**Import venues:**

```bash
flask admin import-venues
```

**Import students:**

```bash
flask admin import-students
```

**Import courses:**

```bash
flask admin import-courses
```

**Import enrollments:**

```bash
flask admin import-enrollments
```

---

### 4. Import Past Timetable

Loads a previous year's timetable from a PDF file and inserts it into the database. Optionally, you can specify an admin username to associate with the imported exams.

```bash
flask admin import-past-timetable --admin_username <admin_username>
```

If you omit `--admin_username`, the first admin in the database will be used.

---

### 5. Clash Matrix

**Create clash matrix:**

```bash
flask create-clash-matrix
```

---

### 6. Exam and Venue Management

**View all venues:**

```bash
flask admin view-venues
```

**View a specific venue:**

```bash
flask admin view-venue "Venue Name"
```

**View all courses (paginated):**

```bash
flask admin view-courses --page <page> --per_page <per_page>
```

**View a course by code:**

```bash
flask admin view-course <course_code>
```

**View courses by subject (paginated):**

```bash
flask admin view-courses-by-subject <subject_code> --page <page> --per_page <per_page>
```

**View all subject codes:**

```bash
flask admin view-subject-codes
```

**Check if a course exists:**

```bash
flask admin course-exists <course_code>
```

---

### 7. Exam Scheduling and Management

**Get all exams:**

```bash
flask admin get-all-exams
```

**Get exams by date:**

```bash
flask admin get-exams-by-date <YYYY-MM-DD>
```

**Reschedule an exam:**

```bash
flask admin reschedule-exam <exam_id> --date <YYYY-MM-DD> --time <time> --venue_id <venue_id>
```

You can omit some arguments to use dynamic lookup (see CLI help for details).

**Split an exam:**

```bash
flask admin split-exam '[{"number_of_students":10},{"number_of_students":10}]' --exam_id <id> --venue_id <id> --date <YYYY-MM-DD> --time <time>
```

**Merge exams:**

```bash
flask admin merge-exams --course_code <course_code> --date <YYYY-MM-DD> --time <time> --venue_id <id>
```

**Get exams that need rescheduling:**

```bash
flask admin get-exams-need-rescheduling
```

**Get all days with exams:**

```bash
flask admin get-all-days-with-exams
```

---

### 6. Load From Last Timetable

**Update user preferences:**

```bash
flask load-from-last
```

This command:

- Parses exam data from a provided PDF
- Creates courses if they do not already exist
- Inserts exam records into the database
- Supports split venues by creating separate exam entries

---

## Running Unit and Integration Tests

Tests are configured using `pytest` and use an isolated test database.

### 1. Set the environment variable to test:

```powershell
$env:ENV="test"
```

### 2. Reload your terminal or VS Code window.

### 3. Initialize the test database:

```bash
python init_test_db.py
```

### 4. Populate the test database (for CLI-related tests):

```bash
pytest App/tests/test_cli.py
```

### 5. Run all other unit and integration tests:

```bash
pytest
```

The test database file can be viewed at: `instance/test.db`

## API Testing (Postman / Newman)

### API Tests (Newman / Postman)

Install Newman:

```bash
npm install -g newman
```

### Run Tests (Production)

```bash
npx newman run "Postman Prod/FINAL EXAM SCHEDULER PROD.postman_collection.json" -e "Postman Prod/Prod Environment.postman_environment" --env-var "base_url=https://uwi-final-exam-scheduler.onrender.com"
```

---

## Environment Variables

Environment variables required for the project (e.g., database URI, secrets) will be provided separately during handover.

---

## Architecture Notes

- The system follows an MVC-style Flask structure with controllers handling business logic.
- Scheduling strategies (e.g., loading from previous timetables or optimisation approaches) are modular and can be extended.

---

## Database Management

### Migrations

```
flask db migrate
```

Use this command when changes to the code affect the database schema (e.g., adding or modifying models).

```
flask db upgrade
```

Use this command to apply the latest schema changes to the database.

---

## Data Handling Assumptions

- Enrollment history is not permanently stored in the database.
- At the end of each semester, enrollment data is exported externally.
- The Enrollment table is cleared before the start of a new semester.

---

## Future Improvements

- Full optimisation-based scheduling strategy integration
- Improved validation and error handling for imported data
- Enhanced UI for schedule visualisation and editing
