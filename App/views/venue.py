from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from App.models.admin import Admin
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    create_venue,
    get_all_venues,
    get_all_venues_json,
    is_admin
)

venue_views = Blueprint('venue_views', __name__, template_folder='../templates')

@venue_views.route('/api/venues', methods=['GET'])
@jwt_required()
def get_venues():
    authenticated_user = jwt_current_user

    # Ensure the user is authenticated before accessing venues
    if not is_admin(authenticated_user.id):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
        
    try:
        venues = get_all_venues_json()
        if venues is None:
            return jsonify({'error': 'No venues found'}), 404
        return jsonify(venues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@venue_views.route('/api/venues/<venue_name>', methods=['GET'])
@jwt_required()
def get_venue_by_name(venue_name):
    authenticated_user = jwt_current_user

    # Ensure the user is authenticated before accessing venues
    if not is_admin(authenticated_user.id):
        return jsonify({'error': 'Access denied - Unauthorized user'}), 401
        
    try:
        venues = get_all_venues_json()
        if venues is None:
            return jsonify({'error': 'No venues found'}), 404
        for venue in venues:
            if venue['name'].lower() == venue_name.lower():
                return jsonify(venue), 200
        return jsonify({'error': 'Venue not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500