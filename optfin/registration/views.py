from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from registration.models import User
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from .jwt_utils import generate_tokens, authenticate_user, verify_token
from .decorators import jwt_required
import json
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")

@require_http_methods(["GET"])
def get_user(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        return JsonResponse({
            "id": user.id,
            "login": user.login,
            "email": user.email,
            "role": user.role,
            "portfolios_created": user.portfolios_created,
            "created_at": user.created_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return JsonResponse({"error": "User not found"}, status=404)


@require_http_methods(["POST"])
def update_user(request, user_id):
    data = json.loads(request.body) if request.body else request.POST
    try:
        user = get_object_or_404(User, id=user_id)

        login = data.get('login')
        email = data.get('email')

        if login:
            user.login = login
        if email:
            user.email = email

        user.save()
        logger.info(f"User updated: {user.login}")
        return JsonResponse({
            "status": "ok",
            "id": user.id,
            "login": user.login,
            "email": user.email,
            "role": user.role,
            "portfolios_created": user.portfolios_created,
            "created_at": user.created_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return JsonResponse({"error": "Failed to update user"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """
    Регистрация нового пользователя
    """
    try:
        data = json.loads(request.body)
        login = data.get('login')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not login or not email or not password:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if User.objects.filter(login=login).exists():
            return JsonResponse({"error": "User with this login already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "User with this email already exists"}, status=400)

        password_hash = make_password(password)

        user = User.objects.create(
            login=login,
            email=email,
            password_hash=password_hash,
            role=role
        )

        tokens = generate_tokens(user)
        user.refresh_token = tokens["refresh_token"]
        user.save()

        return JsonResponse({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "login": user.login,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat()
            },
            "tokens": tokens
        })

    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return JsonResponse({"error": "Registration failed"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    Вход пользователя
    """
    try:
        data = json.loads(request.body)
        login_or_email = data.get('login')
        password = data.get('password')

        if not login_or_email or not password:
            return JsonResponse({"error": "Missing credentials"}, status=400)

        user = authenticate_user(login_or_email, password)
        if not user:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        tokens = generate_tokens(user)
        user.refresh_token = tokens["refresh_token"]
        user.save()

        return JsonResponse({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "login": user.login,
                "email": user.email,
                "role": user.role,
                "portfolios_created": user.portfolios_created,
                "created_at": user.created_at.isoformat()
            },
            "tokens": tokens
        })

    except Exception as e:
        logger.error(f"Error during login: {e}")
        return JsonResponse({"error": "Login failed"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    """
    Обновление токенов
    """
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return JsonResponse({"error": "Missing refresh token"}, status=400)

        payload = verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return JsonResponse({"error": "Invalid refresh token"}, status=401)

        user = User.objects.get(id=payload['user_id'])
        if user.refresh_token != refresh_token:
            return JsonResponse({"error": "Refresh token no longer valid"}, status=401)

        tokens = generate_tokens(user)
        user.refresh_token = tokens["refresh_token"]
        user.save()

        return JsonResponse({
            "message": "Token refreshed successfully",
            "tokens": tokens
        })

    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return JsonResponse({"error": "Token refresh failed"}, status=500)


@jwt_required
@require_http_methods(["GET"])
def get_profile(request):
    """
    Профиль текущего пользователя
    """
    user = request.user
    return JsonResponse({
        "id": user.id,
        "login": user.login,
        "email": user.email,
        "role": user.role,
        "portfolios_created": user.portfolios_created,
        "created_at": user.created_at.isoformat()
    })


@jwt_required
@require_http_methods(["POST"])
def logout(request):
    """
    Выход пользователя — аннулирует refresh-токен
    """
    user = request.user
    user.refresh_token = None
    user.save()
    return JsonResponse({"message": "Logged out successfully"})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        user.delete()
        logger.info(f"User deleted: {user_id}")
        return JsonResponse({"status": "deleted"})
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return JsonResponse({"error": "Failed to delete user"}, status=500)
