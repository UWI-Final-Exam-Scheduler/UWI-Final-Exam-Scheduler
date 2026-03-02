from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user as jwt_current_user   
from App.models import Course
from App.controllers.courses import (
    get_all_courses,
    get_course_by_code,
    get_courses_by_subject
)

course_views = Blueprint('course_views', __name__, template_folder='../templates')

@course_views.route('/api/courses', methods=['GET'])
@jwt_required()
def get_courses():
    authenticated_user = jwt_current_user

    # Ensure the user is authenticated before accessing courses
    if not authenticated_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        courses = get_all_courses()
        if courses is None:
            return jsonify({'error': 'No courses found'}), 404
        courses_data = [{'courseCode': course.courseCode, 'name': course.name} for course in courses]
        return jsonify(courses_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@course_views.route('/api/courses/<course_code>', methods=['GET'])
@jwt_required()
def get_courseInfo(course_code):
    authenticated_user = jwt_current_user

    # Ensure the user is authenticated before accessing course info
    if not authenticated_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        course_data = get_course_by_code(course_code)
        if course_data is None:
            return jsonify({'error': 'Course not found'}), 404
        return jsonify(course_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@course_views.route('/api/courses/subject/<subject_code>', methods=['GET'])
@jwt_required()
def get_coursesBySubject(subject_code):
    authenticated_user = jwt_current_user

    # Ensure the user is authenticated before accessing courses by subject
    if not authenticated_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        courses = get_courses_by_subject(subject_code)
        if courses is None:
            return jsonify({'error': 'No courses found for subject'}), 404
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500