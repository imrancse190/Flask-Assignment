from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.models import User  # Ensure models are imported

    @app.route('/test_db')
    def test_db():
        try:
            db.session.execute('SELECT 1')
            return jsonify({'message': 'Database connected successfully!'})
        except Exception as e:
            return jsonify({'message': 'Database connection failed!', 'error': str(e)})

    return app
