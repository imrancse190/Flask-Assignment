from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_password_reset_email(user):
    token = create_access_token(identity={'id': user.id}, expires_delta=False)
    reset_link = f"{current_app.config['FRONTEND_URL']}/reset_password?token={token}"
    
    msg = Message('Password Reset Request',
                  sender='noreply@example.com',
                  recipients=[user.email])
    msg.body = f"To reset your password, visit the following link: {reset_link}"
    
    with current_app.app_context():
        mail.send(msg)
