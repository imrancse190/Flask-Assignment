from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User, UserRole
from . import db
from .utils import send_password_reset_email
from sqlalchemy.exc import IntegrityError

def register_routes(api):
    user_ns = api.namespace('user', description='User operations')
    
    user_model = api.model('User', {
        'id': fields.Integer(readonly=True),
        'username': fields.String(required=True),
        'first_name': fields.String(required=True),
        'last_name': fields.String(required=True),
        'email': fields.String(required=True),
        'role': fields.String(enum=[role.name for role in UserRole]),
        'active': fields.Boolean()
    })

    register_model = api.model('RegisterUser', {
        'username': fields.String(required=True),
        'first_name': fields.String(required=True),
        'last_name': fields.String(required=True),
        'email': fields.String(required=True),
        'password': fields.String(required=True)
    })

    login_model = api.model('Login', {
        'username': fields.String(required=True),
        'password': fields.String(required=True)
    })

    @user_ns.route('/register')
    class UserRegister(Resource):
        @user_ns.expect(register_model)
        @user_ns.marshal_with(user_model, code=201)
        def post(self):
            '''Register a new user'''
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
                return new_user, 201
            except IntegrityError:
                db.session.rollback()
                api.abort(400, "Username or email already exists.")

    @user_ns.route('/login')
    class UserLogin(Resource):
        @user_ns.expect(login_model)
        def post(self):
            '''Login and receive an access token'''
            data = request.json
            user = User.query.filter_by(username=data['username']).first()
            if user and user.check_password(data['password']):
                if not user.active:
                    return {'message': 'Your account is deactivated.'}, 401
                access_token = create_access_token(identity={'id': user.id, 'username': user.username, 'role': user.role.name})
                return {'access_token': access_token}, 200
            return {'message': 'Invalid username or password.'}, 401

    @user_ns.route('/reset_password')
    class PasswordReset(Resource):
        @user_ns.expect(api.model('ResetPassword', {'email': fields.String(required=True)}))
        def post(self):
            '''Request a password reset'''
            data = request.json
            user = User.query.filter_by(email=data['email']).first()
            if user:
                send_password_reset_email(user)
                return {'message': 'Password reset email sent.'}, 200
            return {'message': 'User with this email not found.'}, 404

    @user_ns.route('/<string:username>')
    class UserResource(Resource):
        @user_ns.marshal_with(user_model)
        @jwt_required()
        def get(self, username):
            '''Get user details'''
            current_user = get_jwt_identity()
            if current_user['role'] != 'ADMIN' and current_user['username'] != username:
                api.abort(403, "Permission denied.")
            user = User.query.filter_by(username=username).first()
            if not user:
                api.abort(404, "User not found.")
            return user

        @user_ns.expect(user_model)
        @user_ns.marshal_with(user_model)
        @user_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Bearer TOKEN'}})
        @jwt_required()
        def put(self, username):
            '''Update user details'''
            current_user = get_jwt_identity()
            if current_user['role'] != 'ADMIN' and current_user['username'] != username:
                api.abort(403, "Permission denied.")
            user = User.query.filter_by(username=username).first()
            if not user:
                api.abort(404, "User not found.")
            data = request.json
            for key, value in data.items():
                if key != 'id' and hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
            return user

        @jwt_required()
        def delete(self, username):
            '''Delete a user'''
            current_user = get_jwt_identity()
            if current_user['role'] != 'ADMIN':
                api.abort(403, "Permission denied.")
            user = User.query.filter_by(username=username).first()
            if not user:
                api.abort(404, "User not found.")
            if user.role == UserRole.ADMIN:
                api.abort(403, "Cannot delete an admin user.")
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted.'}, 200