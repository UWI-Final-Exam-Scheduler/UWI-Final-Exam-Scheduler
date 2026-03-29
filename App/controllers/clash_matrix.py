from App.models.clash_matrix import ClashMatrix
from App.models.course import Course
from App.models.enrollment import Enrollment
from App.database import db
from collections import defaultdict

def create_clash_matrix(enrollments):
    #grouping courses by student
    student_courses = defaultdict(set)
    for student_id, course_code in enrollments:
        student_courses[student_id].add(course_code)

    clash_matrix = defaultdict(lambda: defaultdict(int))

    #building the clash matrix by counting co-enrollments for each pair of courses
    for courses in student_courses.values():
        courses = list(courses)
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                course1, course2 = sorted([courses[i], courses[j]])
                clash_matrix[course1][course2] += 1
                clash_matrix[course2][course1] += 1
    
    #clearing existing clash matrix data each time enrollments is imported
    ClashMatrix.query.delete()

    #inserting new clash matrix data into the database
    clash_list = []
    for course1, clashes in clash_matrix.items():
        for course2, count in clashes.items():
            if course1 < course2:  
                clash = ClashMatrix(course1=course1, course2=course2, clash_count=count)
                clash_list.append(clash)
    db.session.bulk_save_objects(clash_list)
    db.session.commit()
    return clash_matrix

def absolute_threshold(clash_count, abs_threshold=5):
    return clash_count >= abs_threshold

def exceeds_percentage_threshold(clash_count, enrollment_count, course1, course2, perc_thresh=0.1):
    c1_enrollment = enrollment_count.get(course1, 0)
    c2_enrollment = enrollment_count.get(course2, 0)
    
    smaller_class = min(c1_enrollment, c2_enrollment)
    if smaller_class == 0:
        return False
    return (clash_count / smaller_class) >= perc_thresh

# would only show clashes when both thresholds are satisfied
def view_conflicting_courses(abs_threshold=5, perc_threshold=0.1):
    qualifying_clashes = []  # to store clashes that meet the threshold criteria for later processing
    course_has_clash = set() # to track which courses have at least one qualifying clash
    affected_students = set() # to track unique students affected by qualifying clashes

    enrollment_counts = db.session.query(Enrollment.courseCode, db.func.count(Enrollment.student_id)).group_by(Enrollment.courseCode).all()
    enrollment_count = dict(enrollment_counts)

    clashes = ClashMatrix.query.filter(ClashMatrix.clash_count >= abs_threshold).all()  # initial filter to reduce number of clashes to evaluate against percentage threshold

    for clash in clashes:
        if absolute_threshold(clash.clash_count, abs_threshold=abs_threshold) and \
           exceeds_percentage_threshold(
               clash.clash_count,
               enrollment_count,
               clash.course1,
               clash.course2,
               perc_thresh=perc_threshold
           ):
            qualifying_clashes.append(clash)
            course_has_clash.add(clash.course1)
            course_has_clash.add(clash.course2)

    courses_to_fetch = set() # to track which courses to fetch enrollments for when calculating affected students
    for clash in qualifying_clashes:
        courses_to_fetch.add(clash.course1)
        courses_to_fetch.add(clash.course2)

    course_students = defaultdict(set)  # to store sets of students for each course to efficiently calculate affected students

    if courses_to_fetch:
        enrollment_rows = (
            db.session.query(Enrollment.courseCode, Enrollment.student_id)
            .filter(Enrollment.courseCode.in_(courses_to_fetch))
            .all()
        )

        for course_code, student_id in enrollment_rows:
            course_students[course_code].add(student_id)

    #calculate students affected by qualifying clashes by finding intersections of student sets for each pair of conflicting courses
    for clash in qualifying_clashes:
        affected_students.update(
            course_students[clash.course1].intersection(course_students[clash.course2])  
        )

    conflicting_courses = [
        {
            "course1": clash.course1,
            "course2": clash.course2,
            "clash_count": clash.clash_count,
        }
        for clash in qualifying_clashes
    ]

    unique_courses_with_conflicts = [
        {
            "course": course_code,
            "has_clash": True,
        }
        for course_code in course_has_clash
    ]

    total_students = db.session.query(Enrollment.student_id).distinct().count()
    affected_students_percentage = (
        len(affected_students) / total_students * 100 if total_students > 0 else 0
    )

    return {
        # "conflicting_courses": conflicting_courses,
        "courses": unique_courses_with_conflicts,
        # "total_conflicts": len(qualifying_clashes),
        "unique_courses_with_conflicts": len(course_has_clash),
        "total_students_affected": len(affected_students),
        "percentage_students_affected": round(affected_students_percentage, 2),
    }

def view_course_clashes(course_code, abs_threshold=5, perc_threshold=0.1):
    has_clash = False
    course_code = course_code.upper()
    clashes = ClashMatrix.query.filter((ClashMatrix.course1 == course_code) | (ClashMatrix.course2 == course_code)).all()
    
    if not clashes:
        return f"No clashes found for course {course_code}."

    enrollments_counts = db.session.query(Enrollment.courseCode, db.func.count(Enrollment.student_id)).group_by(Enrollment.courseCode).all()
    enrollment_count = dict(enrollments_counts)


    course_clashes = []
    for clash in clashes:
        other_course = clash.course2 if clash.course1 == course_code else clash.course1
        if absolute_threshold(clash.clash_count, abs_threshold=abs_threshold) and \
        exceeds_percentage_threshold(clash.clash_count, enrollment_count, clash.course1, clash.course2, perc_thresh=perc_threshold):
            course_clashes.append({
                "other_course": other_course,
                "clash_count": clash.clash_count
            })

    return {
        "course": course_code,
        "clashes": course_clashes,
        "total_clashes": len(course_clashes)
    }