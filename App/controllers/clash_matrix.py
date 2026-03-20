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
    conflicting_courses = []
    unique_courses = set()
    
    # get total enrollments for each course to use in percentage threshold calculations 
    enrollments_counts = db.session.query(Enrollment.courseCode, db.func.count(Enrollment.student_id)).group_by(Enrollment.courseCode).all()
    enrollment_count = dict(enrollments_counts)

    clashes = ClashMatrix.query.all()
    for clash in clashes:
        if absolute_threshold(clash.clash_count, abs_threshold=abs_threshold) and \
           exceeds_percentage_threshold(clash.clash_count, enrollment_count, clash.course1, clash.course2, perc_thresh=perc_threshold):
            conflicting_courses.append({
                "course1": clash.course1,
                "course2": clash.course2,
                "clash_count": clash.clash_count
            })
            unique_courses.add(clash.course1)
            unique_courses.add(clash.course2)

    return {
        "total_conflicts": len(conflicting_courses),
        "unique_courses_with_conflicts": len(unique_courses),
        "conflicting_courses": conflicting_courses
    }

def view_course_clashes(course_code, abs_threshold=5, perc_threshold=0.1):
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