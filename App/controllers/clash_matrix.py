from App.models.clash_matrix import ClashMatrix
from App.models.course import Course, Enrollment
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