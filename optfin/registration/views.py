from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from registration.models import User
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def create_user(request):
    data = request.POST
    login = data.get('login')
    email = data.get('email')
    password = data.get('password')

    if not login or not email or not password:
        logger.warning("Create user failed: missing required fields")
        return JsonResponse({"error": "Missing required fields"}, status=400)

    password_hash = make_password(password)

    try:
        user = User.objects.create(
            login=login,
            email=email,
            password_hash=password_hash
        )
        logger.info(f"User created: {user.login}")
        return JsonResponse({
            "id": user.id,
            "login": user.login,
            "email": user.email,
            "role": user.role,
            "portfolios_created": user.portfolios_created,
            "created_at": user.created_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return JsonResponse({"error": "Failed to create user"}, status=500)


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
    data = request.POST
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
