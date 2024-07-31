from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, UserRole
from app.schemas import user_schema, users_schema

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users)), 200

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user)), 200

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user = User.query.get_or_404(user_id)
    
    if current_user.role != UserRole.ADMIN and current_user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    
    if current_user.role == UserRole.ADMIN:
        user.active = data.get('active', user.active)
        user.role = UserRole(data.get('role', user.role.value))
    
    db.session.commit()
    return jsonify(user_schema.dump(user)), 200

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != UserRole.ADMIN:
        return jsonify({'message': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200