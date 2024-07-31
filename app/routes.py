from flask import Blueprint, request, jsonify
from app import db
from app.models import User, UserRole
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from app.utils import send_password_reset_email
from sqlalchemy.exc import IntegrityError

api_bp = Blueprint('api', __name__)

# Register a new user
@api_bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    try:
        new_user = User(
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            role=UserRole[data.get('role', 'USER')]
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User registered successfully."}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "Username or email already exists."}), 400

# User login
@api_bp.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity={'id': user.id, 'role': user.role.name})
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid username or password."}), 401

# Password reset request
@api_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user:
        # Send reset email (implement email sending in utils)
        send_password_reset_email(user)
        return jsonify({"msg": "Password reset email sent."}), 200
    return jsonify({"msg": "User with this email not found."}), 404

# Update user details (admin only)
@api_bp.route('/user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found."}), 404

    if current_user['role'] != 'ADMIN' and current_user['id'] != user_id:
        return jsonify({"msg": "Permission denied."}), 403

    data = request.json
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

# Delete user (admin only)
@api_bp.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found."}), 404

    if current_user['role'] != 'ADMIN' and current_user['id'] != user_id:
        return jsonify({"msg": "Permission denied."}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted."}), 200
