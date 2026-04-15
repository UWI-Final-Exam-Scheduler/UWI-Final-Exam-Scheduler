import os
import random
from locust import HttpUser, task, between

ADMIN_USERNAME = os.getenv("LOCUST_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("LOCUST_PASSWORD", "adminpass")

SAMPLE_COURSE_CODES = ["COMP1601", "COMP1602", "COMP2605", "MATH1142", "MATH1152"]
SAMPLE_SUBJECT_CODES = ["COMP", "MATH", "FOUN", "MGMT"]
SAMPLE_VENUE_NAMES = ["JFK Auditorium", "Mechanical Design Office (MD2)", "The Temporary Room at Chemistry"]

SAMPLE_EXAM_DATES = [
    "2026-12-10",
    "2026-11-30",
    "2026-12-16",
    "2026-12-17",
    "2026-12-04",
]

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "Test Data")

class ExamSchedulerAdminUser(HttpUser):
    # Simulates an admin user performing the full range of API operations.
    wait_time = between(0.5, 1)
 
    def on_start(self):
        self.csrf_token = None

        response = self.client.post(
            "/api/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            name="POST /api/auth/login",
        )

        if response.status_code == 200:
            # Extract CSRF token from cookies
            self.csrf_token = self.client.cookies.get("csrf_access_token")
        else:
            raise Exception("Login failed")
 
    def on_stop(self):
        # Log out at the end of the session.
        self.client.get("/api/logout", name="GET /api/logout")
 
    def auth_headers(self) -> dict:
        headers = {}

        if self.csrf_token:
            headers["X-CSRF-TOKEN"] = self.csrf_token

        return headers
    
    # AUTH ROUTES

    @task(2)
    def identify(self):
        # GET /api/auth/identify — lightweight token-validation check.
        self.client.get(
            "/api/auth/identify",
            headers=self.auth_headers(),
            name="GET /api/auth/identify",
        )
 
    @task(1)
    def get_preferences(self):
        # GET /api/auth/preferences — fetch admin threshold preferences.
        self.client.get(
            "/api/auth/preferences",
            headers=self.auth_headers(),
            name="GET /api/auth/preferences",
        )

    @task(1)
    def update_preferences(self):
        # PUT /api/auth/preferences — update admin threshold preferences.
        self.client.put(
            "/api/auth/preferences",
            headers=self.auth_headers(),
            json={
                "abs_threshold": random.randint(0, 100),
                "perc_threshold": random.uniform(0, 100),
            },
            name="PUT /api/auth/preferences",
        )

    # EXAM ROUTES (Highest Weight)

    @task(5)
    def get_all_exams(self):
        # GET /api/exams — fetch entire exam list.
        self.client.get(
            "/api/exams",
            headers=self.auth_headers(),
            name="GET /api/exams",
        )
 
    @task(4)
    def get_exams_by_date(self):
        # GET /api/exams/<date> — fetch exams for a specific date.
        date = random.choice(SAMPLE_EXAM_DATES)
        self.client.get(
            f"/api/exams/{date}",
            headers=self.auth_headers(),
            name="GET /api/exams/<date>",
        )
 
    @task(3)
    def get_days_with_exams(self):
        # GET /api/exams/days_with_exams — fetch all scheduled exam dates.
        self.client.get(
            "/api/exams/days_with_exams",
            headers=self.auth_headers(),
            name="GET /api/exams/days_with_exams",
        )
 
    @task(3)
    def get_exams_needing_rescheduling(self):
        # GET /api/exams/need_rescheduling — unscheduled / conflict list.
        self.client.get(
            "/api/exams/need_rescheduling",
            headers=self.auth_headers(),
            name="GET /api/exams/need_rescheduling",
        )
 
    @task(2)
    def reschedule_exam(self):
        response = self.client.get(
            "/api/exams",
            headers=self.auth_headers(),
            name="GET /api/exams (reschedule setup)",
        )
        if response.status_code != 200:
            return

        exams = response.json()
        if not exams:
            return

        exam = random.choice(exams)
        
        exam_id = exam.get("exam_id")
        if not exam_id:
            return

        self.client.patch(
            "/api/exams/reschedule",
            headers=self.auth_headers(),
            json={
                "examId": exam_id,
                "date": random.choice(SAMPLE_EXAM_DATES),
                "time": random.choice([9, 1, 4]),
                "venueId": None,
                "unschedule": False,
                "preventMerge": False,
            },
            name="PATCH /api/exams/reschedule",
        )

    @task(1)
    def split_then_merge_exam(self):
        response = self.client.get(
            "/api/exams",
            headers=self.auth_headers(),
            name="GET /api/exams (split/merge setup)",
        )
        if response.status_code != 200:
            return

        exams = response.json()
        if not exams:
            return

        # Only pick exams with enough students to split
        eligible = [e for e in exams if e.get("number_of_students", 0) >= 2]
        if not eligible:
            return

        exam = random.choice(eligible)
        exam_id = exam["exam_id"]
        total_students = exam["number_of_students"]

        # Generate 2-4 splits that sum exactly to total_students
        num_splits = random.randint(2, min(4, total_students))
        base = total_students // num_splits
        splits = [{"number_of_students": base} for _ in range(num_splits)]
        splits[0]["number_of_students"] += total_students - (base * num_splits)

        split_response = self.client.post(
            "/api/exams/split",
            headers=self.auth_headers(),
            json={
                "examId": exam_id,
                "splits": splits,
                "venueId": None,
                "time": 9,
                "date": random.choice(SAMPLE_EXAM_DATES),
            },
            name="POST /api/exams/split",
        )
        if split_response.status_code != 201:
            return

        # Immediately merge back using the freshly created IDs
        new_ids = [e["exam_id"] for e in split_response.json()]

        self.client.post(
            "/api/exams/merge",
            headers=self.auth_headers(),
            json={"examIds": new_ids},
            name="POST /api/exams/merge",
        )
 
    # COURSE ROUTES

    @task(4)
    def get_all_courses(self):
        # GET /api/courses — paginated course list.
        page = random.randint(1, 3)
        self.client.get(
            f"/api/courses?page={page}&per_page=20",
            headers=self.auth_headers(),
            name="GET /api/courses",
        )
 
    @task(3)
    def get_course_by_code(self):
        # GET /api/courses/<code> — single course detail lookup.
        code = random.choice(SAMPLE_COURSE_CODES)
        self.client.get(
            f"/api/courses/{code}",
            headers=self.auth_headers(),
            name="GET /api/courses/<code>",
        )
 
    @task(2)
    def get_subject_codes(self):
        # GET /api/courses/subjects — list all distinct subject prefixes.
        self.client.get(
            "/api/courses/subjects",
            headers=self.auth_headers(),
            name="GET /api/courses/subjects",
        )
 
    @task(2)
    def get_courses_by_subject(self):
        # GET /api/courses/subject/<code> — courses filtered by subject.
        subject = random.choice(SAMPLE_SUBJECT_CODES)
        self.client.get(
            f"/api/courses/subject/{subject}?page=1&per_page=20",
            headers=self.auth_headers(),
            name="GET /api/courses/subject/<code>",
        )

    # VENUE ROUTES

    @task(3)
    def get_all_venues(self):
        # GET /api/venues — full venue list.
        self.client.get(
            "/api/venues",
            headers=self.auth_headers(),
            name="GET /api/venues",
        )
 
    @task(2)
    def get_venue_by_name(self):
        # GET /api/venues/<name> — single venue lookup.
        name = random.choice(SAMPLE_VENUE_NAMES)
        self.client.get(
            f"/api/venues/{name}",
            headers=self.auth_headers(),
            name="GET /api/venues/<name>",
        )

    # CLASH-MATRIX ROUTES (Most DB-Intensive)

    @task(2)
    def get_clash_matrix(self):
        # GET /api/clash-matrix — computes the full student-overlap matrix.
        self.client.get(
            "/api/clash-matrix?abs_threshold=5&perc_threshold=0.1",
            headers=self.auth_headers(),
            name="GET /api/clash-matrix",
        )
 
    @task(1)
    def get_course_clash_matrix(self):
        # GET /api/course/<code>/clash-matrix — clashes for one course.
        code = random.choice(SAMPLE_COURSE_CODES)
        self.client.get(
            f"/api/course/{code}/clash-matrix?abs_threshold=5&perc_threshold=0.1",
            headers=self.auth_headers(),
            name="GET /api/course/<code>/clash-matrix",
        )

    # UPLOAD ROUTES

    @task(1)
    def upload_courses_csv(self):
        file_path = os.path.join(TEST_DATA_DIR, "sem2_courses.csv")
        with open(file_path, "rb") as f:
            self.client.post(
                "/api/upload",
                headers=self.auth_headers(),
                files={"file": (os.path.basename(file_path), f, "text/csv")},
                name="POST /api/upload (courses csv)",
            )

    @task(1)
    def upload_students_csv(self):
        file_path = os.path.join(TEST_DATA_DIR, "students.csv")
        with open(file_path, "rb") as f:
            self.client.post(
                "/api/upload",
                headers=self.auth_headers(),
                files={"file": (os.path.basename(file_path), f, "text/csv")},
                name="POST /api/upload (students csv)",
            )

    @task(1)
    def upload_venues_csv(self):
        file_path = os.path.join(TEST_DATA_DIR, "venues.csv")
        with open(file_path, "rb") as f:
            self.client.post(
                "/api/upload",
                headers=self.auth_headers(),
                files={"file": (os.path.basename(file_path), f, "text/csv")},
                name="POST /api/upload (venues csv)",
            )

    @task(1)
    def upload_enrollments_csv(self):
        file_path = os.path.join(TEST_DATA_DIR, "enrollments.csv")
        with open(file_path, "rb") as f:
            self.client.post(
                "/api/upload",
                headers=self.auth_headers(),
                files={"file": (os.path.basename(file_path), f, "text/csv")},
                name="POST /api/upload (enrollments csv)",
            )

    # USER ROUTES

    @task(1)
    def get_users_api(self):
        # GET /api/users — public user list endpoint.
        self.client.get("/api/users", name="GET /api/users")