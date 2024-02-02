from app import db, secret_key, encrypt
from models.User import User


def validate_user_credentials(user_name: str, password: str) -> (int, str, dict):
    status = 401
    message = 'Incorrect username or password'
    user = None
    try:
        user = (
            db.session.query(User)
            .filter(User.user_name == user_name)
            .first()
        )
        if user:
            entered_password_enc = encrypt(secret_key=secret_key, plain_text=password)
            if entered_password_enc == user.password:
                status = 200
                message = 'User successfully authenticated'
                user = {
                    'user_name': user.user_name, 'first_name': user.first_name,
                    'last_name': user.last_name, 'user_email': user.user_email,
                    'roles': [role.role_name for role in user.roles],
                    'entities': [entity.entity_name for entity in user.entities],
                }
    except Exception as e:
        message = str(e)
        status = 500

    return status, message, user
