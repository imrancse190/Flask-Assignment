from flask import Blueprint, request, jsonify
from app import db
from .models import User, UserRole
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from app.utils import send_password_reset_email
from sqlalchemy.exc import IntegrityError

api_bp = Blueprint('api', __name__)

@api_bp.route('/auth/register', methods=['POST'])
def register_user():
    data = request.json
    try:
       
        new_user = User(
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            role=UserRole.USER 
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User registered successfully."}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "Username or email already exists."}), 400
    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/auth/login', methods=['POST'])
def login_user():
    data = request.json
    
    try:
        user = User.query.filter_by(username=data['username']).first()
        print(user)
        if user and not user.active:
            return jsonify({"msg": "Your account is deactivated."}), 401
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity={'id': user.id, 'username': user.username, 'role': user.role.name})
            return jsonify(access_token=access_token), 200
        return jsonify({"msg": "Invalid username or password."}), 401
    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

@api_bp.route('auth/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user:
        send_password_reset_email(user)
        return jsonify({"msg": "Password reset email sent."}), 200
    return jsonify({"msg": "User with this email not found."}), 404

@api_bp.route('/user/<string:username>', methods=['PUT'])
@jwt_required()
def update_user(username):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Request body must be JSON."}), 400

        current_user = get_jwt_identity()
        current_user_id = current_user['id']
        current_user_role = current_user['role']

        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"msg": "User not found."}), 404

        # Admins can update their own info or that of non-admin users
        if current_user_role == 'ADMIN':
            if user.role == UserRole.ADMIN and current_user['username'] != username:
                return jsonify({"msg": "Permission denied. You cannot update another admin."}), 403
        else:
            return jsonify({"msg": "Only admin can update information."}), 403

        # Update user fields
        if 'username' in data:
            user.username = data['username']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])
        if 'active' in data:
            user.active = data['active']
        
        db.session.commit()
        return jsonify({"msg": "User details updated."}), 200
    
    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500


@api_bp.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"msg": "Request body must be JSON."}), 400

        username = data.get('username')
        
        if not username:
            return jsonify({"msg": "Username is required in the request body."}), 400

        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({"msg": "Invalid token or user not found."}), 401

        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"msg": "User not found."}), 404


        if current_user['role'] != 'ADMIN':
            return jsonify({"msg": "Permission denied. You are not an admin."}), 403

        if  current_user['username'] == username or user.role == 'ADMIN':
            return jsonify({"msg": "Permission denied. You cannot delete an admin."}), 403

        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted."}), 200

    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
