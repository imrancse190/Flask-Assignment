from app import create_app, db
from models import User, UserRole

app = create_app()

def add_default_user():
    with app.app_context():
        # Check if the default user already exists
        if not User.query.filter_by(username='admin').first():
            default_user = User(
                username='admin',
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                role=UserRole.ADMIN,
                active=True
            )
            default_user.set_password('adminpassword')
            db.session.add(default_user)
            db.session.commit()
            print("Default user added.")
        else:
            print("Default user already exists.")

if __name__ == '__main__':
    add_default_user()
