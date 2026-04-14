# UWI Final Exam Scheduler

## Overview

The UWI Final Exam Scheduler is a Flask-based web application designed to streamline the exam scheduling process and reduce the occurrence of back-to-back exams for students. It provides tools for importing data, generating schedules, managing exam allocations, and detecting scheduling conflicts via a clash matrix.

---

## Tech Stack

| Layer                 | Technology                                                                             |
| --------------------- | -------------------------------------------------------------------------------------- |
| **Backend**           | Flask (Python)                                                                         |
| **Auth**              | Flask-JWT-Extended (JWT Bearer tokens)                                                 |
| **Database**          | PostgreSQL (NeonDB) via SQLAlchemy ORM                                                 |
| **Migrations**        | Flask-Migrate / Alembic                                                                |
| **Admin UI**          | Flask-Admin                                                                            |
| **PDF Parsing**       | pdfplumber / pdfminer.six                                                              |
| **Optimisation**      | PuLP (LP solver)                                                                       |
| **Data Processing**   | Pandas / CSV handling                                                                  |
| **Production Server** | Gunicorn + gevent workers                                                              |
| **Testing**           | Pytest (unit/integration), Newman (API), Locust (performance), Mocha + Puppeteer (E2E) |
| **Deployment**        | Render                                                                                 |

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

### 2. Set Environment Variables

Create a `.env` file (or export variables) with at minimum:

```
DATABASE_URL=<your_postgres_connection_string>
SECRET_KEY=<your_secret_key>
JWT_SECRET_KEY=<your_jwt_secret>
ENV=development
```

### 3. Run the Application

```bash
flask run
```

The application is accessible at:

```
http://127.0.0.1:5000/
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

The project includes several custom Flask CLI commands to manage the database and load data.

### Reset Database

Drops all tables and recreates the database schema.

```bash
flask db-reset
```

### Import Courses

Imports course data from a CSV file into the database.

```bash
flask import-all-courses
```

### Import Students

Imports student data from a CSV file.

```bash
flask import-all-students
```

### Import Enrollments

Imports enrollment data linking students to courses.

```bash
flask import-all-enrollments
```

### Import Venues

Imports venue data including capacity information.

```bash
flask import-all-venues
```

### Load From Last Timetable

Loads a previous year's timetable from a PDF file and inserts it into the database.

```bash
flask load-from-last
```

This command:

- Parses exam data from a provided PDF using pdfplumber
- Creates courses if they do not already exist
- Inserts exam records into the database
- Supports split venues by creating separate exam entries

---

## Database Management

### Migrations

```bash
flask db migrate
```

Use when changes to the code affect the database schema (e.g., adding or modifying models).

```bash
flask db upgrade
```

Apply the latest schema changes to the database.

---

## API Reference

All endpoints (except `/api/auth/login`) require a valid JWT Bearer token:

```
Authorization: Bearer <access_token>
```

Admin-only endpoints return `401` if the authenticated user does not have the `admin` role.

---

### Auth

| Method | Endpoint                | Auth  | Description                                                           |
| ------ | ----------------------- | ----- | --------------------------------------------------------------------- |
| `POST` | `/api/auth/login`       | None  | Log in; returns `access_token`, `user_id`, `username`, `role`         |
| `GET`  | `/api/auth/identify`    | JWT   | Returns the current user's identity from the token                    |
| `GET`  | `/api/auth/preferences` | Admin | Retrieve clash-detection thresholds for the current admin             |
| `PUT`  | `/api/auth/preferences` | Admin | Update clash-detection thresholds (`abs_threshold`, `perc_threshold`) |
| `GET`  | `/api/logout`           | JWT   | Clears JWT cookie                                                     |

**Login request body:**

```json
{ "username": "admin", "password": "adminpass" }
```

**Preferences body (PUT):**

```json
{ "abs_threshold": 10, "perc_threshold": 0.15 }
```

---

### Exams

All exam endpoints require **Admin** JWT.

| Method  | Endpoint                       | Description                                          |
| ------- | ------------------------------ | ---------------------------------------------------- |
| `GET`   | `/api/exams`                   | List all exams                                       |
| `GET`   | `/api/exams/<date>`            | List exams on a specific date (`YYYY-MM-DD`)         |
| `GET`   | `/api/exams/days_with_exams`   | List all dates that have at least one exam scheduled |
| `GET`   | `/api/exams/need_rescheduling` | List exams that are unscheduled or have conflicts    |
| `PATCH` | `/api/exams/reschedule`        | Reschedule (or unschedule) a single exam             |
| `POST`  | `/api/exams/split`             | Split an exam into multiple sittings                 |
| `POST`  | `/api/exams/merge`             | Merge multiple exam splits back into one             |

**Reschedule body (PATCH):**

```json
{
  "examId": 42,
  "date": "2026-12-10",
  "time": 9,
  "venueId": null,
  "unschedule": false,
  "preventMerge": false
}
```

**Split body (POST):**

```json
{
  "examId": 42,
  "splits": [{ "number_of_students": 30 }, { "number_of_students": 25 }],
  "venueId": null,
  "time": 9,
  "date": "2026-12-10"
}
```

**Merge body (POST):**

```json
{ "examIds": [43, 44] }
```

---

### Courses

All course endpoints require **Admin** JWT.

| Method | Endpoint                                                 | Description                           |
| ------ | -------------------------------------------------------- | ------------------------------------- |
| `GET`  | `/api/courses?page=1&per_page=20`                        | Paginated list of courses             |
| `GET`  | `/api/courses/<course_code>`                             | Single course detail                  |
| `GET`  | `/api/courses/subjects`                                  | List distinct subject prefix codes    |
| `GET`  | `/api/courses/subject/<subject_code>?page=1&per_page=20` | Paginated courses filtered by subject |

---

### Venues

All venue endpoints require **Admin** JWT.

| Method | Endpoint                   | Description          |
| ------ | -------------------------- | -------------------- |
| `GET`  | `/api/venues`              | List all venues      |
| `GET`  | `/api/venues/<venue_name>` | Single venue by name |

---

### Clash Matrix

Requires **Admin** JWT. Identifies pairs of courses sharing enrolled students.

| Method | Endpoint                                                                    | Description                          |
| ------ | --------------------------------------------------------------------------- | ------------------------------------ |
| `GET`  | `/api/clash-matrix?abs_threshold=5&perc_threshold=0.1`                      | Full clash matrix across all courses |
| `GET`  | `/api/course/<course_code>/clash-matrix?abs_threshold=5&perc_threshold=0.1` | Clashes for a single course          |

**Query parameters:**

- `abs_threshold` (int, default `5`) — minimum number of shared students to flag a clash
- `perc_threshold` (float, default `0.1`) — minimum percentage overlap to flag a clash

---

### File Upload

Requires **Admin** JWT. The endpoint auto-detects file type from the filename.

| Method | Endpoint      | Description                                            |
| ------ | ------------- | ------------------------------------------------------ |
| `POST` | `/api/upload` | Upload a CSV or timetable PDF (multipart `file` field) |

**Supported files:**

| Filename pattern      | Action                                            |
| --------------------- | ------------------------------------------------- |
| `*course*.csv`        | Import courses                                    |
| `*student*.csv`       | Import students                                   |
| `*enrollment*.csv`    | Import enrollments                                |
| `*venue*.csv`         | Import venues                                     |
| `*uwi*timetable*.pdf` | Replace all exam data from previous timetable PDF |

---

### Users

| Method | Endpoint     | Auth | Description      |
| ------ | ------------ | ---- | ---------------- |
| `GET`  | `/api/users` | None | Public user list |

---

## Running Tests

### Unit & Integration Tests (Pytest)

Tests run against an isolated test database configured in `App/tests/conftest.py`.

```bash
pytest
```

Tests are located in `App/tests/` and cover controllers, models, strategies, and API views.

---

### API Tests (Newman / Postman)

Install Newman:

```bash
npm install -g newman
```

**Run against local server:**

```bash
npx newman run ".\Postman\FINAL EXAM SCHEDULER.postman_collection.json" -e ".\Postman\Final Exam Scheduler Environment.postman_environment.json" --env-var "base_url=http://127.0.0.1:8080"
```

**Run against production:**

```bash
npx newman run ".\Postman\FINAL EXAM SCHEDULER.postman_collection.json" -e ".\Postman\Final Exam Scheduler Environment.postman_environment.json" --env-var "base_url=https://uwi-final-exam-scheduler.onrender.com"
```

---

### Performance Tests (Locust)

The `locustfile.py` simulates a full admin session exercising all major API endpoints with weighted task distribution.

**Start the Locust web UI:**

```bash
locust -f locustfile.py --host=http://127.0.0.1:8080
```

Then open `http://localhost:8089` to configure users and spawn rate.

