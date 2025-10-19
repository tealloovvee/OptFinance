import jwt
import datetime
from django.conf import settings
from django.contrib.auth.hashers import check_password
from registration.models import User


def generate_tokens(user):
    """
    Генерирует access и refresh токены для пользователя
    """
    payload = {
        'user_id': user.id,
        'login': user.login,
        'email': user.email,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }

    refresh_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME),
        'iat': datetime.datetime.utcnow(),
        'type': 'refresh'
    }

    access_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': settings.JWT_ACCESS_TOKEN_LIFETIME
    }


def verify_token(token):
    """
    Проверяет JWT токен и возвращает данные пользователя
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def authenticate_user(login_or_email, password):
    """
    Аутентифицирует пользователя по логину/email и паролю
    """
    try:
        user = User.objects.get(login=login_or_email)
    except User.DoesNotExist:
        try:
            user = User.objects.get(email=login_or_email)
        except User.DoesNotExist:
            return None

    if check_password(password, user.password_hash):
        return user
    return None


def get_user_from_token(token):
    """
    Получает пользователя из JWT токена
    """
    payload = verify_token(token)
    if not payload or payload.get('type') != 'access':
        return None

    try:
        user = User.objects.get(id=payload['user_id'])
        return user
    except User.DoesNotExist:
        return None
