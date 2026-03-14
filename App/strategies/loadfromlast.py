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
        "Time",
        "Venue",
        "Exam Length",
        "Number of Students"
    ]

    # Front part of the row
    main_pattern = re.compile(
        r"^(\d+)\s+"                              # Exam ID
        r"([A-Z]+)\s+(\d{4})\s+"                  # Course prefix + number
        r"(.+?)\s+"                               # Course title
        r"([A-Z]+\s+\d{2}\s+[A-Z]+\s+\d{4})\s+"   # Date
        r"(\d{1,2}:\d{2}\s+[AP]M)\s+"             # Time
        r"(.+)$"                                  # Rest of line
    )

    # Back part of the row
    rest_pattern = re.compile(
        r"^(.*?)\s+(\d+)\s+(\d+)(?:\s+(.*))?$"
    )

    cleaned_rows = []

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
                        continue

                    exam_id = main_match.group(1)
                    course_code = f"{main_match.group(2)}{main_match.group(3)}"
                    course_title = main_match.group(4)
                    date = main_match.group(5)
                    time = main_match.group(6)   # captured if you need it later
                    rest = main_match.group(7)

                    rest_match = rest_pattern.match(rest)
                    if not rest_match:
                        print(f"Could not parse rest of row: {raw_text}")
                        continue

                    venue = rest_match.group(1).strip()
                    exam_length = rest_match.group(2)
                    num_students = rest_match.group(3)
                    trailing_text = rest_match.group(4)

                    # If text appears after the numbers, it probably belongs to the venue
                    if trailing_text:
                        venue = f"{venue} {trailing_text}".strip()

                    cleaned_rows.append([
                        exam_id,
                        course_code,
                        course_title,
                        date,
                        time,
                        venue,
                        exam_length,
                        num_students
                    ])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(cleaned_rows)

    print(f"CSV saved to: {csv_path}")