from pathlib import Path
from datetime import datetime
import pdfplumber
import re

from App import db
from App.models.exam import Exam
from App.models.venue import Venue
from App.models.course import Course
from App.strategies.strategy import SchedulingStrategy


class LoadFromLastStrategy(SchedulingStrategy):

    def execute(self, **kwargs):
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[2]

        data_dir = project_root / "Data"
        pdf_path = data_dir / "UWI Timetable Cross Reference Final 202510 17NOV2025.pdf"

        main_pattern = re.compile(
            r"^(\d+)\s+"
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
                            print(f"Could not parse main row: {raw_text}")
                            skipped += 1
                            continue

                        exam_id = int(main_match.group(1))
                        course_code = f"{main_match.group(2)}{main_match.group(3)}"
                        course_title = main_match.group(4)
                        date_str = main_match.group(5)
                        time_str = main_match.group(6)
                        rest = main_match.group(7)

                        rest_match = rest_pattern.match(rest)
                        if not rest_match:
                            print(f"Could not parse rest of row: {raw_text}")
                            skipped += 1
                            continue

                        venue_name = rest_match.group(1).strip()
                        exam_length = int(rest_match.group(2))
                        number_of_students = int(rest_match.group(3))
                        trailing_text = rest_match.group(4)

                        if trailing_text:
                            venue_name = f"{venue_name} {trailing_text}".strip()

                        parsed_date = datetime.strptime(date_str, "%A %d %B %Y").date()
                        date_obj = parsed_date.replace(year=datetime.now().year)

                        time_obj = datetime.strptime(time_str, "%I:%M %p").time()

                        course = Course.query.filter_by(courseCode=course_code).first()
                        if not course:
                            course = Course(
                                courseCode=course_code,
                                name=course_title
                            )
                            db.session.add(course)
                            created_courses += 1

                        venue = Venue.query.filter_by(name=venue_name).first()
                        if not venue:
                            print(f"Missing venue: {venue_name}")
                            skipped += 1
                            continue

                        existing_exam = Exam.query.get(exam_id)

                        if existing_exam:
                            existing_exam.courseCode = course_code
                            existing_exam.date = date_obj
                            existing_exam.time = time_obj
                            existing_exam.venue_id = venue.id
                            existing_exam.exam_length = exam_length
                            existing_exam.number_of_students = number_of_students
                            updated += 1
                        else:
                            exam = Exam(
                                id=exam_id,
                                courseCode=course_code,
                                date=date_obj,
                                time=time_obj,
                                venue_id=venue.id,
                                exam_length=exam_length,
                                number_of_students=number_of_students
                            )
                            db.session.add(exam)
                            inserted += 1

        db.session.commit()

        return {
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "created_courses": created_courses
        }