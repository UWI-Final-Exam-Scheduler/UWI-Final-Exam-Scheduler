# UWI Final Exam Scheduler

## Overview

The UWI Final Exam Scheduler is a Flask-based web application designed to streamline the exam scheduling process and reduce the occurrence of back-to-back exams for students. It provides tools for importing data, generating schedules, and managing exam allocations efficiently.

---

## Live Deployment

The deployed application can be accessed here:

👉 [https://uwi-final-exam-scheduler.onrender.com/](https://uwi-final-exam-scheduler.onrender.com/)

---

## Running the Project Locally

### 1. Install Dependencies

Ensure you have Python installed, then install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
flask run
```

The application should now be accessible at:

```
http://127.0.0.1:5000/
```

---

## WSGI CLI Commands

The project includes several custom Flask CLI commands to manage the database and load data.

### 1. Reset Database

Drops all tables and recreates the database schema.

```bash
flask db-reset
```

---

### 2. Import All Courses

Clears the courses table and imports course data from a CSV file.

```bash
flask import-all-courses
```

---

### 3. Load From Last Timetable

Loads a previous year's timetable from a PDF file and inserts it into the database.

```bash
flask load-from-last
```

This command:

* Parses exam data from a provided PDF
* Creates courses if they do not already exist
* Inserts exam records into the database
* Supports split venues by creating separate exam entries

---

## Running Tests

Tests are configured using `pytest` and use an isolated test database.

```bash
pytest
```

---

## Environment Variables

Environment variables required for the project (e.g., database URI, secrets) will be provided separately during handover.

---

## Notes

* The system follows an MVC-style Flask structure with controllers handling business logic.
* Scheduling strategies (e.g., loading from previous timetables or optimisation approaches) are modular and can be extended.

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

* Enrollment history is not permanently stored in the database.
* At the end of each semester, enrollment data is exported externally.
* The Enrollment table is cleared before the start of a new semester.

---

## Future Improvements

* Full optimisation-based scheduling strategy integration
* Improved validation and error handling for imported data
* Enhanced UI for schedule visualisation and editing
