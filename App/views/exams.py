from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from App.controllers import exams, venue
from App.models.admin import Admin
from flask_jwt_extended import jwt_required, current_user as jwt_current_user, get_jwt_identity

from App.controllers import get_exams_that_need_rescheduling, get_exams_by_date, reschedule_exam, get_all_exams, get_all_days_with_exams, sync_exams_with_enrollment_data, split_exam, merge_exams
from App.controllers.auth import is_admin

exams_views = Blueprint('exams_views', __name__, template_folder='../templates')

@exams_views.route('/api/exams', methods=['GET'])
@jwt_required()
def get_exams_view():
    authenticated_user = get_jwt_identity()
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
        
    try:
        exams = get_all_exams()
        if exams is None:
            return jsonify({'error': 'No exams found'}), 404
        return jsonify(exams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@exams_views.route('/api/exams/<string:exam_date>', methods=['GET'])
@jwt_required()
def get_exams_by_date_view(exam_date):
    authenticated_user = get_jwt_identity()
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
        
    try:
        exams = get_exams_by_date(exam_date)
        if exams is None:
            return [], 200
        return jsonify(exams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@exams_views.route('/api/exams/reschedule', methods=['PATCH'])
@jwt_required()
def reschedule_exam_view():
    authenticated_user = get_jwt_identity()
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
        
    data = request.get_json()
    exam_course_code = data.get('courseCode')
    date_str = data.get('date')
    time_str = data.get('time')
    venue_id = data.get('venue_id')
    unschedule = data.get('unschedule', False)

    if not exam_course_code:
        return jsonify({'error': 'courseCode is required'}), 400

    try:
        exam, error = reschedule_exam(exam_course_code, date_str, time_str, venue_id, unschedule)
        if error:
            return jsonify({'error': error}), 404
        return jsonify({
            "courseCode": exam.courseCode,
            "exam_date": exam.date.strftime("%Y-%m-%d") if exam.date else None, 
            "time": exam.time, 
            "venue_id": exam.venue_id,
            "exam_length": exam.exam_length,
            "number_of_students": exam.number_of_students
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@exams_views.route('/api/exams/need_rescheduling', methods=['GET'])
@jwt_required()
def get_exams_that_need_rescheduling_view():
    authenticated_user = get_jwt_identity()
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401 
    try:
        exams = get_exams_that_need_rescheduling()
        if exams is None:
            return [], 200
        return jsonify(exams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@exams_views.route('/api/exams/days_with_exams', methods=['GET'])
@jwt_required()
def get_all_days_with_exams_view():
    authenticated_user = get_jwt_identity()
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401 
    try:
        days = get_all_days_with_exams()
        print("DEBUG days from DB:", days)
        if days is None:
            return [], 200
        return jsonify(days), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exams_views.route('/api/exams/split', methods=['POST'])
@jwt_required()
def split_exam_view():
    authenticated_user = get_jwt_identity()
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401

    data = request.get_json()
    course_code = data.get('courseCode')
    splits = data.get('splits')       
    venue_id = data.get('venueId')    
    time = data.get('time')           
    date = data.get('date')           

    if not course_code:
        return jsonify({'error': 'courseCode is required'}), 400
    if not splits or not isinstance(splits, list):
        return jsonify({'error': 'splits must be a non-empty list'}), 400

    try:
        new_exams, error = split_exam(course_code, splits, venue_id, time, date)
        if error:
            return jsonify({'error': error}), 400

        return jsonify([
            {
                "id": exam.id,
                "courseCode": exam.courseCode,
                "exam_date": exam.date.strftime("%Y-%m-%d") if exam.date else None,
                "time": exam.time,
                "venue_id": exam.venue_id,
                "exam_length": exam.exam_length,
                "number_of_students": exam.number_of_students,
            }
            for exam in new_exams
        ]), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@exams_views.route('/api/exams/merge', methods=['POST'])
@jwt_required()
def merge_exams_view():
    authenticated_user = get_jwt_identity()
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401

    data = request.get_json()
    exam_ids = data.get('examIds')    

    if not exam_ids or not isinstance(exam_ids, list):
        return jsonify({'error': 'examIds must be a non-empty list'}), 400

    try:
        merged_exam, error = merge_exams(exam_ids)
        if error:
            return jsonify({'error': error}), 400

        return jsonify([
            {
                "id": merged_exam.id,
                "courseCode": merged_exam.courseCode,
                "exam_date": merged_exam.date.strftime("%Y-%m-%d") if merged_exam.date else None,
                "time": merged_exam.time,
                "venue_id": merged_exam.venue_id,
                "exam_length": merged_exam.exam_length,
                "number_of_students": merged_exam.number_of_students,
            }
        ]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

