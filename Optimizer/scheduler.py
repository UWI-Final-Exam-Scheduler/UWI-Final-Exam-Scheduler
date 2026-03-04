from pulp import *
import random
from datetime import datetime, timedelta, time

problem = LpProblem("Exam_Scheduling_Problem", LpMinimize)

#these sets need to be populated with actual data
exams = ["COMP3600", "COMP3601", "COMP3602"]  # exams
students = ["S1", "S2", "S3", "S4", "S5"]  # students
venues = ["MD2", "MD3"]  # venues


enrollments = {
    "S1": ["COMP3600"],
    "S2": ["COMP3600", "COMP3601"],
    "S3": ["COMP3601"],
    "S4": ["COMP3602"],
    "S5": ["COMP3600", "COMP3602"]
}

# student_registered_for_exam[(student,exam)] = 1 if student student registered for exam exam, else 0
student_registered_for_exam = {}

for student in students:
    for exam in exams:
        student_registered_for_exam[(student, exam)] = 1 if exam in enrollments.get(student, []) else 0



# Exam period starts here
exam_start_date = datetime(2026, 4, 20)  # Monday
number_of_exam_days  = 15

session_start_times = {
    1: time(9, 0),   # 09:00
    2: time(13, 0),  # 13:00
    3: time(17, 0)   # 17:00
}

timeslots = []

current_date = exam_start_date
working_days_added = 0

while working_days_added < number_of_exam_days:
    if current_date.weekday() < 5:
        for session_time in session_start_times.values():
            slot_datetime = datetime.combine(current_date.date(), session_time)
            timeslots.append(slot_datetime)
        working_days_added += 1
    current_date += timedelta(days=1)

# cost[(exam,venue,timeslot)]
cost = {}  

for exam in exams:
    for venue in venues:
        for timeslot in timeslots:
            cost[(exam, venue, timeslot)] = random.randint(1, 10)


# exam_num_students[exam] = number of students in exam exam
exam_num_students = {
    "COMP3600": 3,
    "COMP3601": 2,
    "COMP3602": 2
}

# capacity_of_venue[venue] = capacity of venue venue
capacity_of_venue = {
    "MD2": 5,
    "MD3": 3
}

student_sched_exam_time = pulp.LpVariable.dicts(
    "student_sched_exam_time",
    ((exam, venue, timeslot) for exam in exams for venue in venues for timeslot in timeslots),
    cat="Binary"
)

#Objective Function
problem += lpSum(cost[exam, venue, timeslot] * student_sched_exam_time[exam, venue, timeslot] for exam in exams for venue in venues for timeslot in timeslots)

#Constraint 1: Each exam must be assigned to exactly one venue and time
for exam in exams:
    problem+= lpSum(student_sched_exam_time[exam, venue, timeslot] for venue in venues for timeslot in timeslots) == 1, f"Exam_{exam}_scheduled_once"

#Constraint 2: No student can have overlapping exams
for student in students: 
    for timeslot in timeslots:
        problem += lpSum(student_registered_for_exam[student, exam]* student_sched_exam_time[exam, venue, timeslot] for exam in exams for venue in venues) <= 1,f"Student_{student}_no_overlap_at_time_{timeslot}"

#Constraint 3: Venue capacity must not be exceeded
for venue in venues:
    for timeslot in timeslots:
        problem += lpSum(student_sched_exam_time[exam, venue, timeslot] for exam in exams) <= capacity_of_venue[venue], f"Venue_{venue}_capacity_at_time_{timeslot}"

        
problem.solve()

print("Status:", LpStatus[problem.status])

for exam in exams:
    for venue in venues:
        for timeslot in timeslots:
            if student_sched_exam_time[exam, venue, timeslot].value() == 1:
                print(f"{exam} → {timeslot.strftime('%A %d %B %Y, %H:%M')} in {venue}")