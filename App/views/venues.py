from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from App.controllers import venue
from App.models.admin import Admin
from flask_jwt_extended import jwt_required, current_user as jwt_current_user, get_jwt_identity

from.index import index_views

from App.controllers.venue import (
    get_all_venues,
    get_venue_by_name,
)
from App.controllers.auth import is_admin

venue_views = Blueprint('venue_views', __name__, template_folder='../templates')

@venue_views.route('/api/venues', methods=['GET'])
@jwt_required()
def get_venues_endpoint():
    authenticated_user = get_jwt_identity()

    # Ensure the user is authenticated before accessing venues
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 403
        
    try:
        venues = get_all_venues()
        if venues is None:
            return jsonify({'error': 'No venues found'}), 404  #mock test needed
        return jsonify(venues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 #mock test needed
    
@venue_views.route('/api/venues/<venue_name>', methods=['GET'])
@jwt_required()
def get_venue_by_name_endpoint(venue_name):
    authenticated_user = get_jwt_identity()

    # Ensure the user is authenticated before accessing venues
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 403
        
    try:
        venue = get_venue_by_name(venue_name)
        if isinstance(venue, str):
            return jsonify({'error': venue}), 404
        return jsonify(venue), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 #mock test needed