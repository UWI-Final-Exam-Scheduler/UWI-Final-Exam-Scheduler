from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from App.controllers import enrollments
from App.models.admin import Admin
from flask_jwt_extended import jwt_required, current_user as jwt_current_user, get_jwt_identity

from.index import index_views

from App.controllers.enrollments import (
    get_all_enrollments,
    get_enrollments_by_student,
)
from App.controllers.auth import is_admin

enrollment_views = Blueprint('enrollment_views', __name__, template_folder='../templates')

@enrollment_views.route('/api/enrollments', methods=['GET'])
@jwt_required()
def get_enrollments_endpoint():
    authenticated_user = get_jwt_identity()

    # Ensure the user is authenticated before accessing enrollments
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
        
    try:
        enrollments = get_all_enrollments()
        if not enrollments:
            return jsonify({'error': 'No enrollments found'}), 404
        return jsonify(enrollments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@enrollment_views.route('/api/enrollments/<int:student_id>', methods=['GET'])
@jwt_required()
def get_enrollments_by_student_endpoint(student_id):
    authenticated_user = get_jwt_identity()

    # Ensure the user is authenticated before accessing enrollments
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
        
    try:
        enrollments = get_enrollments_by_student(student_id)
        if not enrollments:
            return jsonify({'error': f'No enrollments found for student ID {student_id}'}), 404
        return jsonify(enrollments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500