from app import ma
from app.models import User, UserRole

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password',)

    role = ma.Enum(UserRole)

user_schema = UserSchema()
users_schema = UserSchema(many=True)