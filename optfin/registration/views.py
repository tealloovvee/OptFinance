
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from registration.models import User
import logging

logger = logging.getLogger(__name__)

def create_user(request):
    if request.method == "POST":
        data = request.POST
        user = User.objects.create(
            login=data['login'],
            email=data['email'],
            password_hash=data['password']
        )
        logger.info(f"User created: {user.login}")
        return JsonResponse({"id": user.id, "login": user.login})

def get_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return JsonResponse({"id": user.id, "login": user.login, "email": user.email})

def update_user(request, user_id):
    if request.method == "POST":
        data = request.POST
        user = get_object_or_404(User, id=user_id)
        user.login = data.get('login', user.login)
        user.email = data.get('email', user.email)
        user.save()
        logger.info(f"User updated: {user.login}")
        return JsonResponse({"status": "ok"})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    logger.info(f"User deleted: {user_id}")
    return JsonResponse({"status": "deleted"})

