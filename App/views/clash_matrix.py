from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required,get_jwt_identity, current_user as jwt_current_user   
from App.models import ClashMatrix, Enrollment
from App.controllers.auth import is_admin
from App.controllers.clash_matrix import view_conflicting_courses, view_course_clashes

clash_matrix_views = Blueprint('clash_matrix_views', __name__, template_folder='../templates')


@clash_matrix_views.route('/api/course/<course_code>/clash-matrix', methods=['GET'])
@jwt_required()
def get_course_clashes(course_code):
    authenticated_user =  get_jwt_identity()

    # Ensure the user is authenticated before accessing course clashes
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        abs_threshold = request.args.get('abs_threshold', default=5, type=int)
        perc_threshold = request.args.get('perc_threshold', default=0.1, type=float)

        if abs_threshold < 0:
            return jsonify({'error': 'Absolute threshold must be non-negative'}), 400
        if not (0 <= perc_threshold <= 100):
            return jsonify({'error': 'Percentage threshold must be between 0 and 100'}), 400

        course_clashes_data = view_course_clashes(course_code, abs_threshold=abs_threshold, perc_threshold=perc_threshold)
        if isinstance(course_clashes_data, str):  # Check if it's an error message
            return jsonify({'error': course_clashes_data}), 404
        return jsonify(course_clashes_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@clash_matrix_views.route('/api/clash-matrix', methods=['GET'])
@jwt_required()
def get_global_clash_matrix():
    authenticated_user = get_jwt_identity()
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        abs_threshold = request.args.get('abs_threshold', default=5, type=int)
        perc_threshold = request.args.get('perc_threshold', default=0.1, type=float)

        if abs_threshold < 0:
            return jsonify({'error': 'Absolute threshold must be non-negative'}), 400
        if not (0 <= perc_threshold <= 100):
            return jsonify({'error': 'Percentage threshold must be between 0 and 100'}), 400

        # This should return the clash matrix for ALL courses, not just one
        conflicts_data = view_conflicting_courses(abs_threshold=abs_threshold, perc_threshold=perc_threshold)
        return jsonify(conflicts_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500