from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, decode_token
from App.controllers.user import get_user_by_username 

from.index import index_views

from App.controllers import (
    login,

)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


'''
Page/Action Routes
'''    

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/auth/login', methods=['POST'])
def user_login_api():
    data = request.json   #still need to implement better error handling for invalid json

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
        return jsonify(error='bad username or password given'), 401
    
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

@auth_views.route('/api/auth/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response