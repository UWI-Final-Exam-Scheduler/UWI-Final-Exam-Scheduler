from pathlib import Path
from datetime import datetime
import pdfplumber
import re
from datetime import timedelta
from App import db
from App.models.exam import Exam
from App.models.venue import Venue
from App.models.course import Course
from App.strategies.strategy import SchedulingStrategy


class LoadFromLastStrategy(SchedulingStrategy):

    def is_date_within_exam_period(self, date):
        # Determine exam period based on the month of the date
        month = date.month
        year = date.year
        start, end = self.get_exam_period(year, month)
        return start <= date <= end
    
    def is_weekend(self, date):
        return date.weekday() >= 5  # 5 = Saturday, 6 = Sunday
    
    def get_exam_period(self, year, month):
        # Check if 1st/2nd December is a Monday to determine if the exam period starts in November or December for sem1
        if month == 12:
            dec_first = datetime(year, 12, 1).date()
            dec_second = datetime(year, 12, 2).date()
            if dec_first.weekday() == 0:  
                start = dec_first
            elif dec_second.weekday() == 0:
                start = dec_second
            else:
                # Check for last Monday in November
                start = datetime(year, 11, 30).date()
                while start.weekday() != 0:
                    start -= timedelta(days=1)
        # Check if 1st/2nd May is a Monday to determine if the exam period starts in April or May for sem2
        elif month == 5:
            may_first = datetime(year, 5, 1).date()
            may_second = datetime(year, 5, 2).date()
            if may_first.weekday() == 0: 
                start = may_first
            elif may_second.weekday() == 0:
                start = may_second
            else:
                # Check for last Monday in April
                start = datetime(year, 4, 30).date()
                while start.weekday() != 0:
                    start -= timedelta(days=1)
        else:
            # Default to sem1 
            dec_first = datetime(year, 12, 1).date()
            dec_second = datetime(year, 12, 2).date()
            if dec_first.weekday() == 0:
                start = dec_first
            elif dec_second.weekday() == 0:
                start = dec_second
            else:
                # Last Monday in November
                start = datetime(year, 11, 30).date()
                while start.weekday() != 0:
                    start -= timedelta(days=1)
        # 3 weeks (15 weekdays, Monday-Friday only)
        weekdays = 0
        days = []
        d = start
        while weekdays < 15:
            if d.weekday() < 5:
                days.append(d)
                weekdays += 1
            d += timedelta(days=1)
        # The last exam day is always a Friday (days[-1])
        return days[0], days[-1]

    def get_weekdays(self, start, end):
        # Always return exactly 15 weekdays (Monday-Friday), ending on a Friday
        days = []
        d = start
        while len(days) < 15 and d <= end:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        # If there are less than 15, keep going until we have 15 weekdays
        while len(days) < 15:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        # Ensure last day is a Friday
        if days[-1].weekday() != 4:
            # Find the previous Friday in the list
            for i in range(len(days)-1, -1, -1):
                if days[i].weekday() == 4:
                    days = days[:i+1]
                    break
        return days

    def map_exam_date_to_year(self, old_date, old_year, new_year, month):
        old_start, old_end = self.get_exam_period(old_year, month)
        new_start, new_end = self.get_exam_period(new_year, month)
        old_days = self.get_weekdays(old_start, old_end)
        new_days = self.get_weekdays(new_start, new_end)
        try:
            index = old_days.index(old_date)
        except ValueError:
            index = 0
        # map to a weekday, never a weekend/past the last Friday
        if index < len(new_days):
            mapped = new_days[index]
        else:
            mapped = new_days[-1]
        # If mapped day is a weekend, move to previous Friday
        if mapped.weekday() >= 5:
            # Find the previous Friday
            for i in range(index-1, -1, -1):
                if new_days[i].weekday() == 4:
                    mapped = new_days[i]
                    break
        return mapped

    def resolve_pdf_path(self, pdf_path=None):
        if pdf_path:
            return Path(pdf_path)

        current_file = Path(__file__).resolve()
        project_root = current_file.parents[2]
        data_dir = project_root / "Test Data"

        candidates = [
            path for path in data_dir.glob("*.pdf")
            if "uwi" in path.name.lower() and "timetable" in path.name.lower()
        ]

        if not candidates:
            raise FileNotFoundError(
                f"No timetable PDF found in {data_dir}. Expected a PDF filename containing both 'uwi' and 'timetable'."
            )

        return sorted(candidates)[0]

    def execute(self, **kwargs):
        pdf_path = self.resolve_pdf_path(kwargs.get("pdf_path"))
        admin_id = kwargs.get("admin_id")

        main_pattern = re.compile(
            r"^\d+\s+"
            r"([A-Z]+)\s+(\d{4})\s+"
            r"(.+?)\s+"
            r"([A-Z]+\s+\d{2}\s+[A-Z]+\s+\d{4})\s+"
            r"(\d{1,2}:\d{2}\s+[AP]M)\s+"
            r"(.+)$"
        )

        rest_pattern = re.compile(
            r"^(.*?)\s+(\d+)\s+(\d+)(?:\s+(.*))?$"
        )

        inserted = 0
        updated = 0
        skipped = 0
        created_courses = 0

        # to detect semester from first valid date from loaded timetable
        detected_month = None  
        detected_old_year = None
        # assume new year is the current year
        detected_new_year = datetime.now().year
        
        # Bulk load all courses and venues
        all_courses = {c.courseCode: c for c in Course.query.all()}
        all_venues = {v.name: v for v in Venue.query.all()}
        new_courses = []
        new_exams = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    for row in table:
                        if not row or not row[0]:
                            continue

                        raw_text = " ".join(str(row[0]).split())

                        main_match = main_pattern.match(raw_text)
                        if not main_match:
                            skipped += 1
                            continue

                        course_code = f"{main_match.group(1)}{main_match.group(2)}"
                        course_title = main_match.group(3)
                        date_str = main_match.group(4)
                        time_str = main_match.group(5)
                        rest = main_match.group(6)

                        rest_match = rest_pattern.match(rest)
                        if not rest_match:
                            skipped += 1
                            continue

                        venue_name = rest_match.group(1).strip()
                        exam_length = int(rest_match.group(2))
                        number_of_students = int(rest_match.group(3))
                        trailing_text = rest_match.group(4)

                        if trailing_text:
                            venue_name = f"{venue_name} {trailing_text}".strip()

                        parsed_date = datetime.strptime(date_str, "%A %d %B %Y").date()
                        # Detect semester and year from first valid date
                        if detected_month is None:
                            detected_month = parsed_date.month
                            detected_old_year = parsed_date.year
                        # old_dates.append(parsed_date)

                        parsed_time = datetime.strptime(time_str, "%I:%M %p")
                        hour = parsed_time.hour

                        # Convert to 12-hour format (no 0)
                        time_int = hour % 12
                        if time_int == 0:
                            time_int = 12

                        # Map old date to new year, skipping weekends, ensuring 3-week period
                        date_obj = self.map_exam_date_to_year(parsed_date, detected_old_year, detected_new_year, detected_month)
                        course = all_courses.get(course_code)
                        if not course:
                            course = Course(
                                courseCode=course_code,
                                name=course_title
                            )
                            new_courses.append(course)
                            all_courses[course_code] = course
                            created_courses += 1

                        venue = all_venues.get(venue_name)
                        if not venue:
                            skipped += 1
                            continue

                        existing_exam = Exam.query.filter_by(
                            courseCode=course_code,
                            date=date_obj,
                            time=time_int,
                            venue_id=venue.id
                        ).first()

                        if not existing_exam and not any(
                            e.courseCode == course_code and e.date == date_obj and e.time == time_int and e.venue_id == venue.id for e in new_exams
                        ):
                            exam = Exam(
                                courseCode=course_code,
                                date=date_obj,
                                time=time_int,
                                venue_id=venue.id,
                                exam_length=exam_length,
                                number_of_students=number_of_students, 
                                admin_id=admin_id
                            )
                            new_exams.append(exam)
                            inserted += 1

        if new_courses:
            db.session.bulk_save_objects(new_courses)
        if new_exams:
            db.session.bulk_save_objects(new_exams)
        db.session.commit()

        return {
            "msg": f"Past Timetable loaded successfully",
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "created_courses": created_courses
        }