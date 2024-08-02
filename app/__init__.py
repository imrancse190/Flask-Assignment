from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_mail import Mail
from config import Config

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = Api(
    title='User Management API',
    version='1.0',
    description='A user management API with Flask-RESTX'
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    api.init_app(app)
    
    from .routes import register_routes
    register_routes(api)
    
    return app