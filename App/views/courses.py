from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required,get_jwt_identity, current_user as jwt_current_user   
from App.controllers.courses import (
    get_all_courses,
    get_course_by_code,
    get_courses_by_subject,
    get_subject_codes
)
from App.controllers.auth import is_admin

course_views = Blueprint('course_views', __name__, template_folder='../templates')

@course_views.route('/api/courses', methods=['GET'])
@jwt_required()
def get_courses():
    authenticated_user =  get_jwt_identity()

    # Ensure the user is authenticated before accessing courses
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page',20, type=int)

        if page < 1:
            return jsonify({'error': 'Page number must be greater than 0'}), 400
        if per_page < 1:
            return jsonify({'error': 'Per page must be greater than 0'}), 400
        courses = get_all_courses(page=page, per_page=per_page)
        if courses is None:
            return jsonify({'error': 'No courses found'}), 404  # mock test needed
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 #mock test needed

@course_views.route('/api/courses/<course_code>', methods=['GET'])
@jwt_required()
def get_courseInfo(course_code):
    authenticated_user = get_jwt_identity()

    # Ensure the user is authenticated before accessing course info
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
    
    try:
        course_data = get_course_by_code(course_code)
        if course_data is None:
            return jsonify({'error': 'Course not found'}), 404  # mock test needed
        return jsonify(course_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # mock test needed
    
@course_views.route('/api/courses/subject/<subject_code>', methods=['GET'])
@jwt_required()
def get_coursesBySubject(subject_code):
    authenticated_user = get_jwt_identity()

    # Ensure the user is authenticated before accessing courses by subject
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page',20, type=int)

        if page < 1:
            return jsonify({'error': 'Page number must be greater than 0'}), 400
        if per_page < 1:
            return jsonify({'error': 'Per page must be greater than 0'}), 400
        
        courses = get_courses_by_subject(subject_code, page=page, per_page=per_page)
        if courses is None:
            return jsonify({'error': 'No courses found for subject'}), 404  # mock test needed
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # mock test needed

@course_views.route('/api/courses/subjects', methods=['GET'])
@jwt_required()
def get_subjectCodes():
    authenticated_user = get_jwt_identity()

    # Ensure the user is authenticated before accessing subject codes
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
    
    try: 
        subject_codes = get_subject_codes()
        if subject_codes is None:
            return jsonify({'error': 'No subject codes found'}), 404  # mock test needed
        return jsonify(subject_codes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # mock test needed