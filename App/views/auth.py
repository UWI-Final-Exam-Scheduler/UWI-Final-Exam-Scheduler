from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from App.controllers.auth import is_admin
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, decode_token, get_jwt_identity, get_jwt
from App.models import User
from App.controllers.user import get_user_by_username 
from App.controllers.user_preference import get_user_preferences, update_user_preferences
from.index import index_views
from App.controllers import login

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
API Routes
'''

@auth_views.route('/api/auth/login', methods=['POST'])
def user_login_api():
    data = request.json 

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify(error='username and password are required'), 400
    
    user = get_user_by_username(username)
    if not user:
        return jsonify(error="invalid credentials"), 401

    if not user.check_password(password):
        return jsonify(error="incorrect password"), 401
    
    token = login(username, password)
    if not token:
        return jsonify(error="bad username or password given"), 401
    
    decoded_token = decode_token(token)
    user_id = decoded_token.get("sub")
    username = decoded_token.get("username")
    role = decoded_token.get("role")

    response = jsonify(
                    message='login successful',
                    access_token=token,
                    user_id=user_id,
                    username=username,
                    role=role
                )
    set_access_cookies(response, token)
    return response, 200


@auth_views.route('/api/auth/preferences', methods=['GET'])
@jwt_required()
def get_user_preferences_route():
    authenticated_user = get_jwt_identity() 
    
    if not is_admin(authenticated_user):
        return jsonify({'error': 'Access denied - Unauthorized'}), 401
    
    preferences = get_user_preferences(authenticated_user)

    if preferences is None:
        return jsonify(error='User preferences not found'), 404 #mock test needed
    return jsonify(preferences), 200
    

@auth_views.route('/api/auth/preferences', methods=['PUT'])
@jwt_required()
def update_user_preferences_route():
    authenticated_user = get_jwt_identity() 
    data = request.json or {}

    preferences = update_user_preferences(authenticated_user, **data)

    if preferences is None:
        return jsonify(error='Failed to update user preferences'), 400
    return jsonify(preferences), 200


@auth_views.route('/api/auth/identify', methods=['GET'])
@jwt_required()
def identify():
    try:
        claims = get_jwt()
        user_id = get_jwt_identity()  
        username = claims.get('username')  
        role = claims.get('role')
        
        return jsonify({
            'user_id': user_id,
            'username': username,
            'role': role,
            'message': f'Logged in as {username} ({role})'
        }), 200
    except Exception as e:
        return jsonify(error='Unable to identify user'), 401 #mock test needed

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response