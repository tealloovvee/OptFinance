from django.shortcuts import get_object_or_404
from registration.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .jwt_utils import generate_tokens, authenticate_user, verify_token
from .decorators import jwt_required
from telegramBot.bot import send_message_to_admin
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")


@api_view(['GET'])
@jwt_required
def get_user(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        return Response({
            "id": user.id,
            "login": user.login,
            "email": user.email,
            "role": user.role,
            "portfolios_created": user.portfolios_created,
            "created_at": user.created_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@jwt_required
def update_user(request, user_id):
    try:
        data = request.data
        user = get_object_or_404(User, id=user_id)

        login = data.get('login')
        email = data.get('email')

        if login:
            user.login = login
        if email:
            user.email = email

        user.save()
        logger.info(f"User updated: {user.login}")
        return Response({
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
        return Response({"error": "Failed to update user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        data = request.data
        login = data.get('login')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not login or not email or not password:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(login=login).exists():
            return Response({"error": "User with this login already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

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

        return Response({
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
        return Response({"error": "Registration failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        data = request.data
        login_or_email = data.get('login')
        password = data.get('password')

        if not login_or_email or not password:
            return Response({"error": "Missing credentials"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate_user(login_or_email, password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = generate_tokens(user)
        user.refresh_token = tokens["refresh_token"]
        user.save()

        return Response({
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
        return Response({"error": "Login failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def refresh_token(request):
    try:
        data = request.data
        refresh_token_value = data.get('refresh_token')
        if not refresh_token_value:
            return Response({"error": "Missing refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        payload = verify_token(refresh_token_value)
        if not payload or payload.get('type') != 'refresh':
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.get(id=payload['user_id'])
        if user.refresh_token != refresh_token_value:
            return Response({"error": "Refresh token no longer valid"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = generate_tokens(user)
        user.refresh_token = tokens["refresh_token"]
        user.save()

        return Response({
            "message": "Token refreshed successfully",
            "tokens": tokens
        })
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return Response({"error": "Token refresh failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@jwt_required
def get_profile(request):
    user = request.user
    return Response({
        "id": user.id,
        "login": user.login,
        "email": user.email,
        "role": user.role,
        "portfolios_created": user.portfolios_created,
        "created_at": user.created_at.isoformat()
    })


@api_view(['POST'])
@jwt_required
def logout(request):
    user = request.user
    user.refresh_token = None
    user.save()
    return Response({"message": "Logged out successfully"})


@api_view(['DELETE'])
@jwt_required
def delete_user(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        user.delete()
        logger.info(f"User deleted: {user_id}")
        return Response({"status": "deleted"})
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return Response({"error": "Failed to delete user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@jwt_required
def send_message(request):
    try:
        data = request.data
        text = data.get("message")
        if not text:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(send_message_to_admin(user.id, user.login, text))
                    )
                    future.result(timeout=5)
            else:
                loop.run_until_complete(send_message_to_admin(user.id, user.login, text))
        except RuntimeError:
            asyncio.run(send_message_to_admin(user.id, user.login, text))

        return Response({"status": "ok"})
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return Response({"error": "Failed to send message"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
