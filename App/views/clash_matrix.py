from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.controllers.auth import is_admin
from App.controllers.clash_matrix import view_conflicting_courses, view_course_clashes, normalize_percentage_threshold

clash_matrix_views = Blueprint("clash_matrix_views",  __name__, template_folder="../templates",)

@clash_matrix_views.route("/api/course/<course_code>/clash-matrix", methods=["GET"])
@jwt_required()
def get_course_clashes(course_code):
    authenticated_user = get_jwt_identity()

    if not is_admin(authenticated_user):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        abs_threshold_raw = request.args.get("abs_threshold", default=5)
        perc_threshold_raw = request.args.get("perc_threshold", default=0.1)

        try:
            abs_threshold = int(abs_threshold_raw)
        except (ValueError, TypeError):
            return jsonify({"error": "Absolute threshold must be an integer"}), 400

        try:
            perc_threshold = float(perc_threshold_raw)
        except (ValueError, TypeError):
            return jsonify({"error": "Percentage threshold must be a float"}), 400
        
        if abs_threshold < 0:
            return jsonify({"error": "Absolute threshold must be non-negative"}), 400

        perc_threshold = normalize_percentage_threshold(perc_threshold)

        course_clashes_data = view_course_clashes(
            course_code,
            abs_threshold=abs_threshold,
            perc_threshold=perc_threshold,
        )
        return jsonify(course_clashes_data), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 #mock test needed


@clash_matrix_views.route("/api/clash-matrix", methods=["GET"])
@jwt_required()
def get_global_clash_matrix():
    authenticated_user = get_jwt_identity()

    if not is_admin(authenticated_user):
        return jsonify({"error": "Access denied - Unauthorized user"}), 403

    try:
        abs_threshold_raw = request.args.get("abs_threshold", default=5)
        perc_threshold_raw = request.args.get("perc_threshold", default=0.1)

        try:
            abs_threshold = int(abs_threshold_raw)
        except (ValueError, TypeError):
            return jsonify({"error": "Absolute threshold must be an integer"}), 400

        try:
            perc_threshold = float(perc_threshold_raw)
        except (ValueError, TypeError):
            return jsonify({"error": "Percentage threshold must be a float"}), 400
        
        if abs_threshold < 0:
            return jsonify({"error": "Absolute threshold must be non-negative"}), 400

        perc_threshold = normalize_percentage_threshold(perc_threshold)

        conflicts_data = view_conflicting_courses(
            abs_threshold=abs_threshold,
            perc_threshold=perc_threshold,
        )
        return jsonify(conflicts_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 #mock test needed