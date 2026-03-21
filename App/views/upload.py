from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import tempfile, os

from App.models import Course, Student, Enrollment, Venue
from App.database import db
from App.controllers import (import_courses_from_csv, import_students_from_csv, import_enrollments_from_csv, import_venues_from_csv)

upload_views = Blueprint('upload_views', __name__, template_folder='../templates')

ALLOWED_EXTENSIONS = {"csv", "pdf", "xlsx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_views.route('/api/upload', methods=['POST'])
@jwt_required()
def receive_file_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    ext = file.filename.rsplit(".", 1)[1].lower()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
    tmp_file_path = tmp_file.name
    tmp_file.close()

    try:
        file.save(tmp_file_path)
        fname = file.filename.lower()

        if "course" in fname:
            Course.query.delete()
            db.session.commit()
            msg = import_courses_from_csv(tmp_file_path)
        elif "student" in fname:
            Student.query.delete()
            db.session.commit()
            msg = import_students_from_csv(tmp_file_path)
        elif "enrollment" in fname:
            Enrollment.query.delete()
            db.session.commit()
            msg = import_enrollments_from_csv(tmp_file_path)
        elif "venue" in fname:
            Venue.query.delete()
            db.session.commit()
            msg = import_venues_from_csv(tmp_file_path)
        else:
            return jsonify({"error": "Could not determine file type from filename"}), 400
        
        return jsonify({"message": msg})
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)