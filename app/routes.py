from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User, UserRole
from . import db
from .utils import send_password_reset_email, verify_reset_token, generate_reset_token
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

    reset_password_request_model = api.model('ResetPasswordRequest', {
        'username':fields.String(required=True),
        'email': fields.String(required=True)
    })

    reset_password_model = api.model('ResetPassword', {
        'token': fields.String(required=True),
        'new_password': fields.String(required=True)
    })

    @user_ns.route('/register')
    class UserRegister(Resource):
        @user_ns.expect(register_model)
        def post(self):
            '''Register a new user'''
            try:
                data = request.json
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
                return {'msg': "User registered successfully."}, 201
            except IntegrityError:
                db.session.rollback()
                return {'msg': "Username or email already exists."}, 400
            except Exception as e:
                return {'msg': f"An error occurred: {str(e)}"}, 500

    @user_ns.route('/login')
    class UserLogin(Resource):
        @user_ns.expect(login_model)
        def post(self):
            '''Login and receive an access token'''
            try:
                data = request.json
                user = User.query.filter_by(username=data['username']).first()
                if user and not user.active:
                    return {'msg': "Your account is deactivated."}, 401
                if user and user.check_password(data['password']):
                    access_token = create_access_token(identity={'id': user.id, 'username': user.username, 'role': user.role.name})
                    return {'msg': "Login successful.", 'access_token': f'Bearer {access_token}'}, 200
                return {'msg': "Invalid username or password."}, 401
            except Exception as e:
                return {'msg': f"An error occurred: {str(e)}"}, 500

    @user_ns.route('/forget_password')
    class ForgetPassword(Resource):
        @user_ns.expect(reset_password_request_model)
        def post(self):
            '''Request a password reset token'''
            try:
                data = request.json
                user = User.query.filter_by(username=data['username']).first()
                if user and not user.active:
                    return {'msg': "Your account is deactivated."}, 401
                
                
                if user:
                    
                    token = generate_reset_token(user)
                    print(user)
                    # send_password_reset_email(user, token)
                    return ({
                        'msg': 'Token generate successful',
                        'Token': token
                    }), 200
                return {'msg': 'User with this email not found.'}, 404
            except Exception as e:
                return {'msg': f"An error occurred: {str(e)}"}, 500

    @user_ns.route('/reset_password')
    class ResetPassword(Resource):
        @user_ns.expect(reset_password_model)
        def post(self):
            '''Reset password using the token'''
            try:
                data = request.json
                user = verify_reset_token(data['token'])
                if user:
                    user.set_password(data['new_password'])
                    db.session.commit()
                    return {'msg': 'Password has been reset.'}, 200
                return {'msg': 'Invalid or expired token.'}, 400
            except Exception as e:
                return {'msg': f"An error occurred: {str(e)}"}, 500

    @user_ns.route('/<string:username>')
    class UserResource(Resource):
        @user_ns.marshal_with(user_model)
        @user_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Required JWT token', 'required': True}})
        @jwt_required()
        def get(self, username):
            '''Get user details'''
            current_user = get_jwt_identity()
            if current_user['role'] != UserRole.ADMIN and current_user['username'] != username:
                api.abort(403, "Permission denied.")
            
            user = User.query.filter_by(username=username).first()
            if not user:
                api.abort(404, "User not found.")
            return user

        @user_ns.expect(user_model)
        @user_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Required JWT token', 'required': True}})
        @jwt_required()
        def put(self, username):
            '''Update user details'''
            try:
                data = request.json
                if not data:
                    return {'msg': "Request body must be JSON."}, 400

                current_user = get_jwt_identity()
                current_user_role = current_user['role']

                user = User.query.filter_by(username=username).first()
                if not user:
                    return {'msg': "User not found."}, 404

                if current_user_role == UserRole.ADMIN:
                    if user.role == UserRole.ADMIN and current_user['username'] != username:
                        return {'msg': "Permission denied. You cannot update another ADMIN."}, 403
                else:
                    return {'msg': "Only ADMIN can update information."}, 403

                updated_fields = {}
                if 'username' in data:
                    user.username = data['username']
                    updated_fields['username'] = user.username
                if 'first_name' in data:
                    user.first_name = data['first_name']
                    updated_fields['first_name'] = user.first_name
                if 'last_name' in data:
                    user.last_name = data['last_name']
                    updated_fields['last_name'] = user.last_name
                if 'email' in data:
                    user.email = data['email']
                    updated_fields['email'] = user.email
                if 'password' in data:
                    user.set_password(data['password'])
                if 'active' in data:
                    user.active = data['active']
                    updated_fields['active'] = user.active
                if 'role' in data:
                    user.role = UserRole[data['role']]
                    updated_fields['role'] = user.role.name

                db.session.commit()
                return {'msg': "User details updated."}, 200
            
            except Exception as e:
                return {'msg': f"An error occurred: {str(e)}"}, 500

        @user_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Required JWT token', 'required': True}})
        @jwt_required()
        def delete(self, username):
            '''Delete a user'''
            try:
                current_user = get_jwt_identity()
                if not current_user:
                    return {'msg': "Invalid token or user not found."}, 401

                user = User.query.filter_by(username=username).first()
                if not user:
                    return {'msg': "User not found."}, 404

                if current_user['role'] != UserRole.ADMIN:
                    return {'msg': "Permission denied. Only ADMIN can access."}, 403

                if current_user['username'] == username or user.role == UserRole.ADMIN:
                    return {'msg': "Permission denied. You cannot delete an ADMIN and yourself."}, 403

                db.session.delete(user)
                db.session.commit()
                return {'msg': "User deleted."}, 200

            except Exception as e:
                return {'msg': f"An error occurred: {str(e)}"}, 500
