# from .strategy import SchedulingStrategy
from pathlib import Path
import pdfplumber
import csv
import re

class LoadFromLastStrategy ():
    
    # def importTimetable(self):
    #     current_file = Path(__file__).resolve()
    #     project_root = current_file.parents(2)

    #     pdf_path = project_root/ "Data" / "UWI Timetable Cross Reference Final 202510 17NOV2025.pdf"
    #     with pdfplumber.open(pdf_path) as pdf:
    #             for page in pdf.pages:
    #                 table = page.extract_table()

    #                 if table:
    #                     for row in table:
    #                         print(row)
    #     pass



    current_file = Path(__file__).resolve()
    project_root = current_file.parents[2]

    data_dir = project_root / "Data"
    pdf_path = data_dir / "UWI Timetable Cross Reference Final 202510 17NOV2025.pdf"
    csv_path = data_dir / "lastyear.csv"

    headers = [
        "Exam ID",
        "CourseCode",
        "Course Title",
        "Date",
        "Venue",
        "Exam Length",
        "Number of Students"
    ]

    pattern = re.compile(
        r"^(\d+)\s+"                              # Exam ID
        r"([A-Z]{3,4})\s+(\d{4})\s+"             # Course code
        r"(.+?)\s+"                              # Course title
        r"([A-Z]+\s+\d{2}\s+[A-Z]+\s+\d{4})\s+" # Date
        r"(\d{1,2}:\d{2}\s+[AP]M)\s+"            # Time
        r"(.+)\s+"                               # Venue
        r"(\d+)\s+"                              # Exam length
        r"(\d+)$"                                # Number of students
    )

    cleaned_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    if not row or not row[0]:
                        continue

                    raw_text = row[0].strip()

                    match = pattern.match(raw_text)
                    if not match:
                        print(f"Could not parse row: {raw_text}")
                        continue

                    exam_id = match.group(1)
                    course_code = f"{match.group(2)} {match.group(3)}"
                    course_title = match.group(4)
                    date = match.group(5)
                    # time = match.group(6)   # captured, but not used, will see what to do with it later
                    venue = match.group(7)
                    exam_length = match.group(8)
                    num_students = match.group(9)

                    cleaned_rows.append([
                        exam_id,
                        course_code,
                        course_title,
                        date,
                        venue,
                        exam_length,
                        num_students
                    ])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(cleaned_rows)

    print(f"CSV saved to: {csv_path}")