**Override credentials via environment:**

```bash
LOCUST_USERNAME=admin LOCUST_PASSWORD=adminpass locust -f locustfile.py --host=http://127.0.0.1:8080
```

---

### E2E Tests (Mocha + Puppeteer)

Requires Node.js and a running local server on port 8080.

**Install dependencies:**

```bash
npm install
```

**Run tests:**

```bash
npm run e2e
```

E2E tests are located in `e2e/test.js` and use Puppeteer (headless Chrome) with Chai assertions.

---

## Environment Variables

| Variable           | Description                                     |
| ------------------ | ----------------------------------------------- |
| `DATABASE_URL`     | PostgreSQL connection string                    |
| `SECRET_KEY`       | Flask session secret                            |
| `JWT_SECRET_KEY`   | Secret for signing JWTs                         |
| `ENV`              | `development` or `production`                   |
| `PORT`             | Port for Gunicorn (set automatically by Render) |
| `WEB_CONCURRENCY`  | Number of Gunicorn workers (optional)           |
| `GUNICORN_TIMEOUT` | Request timeout in seconds (default `180`)      |

---

## Architecture Notes

- The system follows an MVC-style Flask structure: `models/`, `controllers/`, `views/`, `services/`, and `strategies/`.
- Scheduling is implemented via the Strategy pattern (`App/strategies/`):
  - `LoadFromLastStrategy` — parses a prior-year timetable PDF and seeds the database.
  - `OptimizationStrategy` — LP-based schedule optimisation using PuLP (extensible).
- The `ExamSchedulerService` acts as the orchestration layer between strategies and the database.
- Clash detection is computed on-demand from current enrollment data and filtered by configurable absolute and percentage thresholds (stored per admin in `UserPreference`).

---

## Data Handling Assumptions

- Enrollment history is not permanently stored in the database.
- At the end of each semester, enrollment data is exported externally.
- The Enrollment table is cleared before the start of a new semester.

---

## Future Improvements

- Full LP optimisation strategy (PuLP scaffolding already in place in `App/strategies/optimize.py`)
- Improved validation and error handling for imported data
- Enhanced UI for schedule visualisation and editing
